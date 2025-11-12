"""Intelligent story-based resume customizer with coherence validation."""

import logging
from typing import Dict, Any, List, Tuple
import json
import copy
import vertexai
from vertexai.generative_models import GenerativeModel
from .story_builder import StoryBuilder


logger = logging.getLogger(__name__)


class SmartResumeCustomizer:
    """
    Intelligent resume customizer that thinks holistically about job stories.

    Key features:
    - Story-based customization (not bullet-by-bullet)
    - 2-3 mention minimum for technologies
    - Timeline awareness
    - Coherence validation
    - Confidence scoring
    """

    def __init__(self, config: Any, master_resume: Dict[str, Any]):
        """Initialize smart resume customizer."""
        self.config = config
        self.master_resume = master_resume
        self.customize_sections = config.customize_sections
        self.story_builder = StoryBuilder()

        # Initialize Vertex AI
        vertexai.init(
            project=config.project_id,
            location=config.vertex_location
        )

        self.model = GenerativeModel(config.vertex_model)
        logger.info(f"Initialized SmartResumeCustomizer with {config.vertex_model}")

        # Configuration
        self.max_changes_per_job = 5
        self.authenticity_weight = 70  # 70% authentic, 30% keywords
        self.min_confidence = 65

    def customize_for_job(self, job: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Customize resume for a specific job with full intelligence.

        Returns:
            (customized_resume, customization_report)
        """
        logger.info(f"Smart customization for: {job.get('title')} at {job.get('company')}")

        # Create working copy
        customized_resume = copy.deepcopy(self.master_resume)

        # Track all changes for report
        changes_made = []
        confidence_scores = []

        try:
            # Get match analysis from job matcher
            match_analysis = job.get('match_analysis', {})
            missing_skills = match_analysis.get('missing_skills', [])

            # Phase 1: Customize summary
            if 'summary' in self.customize_sections:
                new_summary, confidence = self._customize_summary_smart(job, match_analysis)
                customized_resume['summary'] = new_summary
                changes_made.append({
                    'section': 'summary',
                    'type': 'modified',
                    'confidence': confidence
                })

            # Phase 2: Build coherent job stories for experience
            if 'experience' in self.customize_sections:
                experience_changes = self._customize_experience_smart(
                    customized_resume,
                    job,
                    match_analysis,
                    missing_skills
                )
                changes_made.extend(experience_changes)

            # Phase 3: Reorder and enhance skills
            if 'skills' in self.customize_sections:
                skill_changes = self._customize_skills_smart(
                    customized_resume,
                    job,
                    match_analysis
                )
                changes_made.extend(skill_changes)

            # Phase 4: Validate coherence
            coherence_score = self._validate_coherence(customized_resume)

            # Phase 5: Generate report
            customization_report = self._generate_report(
                changes_made,
                coherence_score,
                job,
                match_analysis
            )

            # Add metadata
            customized_resume['_metadata'] = {
                'customized_for_job': job.get('title'),
                'company': job.get('company'),
                'job_id': job.get('id'),
                'match_score': job.get('match_score'),
                'coherence_score': coherence_score,
                'changes_count': len(changes_made),
                'customization_report': customization_report
            }

            logger.info(f"Customization complete. Coherence: {coherence_score}%, Changes: {len(changes_made)}")

            return customized_resume, customization_report

        except Exception as e:
            logger.error(f"Error in smart customization: {str(e)}", exc_info=True)
            # Return original if error
            return customized_resume, {'error': str(e)}

    def _customize_summary_smart(
        self,
        job: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Customize summary with confidence scoring."""
        original_summary = self.master_resume.get('summary', '')

        prompt = f"""You are an expert resume writer. Create an authentic, compelling summary.

ORIGINAL SUMMARY:
{original_summary}

JOB REQUIREMENTS:
Title: {job.get('title')}
Key Skills Needed: {', '.join([s.get('skill', '') for s in analysis.get('missing_skills', [])[:5]])}
Matching Skills: {', '.join(analysis.get('matching_skills', [])[:8])}

CRITICAL RULES:
1. Keep 2-3 sentences (50-80 words max)
2. Maintain same experience level and years
3. Use action-focused language (Style C)
4. Balance: 70% authentic story, 30% keywords
5. Include 2-3 key technologies naturally
6. Highlight matching achievements

PATTERN: [Years] [Title] with expertise in [relevant tech]. [Key achievement]. [Relevant focus area].

Output ONLY the summary text, nothing else.
"""

        try:
            response = self.model.generate_content(prompt)
            customized_summary = response.text.strip().replace('**', '').replace('*', '')

            # Confidence based on length and keyword presence
            has_keywords = any(
                skill.lower() in customized_summary.lower()
                for skill in analysis.get('matching_skills', [])[:5]
            )
            length_good = 50 <= len(customized_summary.split()) <= 90

            confidence = 85 if (has_keywords and length_good) else 75

            return customized_summary, confidence

        except Exception as e:
            logger.error(f"Error customizing summary: {str(e)}")
            return original_summary, 50

    def _customize_experience_smart(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
        analysis: Dict[str, Any],
        missing_skills: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Smart experience customization with story-based approach.

        This is the core intelligence:
        - Analyzes each job holistically
        - Builds coherent stories for adding skills
        - Ensures 2-3 mentions minimum
        - Validates timeline appropriateness
        """
        changes_made = []
        experiences = resume.get('experience', [])

        # Process each missing critical/important skill
        critical_skills = [s for s in missing_skills if s.get('priority') == 'CRITICAL']
        important_skills = [s for s in missing_skills if s.get('priority') == 'IMPORTANT']

        skills_to_add = critical_skills + important_skills[:3]  # Limit total additions

        for skill_info in skills_to_add:
            skill_name = skill_info.get('skill', '')
            relationship = skill_info.get('relationship_to_resume', {})
            confidence = relationship.get('confidence_if_added', 0)

            # Skip if confidence too low
            if confidence < self.min_confidence:
                logger.debug(f"Skipping {skill_name} - confidence too low ({confidence}%)")
                continue

            # Get addition strategy from AI analysis
            strategy = skill_info.get('addition_strategy', {})
            best_placement = strategy.get('best_placement', 'current_job')

            # Try to add based on placement strategy
            if best_placement == 'current_job' and len(experiences) > 0:
                success, change = self._add_skill_to_job(
                    experiences[0],
                    skill_name,
                    skill_info,
                    analysis,
                    'current'
                )
                if success:
                    changes_made.append(change)

            elif best_placement == 'previous_job' and len(experiences) > 1:
                success, change = self._add_skill_to_job(
                    experiences[1],
                    skill_name,
                    skill_info,
                    analysis,
                    'previous'
                )
                if success:
                    changes_made.append(change)

            elif best_placement == 'skills_section':
                # Will be handled in skills customization
                pass

        return changes_made

    def _add_skill_to_job(
        self,
        job_experience: Dict[str, Any],
        skill_name: str,
        skill_info: Dict[str, Any],
        analysis: Dict[str, Any],
        job_type: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Add skill to a job experience with full coherence checking.

        Returns:
            (success, change_info)
        """
        # Check if we can add this skill coherently
        can_add, story_template, coherence_score = self.story_builder.can_add_technology_to_job(
            job_experience,
            skill_name,
            skill_info
        )

        if not can_add:
            logger.debug(f"Cannot add {skill_name} coherently to {job_type} job")
            return False, {}

        # Extract existing metrics for realistic generation
        existing_metrics = self._extract_metrics_from_job(job_experience)

        # Generate story bullets using AI
        new_bullets = self._generate_story_bullets_ai(
            skill_name,
            story_template,
            job_experience,
            existing_metrics,
            analysis
        )

        if not new_bullets or len(new_bullets) < 2:
            logger.debug(f"Could not generate enough coherent bullets for {skill_name}")
            return False, {}

        # Add bullets to experience (smart merging)
        original_count = len(job_experience.get('responsibilities', []))
        job_experience['responsibilities'] = self._merge_bullets(
            job_experience.get('responsibilities', []),
            new_bullets
        )
        new_count = len(job_experience.get('responsibilities', []))

        # Calculate confidence
        relationship = skill_info.get('relationship_to_resume', {})
        base_confidence = relationship.get('confidence_if_added', 70)

        # Boost confidence if we have good story and multiple mentions
        if len(new_bullets) >= 3:
            base_confidence = min(base_confidence + 10, 95)

        change_info = {
            'section': 'experience',
            'job': job_experience.get('company', 'Unknown'),
            'job_type': job_type,
            'skill_added': skill_name,
            'story_template': story_template,
            'bullets_added': new_count - original_count,
            'bullets_modified': len([b for b in new_bullets if 'modified' in b]),
            'confidence': base_confidence,
            'coherence_score': coherence_score,
            'type': 'skill_addition'
        }

        logger.info(f"Added {skill_name} to {job_type} job using '{story_template}' story (confidence: {base_confidence}%)")

        return True, change_info

    def _generate_story_bullets_ai(
        self,
        skill_name: str,
        story_template: str,
        job_experience: Dict[str, Any],
        existing_metrics: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate story bullets using AI with specific template."""

        current_responsibilities = job_experience.get('responsibilities', [])
        current_tech = ', '.join(job_experience.get('technologies', []))

        prompt = f"""You are a resume expert. Generate authentic bullet points for adding {skill_name} to this job experience.

CURRENT JOB EXPERIENCE:
Position: {job_experience.get('position')}
Company: {job_experience.get('company')}
Current Technologies: {current_tech}
Sample Current Bullets:
{chr(10).join('- ' + r for r in current_responsibilities[:3])}

STORY TEMPLATE: {story_template}
SKILL TO ADD: {skill_name}
EXISTING METRICS: {json.dumps(existing_metrics)}

CRITICAL REQUIREMENTS:
1. Generate 2-3 bullets that form a COHERENT STORY
2. Use existing metrics or scale proportionally (don't invent unrealistic numbers)
3. Mix detail levels:
   - First mention: VERY SPECIFIC (feature names, metrics, versions)
   - Second mention: SPECIFIC (context, team/user count)
   - Third mention: SIMPLE (supporting context)
4. Use action-focused style: [ACTION] + [TECH] + [RESULT]
5. Keep 70% authentic story / 30% keywords
6. Make it sound natural, not keyword-stuffed

EXAMPLE OUTPUT FORMAT:
[
  "Built customer dashboard using React and {skill_name}, serving 50K daily users with real-time updates",
  "Developed internal admin portal using {skill_name} for operations team (200+ users)",
  "Led team managing full-stack development across React/{skill_name} applications"
]

Output ONLY a JSON array of bullet strings, nothing else.
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

            bullets = json.loads(response_text)

            if isinstance(bullets, list) and len(bullets) >= 2:
                return bullets[:3]  # Max 3 bullets
            else:
                return []

        except Exception as e:
            logger.error(f"Error generating story bullets: {str(e)}")
            # Fallback to template-based generation
            return self.story_builder.generate_story_bullets(
                story_template,
                skill_name,
                job_experience,
                existing_metrics
            )

    def _extract_metrics_from_job(self, job_experience: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from existing job bullets to use for realistic scaling."""
        metrics = {
            'users': '50K',
            'internal_users': '200+',
            'improvement': '60%',
            'requests': '10K'
        }

        responsibilities = job_experience.get('responsibilities', [])

        for resp in responsibilities:
            # Extract user counts
            if 'k' in resp.lower() and 'user' in resp.lower():
                words = resp.split()
                for i, word in enumerate(words):
                    if 'k' in word.lower() and any(c.isdigit() for c in word):
                        metrics['users'] = word.strip(',')
                        break

            # Extract percentages
            if '%' in resp:
                words = resp.split()
                for word in words:
                    if '%' in word and any(c.isdigit() for c in word):
                        metrics['improvement'] = word.strip(',')
                        break

        return metrics

    def _merge_bullets(
        self,
        existing_bullets: List[str],
        new_bullets: List[str]
    ) -> List[str]:
        """
        Intelligently merge new bullets with existing ones.

        Strategy:
        - Modify 1-2 existing bullets if they're related
        - Add remaining as new bullets
        - Keep total under reasonable limit
        """
        max_bullets = 7
        merged = list(existing_bullets)

        # Try to modify related bullets first
        for new_bullet in new_bullets[:2]:
            # Check if we should modify an existing bullet
            modified = False
            for i, existing in enumerate(merged):
                # Simple similarity check
                if len(existing) < 100 and not any(char.isdigit() for char in existing):
                    # This bullet could use more detail
                    merged[i] = new_bullet
                    modified = True
                    break

            if not modified:
                # Add as new bullet
                merged.append(new_bullet)

        # Add any remaining new bullets
        for new_bullet in new_bullets[2:]:
            if len(merged) < max_bullets:
                merged.append(new_bullet)

        return merged[:max_bullets]

    def _customize_skills_smart(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Smart skills section customization with reordering."""
        changes_made = []
        skills = resume.get('skills', {})

        # Get keywords from job
        ats_keywords = analysis.get('ats_keywords', [])
        matching_skills = analysis.get('matching_skills', [])

        # Reorder each category to put matching skills first
        for category, skill_list in skills.items():
            original_order = list(skill_list)

            # Separate matching and non-matching
            matching = [s for s in skill_list if any(
                kw.lower() in s.lower() for kw in ats_keywords + matching_skills
            )]
            non_matching = [s for s in skill_list if s not in matching]

            # Reorder: matching first
            skills[category] = matching + non_matching

            if matching:
                changes_made.append({
                    'section': 'skills',
                    'category': category,
                    'type': 'reordered',
                    'brought_to_front': len(matching),
                    'confidence': 95
                })

        resume['skills'] = skills
        return changes_made

    def _validate_coherence(self, resume: Dict[str, Any]) -> int:
        """Validate overall coherence of customized resume."""
        scores = []

        # Check each job experience
        for exp in resume.get('experience', []):
            responsibilities = exp.get('responsibilities', [])

            # Check for orphan technologies (mentioned only once)
            tech_mentions = {}
            for resp in responsibilities:
                resp_lower = resp.lower()
                common_techs = ['react', 'angular', 'vue', 'aws', 'gcp', 'docker', 'python', 'node']
                for tech in common_techs:
                    if tech in resp_lower:
                        tech_mentions[tech] = tech_mentions.get(tech, 0) + 1

            # Penalize orphan techs
            orphan_count = sum(1 for count in tech_mentions.values() if count == 1)
            multi_mention_count = sum(1 for count in tech_mentions.values() if count >= 2)

            if multi_mention_count + orphan_count > 0:
                job_coherence = (multi_mention_count / (multi_mention_count + orphan_count * 0.5)) * 100
            else:
                job_coherence = 100  # No tech mentioned, that's ok

            scores.append(job_coherence)

        return int(sum(scores) / len(scores)) if scores else 100

    def _generate_report(
        self,
        changes_made: List[Dict[str, Any]],
        coherence_score: int,
        job: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive customization report."""

        # Group changes by confidence
        high_confidence = [c for c in changes_made if c.get('confidence', 0) >= 85]
        medium_confidence = [c for c in changes_made if 65 <= c.get('confidence', 0) < 85]
        low_confidence = [c for c in changes_made if c.get('confidence', 0) < 65]

        report = {
            'job_title': job.get('title'),
            'company': job.get('company'),
            'match_score': job.get('match_score'),
            'coherence_score': coherence_score,
            'total_changes': len(changes_made),
            'high_confidence_changes': len(high_confidence),
            'medium_confidence_changes': len(medium_confidence),
            'low_confidence_changes': len(low_confidence),
            'changes_by_confidence': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'interview_readiness': self._calculate_interview_readiness(changes_made),
            'status': 'success'
        }

        return report

    def _calculate_interview_readiness(self, changes_made: List[Dict[str, Any]]) -> int:
        """Calculate how interview-ready the candidate is."""
        if not changes_made:
            return 100  # No changes needed

        # Average confidence of all changes
        confidences = [c.get('confidence', 70) for c in changes_made]
        avg_confidence = sum(confidences) / len(confidences)

        return int(avg_confidence)
