import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from datetime import date

from pubmed_paper_finder.cli import main, parse_arguments
from pubmed_paper_finder.models import Paper, Author

class TestCLI(unittest.TestCase):
    
    def setUp(self):
        # Create sample data for testing
        self.sample_pmids = ["12345", "67890"]
        self.sample_papers = [
            Paper(
                pubmed_id="12345",
                title="Test Paper 1",
                publication_date=date(2023, 5, 15),
                authors=[
                    Author(
                        name="John Smith",
                        affiliation="Pfizer Inc., New York, NY, USA",
                        email="john.smith@pfizer.com"
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
    
    @patch('pubmed_paper_finder.cli.parse_arguments')
    @patch('pubmed_paper_finder.cli.PubMedAPI')
    @patch('pubmed_paper_finder.cli.identify_non_academic_authors')
    @patch('pubmed_paper_finder.cli.export_to_csv')
    def test_main_success(self, mock_export, mock_identify, mock_api_class, mock_parse_args):
        """Test main function successfully processes papers."""
        # Set up mocks
        mock_args = MagicMock()
        mock_args.query = "test query"
        mock_args.debug = False
        mock_args.file = "test_output.csv"
        mock_args.max_results = 100
        mock_parse_args.return_value = mock_args
        
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        mock_api.search.return_value = self.sample_pmids
        mock_api.fetch_papers.return_value = self.sample_papers
        
        # Set up identify_non_academic_authors to mark the first author as non-academic
        def side_effect(papers):
            for paper in papers:
                if paper.pubmed_id == "12345":
                    paper.authors[0].is_non_academic = True
                    paper.authors[0].company_affiliation = "Pfizer Inc."
            return papers
        
        mock_identify.side_effect = side_effect
        
        # Run the main function
        main()
        
        # Check that functions were called correctly
        mock_parse_args.assert_called_once()
        mock_api.search.assert_called_once_with("test query", max_results=100)
        mock_api.fetch_papers.assert_called_once_with(self.sample_pmids)
        mock_identify.assert_called_once()
        mock_export.assert_called_once()
        
        # Check that the correct papers were passed to export_to_csv
        export_call_args = mock_export.call_args[0]
        self.assertEqual(len(export_call_args[0]), 1)  # Only one paper has non-academic authors
        self.assertEqual(export_call_args[0][0].pubmed_id, "12345")
        self.assertEqual(export_call_args[1], "test_output.csv")
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        """Test argument parsing."""
        # Mock command-line arguments
        mock_parse_args.return_value = MagicMock(
            query="cancer immunotherapy",
            debug=True,
            file="output.csv",
            max_results=50
        )
        
        # Call the function
        args = parse_arguments()
        
        # Check the parsed arguments
        self.assertEqual(args.query, "cancer immunotherapy")
        self.assertTrue(args.debug)
        self.assertEqual(args.file, "output.csv")
        self.assertEqual(args.max_results, 50)