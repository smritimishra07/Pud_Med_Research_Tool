from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date


@dataclass
class Author:
    """
    Represents a paper author with their affiliation information.
    """
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    is_corresponding: bool = False
    is_non_academic: bool = False
    company_affiliation: Optional[str] = None


@dataclass
class Paper:
    """
    Represents a research paper with its metadata.
    """
    pubmed_id: str
    title: str
    publication_date: date
    authors: List[Author] = field(default_factory=list)
    
    @property
    def non_academic_authors(self) -> List[Author]:
        """
        Returns a list of authors affiliated with non-academic institutions.
        """
        return [author for author in self.authors if author.is_non_academic]
    
    @property
    def company_affiliations(self) -> List[str]:
        """
        Returns a list of unique company affiliations from all authors.
        """
        return list(set(
            [author.company_affiliation for author in self.non_academic_authors 
             if author.company_affiliation is not None]
        ))
    
    @property
    def corresponding_author_email(self) -> Optional[str]:
        """
        Returns the email of the corresponding author, if available.
        """
        for author in self.authors:
            if author.is_corresponding and author.email:
                return author.email
        return None