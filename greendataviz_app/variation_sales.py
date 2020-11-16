import functools
from flask import (
    Blueprint,
    flash,
    session,
    redirect,
    url_for,
    g,
    current_app,
    render_template,
    request,
)
from datetime import datetime
from greendataviz_app import greendataviz as gdv

bp = Blueprint("variation_sales", __name__, url_prefix="/variation_sales")


def file_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.filename is None:
            return redirect(url_for("upload_file"))
        else:
            return view(**kwargs)

    return wrapped_view


@file_required
@bp.route("/", methods=["GET", "POST"])
def graph_listing():
    g.smooth = 1
    df = gdv.get_variation_sales_data(
        current_app.config["UPLOAD_FOLDER"] + session["filename"], gdv.printerror_clean
    )
    if "listings" not in session:
        session["listings"] = tuple(l for l in df["Item Name"].unique())
    if request.method == "POST":
        listing = request.form["listing"]
        freq = request.form["frequency"]
        y = request.form['y']
        if not request.form.get("smooth", None):
            g.smooth = 0
        pt = gdv.variation_sales_linegraph(df, listing, freq, y_axis_label=y)
        session["pt"] = datetime.now().strftime("%Y%b%-d:%H%M:%S:%f") + ".pt.csv"
        pt.T.to_csv("./greendataviz_app/static/" + session["pt"])
        g.pt = session["pt"]
        g.listing = listing
        g.freq = freq
        g.y = y
    else:
        g.freq = "W"
        g.y = "Sales"
    g.listings = session["listings"]
    return render_template(
        "variation_sales_multiline_graph.ohq.html"
    )

@bp.before_app_request
def load_filename():
    if "filename" in session:
        g.filename = session["filename"]
