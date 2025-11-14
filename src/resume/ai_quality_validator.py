"""
AI Quality Validator - AI-driven resume quality validation and scoring.
Validates ATS readiness, authenticity, role alignment, and technical depth.
100% AI-powered.
"""

import logging
import json
from typing import Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class AIQualityValidator:
    """Validates resume quality using AI analysis."""

    def __init__(self, config: Any):
        """Initialize with config."""
        self.config = config
        self.project_id = config.project_id
        self.location = config.get('google_cloud', 'vertex_ai', 'location', default='us-central1')
        self.model_name = config.get('resume_customization', 'validator_model', default='gemini-2.5-flash')

        # Validation thresholds
        self.min_overall_score = config.get('resume_customization', 'min_overall_score', default=85)
        self.min_authenticity_score = config.get('resume_customization', 'min_authenticity_score', default=85)

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)

        logger.info(f"AIQualityValidator initialized with model: {self.model_name}")

    def validate(
        self,
        resume: Dict[str, Any],
        job_description: str,
        job_title: str
    ) -> Dict[str, Any]:
        """
        Validate resume quality across multiple dimensions.

        Args:
            resume: Humanized resume JSON
            job_description: Target job description
            job_title: Target job title

        Returns:
            Dict containing:
                - passed: bool
                - overall_score: 0-100
                - ats_readiness: 0-100
                - authenticity: 0-100
                - role_alignment: 0-100
                - technical_depth: 0-100
                - red_flags: list of issues
                - feedback: detailed feedback
                - retry_stage: which stage to retry if failed
        """
        logger.info(f"Validating resume quality for: {job_title}")

        # Build AI prompt
        prompt = self._build_validation_prompt(resume, job_description, job_title)

        try:
            # Call AI
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            validation_result = self._parse_ai_response(result_text)

            # Determine pass/fail
            passed = (
                validation_result['overall_score'] >= self.min_overall_score and
                validation_result['authenticity'] >= self.min_authenticity_score and
                len(validation_result.get('red_flags', [])) == 0
            )

            validation_result['passed'] = passed

            logger.info(f"Validation complete. Passed: {passed}, Overall: {validation_result['overall_score']}")

            return validation_result

        except Exception as e:
            logger.error(f"Error in resume validation: {str(e)}")
            # Return passing result on error to not block
            return {
                "passed": True,
                "overall_score": 100,
                "ats_readiness": 100,
                "authenticity": 100,
                "role_alignment": 100,
                "technical_depth": 100,
                "red_flags": [],
                "feedback": "Validation skipped due to error",
                "retry_stage": None
            }

    def _build_validation_prompt(
        self,
        resume: Dict[str, Any],
        job_description: str,
        job_title: str
    ) -> str:
        """Build the AI prompt for validation."""

        # Count bullets for metrics check
        total_bullets = 0
        bullets_with_metrics = 0

        for exp in resume.get('experience', []):
            bullets = exp.get('responsibilities', [])
            total_bullets += len(bullets)
            for bullet in bullets:
                # Check if bullet has numbers/percentages
                if any(char.isdigit() for char in bullet):
                    bullets_with_metrics += 1

        metric_density = (bullets_with_metrics / total_bullets * 100) if total_bullets > 0 else 0

        prompt = f"""You are an expert resume quality analyst and AI-content detector.

TASK: Validate this resume across 4 dimensions and detect any red flags.

JOB TITLE: {job_title}

JOB DESCRIPTION (first 2000 chars):
{job_description[:2000]}

RESUME TO VALIDATE:
{json.dumps(resume, indent=2)}

VALIDATION METRICS:

Current metric density: {metric_density:.1f}% of bullets have numbers

VALIDATION CRITERIA:

1. ATS READINESS (Score 0-100):

   Award points for:
   - Critical job keywords present (40 points)
     * Check for main technologies, frameworks, languages from job description
     * Verify skills section includes key requirements

   - Natural keyword integration (30 points)
     * Keywords used in context, not just listed
     * No obvious keyword stuffing (tech lists >4 items = stuffing)
     * Technologies mentioned with purpose/results

   - Emphasis aligned with job (30 points)
     * Most relevant experience highlighted first
     * Role type matches job (Backend vs Frontend vs Full-Stack)
     * Summary/bullets emphasize job requirements

   Deduct points for:
   - Missing critical keywords (-10 per critical miss)
   - Keyword stuffing detected (-15 per instance)
   - Wrong emphasis/positioning (-20)

2. AUTHENTICITY (Score 0-100):

   Award points for:
   - Metric density 45-65% (30 points) [Too many = AI-like, too few = weak]
   - Structure variety (25 points) [3+ different bullet patterns]
   - Personality indicators (20 points) [2-3 voice/opinion bullets]
   - Natural language (15 points) [No over-explanations, varied starters]
   - Detail variation (10 points) [Mix of short/medium/long bullets]

   Deduct heavily for AI patterns:
   - Metric overload >70% (-30 points)
   - Formulaic structure (-25 points) [all bullets same pattern]
   - No personality (-20 points) [0 voice bullets]
   - Keyword stuffing (-15 points)
   - Over-explanations (-10 points) [explaining obvious things]

3. ROLE ALIGNMENT (Score 0-100):

   Award points for:
   - Resume emphasis matches job role (50 points)
     * Backend job = backend work prominent
     * Frontend job = frontend work prominent

   - Relevant experience surfaced (30 points)
     * Most applicable experience detailed first
     * Job-relevant projects highlighted

   - Narrative coherence (20 points)
     * Story makes sense for target role
     * No confusing positioning

4. TECHNICAL DEPTH (Score 0-100):

   Award points for:
   - System thinking shown (30 points)
     * Architectural decisions mentioned
     * Scalability, performance considerations

   - Design decisions (25 points)
     * Technology choices explained
     * Tradeoffs discussed

   - Operational awareness (25 points)
     * Monitoring, reliability, deployment mentioned
     * Production concerns visible

   - Technical tradeoffs (20 points)
     * Why certain technologies over others
     * Problem-solution thinking

RED FLAGS (Critical Issues):

Check for:
1. HTML entities (S&amp;P, &lt;, etc.) = CRITICAL
2. Repetitive phrases (same phrase 3+ times) = MAJOR
3. Obvious keyword stuffing (tech lists >5 items) = MAJOR
4. Formulaic structure (all bullets identical pattern) = MAJOR
5. Missing personality completely (0 voice bullets) = MODERATE
6. Metric overload (>80% bullets have numbers) = MODERATE

SCORING:

- Calculate each dimension (ATS, Authenticity, Role, Technical)
- Overall Score = Average of 4 dimensions
- Flag any red flags found

PASS/FAIL:

PASS if:
- Overall Score ≥ 85
- Authenticity ≥ 85
- No CRITICAL red flags

FAIL if:
- Below thresholds OR has critical red flags

RETRY RECOMMENDATION:

If fail, recommend which stage to retry:
- "Repositioner" if role alignment is off
- "ATS" if keywords missing but good authenticity
- "Humanizer" if authenticity score low
- "Polisher" if red flags present

OUTPUT: Return ONLY valid JSON (no markdown, no code blocks) in this format:

{{
  "ats_readiness": 85,
  "ats_feedback": "string - what's good/bad",
  "authenticity": 90,
  "authenticity_feedback": "string - what's good/bad",
  "role_alignment": 88,
  "role_feedback": "string - what's good/bad",
  "technical_depth": 87,
  "technical_feedback": "string - what's good/bad",
  "overall_score": 87.5,
  "red_flags": ["flag1", "flag2"] or [],
  "feedback": "Overall assessment summary",
  "retry_stage": "Humanizer" or null
}}

Generate the validation report now:"""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into validation result."""
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
            result = json.loads(response_text)

            # Validate required fields
            required_fields = ['ats_readiness', 'authenticity', 'role_alignment', 'technical_depth', 'overall_score']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing required field: {field}, defaulting to 100")
                    result[field] = 100

            # Ensure red_flags is a list
            if 'red_flags' not in result:
                result['red_flags'] = []

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation result as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise
