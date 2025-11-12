"""Story-based resume customization with coherence validation."""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import copy


logger = logging.getLogger(__name__)


class StoryBuilder:
    """Builds coherent stories for adding technologies to resume."""

    # Technology timeline - when technologies became mainstream
    TECH_TIMELINE = {
        'react': 2015,
        'angular': 2016,
        'vue': 2016,
        'next.js': 2020,
        'docker': 2015,
        'kubernetes': 2017,
        'aws lambda': 2015,
        'openai': 2020,
        'gemini': 2023,
        'chatgpt': 2023,
        'typescript': 2017,
        'graphql': 2018,
        'tailwind': 2019,
    }

    STORY_TEMPLATES = {
        'multiple_apps': {
            'pattern': 'Different applications using different technologies',
            'min_mentions': 3,
            'example': [
                'Built {customer_app} using {tech_a}, serving {metric} users',
                'Developed {internal_tool} using {tech_b} for {team/purpose}',
                'Created shared {component/api} connecting both applications',
                'Led team managing {tech_a}/{tech_b} codebases'
            ]
        },
        'migration': {
            'pattern': 'Migrated from old to new technology',
            'min_mentions': 3,
            'example': [
                'Maintained legacy {old_tech} application handling {metric}',
                'Led migration from {old_tech} to {new_tech} for {reason}',
                'Rebuilt {feature} in {new_tech}, improving {metric} by {%}',
                'Completed phased rollout over {timeframe}'
            ]
        },
        'integration': {
            'pattern': 'Integrated different technologies/systems',
            'min_mentions': 2,
            'example': [
                'Built {frontend} using {frontend_tech}',
                'Implemented {backend/service} using {backend_tech}',
                'Integrated {system_a} with {system_b} via {method}'
            ]
        },
        'hybrid_cloud': {
            'pattern': 'Multi-cloud or hybrid cloud strategy',
            'min_mentions': 2,
            'example': [
                'Deployed {service_a} on {cloud_1} for {reason}',
                'Used {cloud_2} for {different_service/DR}',
                'Implemented cross-cloud {feature} reducing costs by {%}'
            ]
        },
        'enhancement': {
            'pattern': 'Added new technology to enhance existing system',
            'min_mentions': 2,
            'example': [
                'Optimized {existing_system} by implementing {new_tech}',
                'Integrated {new_tech} improving {metric} by {%}',
                'Deployed using {tech} for {specific_benefit}'
            ]
        }
    }

    def __init__(self):
        """Initialize story builder."""
        pass

    def can_add_technology_to_job(
        self,
        job_experience: Dict[str, Any],
        technology: str,
        job_requirements: Dict[str, Any]
    ) -> Tuple[bool, str, int]:
        """
        Check if technology can be added to this job experience coherently.

        Returns:
            (can_add, best_story_template, coherence_score)
        """
        # Check timeline
        job_start_year = self._extract_year(job_experience.get('start_date', ''))
        tech_exists = self._tech_existed_in_year(technology, job_start_year)

        if not tech_exists:
            logger.debug(f"Cannot add {technology} to job starting {job_start_year} - tech didn't exist")
            return False, '', 0

        # Analyze current tech stack
        current_stack = self._extract_tech_stack(job_experience)

        # Find best story template
        best_template = None
        best_score = 0

        for template_name, template_info in self.STORY_TEMPLATES.items():
            score = self._score_story_template(
                template_name,
                technology,
                current_stack,
                job_experience,
                job_requirements
            )

            if score > best_score:
                best_score = score
                best_template = template_name

        # Need at least 70% coherence score
        can_add = best_score >= 70

        return can_add, best_template or '', best_score

    def _tech_existed_in_year(self, technology: str, year: int) -> bool:
        """Check if technology existed in the given year."""
        if year == 0:
            return True  # Can't determine year, assume it's ok

        tech_lower = technology.lower()

        # Check exact matches
        for tech_name, tech_year in self.TECH_TIMELINE.items():
            if tech_name in tech_lower:
                return year >= tech_year

        # For unknown technologies, assume they existed
        return True

    def _extract_year(self, date_string: str) -> int:
        """Extract year from date string."""
        if not date_string or date_string.lower() == 'present':
            return datetime.now().year

        try:
            # Try various formats
            for fmt in ['%Y-%m', '%Y', '%m/%Y', '%B %Y']:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    return dt.year
                except:
                    continue

            # Try extracting just the year
            year_str = ''.join(c for c in date_string if c.isdigit())
            if len(year_str) == 4:
                return int(year_str)

        except:
            pass

        return 0  # Unknown

    def _extract_tech_stack(self, job_experience: Dict[str, Any]) -> List[str]:
        """Extract technologies from job experience."""
        tech_stack = []

        # From technologies field
        if 'technologies' in job_experience:
            tech_stack.extend(job_experience['technologies'])

        # From responsibilities
        responsibilities = job_experience.get('responsibilities', [])
        for resp in responsibilities:
            # Simple extraction - look for common patterns
            resp_lower = resp.lower()
            common_techs = [
                'react', 'angular', 'vue', 'next.js', 'node.js',
                'python', 'java', 'go', 'typescript', 'javascript',
                'aws', 'gcp', 'azure', 'docker', 'kubernetes',
                'postgresql', 'mongodb', 'redis', 'mysql',
                'openai', 'gemini', 'vertex ai'
            ]

            for tech in common_techs:
                if tech in resp_lower and tech not in [t.lower() for t in tech_stack]:
                    tech_stack.append(tech)

        return tech_stack

    def _score_story_template(
        self,
        template_name: str,
        new_technology: str,
        current_stack: List[str],
        job_experience: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> int:
        """Score how well a story template fits for adding this technology."""
        score = 0

        if template_name == 'multiple_apps':
            # Good if adding similar frontend/backend tech
            similar_frontend = any(t in new_technology.lower() or new_technology.lower() in t
                                  for t in ['react', 'angular', 'vue', 'next.js']
                                  if t in ' '.join(current_stack).lower())
            if similar_frontend:
                score = 95

        elif template_name == 'migration':
            # Good if we have old version of tech
            # e.g., AngularJS → Angular, or JavaScript → TypeScript
            has_old_version = any(
                'angular' in new_technology.lower() and 'angularjs' in t.lower()
                or new_technology.lower() in t.lower()
                for t in current_stack
            )
            if has_old_version:
                score = 90

        elif template_name == 'integration':
            # Always somewhat applicable for backend/API tech
            if any(tech in new_technology.lower() for tech in ['api', 'node', 'python', 'java']):
                score = 75

        elif template_name == 'hybrid_cloud':
            # Good if adding cloud tech and we have another cloud
            is_cloud = any(c in new_technology.lower() for c in ['aws', 'gcp', 'azure'])
            has_cloud = any(c in ' '.join(current_stack).lower() for c in ['aws', 'gcp', 'azure'])
            if is_cloud and has_cloud:
                score = 85

        elif template_name == 'enhancement':
            # Generally applicable fallback
            score = 60

        return score

    def generate_story_bullets(
        self,
        template_name: str,
        new_technology: str,
        job_experience: Dict[str, Any],
        existing_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate bullet points following a story template."""
        template = self.STORY_TEMPLATES.get(template_name, {})
        examples = template.get('example', [])

        generated_bullets = []

        if template_name == 'multiple_apps':
            # Generate bullets for multiple apps story
            customer_metric = existing_metrics.get('users', '50K')
            internal_metric = existing_metrics.get('internal_users', '200+')

            generated_bullets = [
                f"Built customer portal using {{existing_tech}}, serving {customer_metric} daily users",
                f"Developed internal admin dashboard using {new_technology} for operations team ({internal_metric} users)",
                "Created shared REST API connecting customer and admin applications",
                f"Led team managing full-stack development across multiple frontend frameworks"
            ]

        elif template_name == 'migration':
            metric = existing_metrics.get('improvement', '60%')
            generated_bullets = [
                f"Led migration to {new_technology} for improved performance and maintainability",
                f"Rebuilt key features in {new_technology}, improving load time by {metric}",
                "Completed phased rollout minimizing downtime and user impact"
            ]

        elif template_name == 'integration':
            generated_bullets = [
                f"Implemented backend services using {new_technology}",
                f"Integrated {new_technology} with existing systems via REST APIs"
            ]

        elif template_name == 'hybrid_cloud':
            generated_bullets = [
                f"Implemented hybrid cloud architecture using {{existing_cloud}} and {new_technology}",
                f"Deployed services on {new_technology} for disaster recovery and global distribution"
            ]

        elif template_name == 'enhancement':
            metric = existing_metrics.get('improvement', '50%')
            generated_bullets = [
                f"Optimized application performance by implementing {new_technology}",
                f"Integrated {new_technology} improving response time by {metric}"
            ]

        return generated_bullets

    def calculate_coherence_score(
        self,
        modified_job: Dict[str, Any],
        technology: str
    ) -> int:
        """Calculate coherence score for modified job experience."""
        responsibilities = modified_job.get('responsibilities', [])

        # Count mentions of the technology
        mention_count = sum(
            1 for resp in responsibilities
            if technology.lower() in resp.lower()
        )

        # Check for context (not just keyword dropping)
        has_context = any(
            len(resp) > 50 and technology.lower() in resp.lower()
            for resp in responsibilities
        )

        # Check for specific metrics/details
        has_specifics = any(
            any(char.isdigit() for char in resp) and technology.lower() in resp.lower()
            for resp in responsibilities
        )

        score = 0

        # Mention count (40 points)
        if mention_count >= 3:
            score += 40
        elif mention_count >= 2:
            score += 30
        elif mention_count >= 1:
            score += 15

        # Context richness (30 points)
        if has_context:
            score += 30

        # Specificity (30 points)
        if has_specifics:
            score += 30

        return min(score, 100)
