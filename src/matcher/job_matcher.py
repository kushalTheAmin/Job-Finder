"""AI-powered job matcher using Vertex AI."""

import logging
from typing import List, Dict, Any, Tuple
import json
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel


logger = logging.getLogger(__name__)


class JobMatcher:
    """Matches jobs with resume using AI."""

    def __init__(self, config: Any, resume: Dict[str, Any]):
        """Initialize job matcher."""
        self.config = config
        self.resume = resume
        self.min_match_percentage = config.min_match_percentage

        # Initialize Vertex AI
        vertexai.init(
            project=config.project_id,
            location=config.vertex_location
        )

        self.model = GenerativeModel(config.vertex_model)
        logger.info(f"Initialized JobMatcher with {config.vertex_model}")

    def match_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match jobs with resume and filter by threshold."""
        matched_jobs = []

        logger.info(f"Matching {len(jobs)} jobs against resume...")

        for i, job in enumerate(jobs):
            try:
                logger.info(f"Analyzing job {i+1}/{len(jobs)}: {job.get('title', 'Unknown')}")

                # Calculate match score
                match_score, analysis = self._calculate_match(job)

                # Add match information to job
                job['match_score'] = match_score
                job['match_analysis'] = analysis

                # Only include jobs above threshold
                if match_score >= self.min_match_percentage:
                    matched_jobs.append(job)
                    logger.info(f"✓ Match: {match_score}% - {job.get('title')}")
                else:
                    logger.info(f"✗ Below threshold: {match_score}% - {job.get('title')}")

            except Exception as e:
                logger.error(f"Error matching job: {str(e)}")
                continue

        # Sort by match score (highest first)
        matched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        logger.info(f"Found {len(matched_jobs)} jobs matching threshold of {self.min_match_percentage}%")
        return matched_jobs

    def _calculate_match(self, job: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Calculate match percentage between job and resume using AI."""
        # Build prompt for AI
        prompt = self._build_match_prompt(job)

        # Get AI response
        response = self.model.generate_content(prompt)
        response_text = response.text

        # Parse the response
        match_score, analysis = self._parse_match_response(response_text)

        return match_score, analysis

    def _build_match_prompt(self, job: Dict[str, Any]) -> str:
        """Build prompt for AI to analyze job match with dual-brain approach."""
        resume_summary = self._summarize_resume()

        prompt = f"""You are an expert career advisor with dual perspective: ATS Scanner + Human Recruiter.

CANDIDATE RESUME:
{resume_summary}

JOB POSTING:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Description: {job.get('description', 'N/A')[:2500]}

DUAL ANALYSIS REQUIRED:

PART 1 - ATS SCANNER BRAIN:
Analyze like an ATS system:
- Identify CRITICAL skills (in "Required" section or mentioned 3+ times)
- Identify IMPORTANT skills (mentioned 2-3 times in description)
- Identify OPTIONAL skills (mentioned once or "nice to have")
- Extract key technical keywords that ATS will scan for

PART 2 - HUMAN RECRUITER BRAIN:
Think like a human recruiter reading this resume:
- What would make me call this candidate for interview?
- Do the achievements have specific numbers and impact?
- Does the experience progression make sense?
- Are there any red flags (gaps, job hopping, etc.)?

PART 3 - MATCHING ANALYSIS:
1. Calculate match percentage (0-100) considering:
   - Do they have required skills? (40% weight)
   - Do they have transferable/similar skills? (30% weight)
   - Does experience level match? (15% weight)
   - Does domain knowledge match? (15% weight)

2. For each missing skill, determine:
   - Relationship level:
     * Level 1 (Identical): PostgreSQL ↔ MySQL, AWS S3 ↔ GCP Storage
     * Level 2 (Same category): React ↔ Angular, Gemini ↔ OpenAI
     * Level 3 (Learnable): React → Next.js, JavaScript → TypeScript
     * Level 4 (Different): Frontend → Backend, Web → Mobile
   - Confidence if added (0-100): How believable if added to resume?
   - Best placement: Which job/section to add it to?

3. Provide story templates for adding missing skills coherently

OUTPUT FORMAT (JSON):
{{
  "match_percentage": <number 0-100>,
  "matching_skills": [list of matching skills],
  "missing_skills": [
    {{
      "skill": "skill name",
      "priority": "CRITICAL/IMPORTANT/OPTIONAL",
      "mention_count": <number of times mentioned in job>,
      "relationship_to_resume": {{
        "level": 1-4,
        "similar_skill_in_resume": "what they have that's similar",
        "confidence_if_added": <0-100>,
        "reasoning": "why this confidence score"
      }},
      "addition_strategy": {{
        "best_placement": "current_job/previous_job/skills_section/skip",
        "story_template": "suggested story/context for adding this",
        "minimum_mentions_needed": 2 or 3,
        "sample_bullets": ["example bullet 1", "example bullet 2"]
      }}
    }}
  ],
  "technology_mappings": [
    {{
      "resume_tech": "X",
      "job_tech": "Y",
      "relationship_level": 1-4,
      "replacement_confidence": <0-100>,
      "keep_both": true/false
    }}
  ],
  "recruiter_perspective": {{
    "would_interview": true/false,
    "strengths": [list of strong points],
    "concerns": [list of potential concerns],
    "authenticity_score": <0-100>
  }},
  "ats_keywords": [important keywords from job description],
  "key_highlights": [experience points to emphasize from resume]
}}

Provide ONLY the JSON output, no additional text.
Be thoughtful about confidence scores - only rate high if truly believable.
"""
        return prompt

    def _summarize_resume(self) -> str:
        """Create a concise summary of the resume for AI analysis."""
        summary_parts = []

        # Personal info
        info = self.resume.get('personal_info', {})
        summary_parts.append(f"Name: {info.get('name', 'N/A')}")
        summary_parts.append(f"Title: {info.get('title', 'N/A')}")

        # Summary
        if self.resume.get('summary'):
            summary_parts.append(f"\nProfessional Summary:\n{self.resume['summary']}")

        # Skills
        skills = self.resume.get('skills', {})
        all_skills = []
        for category, skill_list in skills.items():
            all_skills.extend(skill_list)
        summary_parts.append(f"\nSkills: {', '.join(all_skills[:50])}")  # Limit skills

        # Experience (last 3 positions)
        experiences = self.resume.get('experience', [])[:3]
        summary_parts.append("\nRecent Experience:")
        for exp in experiences:
            summary_parts.append(f"- {exp.get('position')} at {exp.get('company')} ({exp.get('start_date')} - {exp.get('end_date')})")
            # Add top 3 responsibilities
            for resp in exp.get('responsibilities', [])[:3]:
                summary_parts.append(f"  • {resp}")

        # Education
        education = self.resume.get('education', [])
        if education:
            edu = education[0]
            summary_parts.append(f"\nEducation: {edu.get('degree')} from {edu.get('institution')}")

        return '\n'.join(summary_parts)

    def _parse_match_response(self, response_text: str) -> Tuple[int, Dict[str, Any]]:
        """Parse AI response to extract match score and analysis."""
        try:
            # Extract JSON from response
            # Sometimes AI adds markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            # Parse JSON
            analysis = json.loads(response_text)
            match_score = int(analysis.get('match_percentage', 0))

            # Ensure score is in valid range
            match_score = max(0, min(100, match_score))

            return match_score, analysis

        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            logger.debug(f"Response text: {response_text[:500]}")

            # Return default low score on parse error
            return 0, {
                "error": "Failed to parse AI response",
                "raw_response": response_text[:200]
            }

    def rank_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank jobs by match score and return top matches."""
        # Already sorted by match_score in match_jobs
        max_jobs = self.config.max_jobs_per_day

        if len(jobs) > max_jobs:
            logger.info(f"Limiting to top {max_jobs} jobs")
            return jobs[:max_jobs]

        return jobs
