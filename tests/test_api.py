import unittest
from unittest.mock import patch, MagicMock
from datetime import date
import xml.etree.ElementTree as ET
from io import StringIO

from pubmed_paper_finder.api import PubMedAPI
from pubmed_paper_finder.models import Paper, Author

class TestPubMedAPI(unittest.TestCase):
    
    def setUp(self):
        self.api = PubMedAPI(email="test@example.com", tool="test-tool")
    
    @patch('pubmed_paper_finder.api.requests.get')
    def test_search(self, mock_get):
        """Test the search method of PubMedAPI."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "esearchresult": {
                "idlist": ["12345", "67890"]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.api.search("test query")
        
        # Assertions
        self.assertEqual(result, ["12345", "67890"])
        mock_get.assert_called_once()
        
        # Check that the URL and parameters are correct
        call_args = mock_get.call_args[0][0]
        call_kwargs = mock_get.call_args[1]
        self.assertEqual(call_args, self.api.SEARCH_URL)
        self.assertEqual(call_kwargs['params']['term'], "test query")
        self.assertEqual(call_kwargs['params']['email'], "test@example.com")
        
    @patch('pubmed_paper_finder.api.requests.get')
    def test_fetch_papers(self, mock_get):
        """Test the fetch_papers method of PubMedAPI."""
        # Sample XML response
        xml_response = """
        <!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2019//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd">
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation Status="Publisher" Owner="NLM">
                    <PMID Version="1">12345</PMID>
                    <Article PubModel="Print-Electronic">
                        <ArticleTitle>Test Article Title</ArticleTitle>
                        <Journal>
                            <JournalIssue CitedMedium="Internet">
                                <PubDate>
                                    <Year>2023</Year>
                                    <Month>05</Month>
                                    <Day>15</Day>
                                </PubDate>
                            </JournalIssue>
                        </Journal>
                        <AuthorList CompleteYN="Y">
                            <Author ValidYN="Y">
                                <LastName>Smith</LastName>
                                <ForeName>John</ForeName>
                                <Affiliation>Pfizer Inc., New York, NY, USA. john.smith@pfizer.com</Affiliation>
                            </Author>
                            <Author ValidYN="Y">
                                <LastName>Johnson</LastName>
                                <ForeName>Alice</ForeName>
                                <Affiliation>Stanford University, California, USA.</Affiliation>
                            </Author>
                        </AuthorList>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = xml_response
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.api.fetch_papers(["12345"])
        
        # Assertions
        self.assertEqual(len(result), 1)
        paper = result[0]
        self.assertEqual(paper.pubmed_id, "12345")
        self.assertEqual(paper.title, "Test Article Title")
        self.assertEqual(len(paper.authors), 2)
        self.assertEqual(paper.authors[0].name, "John Smith")
        self.assertEqual(paper.authors[0].affiliation, "Pfizer Inc., New York, NY, USA. john.smith@pfizer.com")
        
        # Check email extraction
        self.assertEqual(paper.authors[0].email, "john.smith@pfizer.com")
        
        # Check date parsing
        self.assertEqual(paper.publication_date.year, 2023)
        self.assertEqual(paper.publication_date.month, 5)
        self.assertEqual(paper.publication_date.day, 15)
        
        # Check that the API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        call_kwargs = mock_get.call_args[1]
        self.assertEqual(call_args, self.api.FETCH_URL)
        self.assertEqual(call_kwargs['params']['id'], "12345")