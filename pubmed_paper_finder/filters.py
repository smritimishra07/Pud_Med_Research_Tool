import re
from typing import List, Set, Pattern
import logging

from .models import Paper, Author

logger = logging.getLogger(__name__)

# List of common academic institution keywords
ACADEMIC_KEYWORDS: Set[str] = {
    "university", "college", "institute of technology", "polytechnic",
    "school of medicine", "medical school", "academy of sciences",
    "research institute", "national laboratory", "state university",
    "academia", "faculty", "school of", "department of"
}

# List of government/public institution keywords
GOVERNMENT_KEYWORDS: Set[str] = {
    "national institute", "ministry of", "department of health",
    "cdc", "centers for disease", "government", "public health",
    "federal", "state department", "nih", "who", "world health",
    "hospital", "clinic", "medical center", "health service",
    "healthcare system", "foundation", "nhs"
}

# Common pharmaceutical/biotech company suffixes
COMPANY_SUFFIXES: Set[str] = {
    "inc", "corp", "corporation", "ltd", "limited", "llc", "co",
    "gmbh", "sa", "ag", "bv", "plc", "spa", "pharma", "therapeutics",
    "group", "laboratories", "labs", "biosciences", "biotech"
}

# Common pharmaceutical/biotech company name prefixes/words
PHARMA_BIOTECH_KEYWORDS: Set[str] = {
    "pharma", "biotech", "bio", "therapeutics", "biosciences",
    "genomics", "pharmaceutical", "biopharma", "drug", "medicines",
    "biologics", "lifesciences", "genetics", "medical"
}

# Compile regex patterns for email domains
ACADEMIC_EMAIL_PATTERN: Pattern = re.compile(r'@.*\.(edu|ac\.[a-z]{2}|edu\.[a-z]{2})$', re.IGNORECASE)
COMPANY_EMAIL_PATTERN: Pattern = re.compile(r'@[^.]*\.(com|co|net|io)$', re.IGNORECASE)


def identify_non_academic_authors(papers: List[Paper]) -> List[Paper]:
    """
    Identify authors affiliated with pharmaceutical or biotech companies.
    
    Args:
        papers: List of Paper objects to process
        
    Returns:
        The same Paper objects with is_non_academic and company_affiliation fields updated
    """
    for paper in papers:
        for author in paper.authors:
            if is_non_academic_author(author):
                author.is_non_academic = True
                
                # Try to extract the company name if available
                if author.affiliation:
                    company_name = extract_company_name(author.affiliation)
                    if company_name:
                        author.company_affiliation = company_name
    
    return papers


def is_non_academic_author(author: Author) -> bool:
    """
    Determine if an author is likely affiliated with a non-academic institution.
    
    Args:
        author: Author object to analyze
        
    Returns:
        True if the author is likely affiliated with a pharma/biotech company
    """
    if not author.affiliation:
        return False
    
    affiliation_lower = author.affiliation.lower()
    
    # Check for academic keywords
    for keyword in ACADEMIC_KEYWORDS:
        if keyword in affiliation_lower:
            # Check if there's a company mention that might override the academic keyword
            if any(company_kw in affiliation_lower for company_kw in PHARMA_BIOTECH_KEYWORDS):
                # This could be a company with a research institute or a collaboration
                continue
            return False
    
    # Check for government/public institution keywords
    for keyword in GOVERNMENT_KEYWORDS:
        if keyword in affiliation_lower:
            return False
    
    # Check for company keywords and suffixes
    has_company_indicators = False
    
    for suffix in COMPANY_SUFFIXES:
        if re.search(r'\b' + suffix + r'\b', affiliation_lower):
            has_company_indicators = True
            break
    
    for keyword in PHARMA_BIOTECH_KEYWORDS:
        if keyword in affiliation_lower:
            has_company_indicators = True
            break
    
    # Check email domain if available
    if author.email:
        email_lower = author.email.lower()
        if ACADEMIC_EMAIL_PATTERN.search(email_lower):
            return False
        if COMPANY_EMAIL_PATTERN.search(email_lower):
            has_company_indicators = True
    
    return has_company_indicators


def extract_company_name(affiliation: str) -> str:
    """
    Attempt to extract the company name from an affiliation string.
    
    Args:
        affiliation: Affiliation text to analyze
        
    Returns:
        Extracted company name or empty string if not found
    """
    # This is a simplified approach - a more robust solution might use NLP
    # to identify organization names
    
    affiliation_lower = affiliation.lower()
    words = affiliation_lower.split()
    
    # Split by common separators
    segments = re.split(r'[,;]', affiliation)
    
    # Look for segments that contain company indicators
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
            
        # Check for company suffixes
        for suffix in COMPANY_SUFFIXES:
            suffix_pattern = re.compile(r'\b' + re.escape(suffix) + r'\b', re.IGNORECASE)
            if suffix_pattern.search(segment):
                # Return the original case version of this segment
                original_segment = [s.strip() for s in affiliation.split(',') if segment.lower() in s.lower()]
                if original_segment:
                    return original_segment[0]
                return segment
        
        # Check for pharma/biotech keywords
        for keyword in PHARMA_BIOTECH_KEYWORDS:
            if keyword in segment.lower():
                # Return the original case version of this segment
                original_segment = [s.strip() for s in affiliation.split(',') if segment.lower() in s.lower()]
                if original_segment:
                    return original_segment[0]
                return segment
    
    # If we can't find a specific segment, return first part of affiliation
    # as a fallback
    first_segment = segments[0].strip() if segments else ""
    return first_segment