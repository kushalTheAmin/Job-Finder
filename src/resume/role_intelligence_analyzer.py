"""
Role Intelligence Analyzer - AI-driven role mismatch detection and repositioning strategy.
100% AI-powered, no rules-based logic.
"""

import logging
import json
from typing import Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class RoleIntelligenceAnalyzer:
    """Analyzes role mismatches and generates repositioning strategies using AI."""

    def __init__(self, config: Any):
        """Initialize with config."""
        self.config = config
        self.project_id = config.project_id
        self.location = config.get('google_cloud', 'vertex_ai', 'location', default='us-central1')
        self.model_name = config.get('resume_customization', 'role_analysis_model', default='gemini-2.5-flash')

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model = GenerativeModel(self.model_name)

        logger.info(f"RoleIntelligenceAnalyzer initialized with model: {self.model_name}")

    def analyze(self, job_description: str, job_title: str, resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze role mismatch between job and resume using AI.

        Args:
            job_description: Full job posting text
            job_title: Job title from posting
            resume: Resume JSON data

        Returns:
            Dict containing:
                - mismatch_severity: CRITICAL/MODERATE/MINOR/NONE
                - job_role_type: Backend/Frontend/Full-Stack/Data/DevOps/etc
                - resume_role_type: Current emphasis in resume
                - gap_description: What's the disconnect
                - repositioning_strategy: Detailed strategy for repositioning
        """
        logger.info(f"Analyzing role match for: {job_title}")

        # Build AI prompt
        prompt = self._build_analysis_prompt(job_description, job_title, resume)

        try:
            # Call AI
            response = self.model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            result = self._parse_ai_response(result_text)

            # Log analysis results
            mismatch = result.get('mismatch_severity', 'UNKNOWN')
            logger.info(f"✓ Role analysis complete. Mismatch severity: {mismatch}")

            if mismatch != 'NONE':
                job_domain = result.get('job_domain_focus', 'Unknown')
                resume_domain = result.get('resume_domain_focus', 'Unknown')
                domain_mismatch = result.get('domain_mismatch', False)

                logger.info(f"  Job domain: {job_domain}")
                logger.info(f"  Resume domain: {resume_domain}")
                if domain_mismatch:
                    logger.info(f"  ⚠ Domain mismatch detected - repositioning needed")

                gap = result.get('gap_description', '')
                if gap:
                    logger.debug(f"  Gap: {gap[:100]}...")

                # Log repositioning strategy
                strategy = result.get('repositioning_strategy', {})
                if strategy.get('domain_context_shift'):
                    logger.info(f"  Domain shift: {strategy.get('domain_context_shift')}")

            return result

        except Exception as e:
            logger.error(f"Error in role analysis: {str(e)}")
            # Return no-mismatch default
            return {
                "mismatch_severity": "NONE",
                "job_role_type": "Full-Stack",
                "resume_role_type": "Full-Stack",
                "gap_description": "Unable to analyze due to error",
                "repositioning_strategy": {
                    "narrative_reframe": "Present experience as-is",
                    "emphasize_sections": [],
                    "deemphasize_sections": [],
                    "reframe_bullets": [],
                    "summary_rewrite": ""
                }
            }

    def _build_analysis_prompt(self, job_description: str, job_title: str, resume: Dict[str, Any]) -> str:
        """Build the AI prompt for role analysis."""

        # Extract key resume info
        experience_summary = self._summarize_experience(resume)
        skills = resume.get('skills', {})

        prompt = f"""You are an expert technical recruiter with 15 years analyzing resumes and job requirements.

TASK: Analyze role mismatch between this job posting and this candidate's resume.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:3000]}

CANDIDATE RESUME SUMMARY:
Current Role: {resume.get('professional_summary', '')[:200]}

Experience:
{experience_summary}

Skills:
{json.dumps(skills, indent=2)[:1000]}

ANALYZE:

1. Job Role Analysis:
   - Primary Role Type: [Backend Engineer/Frontend Engineer/Full-Stack/Data Engineer/DevOps/ML Engineer/Mobile/etc]
   - Domain/Industry Focus: [Market Intelligence/E-commerce/Fintech/Healthcare/Analytics/Automotive/etc]
   - Business Context: [What business problem does this role solve? e.g., "data-driven decision making", "customer-facing analytics"]
   - Primary Tech Focus: [Main 3-5 technologies the job emphasizes]
   - Secondary Tech Focus: [Supporting technologies]
   - Key Value Propositions: [Top 3 value statements from job - e.g., "innovation", "AI-first", "scale"]
   - Key Responsibilities: [Top 3 responsibilities]
   - Seniority Level: [Junior/Mid/Senior/Staff/Principal]

2. Resume Role Analysis:
   - Current Role Type: [What role does this resume primarily showcase?]
   - Domain/Industry Focus: [What domain does the resume emphasize? e.g., "automotive analytics", "financial services"]
   - Business Context: [What business value does the resume emphasize? e.g., "performance optimization", "user engagement"]
   - Primary Tech Focus: [What 3-5 technologies does the resume emphasize most?]
   - Secondary Tech Focus: [What's mentioned but not emphasized?]
   - Key Strengths: [Top 3 areas candidate shows depth in]
   - Experience Level: [Junior/Mid/Senior/Staff/Principal]

3. Mismatch Detection:
   - Is there a role type mismatch? [Yes/No]
   - Is there a domain/focus mismatch? [Yes/No - e.g., automotive analytics resume vs market intelligence job]
   - Is there a business value mismatch? [Yes/No - e.g., resume emphasizes UI/UX but job emphasizes data processing]
   - Severity: [CRITICAL/MODERATE/MINOR/NONE]
   - Primary Gap: [What's the main disconnect? Be specific - include domain and business context, not just tech]
   - Secondary Gaps: [What else doesn't align?]
   - Hidden Strengths: [What relevant experience exists but is buried/de-emphasized? Look for transferable skills in wrong context]

4. Repositioning Strategy (if mismatch exists):

   A. Narrative Reframe:
   - How should we reposition this candidate's story?
   - What angle highlights their fit for THIS specific role?
   - What domain/business context shift is needed? (e.g., from "automotive analytics" to "market intelligence")
   - Example: "Reposition as data-driven full-stack engineer building market intelligence platforms, not just automotive dashboards"

   B. Professional Summary - COMPLETE REWRITE REQUIRED:
   - MUST incorporate job's domain focus (e.g., "market intelligence", "e-commerce", "fintech")
   - MUST use job's key value propositions (e.g., "AI-first", "data-driven", "innovation")
   - MUST lead with relevant technical identity matching job (e.g., "Full-Stack Engineer specializing in AI-powered analytics platforms")
   - MUST be 2-4 sentences, role-specific
   - Example for market intelligence job: "Full-Stack Engineer with 8+ years building data-driven intelligence platforms and AI-powered analytics. Led development of real-time dashboards and LLM-integrated systems serving enterprise clients. Expert in React, Python, and cloud-scale data visualization."

   C. Emphasize (expand, move up, add detail):
   - Which job experiences should be expanded?
   - Which specific bullet points need more architectural depth?
   - Which technologies need to be surfaced more? (especially those matching job's primary tech focus)
   - Which projects align with job's domain/business context and should be highlighted?

   D. De-emphasize (condense, move down, reduce detail):
   - Which experiences are less relevant and should be condensed?
   - Which bullet points distract from the target narrative?
   - Which technologies should be mentioned less prominently?

   E. Reframe Bullets (change angle, not content):
   - For each key bullet that needs reframing, provide:
     * Original focus: [What does it currently emphasize?]
     * New angle: [What aspect should we emphasize instead? Must match job's business context]
     * Example rewrite: [Show the transformation]
     * Domain shift needed: [e.g., "automotive metrics" → "business intelligence metrics"]

CRITICAL RULES:
- If the candidate truly doesn't have relevant experience, set severity to CRITICAL and explain why
- If experience exists but is buried, set severity to MODERATE and show how to surface it
- If resume already aligns well, set severity to NONE
- Be honest about gaps - don't oversell
- Focus on repositioning EXISTING experience, not fabricating new experience

OUTPUT: Return ONLY valid JSON (no markdown, no code blocks) in this exact format:

{{
  "mismatch_severity": "CRITICAL|MODERATE|MINOR|NONE",
  "job_role_type": "string",
  "job_domain_focus": "string - e.g., Market Intelligence, E-commerce, Fintech",
  "job_business_context": "string - what business problem this role solves",
  "job_primary_focus": ["tech1", "tech2", "tech3"],
  "job_key_value_propositions": ["value1", "value2", "value3"],
  "job_key_responsibilities": ["resp1", "resp2", "resp3"],
  "resume_role_type": "string",
  "resume_domain_focus": "string - current domain emphasis",
  "resume_business_context": "string - current business value emphasis",
  "resume_primary_focus": ["tech1", "tech2", "tech3"],
  "gap_description": "string - include role, domain, and business context gaps",
  "domain_mismatch": true/false,
  "hidden_strengths": ["strength1", "strength2"],
  "repositioning_strategy": {{
    "narrative_reframe": "string - how to reposition the candidate including domain shift",
    "domain_context_shift": "string - e.g., 'automotive analytics' to 'market intelligence'",
    "summary_rewrite": "string - COMPLETE new professional summary with job's domain focus and value propositions",
    "emphasize_sections": ["section or bullet to expand"],
    "deemphasize_sections": ["section or bullet to condense"],
    "reframe_bullets": [
      {{
        "original_focus": "string",
        "new_angle": "string - must match job's business context",
        "domain_shift": "string - how domain context changes",
        "example_rewrite": "string"
      }}
    ]
  }}
}}

Generate the JSON now:"""

        return prompt

    def _summarize_experience(self, resume: Dict[str, Any]) -> str:
        """Summarize experience for the prompt."""
        experiences = resume.get('experience', [])[:3]  # Top 3 jobs
        summary_lines = []

        for exp in experiences:
            company = exp.get('company', 'Unknown')
            title = exp.get('position', exp.get('title', 'Unknown'))
            bullets = exp.get('responsibilities', [])[:3]  # Top 3 bullets
            summary_lines.append(f"- {title} at {company}")
            for bullet in bullets:
                summary_lines.append(f"  • {bullet[:100]}...")

        return "\n".join(summary_lines)

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
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
            required_fields = ['mismatch_severity', 'job_role_type', 'resume_role_type', 'repositioning_strategy']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing required field: {field}")
                    result[field] = ""

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")
            raise
