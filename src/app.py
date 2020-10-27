from flask import Flask, url_for
import greendataviz as gdv

app = Flask(__name__)
_sesh = dict()

@app.route('/')
def entrance():
    return f'<a href={url_for("variation_sales")}>Variation Sales</a>'

@app.route('/variation-sales')
def variation_sales():
    f = '../../data/EtsySoldOrderItems2020.csv'
    listings = gdv.get_listings(f)
    return str([f'<a href={url_for("variation_sales_graph", listing=l)}>{l}</a><br>' for l in listings])
    
@app.route('/variation-sales-graph/<listing>')
def variation_sales_graph(listing):
    graph_name, _ = gdv.variation_sales_linegraph(gdv._sesh['df'], listing, 'W')
    return f'<img src="{url_for("static", filename=graph_name)}">'

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))

