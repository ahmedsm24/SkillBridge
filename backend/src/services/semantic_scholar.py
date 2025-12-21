"""
Semantic Scholar API integration for fetching research papers and case studies.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
import httpx
import os

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarService:
    """Service for fetching research papers from Semantic Scholar API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Semantic Scholar service.
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.headers = {}
        if self.api_key:
            self.headers["x-api-key"] = self.api_key
    
    async def search_papers(
        self,
        query: str,
        limit: int = 5,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for papers by query.
        
        Args:
            query: Search query (skill, topic, or keyword)
            limit: Maximum number of papers to return
            fields: Fields to include in response
            
        Returns:
            List of paper dictionaries
        """
        if fields is None:
            fields = [
                "paperId",
                "title",
                "abstract",
                "year",
                "citationCount",
                "url",
                "authors",
                "venue",
                "openAccessPdf"
            ]
        
        params = {
            "query": query,
            "limit": limit,
            "fields": ",".join(fields)
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{SEMANTIC_SCHOLAR_API_URL}/paper/search",
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    papers = data.get("data", [])
                    return self._format_papers(papers)
                elif response.status_code == 429:
                    logger.warning("Semantic Scholar rate limit reached")
                    return []
                else:
                    logger.error(f"Semantic Scholar API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching papers: {str(e)}")
            return []
    
    async def get_papers_for_skills(
        self,
        skills: List[str],
        domain: str = "",
        papers_per_skill: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get relevant papers for a list of skills.
        
        Args:
            skills: List of skills to find papers for
            domain: Industry domain to contextualize search
            papers_per_skill: Number of papers per skill
            
        Returns:
            Dictionary mapping skills to their relevant papers
        """
        results = {}
        
        for skill in skills[:5]:  # Limit to 5 skills to avoid rate limits
            query = f"{skill} {domain}".strip() if domain else skill
            papers = await self.search_papers(query, limit=papers_per_skill)
            results[skill] = papers
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return results
    
    async def get_case_studies(
        self,
        topic: str,
        domain: str = "",
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get case study papers for a topic.
        
        Args:
            topic: Topic to search for
            domain: Industry domain
            limit: Maximum number of case studies
            
        Returns:
            List of case study papers
        """
        # Search for case studies, surveys, and review papers
        queries = [
            f"{topic} case study {domain}",
            f"{topic} industry application {domain}",
            f"{topic} practical implementation"
        ]
        
        all_papers = []
        seen_ids = set()
        
        for query in queries:
            papers = await self.search_papers(query.strip(), limit=2)
            for paper in papers:
                if paper.get("id") not in seen_ids:
                    seen_ids.add(paper.get("id"))
                    all_papers.append(paper)
            await asyncio.sleep(0.3)
        
        return all_papers[:limit]
    
    async def get_learning_resources(
        self,
        skill: str,
        level: str = "intermediate"
    ) -> List[Dict[str, Any]]:
        """
        Get learning-focused papers (tutorials, surveys, introductions).
        
        Args:
            skill: Skill to find resources for
            level: Difficulty level (beginner, intermediate, advanced)
            
        Returns:
            List of learning resource papers
        """
        level_queries = {
            "beginner": ["introduction", "tutorial", "beginner guide"],
            "intermediate": ["survey", "overview", "practical"],
            "advanced": ["advanced", "state-of-the-art", "deep dive"]
        }
        
        query_terms = level_queries.get(level, level_queries["intermediate"])
        all_papers = []
        
        for term in query_terms[:2]:
            query = f"{skill} {term}"
            papers = await self.search_papers(query, limit=2)
            all_papers.extend(papers)
            await asyncio.sleep(0.3)
        
        # Remove duplicates and return
        seen = set()
        unique_papers = []
        for paper in all_papers:
            if paper.get("id") not in seen:
                seen.add(paper.get("id"))
                unique_papers.append(paper)
        
        return unique_papers[:5]
    
    def _format_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format papers for consistent output"""
        formatted = []
        
        for paper in papers:
            if not paper:
                continue
                
            # Get authors
            authors = paper.get("authors", [])
            author_names = [a.get("name", "") for a in authors[:3]]
            if len(authors) > 3:
                author_names.append("et al.")
            
            # Get PDF URL if available
            pdf_info = paper.get("openAccessPdf")
            pdf_url = pdf_info.get("url") if pdf_info else None
            
            formatted.append({
                "id": paper.get("paperId"),
                "title": paper.get("title", "Untitled"),
                "abstract": paper.get("abstract", "")[:500] if paper.get("abstract") else None,
                "authors": ", ".join(author_names) if author_names else "Unknown",
                "year": paper.get("year"),
                "citations": paper.get("citationCount", 0),
                "venue": paper.get("venue", ""),
                "url": paper.get("url", f"https://www.semanticscholar.org/paper/{paper.get('paperId')}"),
                "pdf_url": pdf_url,
                "type": "paper"
            })
        
        return formatted


# Singleton instance
semantic_scholar = SemanticScholarService()

