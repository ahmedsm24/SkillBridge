"""
Training module generator that creates personalized learning paths
based on identified skill gaps.
"""
import logging
import asyncio
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

from src.services.semantic_scholar import semantic_scholar

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
    
    def generate_project_training(
        self,
        gap_analysis: Dict[str, Any],
        project_info: Dict[str, Any],
        existing_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Generate training modules tailored for a specific project.
        
        This creates a two-phase training program:
        1. Foundation Phase: Fill skill gaps from resume analysis
        2. Project Phase: Project-specific skills and knowledge
        
        Args:
            gap_analysis: Results from gap analysis
            project_info: Project details including name, description, tech stack, team context
            existing_skills: Skills the candidate already has
            
        Returns:
            Dictionary with project-tailored training module structure
        """
        project_name = project_info.get("name", "Project")
        project_description = project_info.get("description", "")
        tech_stack = project_info.get("tech_stack", [])
        team_role = project_info.get("team_role", "Developer")
        organization = project_info.get("organization", "")
        project_goals = project_info.get("goals", [])
        timeline = project_info.get("timeline", "")
        
        priority_gaps = gap_analysis.get("gap_priority", [])
        
        # Generate using LLM if available
        if self.llm:
            try:
                return self._generate_project_training_llm(
                    priority_gaps, project_info, existing_skills
                )
            except Exception as e:
                logger.warning(f"LLM project training generation failed: {str(e)}")
        
        # Fallback to template-based generation
        return self._generate_project_training_template(
            priority_gaps, project_info, existing_skills
        )
    
    def _generate_project_training_llm(
        self,
        priority_gaps: List[Dict[str, Any]],
        project_info: Dict[str, Any],
        existing_skills: List[str]
    ) -> Dict[str, Any]:
        """Generate project-specific training using LLM"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert corporate training designer specializing in onboarding team members for specific projects.
            Create a comprehensive two-phase training program:
            
            PHASE 1 - FOUNDATION: Address skill gaps to bring the team member up to speed
            PHASE 2 - PROJECT SPECIFIC: Train on project-specific requirements, tools, and context
            
            Return only valid JSON."""),
            ("human", """
            Team Member Info:
            - Current Skills: {existing_skills}
            - Role: {team_role}
            - Skill Gaps: {priority_gaps}
            
            Project Info:
            - Project Name: {project_name}
            - Description: {project_description}
            - Tech Stack: {tech_stack}
            - Organization: {organization}
            - Goals: {project_goals}
            - Timeline: {timeline}
            
            Create a training program with two phases. Return JSON with this structure:
            {{
                "title": "Training Program Title",
                "description": "Overall description",
                "team_role": "Role name",
                "project_name": "Project name",
                "phases": [
                    {{
                        "phase_number": 1,
                        "phase_name": "Foundation Training",
                        "description": "Phase description",
                        "modules": [...]
                    }},
                    {{
                        "phase_number": 2,
                        "phase_name": "Project-Specific Training",
                        "description": "Phase description",
                        "modules": [...]
                    }}
                ],
                "learning_objectives": ["obj1", "obj2"],
                "modules": [full list of all modules],
                "case_studies": [...],
                "resources": [...],
                "estimated_duration": "Total duration",
                "milestones": [
                    {{"week": 1, "milestone": "Description", "deliverable": "What they should complete"}}
                ]
            }}
            """)
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "priority_gaps": json.dumps(priority_gaps[:5]),
            "existing_skills": str(existing_skills[:15]),
            "team_role": project_info.get("team_role", "Developer"),
            "project_name": project_info.get("name", "Project"),
            "project_description": project_info.get("description", ""),
            "tech_stack": str(project_info.get("tech_stack", [])),
            "organization": project_info.get("organization", ""),
            "project_goals": str(project_info.get("goals", [])),
            "timeline": project_info.get("timeline", "")
        }).content
        
        try:
            training_data = json.loads(result.strip())
            return training_data
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response for project training")
            return self._generate_project_training_template(
                priority_gaps, project_info, existing_skills
            )
    
    def _generate_project_training_template(
        self,
        priority_gaps: List[Dict[str, Any]],
        project_info: Dict[str, Any],
        existing_skills: List[str]
    ) -> Dict[str, Any]:
        """Generate project-specific training using templates"""
        project_name = project_info.get("name", "Project")
        tech_stack = project_info.get("tech_stack", [])
        team_role = project_info.get("team_role", "Developer")
        organization = project_info.get("organization", "Organization")
        
        # Phase 1: Foundation modules based on skill gaps
        foundation_modules = []
        for i, gap in enumerate(priority_gaps[:3]):
            skill = gap.get("skill", "Unknown Skill")
            foundation_modules.append({
                "title": f"Foundation {i+1}: {skill.title()}",
                "description": f"Build foundational knowledge in {skill}",
                "phase": "foundation",
                "learning_objectives": [
                    f"Understand core concepts of {skill}",
                    f"Apply {skill} in practical scenarios"
                ],
                "content": [
                    {"section": "Core Concepts", "content": f"Fundamental concepts of {skill}"},
                    {"section": "Best Practices", "content": f"Industry best practices for {skill}"}
                ],
                "practical_exercises": [
                    {"title": f"{skill} Fundamentals", "description": f"Hands-on practice with {skill}"}
                ],
                "estimated_duration": "1 week",
                "difficulty": "intermediate"
            })
        
        # Phase 2: Project-specific modules
        project_modules = []
        
        # Tech stack modules
        for i, tech in enumerate(tech_stack[:3]):
            project_modules.append({
                "title": f"Project Tech: {tech}",
                "description": f"Learn {tech} as used in {project_name}",
                "phase": "project",
                "learning_objectives": [
                    f"Understand {tech} in the context of {project_name}",
                    f"Apply {tech} to project requirements"
                ],
                "content": [
                    {"section": "Overview", "content": f"How {tech} is used in {project_name}"},
                    {"section": "Project Setup", "content": f"Setting up {tech} for the project"}
                ],
                "practical_exercises": [
                    {"title": f"{tech} Project Task", "description": f"Complete a task using {tech} for {project_name}"}
                ],
                "estimated_duration": "3-5 days",
                "difficulty": "intermediate"
            })
        
        # Project context module
        project_modules.append({
            "title": f"Project Context: {project_name}",
            "description": f"Understanding {project_name} goals, architecture, and workflow",
            "phase": "project",
            "learning_objectives": [
                "Understand project goals and objectives",
                "Learn project architecture and codebase",
                "Understand team workflow and processes"
            ],
            "content": [
                {"section": "Project Overview", "content": f"Goals and scope of {project_name}"},
                {"section": "Architecture", "content": "Technical architecture and design decisions"},
                {"section": "Team Workflow", "content": "Development workflow, code review, deployment"}
            ],
            "practical_exercises": [
                {"title": "Codebase Exploration", "description": "Navigate and understand the project codebase"},
                {"title": "First Contribution", "description": "Make your first contribution to the project"}
            ],
            "estimated_duration": "1 week",
            "difficulty": "intermediate"
        })
        
        all_modules = foundation_modules + project_modules
        
        return {
            "title": f"{team_role} Training for {project_name}",
            "description": f"Comprehensive training program for {team_role} joining {project_name} at {organization}",
            "team_role": team_role,
            "project_name": project_name,
            "organization": organization,
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Foundation Training",
                    "description": "Build foundational skills based on identified gaps",
                    "modules": foundation_modules,
                    "estimated_duration": f"{len(foundation_modules)} weeks"
                },
                {
                    "phase_number": 2,
                    "phase_name": "Project-Specific Training",
                    "description": f"Learn project-specific skills for {project_name}",
                    "modules": project_modules,
                    "estimated_duration": f"{len(project_modules)} weeks"
                }
            ],
            "learning_objectives": [
                "Bridge identified skill gaps",
                f"Gain proficiency in {project_name} tech stack",
                "Understand project context and contribute effectively",
                f"Integrate into {organization} team workflow"
            ],
            "modules": all_modules,
            "case_studies": [
                {
                    "title": f"{project_name} Feature Implementation",
                    "description": f"Walk through implementing a feature in {project_name}",
                    "learning_outcomes": ["Understand development workflow", "Apply learned skills"]
                }
            ],
            "resources": [
                {"type": "documentation", "title": "Project Documentation", "url": "Internal docs"},
                {"type": "tutorial", "title": "Tech Stack Tutorials", "url": "Relevant tutorials"}
            ],
            "estimated_duration": f"{len(all_modules) + 1} weeks",
            "milestones": [
                {"week": 1, "milestone": "Foundation Complete", "deliverable": "Pass foundation assessments"},
                {"week": len(foundation_modules) + 1, "milestone": "Project Onboarded", "deliverable": "First PR merged"},
                {"week": len(all_modules), "milestone": "Fully Productive", "deliverable": "Independent task completion"}
            ]
        }
    
    async def enrich_with_research_papers(
        self,
        training_data: Dict[str, Any],
        skill_gaps: List[str],
        domain: str = ""
    ) -> Dict[str, Any]:
        """
        Enrich training modules with real research papers from Semantic Scholar.
        
        Args:
            training_data: Generated training data
            skill_gaps: List of skills to find papers for
            domain: Industry domain for context
            
        Returns:
            Training data enriched with research papers
        """
        try:
            # Fetch papers for each skill
            papers_by_skill = await semantic_scholar.get_papers_for_skills(
                skills=skill_gaps[:5],
                domain=domain,
                papers_per_skill=3
            )
            
            # Fetch case study papers
            main_topic = skill_gaps[0] if skill_gaps else domain
            case_study_papers = await semantic_scholar.get_case_studies(
                topic=main_topic,
                domain=domain,
                limit=3
            )
            
            # Add papers to resources
            research_resources = []
            for skill, papers in papers_by_skill.items():
                for paper in papers:
                    research_resources.append({
                        "type": "research_paper",
                        "title": paper.get("title", ""),
                        "authors": paper.get("authors", ""),
                        "year": paper.get("year"),
                        "citations": paper.get("citations", 0),
                        "url": paper.get("url", ""),
                        "pdf_url": paper.get("pdf_url"),
                        "abstract": paper.get("abstract"),
                        "skill": skill,
                        "venue": paper.get("venue", "")
                    })
            
            # Add case studies
            enriched_case_studies = training_data.get("case_studies", [])
            for paper in case_study_papers:
                enriched_case_studies.append({
                    "title": paper.get("title", ""),
                    "description": paper.get("abstract", "")[:300] + "..." if paper.get("abstract") else "Research case study",
                    "authors": paper.get("authors", ""),
                    "year": paper.get("year"),
                    "url": paper.get("url", ""),
                    "pdf_url": paper.get("pdf_url"),
                    "type": "research",
                    "learning_outcomes": [
                        "Understand real-world application",
                        "Learn from published research",
                        "Apply academic insights to practice"
                    ]
                })
            
            # Merge with existing resources
            existing_resources = training_data.get("resources", [])
            training_data["resources"] = existing_resources + research_resources
            training_data["case_studies"] = enriched_case_studies
            training_data["research_papers_count"] = len(research_resources)
            
            logger.info(f"Enriched training with {len(research_resources)} research papers")
            
        except Exception as e:
            logger.warning(f"Failed to enrich with research papers: {str(e)}")
            # Return original data if enrichment fails
        
        return training_data
    
    async def generate_training_modules_async(
        self,
        gap_analysis: Dict[str, Any],
        job_title: str,
        domain: str,
        existing_skills: List[str],
        include_research: bool = True
    ) -> Dict[str, Any]:
        """
        Async version of generate_training_modules with research paper enrichment.
        
        Args:
            gap_analysis: Results from gap analysis
            job_title: Target job title
            domain: Industry domain
            existing_skills: Skills the candidate already has
            include_research: Whether to fetch research papers
            
        Returns:
            Training data enriched with research papers
        """
        # Generate base training modules
        training_data = self.generate_training_modules(
            gap_analysis=gap_analysis,
            job_title=job_title,
            domain=domain,
            existing_skills=existing_skills
        )
        
        # Enrich with research papers if requested
        if include_research:
            skill_gaps = [gap.get("skill", "") for gap in gap_analysis.get("gap_priority", [])]
            training_data = await self.enrich_with_research_papers(
                training_data=training_data,
                skill_gaps=skill_gaps,
                domain=domain
            )
        
        return training_data
    
    async def generate_project_training_async(
        self,
        gap_analysis: Dict[str, Any],
        project_info: Dict[str, Any],
        existing_skills: List[str],
        include_research: bool = True
    ) -> Dict[str, Any]:
        """
        Async version of generate_project_training with research paper enrichment.
        
        Args:
            gap_analysis: Results from gap analysis
            project_info: Project details
            existing_skills: Skills the candidate already has
            include_research: Whether to fetch research papers
            
        Returns:
            Training data enriched with research papers
        """
        # Generate base project training
        training_data = self.generate_project_training(
            gap_analysis=gap_analysis,
            project_info=project_info,
            existing_skills=existing_skills
        )
        
        # Enrich with research papers if requested
        if include_research:
            skill_gaps = [gap.get("skill", "") for gap in gap_analysis.get("gap_priority", [])]
            # Also include tech stack in search
            tech_stack = project_info.get("tech_stack", [])
            all_topics = skill_gaps + tech_stack
            
            domain = project_info.get("organization", "")
            training_data = await self.enrich_with_research_papers(
                training_data=training_data,
                skill_gaps=all_topics[:6],
                domain=domain
            )
        
        return training_data

