"""
Authenticity Humanizer - AI-driven transformation to make resumes feel human-written.
Removes AI patterns, adds personality, varies structure.
100% AI-powered.
"""

import logging
import json
from typing import Dict, Any, Optional
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class AuthenticityHumanizer:
    """Makes AI-optimized resumes feel authentically human-written."""

    def __init__(self, config: Any):
        """Initialize with config."""
        self.config = config
        self.project_id = config.project_id
        self.location = config.get('google_cloud', 'vertex_ai', 'location', default='us-central1')
        self.model_name = config.get('resume_customization', 'humanizer_model', default='gemini-2.5-flash')

        # Humanization settings
        self.target_metric_density = config.get('resume_customization', 'target_metric_density', default=55)
        self.personality_bullets = config.get('resume_customization', 'personality_bullets_per_resume', default=3)

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)

        logger.info(f"AuthenticityHumanizer initialized with model: {self.model_name}")

    def humanize(
        self,
        resume: Dict[str, Any],
        previous_attempt: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transform resume to feel authentically human-written.

        Args:
            resume: ATS-optimized resume JSON
            previous_attempt: Previous humanization attempt (for retry)
            feedback: Validator feedback (for retry)

        Returns:
            Humanized resume JSON with authentic feel
        """
        logger.info("Humanizing resume for authentic feel")

        # Build AI prompt
        prompt = self._build_humanization_prompt(resume, previous_attempt, feedback)

        try:
            # Call AI
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            humanized_resume = self._parse_ai_response(result_text, resume)

            logger.info("Resume humanization complete")

            return humanized_resume

        except Exception as e:
            logger.error(f"Error in resume humanization: {str(e)}")
            # Return original resume on error
            return resume

    def _build_humanization_prompt(
        self,
        resume: Dict[str, Any],
        previous_attempt: Optional[Dict[str, Any]],
        feedback: Optional[str]
    ) -> str:
        """Build the AI prompt for humanization."""

        retry_context = ""
        if previous_attempt and feedback:
            retry_context = f"""
PREVIOUS ATTEMPT HAD ISSUES:
{feedback}

Please address these issues in this attempt.
"""

        prompt = f"""You are an expert at making AI-written content feel authentically human.

TASK: Transform this ATS-optimized resume to feel like a confident senior engineer wrote it naturally.

RESUME TO HUMANIZE:
{json.dumps(resume, indent=2)}

{retry_context}

AI DETECTION RED FLAGS TO ELIMINATE:

1. ❌ METRIC OVERLOAD
   - Problem: Every bullet has percentages/numbers
   - Fix: Remove metrics from {100 - self.target_metric_density}% of bullets randomly
   - Keep: High-impact metrics (major performance improvements, scale achievements)
   - Remove: Obvious metrics (component counts, team sizes, percentage improvements <25%)

   Before: "Built 50+ components" → After: "Built comprehensive component library"
   Before: "Reduced load time by 15%" → After: "Improved page load performance"
   Keep: "Reduced latency from 2s to 200ms" (major improvement)

2. ❌ FORMULAIC STRUCTURE
   - Problem: Every bullet follows [ACTION] + [TECH] + [RESULT] pattern
   - Fix: Vary the structure significantly

   Patterns to use:
   - Action only: "Led code reviews and mentored junior developers"
   - Result first: "Achieved 99.9% uptime through robust monitoring and auto-scaling"
   - Context-heavy: "When the legacy system couldn't scale, architected new microservices platform"
   - Descriptive: "Responsible for backend services serving 10M+ daily users"
   - Process-focused: "Established testing practices that became team standard"

3. ❌ KEYWORD DENSITY
   - Problem: Too many tech terms per sentence
   - Fix: Spread out technologies naturally

   Before: "Built React, TypeScript, Redux app with Node.js, PostgreSQL, Redis backend"
   After: "Built full-stack application with React frontend and Node.js API layer"

4. ❌ NO PERSONALITY
   - Problem: Sounds like a robot
   - Fix: Add {self.personality_bullets} personality/voice bullets showing:
     * Technical preferences: "Prefer Redis over Memcached for rich data structures"
     * Opinions: "Strong advocate for code reviews and pair programming"
     * Passion: "Obsessed with keeping API latency under 100ms"
     * Process beliefs: "Believe in testing pyramid: unit > integration > E2E"
     * Architecture philosophy: "Favor simplicity over cleverness in system design"

   Place these strategically in experience section, not all together.

5. ❌ OVER-EXPLANATIONS
   - Problem: Explaining obvious things
   - Fix: Remove unnecessary explanations

   Before: "MongoDB and DynamoDB for flexible NoSQL data storage"
   After: "MongoDB and DynamoDB"

   Before: "Agile methodologies like Scrum and Kanban"
   After: "Scrum team"

6. ❌ UNIFORM DETAIL LEVEL
   - Problem: Every bullet has same level of detail
   - Fix: Create natural variation

   Detail distribution:
   - 30% bullets: Short (1 line, 8-15 words)
     Example: "Participated in system design discussions"
   - 50% bullets: Medium (1-2 lines, 20-30 words)
     Example: "Built authentication service with JWT and OAuth2, handling 50K requests/day"
   - 20% bullets: Long (2-3 lines, 35-50 words with context)
     Example: "Architected event-driven notification system using Kafka and Redis, designing for exactly-once delivery semantics while maintaining sub-second latency. Scaled to process 100M+ events daily."

7. ❌ PERFECT GRAMMAR/STYLE
   - Problem: Too polished, no variation
   - Fix: Add natural human patterns
   - Some bullets start with "Helped", "Participated", "Contributed" (not everything is "Led")
   - Occasional use of "and" to connect related points naturally
   - Not every responsibility is a major achievement

AUTHENTICITY REQUIREMENTS:

Target Metrics:
- Only {self.target_metric_density}% of bullets should have numbers/percentages
- At least {self.personality_bullets} personality/voice bullets
- 3+ different bullet structures used
- Detail levels vary significantly
- Tech density varies (some tech-heavy, some minimal)

Natural Patterns:
- Not every bullet needs a metric
- Not every project was wildly successful
- Some work is collaborative (Helped, Participated, Contributed)
- Mix of leadership and execution
- Some descriptive bullets about responsibilities

CRITICAL RULES:
- DO NOT change company names, job titles, dates
- DO NOT fabricate new experiences
- DO remove/modify metrics to reduce density
- DO add personality bullets based on existing experience patterns
- DO vary structure significantly
- Maintain technical accuracy

OUTPUT: Return ONLY valid JSON (no markdown, no code blocks) with the humanized resume.

The JSON must match the input structure exactly, just with humanized content.

Generate the humanized resume now:"""

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
            humanized_resume = json.loads(response_text)

            # Validate structure
            required_keys = ['name', 'contact', 'experience']
            for key in required_keys:
                if key not in humanized_resume:
                    logger.warning(f"Missing key {key}, using original")
                    humanized_resume[key] = original_resume.get(key)

            return humanized_resume

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse humanized resume as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            return original_resume
