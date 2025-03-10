"""
PubMed Paper Finder Module API - Reusable functions for finding and filtering papers with 
pharmaceutical/biotech company affiliated authors
"""

from typing import List, Optional, Dict, Any
import logging

from .api import PubMedAPI
from .filters import identify_non_academic_authors
from .models import Paper
from .utils import export_to_csv

logger = logging.getLogger(__name__)

def find_papers_with_company_authors(
    query: str, 
    max_results: int = 100,
    email: str = "your.email@example.com",
    tool: str = "pubmed-paper-finder"
) -> List[Paper]:
    """
    Find papers matching the query and identify those with authors affiliated with
    pharmaceutical or biotech companies.
    
    Args:
        query: PubMed search query (supports full PubMed syntax)
        max_results: Maximum number of results to fetch
        email: Email to include in API requests (NCBI recommendation)
        tool: Tool name to include in API requests (NCBI recommendation)
        
    Returns:
        List of Paper objects with at least one non-academic author
    """
    # Initialize PubMed API client
    api = PubMedAPI(email=email, tool=tool)
    
    # Search for papers
    pmids = api.search(query, max_results=max_results)
    
    if not pmids:
        logger.info("No papers found matching the query")
        return []
    
    # Fetch paper details
    papers = api.fetch_papers(pmids)
    
    # Identify non-academic authors
    papers = identify_non_academic_authors(papers)
    
    # Filter papers with at least one non-academic author
    papers_with_company_authors = [p for p in papers if p.non_academic_authors]
    
    return papers_with_company_authors

def get_papers_as_dict(papers: List[Paper]) -> List[Dict[str, Any]]:
    """
    Convert a list of Paper objects to a list of dictionaries suitable for further processing.
    
    Args:
        papers: List of Paper objects
        
    Returns:
        List of dictionaries with paper information
    """
    result = []
    
    for paper in papers:
        if not paper.non_academic_authors:
            continue
            
        non_academic_authors = [author.name for author in paper.non_academic_authors]
        company_affiliations = paper.company_affiliations
        
        paper_dict = {
            "pubmed_id": paper.pubmed_id,
            "title": paper.title,
            "publication_date": paper.publication_date,
            "non_academic_authors": non_academic_authors,
            "company_affiliations": company_affiliations,
            "corresponding_author_email": paper.corresponding_author_email
        }
        
        result.append(paper_dict)
        
    return result

def find_and_export_papers(
    query: str,
    output_file: Optional[str] = None,
    max_results: int = 100,
    email: str = "your.email@example.com",
    tool: str = "pubmed-paper-finder"
) -> Optional[str]:
    """
    Find papers matching the query, identify those with authors affiliated with
    pharmaceutical or biotech companies, and export the results.
    
    Args:
        query: PubMed search query (supports full PubMed syntax)
        output_file: Path to save the CSV file, if None returns the CSV content as a string
        max_results: Maximum number of results to fetch
        email: Email to include in API requests (NCBI recommendation)
        tool: Tool name to include in API requests (NCBI recommendation)
        
    Returns:
        CSV content as string if output_file is None, else None
    """
    papers = find_papers_with_company_authors(
        query=query,
        max_results=max_results,
        email=email,
        tool=tool
    )
    
    if not papers:
        logger.info("No papers found with authors from pharmaceutical/biotech companies")
        return None if output_file else ""
    
    return export_to_csv(papers, output_file)