# Publishing to TestPyPI

This guide explains how to publish the `pubmed-paper-finder` package to TestPyPI.

## Prerequisites

Make sure you have Poetry installed and you have created an account on TestPyPI:
1. Visit https://test.pypi.org/account/register/ to create an account
2. Install Poetry: https://python-poetry.org/docs/#installation

## Steps to Publish

1. Configure Poetry to use TestPyPI:

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
```

2. Generate a TestPyPI API token:
   - Go to https://test.pypi.org/manage/account/#api-tokens
   - Create a token with scope "Upload packages"

3. Add the token to Poetry:

```bash
poetry config pypi-token.testpypi your-token-here
```

4. Build the package:

```bash
poetry build
```

This will create distribution files in the `dist/` directory.

5. Publish to TestPyPI:

```bash
poetry publish -r testpypi
```

## Automatic CI/CD Setup (Optional)

For a more automated approach, you can set up GitHub Actions to publish to TestPyPI on each release:

1. Create a `.github/workflows/publish.yml` file with the following content:

```yaml
name: Publish to TestPyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install Poetry
      run: curl -sSL https://install.python-poetry.org | python3 -
    - name: Configure Poetry
      run: |
        poetry config repositories.testpypi https://test.pypi.org/legacy/
        poetry config pypi-token.testpypi ${{ secrets.TEST_PYPI_TOKEN }}
    - name: Build and publish
      run: |
        poetry build
        poetry publish -r testpypi
```

2. Add your TestPyPI token as a GitHub repository secret named `TEST_PYPI_TOKEN`.

## Installing the Package from TestPyPI

After publishing, you can install the package from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ pubmed-paper-finder
```

## Using the Published Package

Once installed, you can use the package in your Python code:

```python
from pubmed_paper_finder.module import find_papers_with_company_authors, find_and_export_papers

# Find papers with company authors
papers = find_papers_with_company_authors("cancer immunotherapy")

# Export to CSV
find_and_export_papers("diabetes", output_file="results.csv")
```

You can also use the command-line tool:

```bash
get-papers-list "covid-19 treatment" --file results.csv
```