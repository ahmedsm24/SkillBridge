"""
Resume parsing service that extracts information from resume documents.
Supports PDF and text file formats.
"""
import re
import logging
from typing import Dict, List, Optional, Any
from io import BytesIO
import pdfplumber
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


class ResumeParser:
    """Service for parsing and extracting information from resumes"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the resume parser.
        
        Args:
            openai_api_key: OpenAI API key for LLM-based extraction
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
    
    def parse_pdf(self, file_content: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_content: PDF file content as bytes
            
        Returns:
            Extracted text from PDF
        """
        try:
            text = ""
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise ValueError(f"Failed to parse PDF: {str(e)}")
    
    def parse_text(self, file_content: bytes) -> str:
        """
        Extract text from text file.
        
        Args:
            file_content: Text file content as bytes
            
        Returns:
            Extracted text
        """
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            return file_content.decode('latin-1')
    
    def extract_skills(self, resume_text: str) -> List[str]:
        """
        Extract skills from resume text using pattern matching and LLM.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            List of extracted skills
        """
        skills = []
        
        # Pattern-based extraction
        skill_patterns = [
            r'(?i)(?:skills?|technical skills?|technologies?|tools?|proficiencies?)[:]\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)(?:proficient in|experienced with|familiar with|expert in)[:]\s*(.+?)(?:\.|,|\n)',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, resume_text, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Split by commas, semicolons, or newlines
                extracted = re.split(r'[,;]\s*|\n', match)
                skills.extend([s.strip() for s in extracted if s.strip()])
        
        # Use LLM for better extraction if available
        if self.llm:
            try:
                if self.use_legacy:
                    prompt = PromptTemplate(
                        input_variables=["resume_text"],
                        template="""
                        Extract all technical skills, programming languages, frameworks, tools, and domain-specific knowledge from the following resume text.
                        Return only a JSON array of skill names, without any additional text.
                        
                        Resume text:
                        {resume_text}
                        
                        JSON array:
                        """
                    )
                    chain = LLMChain(llm=self.llm, prompt=prompt)
                    result = chain.run(resume_text=resume_text[:4000])  # Limit text length
                else:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", "You are a resume parser. Extract all technical skills, programming languages, frameworks, tools, and domain-specific knowledge. Return only a JSON array of skill names."),
                        ("human", "Resume text:\n{resume_text}\n\nJSON array:")
                    ])
                    chain = prompt | self.llm
                    result = chain.invoke({"resume_text": resume_text[:4000]}).content
                
                # Try to parse JSON from result
                try:
                    llm_skills = json.loads(result.strip())
                    if isinstance(llm_skills, list):
                        skills.extend(llm_skills)
                except json.JSONDecodeError:
                    # If not JSON, try to extract from text
                    llm_skills = re.findall(r'"([^"]+)"', result)
                    skills.extend(llm_skills)
            except Exception as e:
                logger.warning(f"LLM skill extraction failed: {str(e)}")
        
        # Clean and deduplicate
        skills = [s.lower().strip() for s in skills if len(s) > 1]
        skills = list(set(skills))
        
        return skills
    
    def extract_experience(self, resume_text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience from resume text.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            List of experience entries with company, role, duration, etc.
        """
        experience = []
        
        # Pattern-based extraction
        exp_pattern = r'(?i)(?:experience|work history|employment)[:]\s*(.+?)(?:\n\n\n|\n[A-Z]{3,}|$)'
        matches = re.findall(exp_pattern, resume_text, re.MULTILINE | re.DOTALL)
        
        for match in matches[:5]:  # Limit to 5 most recent
            # Try to extract company, role, dates
            lines = match.split('\n')
            entry = {
                "role": "",
                "company": "",
                "duration": "",
                "description": ""
            }
            
            for line in lines[:3]:
                line = line.strip()
                if not line:
                    continue
                # Check for date patterns
                if re.search(r'\d{4}|\d{1,2}/\d{4}', line):
                    entry["duration"] = line
                elif not entry["role"]:
                    entry["role"] = line
                elif not entry["company"]:
                    entry["company"] = line
            
            entry["description"] = '\n'.join(lines[3:])
            if entry["role"] or entry["company"]:
                experience.append(entry)
        
        return experience
    
    def extract_education(self, resume_text: str) -> List[Dict[str, Any]]:
        """
        Extract education history from resume text.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            List of education entries
        """
        education = []
        
        # Pattern-based extraction
        edu_pattern = r'(?i)(?:education|academic background|qualifications)[:]\s*(.+?)(?:\n\n\n|\n[A-Z]{3,}|$)'
        matches = re.findall(edu_pattern, resume_text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            lines = match.split('\n')
            entry = {
                "degree": "",
                "institution": "",
                "year": "",
                "field": ""
            }
            
            for line in lines[:3]:
                line = line.strip()
                if not line:
                    continue
                if re.search(r'\d{4}', line):
                    entry["year"] = re.search(r'\d{4}', line).group()
                elif not entry["degree"]:
                    entry["degree"] = line
                elif not entry["institution"]:
                    entry["institution"] = line
            
            if entry["degree"] or entry["institution"]:
                education.append(entry)
        
        return education
    
    def parse_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Main method to parse a resume file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with parsed resume data
        """
        # Determine file type and extract text
        if filename.lower().endswith('.pdf'):
            raw_text = self.parse_pdf(file_content)
        elif filename.lower().endswith(('.txt', '.docx')):
            raw_text = self.parse_text(file_content)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
        
        # Extract structured information
        skills = self.extract_skills(raw_text)
        experience = self.extract_experience(raw_text)
        education = self.extract_education(raw_text)
        
        return {
            "filename": filename,
            "raw_text": raw_text,
            "skills": skills,
            "experience": experience,
            "education": education,
            "parsed_data": {
                "skills": skills,
                "experience": experience,
                "education": education
            }
        }

