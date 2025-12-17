"""
Training module generator that creates personalized learning paths
based on identified skill gaps.
"""
import logging
from typing import Dict, List, Optional, Any
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    try:
        from langchain.llms import OpenAI
        from langchain.prompts import PromptTemplate
        from langchain.chains import LLMChain
        LANGCHAIN_AVAILABLE = True
        LANGCHAIN_LEGACY = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        LANGCHAIN_LEGACY = False
import json

logger = logging.getLogger(__name__)


class TrainingGenerator:
    """Service for generating personalized training modules"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the training generator.
        
        Args:
            openai_api_key: OpenAI API key for LLM-based generation
        """
        self.openai_api_key = openai_api_key
        if self.openai_api_key and LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key, model="gpt-3.5-turbo")
                self.use_legacy = False
            except:
                try:
                    self.llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
                    self.use_legacy = True
                except:
                    self.llm = None
                    self.use_legacy = False
        else:
            self.llm = None
            self.use_legacy = False
    
    def generate_training_modules(
        self,
        gap_analysis: Dict[str, Any],
        job_title: str,
        domain: str,
        existing_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive training modules based on gap analysis.
        
        Args:
            gap_analysis: Results from gap analysis
            job_title: Target job title
            domain: Industry domain (e.g., "biotech")
            existing_skills: Skills the candidate already has
            
        Returns:
            Dictionary with training module structure
        """
        skill_gaps = gap_analysis.get("skill_gaps", [])
        priority_gaps = gap_analysis.get("gap_priority", [])
        
        if not skill_gaps:
            return self._generate_default_module(job_title, domain)
        
        # Generate modules using LLM if available
        if self.llm:
            try:
                return self._generate_with_llm(
                    priority_gaps, job_title, domain, existing_skills
                )
            except Exception as e:
                logger.warning(f"LLM generation failed: {str(e)}, using template-based generation")
                import traceback
                logger.debug(traceback.format_exc())
        
        # Fallback to template-based generation
        return self._generate_template_based(priority_gaps, job_title, domain)
    
    def _generate_with_llm(
        self,
        priority_gaps: List[Dict[str, Any]],
        job_title: str,
        domain: str,
        existing_skills: List[str]
    ) -> Dict[str, Any]:
        """Generate training modules using LLM"""
        if self.use_legacy:
            prompt = PromptTemplate(
                input_variables=["priority_gaps", "job_title", "domain", "existing_skills"],
                template="""
                You are an expert training curriculum designer. Create a comprehensive training program for a candidate
                transitioning to {job_title} in the {domain} industry.
                
                The candidate already has these skills: {existing_skills}
                
                They need to learn these skills (in priority order):
                {priority_gaps}
                
                Create a training program with:
                1. Learning objectives
                2. Multiple training modules (each covering a skill gap)
                3. Case studies relevant to {domain} industry
                4. Practical exercises
                5. Recommended resources (papers, tutorials, courses)
                
                For each module, include:
                - Title
                - Description
                - Learning objectives
                - Content outline
                - Practical exercises
                - Estimated duration
                
                Focus on practical, hands-on learning that bridges theory with real-world application in {domain}.
                Include case studies that demonstrate the application of these skills in {domain} contexts.
                
                Return a JSON object with this structure:
                {{
                    "title": "Training Program Title",
                    "description": "Overall description",
                    "learning_objectives": ["obj1", "obj2"],
                    "modules": [
                        {{
                            "title": "Module Title",
                            "description": "Module description",
                            "learning_objectives": ["obj1", "obj2"],
                            "content": [
                                {{"section": "Section title", "content": "Section content"}}
                            ],
                            "practical_exercises": [
                                {{"title": "Exercise title", "description": "Exercise description"}}
                            ],
                            "estimated_duration": "X hours/days/weeks",
                            "difficulty": "beginner|intermediate|advanced"
                        }}
                    ],
                    "case_studies": [
                        {{
                            "title": "Case study title",
                            "description": "Case study description",
                            "learning_outcomes": ["outcome1", "outcome2"]
                        }}
                    ],
                    "resources": [
                        {{"type": "paper|tutorial|course", "title": "Resource title", "url": "url or description"}}
                    ],
                    "estimated_duration": "Overall duration"
                }}
                
                JSON:
                """
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(
                priority_gaps=json.dumps(priority_gaps[:5]),
                job_title=job_title,
                domain=domain,
                existing_skills=str(existing_skills[:15])
            )
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert training curriculum designer. Create comprehensive training programs. Return only valid JSON."),
                ("human", "Job: {job_title} in {domain}\nExisting skills: {existing_skills}\nGaps to address: {priority_gaps}\n\nCreate training program with modules, case studies, exercises, resources. Return JSON:")
            ])
            chain = prompt | self.llm
            result = chain.invoke({
                "priority_gaps": json.dumps(priority_gaps[:5]),
                "job_title": job_title,
                "domain": domain,
                "existing_skills": str(existing_skills[:15])
            }).content
        
        try:
            training_data = json.loads(result.strip())
            return training_data
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return self._generate_template_based(priority_gaps, job_title, domain)
    
    def _generate_template_based(
        self,
        priority_gaps: List[Dict[str, Any]],
        job_title: str,
        domain: str
    ) -> Dict[str, Any]:
        """Generate training modules using templates"""
        modules = []
        
        for i, gap in enumerate(priority_gaps[:5]):
            skill = gap.get("skill", "Unknown Skill")
            importance = gap.get("importance", "important")
            
            module = {
                "title": f"Module {i+1}: {skill.title()}",
                "description": f"Learn {skill} for {job_title} in {domain}",
                "learning_objectives": [
                    f"Understand the fundamentals of {skill}",
                    f"Apply {skill} in {domain} contexts",
                    f"Practice {skill} through hands-on exercises"
                ],
                "content": [
                    {
                        "section": "Introduction",
                        "content": f"Introduction to {skill} and its relevance to {job_title} in {domain}"
                    },
                    {
                        "section": "Core Concepts",
                        "content": f"Deep dive into {skill} concepts and methodologies"
                    },
                    {
                        "section": "Practical Application",
                        "content": f"Applying {skill} to real-world {domain} scenarios"
                    }
                ],
                "practical_exercises": [
                    {
                        "title": f"Exercise 1: {skill} Basics",
                        "description": f"Hands-on exercise to practice {skill} fundamentals"
                    },
                    {
                        "title": f"Exercise 2: {skill} in {domain}",
                        "description": f"Apply {skill} to a {domain}-specific problem"
                    }
                ],
                "estimated_duration": "1-2 weeks",
                "difficulty": "intermediate" if importance == "critical" else "beginner"
            }
            modules.append(module)
        
        return {
            "title": f"Training Program for {job_title} in {domain}",
            "description": f"Comprehensive training program to bridge skill gaps for {job_title}",
            "learning_objectives": [
                "Bridge identified skill gaps",
                f"Gain proficiency in {domain} domain knowledge",
                "Apply learned skills through practical exercises"
            ],
            "modules": modules,
            "case_studies": [
                {
                    "title": f"{domain.title()} Case Study 1",
                    "description": f"Real-world case study applying learned skills in {domain}",
                    "learning_outcomes": ["Practical application", "Problem-solving", "Domain expertise"]
                }
            ],
            "resources": [
                {
                    "type": "tutorial",
                    "title": "Online Tutorials",
                    "url": "Search for relevant tutorials on the identified skills"
                },
                {
                    "type": "paper",
                    "title": "Research Papers",
                    "url": "Review recent papers in the field"
                }
            ],
            "estimated_duration": f"{len(modules) * 2} weeks"
        }
    
    def _generate_default_module(self, job_title: str, domain: str) -> Dict[str, Any]:
        """Generate a default training module when no gaps are identified"""
        return {
            "title": f"Orientation Program for {job_title}",
            "description": f"Introduction to {job_title} role in {domain}",
            "learning_objectives": [
                "Understand role expectations",
                "Familiarize with domain-specific practices"
            ],
            "modules": [
                {
                    "title": "Role Introduction",
                    "description": f"Introduction to {job_title} responsibilities",
                    "learning_objectives": ["Understand role", "Learn expectations"],
                    "content": [{"section": "Overview", "content": "Role overview"}],
                    "practical_exercises": [],
                    "estimated_duration": "1 week",
                    "difficulty": "beginner"
                }
            ],
            "case_studies": [],
            "resources": [],
            "estimated_duration": "1 week"
        }

