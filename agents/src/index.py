"""
Multi-Agent System for Resume-to-Training Module Generation.
Uses LangGraph to orchestrate specialized agents for resume analysis,
gap identification, and training module generation.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(BaseModel):
    """State shared between agents"""
    resume_data: Dict[str, Any]
    job_description: Dict[str, Any]
    extracted_skills: List[str]
    job_skills: Dict[str, List[str]]
    gap_analysis: Dict[str, Any]
    training_modules: Dict[str, Any]
    error: Optional[str] = None


class ResumeAnalyzerAgent:
    """Agent responsible for analyzing resumes and extracting skills"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.name = "resume_analyzer"
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resume and extract skills"""
        logger.info(f"{self.name}: Analyzing resume...")
        
        resume_data = state.get("resume_data", {})
        resume_text = resume_data.get("raw_text", "")
        
        # Extract skills (simplified - in production, use the ResumeParser service)
        skills = resume_data.get("skills", [])
        
        return {
            "extracted_skills": skills,
            "resume_data": resume_data
        }


class GapAnalyzerAgent:
    """Agent responsible for identifying skill gaps"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.name = "gap_analyzer"
    
    def analyze_gaps(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gaps between resume skills and job requirements"""
        logger.info(f"{self.name}: Analyzing skill gaps...")
        
        extracted_skills = state.get("extracted_skills", [])
        job_skills = state.get("job_skills", {})
        required_skills = job_skills.get("required", [])
        
        # Simple gap analysis
        missing_skills = [skill for skill in required_skills if skill.lower() not in [s.lower() for s in extracted_skills]]
        existing_skills = [skill for skill in required_skills if skill.lower() in [s.lower() for s in extracted_skills]]
        
        gap_analysis = {
            "existing_skills": existing_skills,
            "missing_skills": missing_skills,
            "gap_priority": [
                {"skill": skill, "priority": idx + 1, "importance": "important"}
                for idx, skill in enumerate(missing_skills[:5])
            ]
        }
        
        return {"gap_analysis": gap_analysis}


class TrainingGeneratorAgent:
    """Agent responsible for generating training modules"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.name = "training_generator"
    
    def generate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate training modules based on gap analysis"""
        logger.info(f"{self.name}: Generating training modules...")
        
        gap_analysis = state.get("gap_analysis", {})
        job_description = state.get("job_description", {})
        job_title = job_description.get("title", "Position")
        domain = job_description.get("domain", "general")
        
        priority_gaps = gap_analysis.get("gap_priority", [])
        
        # Generate modules (simplified - in production, use the TrainingGenerator service)
        modules = []
        for idx, gap in enumerate(priority_gaps[:5]):
            modules.append({
                "title": f"Module {idx + 1}: {gap.get('skill', 'Skill')}",
                "description": f"Learn {gap.get('skill')} for {job_title}",
                "learning_objectives": [
                    f"Understand {gap.get('skill')}",
                    f"Apply {gap.get('skill')} in {domain} contexts"
                ],
                "estimated_duration": "1-2 weeks",
                "difficulty": "intermediate"
            })
        
        training_modules = {
            "title": f"Training Program for {job_title}",
            "modules": modules,
            "estimated_duration": f"{len(modules) * 2} weeks"
        }
        
        return {"training_modules": training_modules}


def create_agent_graph():
    """Create the LangGraph workflow"""
    
    # Initialize agents
    resume_analyzer = ResumeAnalyzerAgent()
    gap_analyzer = GapAnalyzerAgent()
    training_generator = TrainingGeneratorAgent()
    
    # Create graph
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("resume_analyzer", resume_analyzer.analyze)
    workflow.add_node("gap_analyzer", gap_analyzer.analyze_gaps)
    workflow.add_node("training_generator", training_generator.generate)
    
    # Define edges
    workflow.set_entry_point("resume_analyzer")
    workflow.add_edge("resume_analyzer", "gap_analyzer")
    workflow.add_edge("gap_analyzer", "training_generator")
    workflow.add_edge("training_generator", END)
    
    # Compile graph
    app = workflow.compile()
    
    return app


def run_agent_pipeline(resume_data: Dict[str, Any], job_description: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete agent pipeline.
    
    Args:
        resume_data: Parsed resume data
        job_description: Job description data
        
    Returns:
        Final state with training modules
    """
    app = create_agent_graph()
    
    initial_state = {
        "resume_data": resume_data,
        "job_description": job_description,
        "job_skills": job_description.get("required_skills", {}),
        "extracted_skills": [],
        "gap_analysis": {},
        "training_modules": {}
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    return final_state


if __name__ == "__main__":
    # Example usage
    example_resume = {
        "raw_text": "John Doe\nSkills: Python, Machine Learning, Data Science",
        "skills": ["python", "machine learning", "data science"]
    }
    
    example_job = {
        "title": "ML Intern at Biotech",
        "domain": "biotech",
        "required_skills": {
            "required": ["python", "machine learning", "causal inference", "health data", "RCTs"]
        }
    }
    
    result = run_agent_pipeline(example_resume, example_job)
    print("Final state:", result)



