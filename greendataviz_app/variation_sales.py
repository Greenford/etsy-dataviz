import functools, tempfile
from flask import Blueprint, session, redirect, url_for, g, current_app, render_template, request
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

#    @file_required 
#    @bp.route("/")
#    def index():
#        f = current_app.config["UPLOAD_FOLDER"] + session["filename"]
#        listings = gdv.get_listings(f)
#        return str(
#            [
#                f'<a href={url_for("variation_sales.graph_listing", listing=l)}>{l}</a><br>'
#                for l in listings
#            ]
#        )

@file_required 
@bp.route("/", methods=['GET', 'POST'])
def graph_listing():
    smooth = 0
    if request.method is 'POST':
        listing = request.form['listing']
        freq = request.form['frequency']
        if request.form['smooth'] is "yes":
            smooth = 1
        _, pt = gdv.variation_sales_linegraph(gdv._sesh["df"], listing, freq)
#    return f'<img src="{url_for("static", filename=graph_name)}">'
        chart_data = pt.to_dict(orient='records')
        chart_data = json.dumps(chart_data, indent=2)
        data = {'chart_data':chart_data}
        pt.T.to_csv(tempfile.gettempdir()+'/d3test.csv')
        return render_template('variation_sales_multiline_graph.ohq.html', smooth=smooth, data=data) 
    else:
        return render_template('variation_sales_multiline_graph.ohq.html', smooth=0, data=None)
@bp.before_app_request
def load_filename():
    g.filename = session.get('filename')

@bp.before_app_request
def load_listings():
    if 'filename' in session:
        g.listings = gdv.get_listings(current_app.config['UPLOAD_FOLDER'] + session.get('filename'))
    else:
        return None

