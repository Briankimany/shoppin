
from app.main import app

if __name__ == "__main__":
    app.run("0.0.0.0",debug=True ,
            # ssl_context = 'adhoc',
              port = 5500)
