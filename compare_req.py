import re
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('req_comparison.log'),
        logging.StreamHandler()
    ]
)

def normalize(line):
    try:
        normalized = re.sub(r'[<>=~!].*', '', line.strip()).lower()
        logging.debug(f"Normalized '{line.strip()}' to '{normalized}'")
        return normalized
    except Exception as e:
        logging.error(f"Error normalizing line '{line}': {str(e)}")
        raise

if __name__ == "__main__":
    logging.info("Starting requirements comparison")
    
    try:
        # Verify arguments
        if len(sys.argv) != 3:
            logging.error("Usage: python compare_reqs.py <requirements.txt> <current_reqs.txt>")
            sys.exit(2)
            
        reqs_file, current_file = sys.argv[1], sys.argv[2]
        
        # Verify files exist
        for f in [reqs_file, current_file]:
            if not Path(f).exists():
                logging.error(f"File not found: {f}")
                sys.exit(1)
        
        # Process files
        with open(reqs_file) as f1, open(current_file) as f2:
            reqs = {normalize(line) for line in f1 if line.strip() and not line.startswith('#')}
            installed = {normalize(line) for line in f2}
        
        missing = reqs - installed
        logging.info(f"Found {len(missing)} missing packages:")
        
        # Write output
        with open('reqs_diff.txt', 'w') as f:
            f.write('\n'.join(sorted(missing)))
        
        exit_code = 0 if not missing else 1
        logging.info(f"Comparison complete. Exit code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logging.exception("Fatal error during comparison")
        sys.exit(3)