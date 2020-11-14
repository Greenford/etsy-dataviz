import os
from flask import Flask, flash, url_for, request, redirect, session, render_template

from greendataviz_app import greendataviz as gdv
from werkzeug.utils import secure_filename
from datetime import datetime


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def entrance():
        return render_template("home.html")

    def allowed_file(filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
        )

    @app.route("/upload-file", methods=["GET", "POST"])
    def upload_file():
        if request.method == "POST":

            # check if the post request has the file part
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["file"]

            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                session["filename"] = datetime.now().strftime(
                    "%Y %b %-d %H%M:%S:%f"
                ) + secure_filename(file.filename)

                session.permanent = False
                if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                    os.makedirs(app.config["UPLOAD_FOLDER"])
                file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], session["filename"])
                )
                return redirect(url_for("entrance"))
            else:
                flash(
                    "".join([f"{e}, " for e in app.config["ALLOWED_EXTENSIONS"]])
                    + "file types only."
                )
                return redirect(request.url)
        else:
            return render_template("upload_file.html")

    @app.route("/clear-file")
    def clear_file():
        session.pop('filename')
        flash('File Cleared')
        return redirect(url_for('entrance'))

    @app.route("/help")
    def help():
        return "Content forthcoming"

    from . import variation_sales

    app.register_blueprint(variation_sales.bp)

    return app
