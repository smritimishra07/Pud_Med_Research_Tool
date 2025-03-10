# PubMed Paper Finder

A Python command-line tool and module to fetch research papers from PubMed based on user-specified queries and identify papers with authors affiliated with pharmaceutical or biotech companies.

## Features

- Search PubMed using full PubMed query syntax
- Identify authors affiliated with pharmaceutical or biotech companies using LLM-powered analysis
- Export results to CSV with detailed information
- Command-line interface with customizable options
- Reusable Python module API
- Available on TestPyPI

## Installation

### From TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ pubmed-paper-finder
```

### From Source

#### Prerequisites

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management

#### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pubmed-paper-finder.git
   cd pubmed-paper-finder
   ```

2. Install dependencies:
   ```
   poetry install
   ```

This will set up a virtual environment and install all required dependencies.

## Usage

### Command-line Interface

#### Using Poetry

```bash
get-papers-list "your PubMed query"
```

#### Direct Python Module Execution

If you encounter issues with Poetry or the installed script, you can run the module directly:

```bash
python -m pubmed_paper_finder.cli "your PubMed query"
```

For example, to search for COVID-19 papers:
```bash
python -m pubmed_paper_finder.cli "COVID-19"
```

To save results to a CSV file:
```bash
python -m pubmed_paper_finder.cli "COVID-19" --file results.csv
```

#### Command-line Options

- `-h, --help`: Display usage instructions
- `-d, --debug`: Print debug information during execution
- `-f, --file FILE`: Specify the filename to save the results (CSV format)
- `-m, --max-results MAX_RESULTS`: Maximum number of results to fetch (default: 100)

#### Examples

Search for diabetes research papers and print results to console:
```bash
get-papers-list "diabetes"
```

Search for cancer immunotherapy papers and save results to a file:
```bash
get-papers-list "cancer immunotherapy" --file results.csv
```

Debug mode with limited results:
```bash
get-papers-list "COVID-19 treatment" --debug --max-results 20
```

### Using as a Python Module

```python
from pubmed_paper_finder.module import find_papers_with_company_authors, find_and_export_papers

# Find papers with company-affiliated authors
papers = find_papers_with_company_authors("cancer immunotherapy", max_results=50)

# Process papers
for paper in papers:
    print(f"Paper ID: {paper.pubmed_id}")
    print(f"Title: {paper.title}")
    
    for author in paper.non_academic_authors:
        print(f"Non-academic author: {author.name}")
        print(f"Company: {author.company_affiliation}")

# Export to CSV directly
find_and_export_papers("diabetes", output_file="results.csv")
```

## Output Format

The CSV output includes the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Title of the paper
- **Publication Date**: Date the paper was published
- **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions
- **Company Affiliation(s)**: Names of pharmaceutical/biotech companies
- **Corresponding Author Email**: Email address of the corresponding author

## Code Organization

The project is organized as follows:

- `pubmed_paper_finder/`: Main package directory
  - `__init__.py`: Package initialization
  - `api.py`: PubMed API client implementation
  - `cli.py`: Command-line interface implementation
  - `filters.py`: Logic for identifying non-academic authors
  - `models.py`: Data models for papers and authors
  - `module.py`: Reusable module API functions
  - `utils.py`: Utility functions for logging, CSV export, etc.
- `tests/`: Unit tests
- `pyproject.toml`: Poetry configuration file
- `README.md`: This documentation

## How It Works

1. The tool accepts a search query from the user
2. It searches PubMed using the NCBI E-utilities API
3. For each paper found, it fetches detailed information including authors and affiliations
4. It analyzes author affiliations to identify those from pharmaceutical or biotech companies using a combination of rule-based heuristics and LLM-powered analysis
5. It exports the filtered results to CSV

## Heuristics for Identifying Non-Academic Authors

The tool uses a hybrid approach to identify non-academic authors:

1. **Rule-based Affiliation text analysis**:
   - Checks for the presence of company-related terms (Inc, Corp, GmbH, etc.)
   - Looks for pharmaceutical/biotech specific keywords (Pharma, Biotech, Therapeutics, etc.)
   - Excludes affiliations with academic institution keywords (University, College, etc.)
   - Excludes government and public health institution keywords

2. **Email domain analysis**:
   - Academic domains typically end with .edu or .ac.xx
   - Company domains typically end with .com, .co, etc.

3. **Company name extraction**:
   - Attempts to extract the specific company name from the affiliation text
   - Uses patterns and keywords to identify the most likely company name

4. **LLM-powered analysis**:
   - For complex or ambiguous affiliations, the tool employs a large language model at runtime
   - The LLM analyzes the context of the affiliation description to determine if it represents a commercial entity
   - Particularly useful for international affiliations or those with non-standard naming conventions
   - Helps extract the precise company name from complex affiliation strings

## Tools Used

- [Poetry](https://python-poetry.org/): Dependency management and packaging
- [Requests](https://docs.python-requests.org/): HTTP client for API calls
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/): XML parsing
- [Pandas](https://pandas.pydata.org/): Data manipulation and CSV export
- [argparse](https://docs.python.org/3/library/argparse.html): Command-line argument parsing
- [logging](https://docs.python.org/3/library/logging.html): Logging framework
- [re](https://docs.python.org/3/library/re.html): Regular expressions for text analysis
- [OpenAI API](https://openai.com/blog/openai-api): Used at runtime for advanced affiliation analysis
- [ChatGPT](https://openai.com/): Used for general code structure and best practices recommendations during development
- [GitHub Copilot](https://github.com/features/copilot): Used for code completion and suggestions during development
- [PyTest](https://docs.pytest.org/): Testing framework

## Development

### Running Tests

#### Using Poetry
```bash
poetry run pytest
```

#### Direct Python Module Execution
If Poetry is not available or properly configured, tests can be run directly with:
```bash
python -m pytest
```

To run specific test files:
```bash
python -m pytest tests/test_api.py
```

### Type Checking

```bash
poetry run mypy pubmed_paper_finder
```

### Code Formatting

```bash
poetry run black pubmed_paper_finder
poetry run isort pubmed_paper_finder
```

## Publishing to TestPyPI

The package is available on TestPyPI. To publish updates:

1. Configure Poetry to use TestPyPI:
```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
```

2. Build and publish:
```bash
poetry build
poetry publish -r testpypi
```

See `Publishing to TestPyPI.md` for detailed instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.