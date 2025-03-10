import csv
import logging
import sys
from typing import List, Optional, TextIO
import pandas as pd

from .models import Paper

logger = logging.getLogger(__name__)

def setup_logging(debug: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        debug: If True, set log level to DEBUG
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )

def export_to_csv(papers: List[Paper], file_path: Optional[str] = None) -> Optional[str]:
    """
    Export papers to CSV format.
    
    Args:
        papers: List of Paper objects to export
        file_path: Path to save the CSV file, if None print to stdout
        
    Returns:
        CSV content as string if file_path is None, else None
    """
    # Create a list of dictionaries for DataFrame
    data = []
    
    for paper in papers:
        # Only include papers with at least one non-academic author
        if not paper.non_academic_authors:
            continue
            
        non_academic_authors = [author.name for author in paper.non_academic_authors]
        company_affiliations = paper.company_affiliations
        
        row = {
            "PubmedID": paper.pubmed_id,
            "Title": paper.title,
            "Publication Date": paper.publication_date,
            "Non-academic Author(s)": "; ".join(non_academic_authors),
            "Company Affiliation(s)": "; ".join(company_affiliations),
            "Corresponding Author Email": paper.corresponding_author_email or ""
        }
        
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to CSV
    if file_path:
        df.to_csv(file_path, index=False)
        logger.info(f"Results saved to {file_path}")
        return None
    else:
        return df.to_csv(index=False)