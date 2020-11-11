import functools
from flask import Blueprint, flash, session, redirect, url_for, g, current_app, render_template, request
from datetime import datetime
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
@bp.route("/", methods=['GET', 'POST'])
def graph_listing():
    g.smooth = 1
    if request.method == 'POST':
        listing = request.form['listing']
        freq = request.form['frequency']
        if not request.form.get('smooth', None):
            g.smooth = 0
        _, pt = gdv.variation_sales_linegraph(gdv._sesh["df"], listing, freq)
#        chart_data = pt.to_dict(orient='records')
#        chart_data = json.dumps(chart_data, indent=2)
#        data = {'chart_data':chart_data}
        session['pt'] = datetime.now().strftime("%Y%b%-d:%H%M:%S:%f")+".pt.csv"
        pt.T.to_csv('./greendataviz_app/static/'+session['pt'])
        g.pt = session['pt']
        g.listing = listing
        g.freq = freq
    else:
        g.listing = g.listings[0]
        g.freq = 'W'
    return render_template('variation_sales_multiline_graph.ohq.html')#, smooth=smooth, data=data) 

@bp.before_app_request
def load_g():
    if 'filename' in session:
        g.filename = session.get('filename')
        session['listings'] = tuple(gdv.get_listings(
            current_app.config['UPLOAD_FOLDER'] + session['filename']
        ).flat)
        g.listings = session['listings']
    


