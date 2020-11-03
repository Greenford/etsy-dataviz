import functools
from flask import Blueprint, session, redirect, url_for, g, current_app
from greendataviz_app import greendataviz as gdv

bp = Blueprint('variation_sales', __name__, url_prefix='/variation_sales')

def file_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.filename is None:
            return redirect(url_for('upload_file'))
        else:
            return view(**kwargs)
    return wrapped_view

@file_required 
@bp.route("/")
def index():
    f = current_app.config["UPLOAD_FOLDER"] + session["filename"]
    listings = gdv.get_listings(f)
    return str(
        [
            f'<a href={url_for("variation_sales.graph_listing", listing=l)}>{l}</a><br>'
            for l in listings
        ]
    )

@file_required 
@bp.route("/<listing>")
def graph_listing(listing):
    graph_name, _ = gdv.variation_sales_linegraph(gdv._sesh["df"], listing, "W")
    return f'<img src="{url_for("static", filename=graph_name)}">'

@bp.before_app_request
def load_filename():
    g.filename = session.get('filename')




