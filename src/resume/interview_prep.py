"""Interview preparation guide generator."""

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class InterviewPrepGenerator:
    """Generates interview preparation guides based on resume changes."""

    TECH_RESOURCES = {
        'angular': {
            'crash_course': 'https://angular.io/start',
            'vs_react': 'https://www.freecodecamp.org/news/angular-vs-react/',
            'study_time': 2
        },
        'react': {
            'crash_course': 'https://react.dev/learn',
            'hooks_guide': 'https://react.dev/reference/react',
            'study_time': 2
        },
        'next.js': {
            'crash_course': 'https://nextjs.org/learn',
            'vs_react': 'https://nextjs.org/docs',
            'study_time': 1.5
        },
        'aws': {
            'fundamentals': 'https://aws.amazon.com/getting-started/',
            'vs_gcp': 'https://cloud.google.com/docs/get-started',
            'services_overview': 'https://aws.amazon.com/products/',
            'study_time': 4
        },
        'gcp': {
            'fundamentals': 'https://cloud.google.com/docs/get-started',
            'services_overview': 'https://cloud.google.com/products',
            'study_time': 4
        },
        'docker': {
            'crash_course': 'https://docs.docker.com/get-started/',
            'best_practices': 'https://docs.docker.com/develop/dev-best-practices/',
            'study_time': 2
        },
        'kubernetes': {
            'basics': 'https://kubernetes.io/docs/tutorials/kubernetes-basics/',
            'concepts': 'https://kubernetes.io/docs/concepts/',
            'study_time': 3
        },
        'openai': {
            'api_docs': 'https://platform.openai.com/docs/introduction',
            'cookbook': 'https://cookbook.openai.com/',
            'study_time': 2
        },
        'typescript': {
            'handbook': 'https://www.typescriptlang.org/docs/handbook/intro.html',
            'from_javascript': 'https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html',
            'study_time': 1.5
        },
        'graphql': {
            'introduction': 'https://graphql.org/learn/',
            'best_practices': 'https://graphql.org/learn/best-practices/',
            'study_time': 2
        }
    }

    def __init__(self):
        """Initialize interview prep generator."""
        pass

    def generate_prep_guide(
        self,
        customization_report: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate interview preparation guide.

        Returns comprehensive guide with:
        - What was added/changed
        - Study recommendations
        - Sample interview questions
        - Estimated study time
        """
        changes = customization_report.get('changes_by_confidence', {})
        high_conf = changes.get('high', [])
        medium_conf = changes.get('medium', [])

        # Extract skills that were added
        skills_added = self._extract_added_skills(high_conf + medium_conf)

        # Generate prep sections
        prep_guide = {
            'job_info': {
                'title': job.get('title'),
                'company': job.get('company'),
                'match_score': job.get('match_score')
            },
            'overview': self._generate_overview(customization_report),
            'changes_summary': self._summarize_changes(high_conf, medium_conf),
            'study_plan': self._generate_study_plan(skills_added),
            'interview_questions': self._generate_sample_questions(skills_added),
            'total_study_time': self._calculate_study_time(skills_added),
            'confidence_assessment': self._assess_confidence(customization_report)
        }

        return prep_guide

    def _extract_added_skills(self, changes: List[Dict[str, Any]]) -> List[str]:
        """Extract list of skills that were added."""
        skills = []

        for change in changes:
            if change.get('type') == 'skill_addition':
                skill = change.get('skill_added', '')
                if skill and skill not in skills:
                    skills.append(skill.lower())

        return skills

    def _generate_overview(self, report: Dict[str, Any]) -> str:
        """Generate overview section."""
        total = report.get('total_changes', 0)
        coherence = report.get('coherence_score', 0)
        readiness = report.get('interview_readiness', 0)

        if readiness >= 85:
            readiness_text = "HIGH - You can defend these changes easily"
        elif readiness >= 70:
            readiness_text = "MEDIUM - Review the topics below before interview"
        else:
            readiness_text = "LOW - Significant preparation needed"

        overview = f"""
INTERVIEW PREPARATION GUIDE
for {report.get('job_title', 'Position')} at {report.get('company', 'Company')}

Resume Match Score: {report.get('match_score', 0)}%
Resume Coherence: {coherence}%
Interview Readiness: {readiness_text}

Total Changes Made: {total}
└─ High Confidence: {report.get('high_confidence_changes', 0)} (easy to defend)
└─ Medium Confidence: {report.get('medium_confidence_changes', 0)} (review recommended)
└─ Low Confidence: {report.get('low_confidence_changes', 0)} (significant prep needed)
"""
        return overview.strip()

    def _summarize_changes(
        self,
        high_conf: List[Dict[str, Any]],
        medium_conf: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Summarize changes made to resume."""
        summary = {
            'high_confidence': [],
            'medium_confidence': []
        }

        for change in high_conf:
            if change.get('type') == 'skill_addition':
                skill = change.get('skill_added', '')
                job_type = change.get('job_type', 'current')
                conf = change.get('confidence', 0)
                summary['high_confidence'].append(
                    f"✅ Added {skill} to {job_type} job ({conf}% confidence)"
                )

        for change in medium_conf:
            if change.get('type') == 'skill_addition':
                skill = change.get('skill_added', '')
                job_type = change.get('job_type', 'current')
                conf = change.get('confidence', 0)
                summary['medium_confidence'].append(
                    f"⚠️  Added {skill} to {job_type} job ({conf}% confidence)"
                )

        return summary

    def _generate_study_plan(self, skills_added: List[str]) -> List[Dict[str, Any]]:
        """Generate detailed study plan for each skill."""
        study_plan = []

        for skill in skills_added:
            skill_lower = skill.lower()

            # Find matching resources
            resources = None
            for tech, res in self.TECH_RESOURCES.items():
                if tech in skill_lower:
                    resources = res
                    break

            if resources:
                plan_item = {
                    'skill': skill,
                    'study_time_hours': resources.get('study_time', 2),
                    'resources': [
                        {'name': k.replace('_', ' ').title(), 'url': v}
                        for k, v in resources.items()
                        if isinstance(v, str) and v.startswith('http')
                    ],
                    'key_topics': self._get_key_topics(skill),
                    'sample_answer': self._generate_sample_answer(skill)
                }
                study_plan.append(plan_item)
            else:
                # Generic plan for unknown tech
                plan_item = {
                    'skill': skill,
                    'study_time_hours': 2,
                    'resources': [
                        {'name': 'Official Documentation', 'url': f'Search: {skill} official docs'},
                        {'name': 'Tutorial', 'url': f'Search: {skill} crash course'}
                    ],
                    'key_topics': [
                        f'Basic concepts of {skill}',
                        f'How {skill} compares to alternatives',
                        f'Common use cases for {skill}'
                    ],
                    'sample_answer': f'I have experience with {skill} and understand its core concepts...'
                }
                study_plan.append(plan_item)

        return study_plan

    def _get_key_topics(self, skill: str) -> List[str]:
        """Get key topics to study for a skill."""
        skill_lower = skill.lower()

        topic_map = {
            'angular': [
                'Components and templates',
                'Services and dependency injection',
                'Angular vs React differences',
                'RxJS observables basics',
                'Angular CLI and project structure'
            ],
            'react': [
                'Components and JSX',
                'Hooks (useState, useEffect)',
                'State management',
                'React vs Angular',
                'Component lifecycle'
            ],
            'next.js': [
                'Server-side rendering (SSR)',
                'Static site generation (SSG)',
                'How Next.js extends React',
                'File-based routing',
                'API routes'
            ],
            'aws': [
                'Core services: EC2, S3, Lambda',
                'How AWS compares to GCP',
                'Serverless architecture',
                'Cloud deployment basics',
                'IAM and security basics'
            ],
            'docker': [
                'Containers vs VMs',
                'Dockerfile basics',
                'Docker Compose',
                'Container orchestration',
                'Common Docker commands'
            ],
            'openai': [
                'API basics and authentication',
                'Chat completions',
                'How OpenAI differs from Gemini/Vertex AI',
                'Prompt engineering',
                'Token limits and pricing'
            ]
        }

        for tech, topics in topic_map.items():
            if tech in skill_lower:
                return topics

        return [f'Basic concepts of {skill}', f'Common use cases', f'Best practices']

    def _generate_sample_answer(self, skill: str) -> str:
        """Generate sample answer template for interview questions."""
        skill_lower = skill.lower()

        if 'angular' in skill_lower and 'react' in skill_lower:
            return "I've worked with both React and Angular. My primary expertise is in React, but I've also built applications with Angular, particularly for [mention admin dashboard from resume]. The concepts are very similar - components, state management, etc."

        elif 'openai' in skill_lower or 'gemini' in skill_lower:
            return "I have experience with LLM APIs - primarily Gemini/Vertex AI in my current role. I understand the core concepts of prompting, completions, and token management, which are consistent across providers like OpenAI and Gemini."

        elif 'aws' in skill_lower or 'gcp' in skill_lower:
            return "I've worked with cloud platforms - [mention which from resume]. The core concepts like serverless functions, object storage, and managed databases are consistent across AWS and GCP, just with different naming."

        else:
            return f"I have experience with {skill} in [mention context from resume]. I understand the core concepts and have used it in production environments."

    def _generate_sample_questions(self, skills_added: List[str]) -> List[Dict[str, str]]:
        """Generate sample interview questions for added skills."""
        questions = []

        for skill in skills_added:
            skill_lower = skill.lower()

            if 'angular' in skill_lower or 'react' in skill_lower:
                questions.append({
                    'question': f'Tell me about your experience with {skill}',
                    'suggested_answer': f'I\'ve used {skill} to build [mention from resume]. My main project was [describe project]. The key features included...'
                })
                questions.append({
                    'question': f'What\'s the difference between {skill} and [alternative]?',
                    'suggested_answer': 'Both are component-based frameworks. The main differences are [mention 2-3 key differences]. I\'ve found that...'
                })

            if 'aws' in skill_lower or 'gcp' in skill_lower or 'cloud' in skill_lower:
                questions.append({
                    'question': 'Describe a cloud architecture you\'ve built',
                    'suggested_answer': 'In [mention role], I built a system using [services]. The architecture included [describe components]. We chose this approach because...'
                })

            if 'api' in skill_lower or 'openai' in skill_lower:
                questions.append({
                    'question': 'How have you worked with APIs?',
                    'suggested_answer': 'I\'ve integrated various APIs including [mention from resume]. For example, with the {skill} API, I [describe use case]...'
                })

        # Add general questions
        questions.append({
            'question': 'Walk me through your most recent project',
            'suggested_answer': 'Start with the project from your current job on resume. Mention the technologies, your role, and the impact.'
        })

        return questions[:6]  # Limit to 6 questions

    def _calculate_study_time(self, skills_added: List[str]) -> Dict[str, Any]:
        """Calculate total study time needed."""
        total_hours = 0

        for skill in skills_added:
            skill_lower = skill.lower()
            for tech, resources in self.TECH_RESOURCES.items():
                if tech in skill_lower:
                    total_hours += resources.get('study_time', 2)
                    break
            else:
                total_hours += 2  # Default

        return {
            'total_hours': total_hours,
            'recommended_schedule': self._create_study_schedule(total_hours),
            'urgency': 'High' if total_hours > 6 else 'Medium' if total_hours > 3 else 'Low'
        }

    def _create_study_schedule(self, total_hours: int) -> str:
        """Create a study schedule recommendation."""
        if total_hours <= 3:
            return "Can be completed in 1-2 evenings before interview"
        elif total_hours <= 6:
            return "Plan for 2-3 days of evening study (2-3 hours per day)"
        else:
            return f"Plan for {int(total_hours/2)} days of study (2 hours per day) or complete over a weekend"

    def _assess_confidence(self, report: Dict[str, Any]) -> str:
        """Assess overall confidence level."""
        readiness = report.get('interview_readiness', 0)

        if readiness >= 85:
            return """
✅ HIGH CONFIDENCE
You can defend all resume changes easily. The technologies added are very similar
to what you already know. Quick review of key concepts should be sufficient.
"""
        elif readiness >= 70:
            return """
⚠️  MEDIUM CONFIDENCE
Most changes are defensible, but spend time reviewing the topics marked as medium
confidence. Focus on understanding key differences and being ready to discuss your
experience honestly.
"""
        else:
            return """
⚠️  LOWER CONFIDENCE
Several changes require significant preparation. Review all study materials carefully
and practice explaining your experience. Be ready to acknowledge areas where you're
still learning.
"""

    def format_as_text(self, prep_guide: Dict[str, Any]) -> str:
        """Format prep guide as readable text."""
        output = []

        # Overview
        output.append("=" * 70)
        output.append(prep_guide.get('overview', ''))
        output.append("=" * 70)
        output.append("")

        # Changes summary
        output.append("CHANGES MADE TO YOUR RESUME:")
        output.append("-" * 70)
        changes = prep_guide.get('changes_summary', {})
        for change in changes.get('high_confidence', []):
            output.append(change)
        for change in changes.get('medium_confidence', []):
            output.append(change)
        output.append("")

        # Study plan
        output.append("STUDY PLAN:")
        output.append("-" * 70)
        for item in prep_guide.get('study_plan', []):
            output.append(f"\n📚 {item['skill'].upper()} ({item['study_time_hours']} hours)")
            output.append("\nKey Topics:")
            for topic in item['key_topics']:
                output.append(f"  • {topic}")
            output.append("\nResources:")
            for resource in item['resources']:
                output.append(f"  • {resource['name']}: {resource['url']}")
            output.append(f"\nSample Answer: \"{item['sample_answer']}\"")
            output.append("")

        # Interview questions
        output.append("\nSAMPLE INTERVIEW QUESTIONS:")
        output.append("-" * 70)
        for i, q in enumerate(prep_guide.get('interview_questions', []), 1):
            output.append(f"\nQ{i}: {q['question']}")
            output.append(f"A: {q['suggested_answer']}")
            output.append("")

        # Study time
        time_info = prep_guide.get('total_study_time', {})
        output.append("\nTOTAL STUDY TIME NEEDED:")
        output.append("-" * 70)
        output.append(f"Total: {time_info.get('total_hours', 0)} hours")
        output.append(f"Schedule: {time_info.get('recommended_schedule', '')}")
        output.append(f"Urgency: {time_info.get('urgency', 'Medium')}")
        output.append("")

        # Confidence assessment
        output.append("\nCONFIDENCE ASSESSMENT:")
        output.append("-" * 70)
        output.append(prep_guide.get('confidence_assessment', ''))
        output.append("")

        output.append("=" * 70)
        output.append("Good luck with your interview! 🚀")
        output.append("=" * 70)

        return '\n'.join(output)
