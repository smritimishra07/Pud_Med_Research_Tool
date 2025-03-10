import argparse
import logging
import sys
from typing import List, Optional

from .module import find_and_export_papers
from .utils import setup_logging

logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed and identify those with authors from pharma/biotech companies"
    )
    
    parser.add_argument(
        "query",
        help="PubMed search query (supports full PubMed syntax)"
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Path to save the results (CSV format). If not provided, print to console."
    )
    
    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch (default: 100)"
    )
    
    return parser.parse_args()

def main() -> None:
    """
    Main entry point for the command-line interface.
    """
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.debug)
    
    logger.info(f"Searching for papers with query: {args.query}")
    
    try:
        # Use the module API to find and export papers
        csv_output = find_and_export_papers(
            query=args.query,
            output_file=args.file,
            max_results=args.max_results
        )
        
        if csv_output:
            print(csv_output)
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()