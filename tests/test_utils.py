import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import logging
from datetime import date

import pandas as pd

from pubmed_paper_finder.models import Paper, Author
from pubmed_paper_finder.utils import setup_logging, export_to_csv

class TestUtils(unittest.TestCase):
    
    def setUp(self):
        # Create sample papers for testing
        self.sample_papers = [
            Paper(
                pubmed_id="12345",
                title="Test Paper 1",
                publication_date=date(2023, 5, 15),
                authors=[
                    Author(
                        name="John Smith",
                        affiliation="Pfizer Inc., New York, NY, USA",
                        email="john.smith@pfizer.com",
                        is_non_academic=True,
                        company_affiliation="Pfizer Inc."
                    ),
                    Author(
                        name="Alice Johnson",
                        affiliation="Stanford University, CA, USA",
                        email="alice@stanford.edu",
                        is_corresponding=True
                    )
                ]
            ),
            Paper(
                pubmed_id="67890",
                title="Test Paper 2",
                publication_date=date(2023, 6, 20),
                authors=[
                    Author(
                        name="Jane Doe",
                        affiliation="Harvard University, MA, USA",
                        email="jane@harvard.edu"
                    )
                ]
            )
        ]
    
    @patch('pubmed_paper_finder.utils.logging.basicConfig')
    def test_setup_logging_debug(self, mock_basicConfig):
        """Test setup_logging with debug=True."""
        setup_logging(debug=True)
        
        mock_basicConfig.assert_called_once()
        call_kwargs = mock_basicConfig.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.DEBUG)
        
    @patch('pubmed_paper_finder.utils.logging.basicConfig')
    def test_setup_logging_info(self, mock_basicConfig):
        """Test setup_logging with debug=False."""
        setup_logging(debug=False)
        
        mock_basicConfig.assert_called_once()
        call_kwargs = mock_basicConfig.call_args[1]
        self.assertEqual(call_kwargs['level'], logging.INFO)
    
    @patch('pubmed_paper_finder.utils.pd.DataFrame.to_csv')
    def test_export_to_csv_with_file(self, mock_to_csv):
        """Test export_to_csv with a file path."""
        result = export_to_csv(self.sample_papers, "test_output.csv")
        
        # Check that to_csv was called with the right parameters
        mock_to_csv.assert_called_once()
        call_args = mock_to_csv.call_args[0][0]
        self.assertEqual(call_args, "test_output.csv")
        
        # Result should be None when saving to file
        self.assertIsNone(result)
    
    def test_export_to_csv_without_file(self):
        """Test export_to_csv without a file path (return as string)."""
        result = export_to_csv(self.sample_papers)
        
        # Result should be a string
        self.assertIsInstance(result, str)
        
        # Should contain paper with non-academic author
        self.assertIn("12345", result)
        self.assertIn("Test Paper 1", result)
        self.assertIn("John Smith", result)
        self.assertIn("Pfizer Inc.", result)
        
        # Should not contain paper without non-academic authors
        self.assertNotIn("67890", result)
        self.assertNotIn("Test Paper 2", result)