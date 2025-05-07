import markdown
from flask import render_template , Blueprint
from pathlib import Path

curr = Path().cwd() / "app"/"templates"

info_bp = Blueprint("info", __name__,
                     url_prefix="/info")

def load_markdown(file):
    """Reads a Markdown file and converts it to HTML"""

    with open(curr/f"info/static_pages/{file}", "r", encoding="utf-8") as f:
        return markdown.markdown(f.read())

@info_bp.route("/<file>")
def serve_file(file):
    
    file_name ="info/vendor/"+ file+'.html'
    print(file_name)
    return render_template(file_name)

@info_bp.route("/about")
def about():
    content = load_markdown("about.md")
    return render_template("info/about.html", content=content)

@info_bp.route("/terms")
def terms():
    content = load_markdown("terms.md")
    return render_template("info/terms.html", content=content)

@info_bp.route("/privacy")
def privacy():
    content = load_markdown("privacy.md")
    return render_template("info/privacy.html", content=content)
@info_bp.route('/contacts')
def contact():
    content = load_markdown("contact.md")
    return render_template('info/contact.html' , content=content)

@info_bp.route("/shipings")
def shipping():
    return "shipping terms"
@info_bp.route("cookies")
def cookies():
    return "cookies policy"
@info_bp.route("returns")
def returns ():
    return "Returns policy"
@info_bp.route("index")
def index():
    return "index"
@info_bp.route("faq")
def faq():
    return "faq"