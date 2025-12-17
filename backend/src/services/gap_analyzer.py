"""
Gap analysis service that compares resume skills with job requirements
and identifies skill gaps that need to be addressed.
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
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


class GapAnalyzer:
    """Service for analyzing skill gaps between resume and job requirements"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the gap analyzer.
        
        Args:
            openai_api_key: OpenAI API key for LLM-based analysis
        """
        self.openai_api_key = openai_api_key
        if openai_api_key and LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key, model="gpt-3.5-turbo")
                self.use_legacy = False
            except:
                try:
                    self.llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
                    self.use_legacy = True
                except:
                    self.llm = None
                    self.use_legacy = False
        else:
            self.llm = None
            self.use_legacy = False
    
    def extract_job_skills(self, job_description: str) -> Dict[str, List[str]]:
        """
        Extract required and preferred skills from job description.
        
        Args:
            job_description: Job description text
            
        Returns:
            Dictionary with 'required' and 'preferred' skills lists
        """
        required_skills = []
        preferred_skills = []
        
        if self.llm:
            try:
                if self.use_legacy:
                    prompt = PromptTemplate(
                        input_variables=["job_description"],
                        template="""
                        Analyze the following job description and extract:
                        1. Required skills (must-have)
                        2. Preferred skills (nice-to-have)
                        3. Domain knowledge areas
                        4. Tools and technologies
                        
                        Return a JSON object with this structure:
                        {{
                            "required_skills": ["skill1", "skill2"],
                            "preferred_skills": ["skill3", "skill4"],
                            "domain_knowledge": ["domain1", "domain2"],
                            "tools": ["tool1", "tool2"]
                        }}
                        
                        Job description:
                        {job_description}
                        
                        JSON:
                        """
                    )
                    chain = LLMChain(llm=self.llm, prompt=prompt)
                    result = chain.run(job_description=job_description[:4000])
                else:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", "You are a job description analyzer. Extract required skills, preferred skills, domain knowledge, and tools. Return only valid JSON."),
                        ("human", "Job description:\n{job_description}\n\nJSON:")
                    ])
                    chain = prompt | self.llm
                    result = chain.invoke({"job_description": job_description[:4000]}).content
                
                try:
                    extracted = json.loads(result.strip())
                    required_skills = extracted.get("required_skills", [])
                    preferred_skills = extracted.get("preferred_skills", [])
                    # Combine domain knowledge and tools
                    all_required = required_skills + extracted.get("domain_knowledge", []) + extracted.get("tools", [])
                    all_preferred = preferred_skills
                    return {
                        "required": all_required,
                        "preferred": all_preferred
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM response as JSON")
            except Exception as e:
                logger.warning(f"LLM skill extraction failed: {str(e)}")
        
        # Fallback: simple keyword extraction
        keywords = [
            "python", "machine learning", "deep learning", "data science",
            "statistics", "causal inference", "RCT", "clinical trials",
            "health data", "biotech", "pharmaceutical", "R", "SQL",
            "pytorch", "tensorflow", "pandas", "numpy"
        ]
        
        job_lower = job_description.lower()
        for keyword in keywords:
            if keyword in job_lower:
                required_skills.append(keyword)
        
        return {
            "required": required_skills,
            "preferred": preferred_skills
        }
    
    def normalize_skill(self, skill: str) -> str:
        """
        Normalize skill name for comparison.
        
        Args:
            skill: Skill name
            
        Returns:
            Normalized skill name
        """
        skill = skill.lower().strip()
        # Common aliases
        aliases = {
            "ml": "machine learning",
            "dl": "deep learning",
            "ai": "artificial intelligence",
            "rct": "randomized controlled trials",
            "rcts": "randomized controlled trials"
        }
        return aliases.get(skill, skill)
    
    def calculate_skill_overlap(self, resume_skills: List[str], job_skills: List[str]) -> Tuple[List[str], List[str]]:
        """
        Calculate overlap between resume skills and job skills.
        
        Args:
            resume_skills: Skills from resume
            job_skills: Skills required by job
            
        Returns:
            Tuple of (matching_skills, missing_skills)
        """
        resume_normalized = [self.normalize_skill(s) for s in resume_skills]
        job_normalized = [self.normalize_skill(s) for s in job_skills]
        
        matching = []
        missing = []
        
        for job_skill in job_normalized:
            found = False
            for resume_skill in resume_normalized:
                # Check for exact match or substring match
                if job_skill in resume_skill or resume_skill in job_skill:
                    matching.append(job_skill)
                    found = True
                    break
            if not found:
                missing.append(job_skill)
        
        return matching, missing
    
    def analyze_gaps(
        self,
        resume_skills: List[str],
        resume_experience: List[Dict[str, Any]],
        job_description: str,
        job_title: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive gap analysis.
        
        Args:
            resume_skills: Skills extracted from resume
            resume_experience: Work experience from resume
            job_description: Full job description text
            job_title: Job title
            domain: Domain/industry (e.g., "biotech", "finance")
            
        Returns:
            Dictionary with gap analysis results
        """
        # Extract job skills
        job_skills_dict = self.extract_job_skills(job_description)
        all_job_skills = job_skills_dict["required"] + job_skills_dict["preferred"]
        
        # Calculate overlaps
        matching_skills, missing_skills = self.calculate_skill_overlap(resume_skills, all_job_skills)
        required_matching, required_missing = self.calculate_skill_overlap(
            resume_skills, job_skills_dict["required"]
        )
        
        # Use LLM for deeper analysis if available
        gap_details = []
        if self.llm and missing_skills:
            try:
                if self.use_legacy:
                    prompt = PromptTemplate(
                        input_variables=["resume_skills", "missing_skills", "job_title", "domain", "job_description"],
                        template="""
                        Analyze the skill gaps for a candidate applying to {job_title} in the {domain} domain.
                        
                        Candidate's current skills: {resume_skills}
                        Missing skills: {missing_skills}
                        Job description: {job_description}
                        
                        For each missing skill, provide:
                        1. Why this skill is important for the role
                        2. How critical it is (critical, important, nice-to-have)
                        3. Suggested learning path priority (1-5, where 1 is highest)
                        4. Related skills that might help bridge the gap
                        
                        Return a JSON array of objects with this structure:
                        [
                            {{
                                "skill": "skill_name",
                                "importance": "critical|important|nice-to-have",
                                "priority": 1-5,
                                "reason": "why it's needed",
                                "related_skills": ["skill1", "skill2"]
                            }}
                        ]
                        
                        JSON:
                        """
                    )
                    chain = LLMChain(llm=self.llm, prompt=prompt)
                    result = chain.run(
                        resume_skills=str(resume_skills[:20]),
                        missing_skills=str(missing_skills),
                        job_title=job_title,
                        domain=domain or "general",
                        job_description=job_description[:2000]
                    )
                else:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", "You are a skill gap analyzer. Analyze gaps and return only valid JSON array."),
                        ("human", "Job: {job_title} in {domain}\nCandidate skills: {resume_skills}\nMissing: {missing_skills}\nJob desc: {job_description}\n\nReturn JSON array with skill, importance, priority (1-5), reason, related_skills:")
                    ])
                    chain = prompt | self.llm
                    result = chain.invoke({
                        "resume_skills": str(resume_skills[:20]),
                        "missing_skills": str(missing_skills),
                        "job_title": job_title,
                        "domain": domain or "general",
                        "job_description": job_description[:2000]
                    }).content
                
                try:
                    gap_details = json.loads(result.strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse gap analysis as JSON")
            except Exception as e:
                logger.warning(f"LLM gap analysis failed: {str(e)}")
        
        # If no LLM analysis, create basic gap details
        if not gap_details:
            for i, skill in enumerate(missing_skills[:10]):  # Limit to top 10
                gap_details.append({
                    "skill": skill,
                    "importance": "important" if skill in job_skills_dict["required"] else "nice-to-have",
                    "priority": i + 1,
                    "reason": f"Required for {job_title} position",
                    "related_skills": []
                })
        
        # Sort by priority
        gap_details.sort(key=lambda x: x.get("priority", 999))
        
        # Calculate confidence score
        total_skills = len(all_job_skills)
        match_ratio = len(matching_skills) / total_skills if total_skills > 0 else 0
        confidence_score = match_ratio * 100
        
        return {
            "existing_skills": matching_skills,
            "missing_skills": missing_skills,
            "skill_gaps": gap_details,
            "gap_priority": gap_details[:5],  # Top 5 priority gaps
            "confidence_score": round(confidence_score, 2),
            "analysis_notes": f"Found {len(matching_skills)} matching skills out of {total_skills} required. "
                            f"Identified {len(missing_skills)} skill gaps to address."
        }

