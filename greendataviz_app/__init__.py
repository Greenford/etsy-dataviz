import os
from flask import Flask, flash, url_for, request, redirect
from greendataviz_app import greendataviz as gdv

ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = './data/uploads'

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE = os.path.join(app.instance_path, 'greendataviz_app.sqlite'),
        UPLOAD_FOLDER = UPLOAD_FOLDER,
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
        f = './data/uploads/orderitems.csv'
        listings = gdv.get_listings(f)
        return str([f'<a href={url_for("variation_sales_graph", listing=l)}>{l}</a><br>' for l in listings])
        
    @app.route('/variation-sales-graph/<listing>')
    def variation_sales_graph(listing):
        graph_name, _ = gdv.variation_sales_linegraph(gdv._sesh['df'], listing, 'W')
        return f'<img src="{url_for("static", filename=graph_name)}">'

    def allowed_file(filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/upload-file', methods = ['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
        # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                #filename = secure_filename(file.filename)
                filename = 'orderitems.csv'
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('entrance',
                                        filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''
    
    return app
#    if __name__ == '__main__':
#        app.run(ssl_context=('cert.pem', 'key.pem'))

