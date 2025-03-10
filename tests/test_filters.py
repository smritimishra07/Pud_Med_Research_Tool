import unittest
from datetime import date

from pubmed_paper_finder.models import Author, Paper
from pubmed_paper_finder.filters import (
    is_non_academic_author,
    extract_company_name,
    identify_non_academic_authors
)

class TestFilters(unittest.TestCase):
    
    def test_is_non_academic_author_with_pharma(self):
        """Test identification of pharmaceutical company authors."""
        author = Author(
            name="John Smith",
            affiliation="Pfizer Inc., New York, NY, USA",
            email="john.smith@pfizer.com"
        )
        self.assertTrue(is_non_academic_author(author))
        
    def test_is_non_academic_author_with_biotech(self):
        """Test identification of biotech company authors."""
        author = Author(
            name="Jane Doe",
            affiliation="Genentech Biotech Research, South San Francisco, CA, USA",
            email="doe.j@gene.com"
        )
        self.assertTrue(is_non_academic_author(author))
        
    def test_is_non_academic_author_with_academic(self):
        """Test correct identification of academic authors."""
        author = Author(
            name="Alice Johnson",
            affiliation="Department of Biology, Stanford University, CA, USA",
            email="alice@stanford.edu"
        )
        self.assertFalse(is_non_academic_author(author))
        
    def test_is_non_academic_author_with_government(self):
        """Test correct identification of government institution authors."""
        author = Author(
            name="Bob Williams",
            affiliation="National Institutes of Health, Bethesda, MD, USA",
            email="bob.williams@nih.gov"
        )
        self.assertFalse(is_non_academic_author(author))