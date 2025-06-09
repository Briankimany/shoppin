from pathlib import Path
import sys 

current_dir = Path(__file__).parent
sys.path.append(str(current_dir.absolute()))

from app.main import app

def main():

    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    debug = sys.argv[3] == '1' if len(sys.argv) > 3 else False
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
    print("Done running server. ")
    sys.exit(0)
if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        sys.exit(3)