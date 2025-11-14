"""
Final Polisher - AI-driven final quality pass and cleanup.
Ensures consistency, flow, clarity, and professional tone.
100% AI-powered.
"""

import logging
import json
from typing import Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class FinalPolisher:
    """Performs final quality pass and cleanup using AI."""

    def __init__(self, config: Any):
        """Initialize with config."""
        self.config = config
        self.project_id = config.project_id
        self.location = config.get('google_cloud', 'vertex_ai', 'location', default='us-central1')
        self.model_name = config.get('resume_customization', 'polisher_model', default='gemini-2.5-flash')

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)

        logger.info(f"FinalPolisher initialized with model: {self.model_name}")

    def polish(
        self,
        resume: Dict[str, Any],
        validation_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform final polish and cleanup.

        Args:
            resume: Validated resume JSON
            validation_feedback: Feedback from AIQualityValidator

        Returns:
            Final polished resume JSON
        """
        logger.info("Performing final polish and cleanup")

        # Build AI prompt
        prompt = self._build_polish_prompt(resume, validation_feedback)

        try:
            # Call AI
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            polished_resume = self._parse_ai_response(result_text, resume)

            logger.info("Final polish complete")

            return polished_resume

        except Exception as e:
            logger.error(f"Error in final polish: {str(e)}")
            # Return original resume on error
            return resume

    def _build_polish_prompt(
        self,
        resume: Dict[str, Any],
        validation_feedback: Dict[str, Any]
    ) -> str:
        """Build the AI prompt for final polish."""

        prompt = f"""You are a senior resume editor doing final quality pass.

TASK: Perform final polish and cleanup to ensure this resume is perfect.

VALIDATED RESUME:
{json.dumps(resume, indent=2)}

VALIDATION FEEDBACK:
{json.dumps(validation_feedback, indent=2)}

YOUR JOB: Final polish and cleanup

CHECKS:

1. CONSISTENCY:

   A. Date Formats:
      - All dates use same format (e.g., "Jan 2020" or "January 2020", not both)
      - "Present" or "Current" (pick one, use consistently)
      - Check education dates, experience dates

   B. Bullet Point Styles:
      - All bullets use same symbol (• not - or *)
      - Consistent capitalization (all start with capital letter)
      - Consistent ending (no periods vs periods - pick one style)

   C. Capitalization:
      - Technology names: JavaScript (not javascript), TypeScript, React, Node.js
      - Company names: Proper case
      - Job titles: Consistent capitalization

   D. Spacing:
      - Consistent spacing between sections
      - No double spaces
      - Clean line breaks

2. FLOW & READABILITY:

   A. Experience Ordering:
      - Most recent first (reverse chronological)
      - Within each job, most impressive bullets first
      - Logical progression of responsibility

   B. Reading Flow:
      - Smooth transitions between bullets
      - Related achievements grouped together
      - Clear narrative arc within each role

   C. Clarity:
      - Remove any ambiguous statements
      - Ensure technical terms are accurate
      - No jargon without context for the role
      - Every bullet is clear and specific

3. PROFESSIONAL TONE:

   A. Confidence Level:
      - Not arrogant ("revolutionized", "transformed the industry")
      - Not timid ("helped a little", "tried to")
      - Appropriate confidence ("Led", "Built", "Architected")

   B. Action-Oriented:
      - Strong action verbs
      - Clear ownership when appropriate
      - Results-focused where relevant

   C. Technical Accuracy:
      - Technology names spelled correctly
      - No made-up terms
      - Realistic claims

4. MINOR FIXES:

   A. HTML Entities:
      - Fix any remaining &amp; → &
      - Fix &lt; → <, &gt; → >
      - Fix &quot; → "

   B. Duplicate Information:
      - Remove any repeated bullets
      - Remove redundant information

   C. Length Optimization:
      - Trim excessive length if needed
      - Keep resume concise and impactful
      - Remove filler words

   D. Grammar & Spelling:
      - Fix any typos
      - Ensure parallel structure in bullet lists
      - Consistent tense (past tense for past roles)

5. FINAL VALIDATION:

   - Scan for any remaining issues from validation feedback
   - Ensure all red flags are addressed
   - Verify overall quality

CRITICAL RULES:
- DO NOT change dates, company names, core facts
- DO NOT add or remove major experience
- DO fix minor inconsistencies, typos, formatting
- DO ensure professional polish
- Maintain the voice and authenticity from humanization stage

OUTPUT: Return ONLY valid JSON (no markdown, no code blocks) with the polished resume.

The JSON must match the input structure exactly, just with polished content.

Generate the polished resume now:"""

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
            polished_resume = json.loads(response_text)

            # Validate structure
            required_keys = ['name', 'contact', 'experience']
            for key in required_keys:
                if key not in polished_resume:
                    logger.warning(f"Missing key {key}, using original")
                    polished_resume[key] = original_resume.get(key)

            return polished_resume

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse polished resume as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            return original_resume
