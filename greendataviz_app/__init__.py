import os
from flask import Flask, url_for
from greendataviz_app import greendataviz as gdv

 def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE = os.path.join(app.instance_path, 'greendataviz_app.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
     def entrance():
        return f'<a href={url_for("variation_sales")}>Variation Sales</a>'

    @app.route('/variation-sales')
    def variation_sales():
        f = './data/EtsySoldOrderItems2020.csv'
        listings = gdv.get_listings(f)
        return str([f'<a href={url_for("variation_sales_graph", listing=l)}>{l}</a><br>' for l in listings])
        
    @app.route('/variation-sales-graph/<listing>')
    def variation_sales_graph(listing):
        graph_name, _ = gdv.variation_sales_linegraph(gdv._sesh['df'], listing, 'W')
        return f'<img src="{url_for("static", filename=graph_name)}">'

    return app
#    if __name__ == '__main__':
#        app.run(ssl_context=('cert.pem', 'key.pem'))

