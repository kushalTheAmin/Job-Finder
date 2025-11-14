"""
Narrative Repositioner - AI-driven resume narrative transformation.
Repositions candidate's story to match target role emphasis.
100% AI-powered.
"""

import logging
import json
from typing import Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class NarrativeRepositioner:
    """Repositions resume narrative using AI based on role analysis."""

    def __init__(self, config: Any):
        """Initialize with config."""
        self.config = config
        self.project_id = config.project_id
        self.location = config.get('google_cloud', 'vertex_ai', 'location', default='us-central1')
        self.model_name = config.get('resume_customization', 'repositioning_model', default='gemini-2.5-flash')

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)

        logger.info(f"NarrativeRepositioner initialized with model: {self.model_name}")

    def reposition(
        self,
        resume: Dict[str, Any],
        repositioning_strategy: Dict[str, Any],
        job_title: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Reposition resume narrative based on strategy from RoleIntelligenceAnalyzer.

        Args:
            resume: Original resume JSON
            repositioning_strategy: Strategy from RoleIntelligenceAnalyzer
            job_title: Target job title
            job_description: Target job description

        Returns:
            Repositioned resume JSON with narrative transformed
        """
        logger.info(f"Repositioning narrative for: {job_title}")

        # If no repositioning needed, return original
        if not repositioning_strategy or repositioning_strategy.get('narrative_reframe') == 'Present experience as-is':
            logger.info("No repositioning needed")
            return resume

        # Build AI prompt
        prompt = self._build_repositioning_prompt(
            resume, repositioning_strategy, job_title, job_description
        )

        try:
            # Call AI
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            repositioned_resume = self._parse_ai_response(result_text, resume)

            logger.info("Narrative repositioning complete")

            return repositioned_resume

        except Exception as e:
            logger.error(f"Error in narrative repositioning: {str(e)}")
            # Return original resume on error
            return resume

    def _build_repositioning_prompt(
        self,
        resume: Dict[str, Any],
        strategy: Dict[str, Any],
        job_title: str,
        job_description: str
    ) -> str:
        """Build the AI prompt for narrative repositioning."""

        prompt = f"""You are an expert resume writer specializing in career repositioning and narrative transformation.

TASK: Rewrite this resume to reposition the candidate for a {job_title} role.

TARGET JOB TITLE: {job_title}

TARGET JOB DESCRIPTION (first 2000 chars):
{job_description[:2000]}

REPOSITIONING STRATEGY:
{json.dumps(strategy, indent=2)}

CURRENT RESUME:
{json.dumps(resume, indent=2)}

YOUR JOB: Transform this resume to match the target role emphasis.

INSTRUCTIONS:

1. PROFESSIONAL SUMMARY REWRITE:
   - Replace current summary with the one from repositioning_strategy
   - Make it role-specific and compelling
   - 2-3 sentences maximum
   - Lead with target role identity (e.g., "Backend Engineer with...")

2. EXPERIENCE NARRATIVE TRANSFORMATION:

   A. For sections to EMPHASIZE (expand, add detail):
      - Expand bullets to 2-3 lines with architectural context
      - Add system design thinking and decision-making
      - Highlight technical depth relevant to target role
      - Include scalability, performance, operational concerns
      - Show architectural tradeoffs and reasoning

      Example transformation:
      Before: "Built microservices architecture"
      After: "Architected microservices platform using Node.js and Redis, designing service boundaries to enable independent team deployment while maintaining data consistency through event sourcing patterns. Reduced deployment time from days to hours."

   B. For sections to DE-EMPHASIZE (condense):
      - Reduce to single line, factual statements
      - Remove metrics if not critical
      - Keep it accurate but minimal

      Example transformation:
      Before: "Built enterprise component library (50+ components) with design system and Storybook docs—reduced new feature development time by 30%"
      After: "Developed reusable component library for consistent UI across applications"

   C. For bullets to REFRAME (change angle):
      - Use the example rewrites from repositioning_strategy
      - Emphasize the aspect that matches target role
      - Don't change the core facts, just the presentation angle

      Example:
      Original angle: Frontend component architecture
      New angle: Full-stack integration with backend services
      Rewrite: Instead of "Built React components", say "Integrated React frontend with Node.js APIs and Redis caching layer"

3. EXPERIENCE REORDERING:
   - Within each job, put most relevant bullets FIRST
   - Most impressive, role-relevant achievements at the top
   - Less relevant work moves to bottom or gets removed

4. DETAIL LEVEL VARIATION (CRITICAL):
   - Emphasized bullets: 2-3 lines, rich architectural detail
   - Standard bullets: 1-2 lines, good detail
   - De-emphasized bullets: 1 line, factual only
   - This creates natural emphasis hierarchy

5. ROLE-SPECIFIC LANGUAGE:
   - If target is Backend: Use "service architecture", "API design", "data modeling", "system performance"
   - If target is Frontend: Use "user experience", "component architecture", "performance optimization", "accessibility"
   - If target is Full-Stack: Balance both, lead with the primary focus
   - Use terminology from the job description

6. MAINTAIN AUTHENTICITY:
   - DO NOT fabricate experience that doesn't exist
   - DO NOT add technologies the candidate never used
   - DO reframe existing experience to highlight relevant aspects
   - DO add context that was implied but not stated

7. SKILLS SECTION:
   - Reorder skills to match target role priority
   - Most relevant skills first in each category
   - Can add categories if needed (e.g., "Backend", "Frontend", "Cloud")

CRITICAL RULES:
- Keep all dates, company names, job titles EXACTLY as they are
- Don't invent new experiences or technologies
- Focus on repositioning HOW things are presented, not WHAT was done
- Maintain chronological order of jobs
- Output must be complete, valid JSON matching the input structure

OUTPUT FORMAT: Return ONLY valid JSON (no markdown, no code blocks) with the complete repositioned resume.

The JSON should have the exact same structure as the input resume, just with modified content.

Generate the repositioned resume now:"""

        return prompt

    def _parse_ai_response(self, response_text: str, original_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into resume JSON."""
        try:
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            repositioned_resume = json.loads(response_text)

            # Validate structure matches original
            required_keys = ['name', 'contact', 'experience']
            for key in required_keys:
                if key not in repositioned_resume:
                    logger.warning(f"Missing key {key} in repositioned resume, using original")
                    repositioned_resume[key] = original_resume.get(key)

            return repositioned_resume

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse repositioned resume as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            # Return original on parse failure
            return original_resume
