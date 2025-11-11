"""AI-powered resume customizer using Vertex AI."""

import logging
from typing import Dict, Any, List
import json
import copy
import vertexai
from vertexai.generative_models import GenerativeModel


logger = logging.getLogger(__name__)


class ResumeCustomizer:
    """Customizes resume for specific job postings using AI."""

    def __init__(self, config: Any, master_resume: Dict[str, Any]):
        """Initialize resume customizer."""
        self.config = config
        self.master_resume = master_resume
        self.customize_sections = config.customize_sections

        # Initialize Vertex AI
        vertexai.init(
            project=config.project_id,
            location=config.vertex_location
        )

        self.model = GenerativeModel(config.vertex_model)
        logger.info(f"Initialized ResumeCustomizer with {config.vertex_model}")

    def customize_for_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Customize resume for a specific job."""
        logger.info(f"Customizing resume for: {job.get('title')} at {job.get('company')}")

        # Create a copy of master resume
        customized_resume = copy.deepcopy(self.master_resume)

        try:
            # Get match analysis from job
            match_analysis = job.get('match_analysis', {})

            # Customize different sections
            if 'summary' in self.customize_sections:
                customized_resume['summary'] = self._customize_summary(job, match_analysis)

            if 'skills' in self.customize_sections:
                customized_resume['skills'] = self._customize_skills(job, match_analysis)

            if 'experience' in self.customize_sections:
                customized_resume['experience'] = self._customize_experience(job, match_analysis)

            # Add metadata
            customized_resume['_metadata'] = {
                'customized_for_job': job.get('title'),
                'company': job.get('company'),
                'job_id': job.get('id'),
                'match_score': job.get('match_score'),
                'customized_sections': self.customize_sections
            }

            logger.info("Resume customization completed")
            return customized_resume

        except Exception as e:
            logger.error(f"Error customizing resume: {str(e)}")
            return customized_resume

    def _customize_summary(self, job: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Customize professional summary for the job."""
        original_summary = self.master_resume.get('summary', '')

        prompt = f"""You are an expert resume writer. Customize the professional summary to match this specific job posting.

ORIGINAL SUMMARY:
{original_summary}

JOB DETAILS:
Title: {job.get('title')}
Company: {job.get('company')}
Description: {job.get('description', '')[:1500]}

MATCH ANALYSIS:
Matching Skills: {', '.join(analysis.get('matching_skills', [])[:10])}
Key Highlights: {', '.join(analysis.get('key_highlights', [])[:5])}
ATS Keywords: {', '.join(analysis.get('ats_keywords', [])[:10])}

REQUIREMENTS:
1. Keep the summary concise (2-3 sentences, 50-80 words)
2. Highlight skills and experience most relevant to this job
3. Use keywords from the job description naturally
4. Maintain authenticity - don't claim skills not in original
5. Emphasize the matching skills and experiences
6. Keep the same years of experience and level

Output ONLY the customized summary text, no additional commentary.
"""

        try:
            response = self.model.generate_content(prompt)
            customized = response.text.strip()

            # Clean up any markdown or extra formatting
            customized = customized.replace('**', '').replace('*', '')

            # Validate length
            if len(customized) > 500:
                logger.warning("Summary too long, truncating")
                customized = customized[:500]

            return customized

        except Exception as e:
            logger.error(f"Error customizing summary: {str(e)}")
            return original_summary

    def _customize_skills(self, job: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Customize skills section to emphasize relevant skills."""
        original_skills = self.master_resume.get('skills', {})

        # Get technology mappings from analysis
        tech_mappings = analysis.get('technology_mappings', [])
        ats_keywords = analysis.get('ats_keywords', [])

        # Create a copy of skills
        customized_skills = copy.deepcopy(original_skills)

        try:
            # Apply technology mappings to emphasize certain skills
            for category, skills_list in customized_skills.items():
                updated_skills = []

                for skill in skills_list:
                    # Check if this skill should be modified
                    modified = False

                    for mapping in tech_mappings:
                        resume_tech = mapping.get('resume_tech', '')
                        job_tech = mapping.get('job_tech', '')
                        emphasis = mapping.get('emphasis', 'medium')

                        # If skill matches resume tech and has high emphasis, adjust it
                        if resume_tech.lower() in skill.lower() and job_tech:
                            # Replace or add alternative notation
                            if emphasis == 'high':
                                updated_skills.append(f"{job_tech}")
                                modified = True
                                break

                    if not modified:
                        updated_skills.append(skill)

                # Re-order: put matching skills first
                matching_skills = [s for s in updated_skills if any(
                    kw.lower() in s.lower() for kw in ats_keywords
                )]
                other_skills = [s for s in updated_skills if s not in matching_skills]

                customized_skills[category] = matching_skills + other_skills

            return customized_skills

        except Exception as e:
            logger.error(f"Error customizing skills: {str(e)}")
            return original_skills

    def _customize_experience(self, job: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Customize experience descriptions for the job."""
        original_experience = self.master_resume.get('experience', [])

        # Get customization guidance
        tech_mappings = analysis.get('technology_mappings', [])
        key_highlights = analysis.get('key_highlights', [])
        recommendations = analysis.get('recommendations', [])

        customized_experience = []

        for exp in original_experience:
            customized_exp = copy.deepcopy(exp)

            try:
                # Customize responsibilities using AI
                customized_exp['responsibilities'] = self._customize_responsibilities(
                    exp.get('responsibilities', []),
                    job,
                    tech_mappings,
                    key_highlights
                )

                customized_experience.append(customized_exp)

            except Exception as e:
                logger.error(f"Error customizing experience: {str(e)}")
                customized_experience.append(exp)

        return customized_experience

    def _customize_responsibilities(
        self,
        responsibilities: List[str],
        job: Dict[str, Any],
        tech_mappings: List[Dict[str, Any]],
        key_highlights: List[str]
    ) -> List[str]:
        """Customize responsibility descriptions."""
        if not responsibilities:
            return responsibilities

        prompt = f"""You are an expert resume writer. Customize these job responsibilities to better match the target job posting.

ORIGINAL RESPONSIBILITIES:
{json.dumps(responsibilities, indent=2)}

TARGET JOB:
Title: {job.get('title')}
Description: {job.get('description', '')[:1000]}

TECHNOLOGY MAPPINGS TO APPLY:
{json.dumps(tech_mappings, indent=2)}

GUIDANCE:
1. Keep the core achievements and metrics unchanged
2. Replace or emphasize technologies based on the mappings (e.g., "Vertex AI" → "OpenAI" if job mentions OpenAI)
3. Use keywords from job description naturally
4. Maintain authenticity - only adjust technology names and emphasis, not facts
5. Keep bullet points concise and achievement-focused
6. Maintain same number of responsibilities

CRITICAL RULES:
- If original says "Vertex AI", and job wants "OpenAI", change to "OpenAI"
- If original says "React", and job wants "Angular", change to "Angular"
- Keep numbers, metrics, and core responsibilities identical
- Only modify technology names and frameworks to match job requirements

Output ONLY a JSON array of customized responsibilities, no additional text.
Format: ["responsibility 1", "responsibility 2", ...]
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            customized = json.loads(response_text)

            # Validate
            if isinstance(customized, list) and len(customized) > 0:
                return customized
            else:
                return responsibilities

        except Exception as e:
            logger.error(f"Error customizing responsibilities: {str(e)}")
            return responsibilities
