import logging
import time
from typing import Dict, List, Optional, Any, Iterator
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

from .models import Paper, Author

logger = logging.getLogger(__name__)

class PubMedAPI:
    """
    Client for interacting with the PubMed API to search and fetch paper details.
    """
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    SEARCH_URL = f"{BASE_URL}/esearch.fcgi"
    FETCH_URL = f"{BASE_URL}/efetch.fcgi"
    SUMMARY_URL = f"{BASE_URL}/esummary.fcgi"
    
    def __init__(self, email: str = "your.email@example.com", tool: str = "pubmed-paper-finder"):
        """
        Initialize the PubMed API client.
        
        Args:
            email: Email to include in API requests (NCBI recommendation)
            tool: Tool name to include in API requests (NCBI recommendation)
        """
        self.email = email
        self.tool = tool
        
    def search(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers matching the query and return PubMed IDs.
        
        Args:
            query: The search query in PubMed syntax
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs matching the query
        """
        logger.debug(f"Searching PubMed with query: {query}")
        
        params: Dict[str, Any] = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "tool": self.tool,
            "email": self.email
        }
        
        response = requests.get(self.SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        pmids = data.get("esearchresult", {}).get("idlist", [])
        logger.debug(f"Found {len(pmids)} papers matching the query")
        
        return pmids
    
    def fetch_papers(self, pmids: List[str]) -> List[Paper]:
        """
        Fetch detailed information for a list of PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs to fetch
            
        Returns:
            List of Paper objects with detailed information
        """
        if not pmids:
            return []
        
        # Process in batches to avoid large requests
        batch_size = 50
        all_papers: List[Paper] = []
        
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i+batch_size]
            
            params: Dict[str, Any] = {
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "xml",
                "tool": self.tool,
                "email": self.email
            }
            
            logger.debug(f"Fetching details for batch of {len(batch_pmids)} papers")
            
            response = requests.get(self.FETCH_URL, params=params)
            response.raise_for_status()
            
            # Parse XML response
            papers = self._parse_fetch_response(response.text)
            all_papers.extend(papers)
            
            # Be nice to the API with a small delay between batches
            if i + batch_size < len(pmids):
                time.sleep(0.5)
        
        return all_papers
    
    def _parse_fetch_response(self, xml_text: str) -> List[Paper]:
        """
        Parse the XML response from efetch to extract paper information.
        
        Args:
            xml_text: XML response text from PubMed efetch
            
        Returns:
            List of Paper objects parsed from the XML
        """
        soup = BeautifulSoup(xml_text, "xml")
        papers: List[Paper] = []
        
        for article_elem in soup.find_all("PubmedArticle"):
            try:
                pmid = article_elem.find("PMID").text
                
                # Get title
                title_elem = article_elem.find("ArticleTitle")
                title = title_elem.text if title_elem else "Unknown Title"
                
                # Get publication date
                pub_date = self._parse_publication_date(article_elem)
                
                # Create paper object
                paper = Paper(
                    pubmed_id=pmid,
                    title=title,
                    publication_date=pub_date
                )
                
                # Parse authors
                self._parse_authors(article_elem, paper)
                
                papers.append(paper)
            except Exception as e:
                logger.error(f"Error parsing article: {e}")
                continue
        
        return papers
    
    def _parse_publication_date(self, article_elem) -> datetime.date:
        """
        Extract publication date from article element.
        
        Args:
            article_elem: BeautifulSoup element for the article
            
        Returns:
            Date object representing the publication date
        """
        # Try to find PubDate in PubMedPubDate with PubStatus="pubmed"
        pub_date_elem = article_elem.find("PubMedPubDate", {"PubStatus": "pubmed"})
        
        if not pub_date_elem:
            # Fallback to ArticleDate or PubDate in Journal
            pub_date_elem = article_elem.find("ArticleDate") or article_elem.find("PubDate")
        
        year = pub_date_elem.find("Year")
        month = pub_date_elem.find("Month")
        day = pub_date_elem.find("Day")
        
        year_val = int(year.text) if year else 1900
        month_val = int(month.text) if month else 1
        day_val = int(day.text) if day else 1
        
        return datetime(year_val, month_val, day_val).date()
    
    def _parse_authors(self, article_elem, paper: Paper) -> None:
        """
        Extract author information from article element and add to paper.
        
        Args:
            article_elem: BeautifulSoup element for the article
            paper: Paper object to update with author information
        """
        author_list = article_elem.find("AuthorList")
        if not author_list:
            return
        
        for author_elem in author_list.find_all("Author"):
            try:
                # Get author name
                last_name = author_elem.find("LastName")
                fore_name = author_elem.find("ForeName")
                
                if last_name and fore_name:
                    name = f"{fore_name.text} {last_name.text}"
                elif last_name:
                    name = last_name.text
                else:
                    collective_name = author_elem.find("CollectiveName")
                    if collective_name:
                        name = collective_name.text
                    else:
                        continue  # Skip author with no name
                
                # Check if corresponding author
                is_corresponding = False
                author_id_list = author_elem.find_all("Identifier")
                for id_elem in author_id_list:
                    if id_elem.get("Source") == "CORRESP":
                        is_corresponding = True
                
                # Get affiliation
                affiliation_text = None
                affiliation = author_elem.find("Affiliation")
                if affiliation:
                    affiliation_text = affiliation.text
                
                # Get email (often embedded in affiliation text)
                email = None
                if affiliation_text:
                    # Simple email extraction - could be improved
                    import re
                    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', affiliation_text)
                    if email_match:
                        email = email_match.group(0)
                
                author = Author(
                    name=name,
                    affiliation=affiliation_text,
                    email=email,
                    is_corresponding=is_corresponding
                )
                
                paper.authors.append(author)
                
            except Exception as e:
                logger.error(f"Error parsing author: {e}")
                continue