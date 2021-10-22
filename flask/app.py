from flask import Flask, request, session, g, send_file, render_template, make_response
from waitress import serve
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import json5
from werkzeug.utils import secure_filename
import os

"""
@author Mehul Agrawal <mehulagrawal710@gmail.com>
"""

####### Reading Configurations ########


def getConfiguration(path):
    configFile = open(path, "r")
    configuration = json5.load(configFile)
    configFile.close()
    return configuration


CONFIG_FILE_PATH = "./config/config.json"

configuration = getConfiguration(CONFIG_FILE_PATH)

FLASK_HOST = configuration["flask_host"]
FLASK_PORT = configuration["flask_port"]

############ Logging #############

my_handler = RotatingFileHandler(
    configuration["log_file_name"],
    mode=configuration["log_file_mode"],
    maxBytes=configuration["log_file_max_size_mb"] * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=0,
)

my_handler.setFormatter(logging.Formatter(configuration["log_format"]))
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger("root")
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)


def printLog(msg):
    app_log.info(msg)
    print(">", msg)
    print()


############## Helper ################


#######################################

app = Flask(__name__)
app.secret_key = "iufh4857o3yfhh3"
app.static_folder = "static"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB
CORS(app)

####### Interceptor ########


@app.before_first_request
def before_first_request_func():

    """
    This function will run once before the first request to this instance of the application.
    You may want to use this function to create any databases/tables required for your app.
    """

    print("This function will run once ")


@app.before_request
def before_request_func():

    """
    This function will run before every request. Let's add something to the session & g.
    It's a good place for things like establishing database connections, retrieving
    user information from the session, assigning values to the flask g object etc..
    We have access to the request context.
    """

    session["foo"] = "bar"
    g.username = "root"
    print("before_request is running!")


####### API Routings ########


@app.route("/")
def index():

    """
    A simple route that gets a session value added by the before_request function,
    the g.username and returns a string.
    Uncommenting `raise ValueError` will throw an error but the teardown_request
    funtion will still run.
    """

    # raise ValueError("after_request will not run")

    username = g.username
    foo = session.get("foo")
    print("index is running!", username, foo)
    return "Hello world"


@app.route("/home", methods=["GET", "POST"])
def home():
    allfiles = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template(
        "index.html", baseurl=request.host_url, name="Mehul", uploaded_files=allfiles
    )


@app.route("/upload", methods=["GET", "POST"])
def upload():
    try:
        file = request.files["f"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    except Exception as e:
        print(e)
        return """Failed"""
    return """File uploaded successfully :)"""


@app.route("/download", methods=["GET", "POST"])
def download():
    filename = request.args.get("filename")
    print(filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        return send_file(file_path, attachment_filename=filename, as_attachment=True)
    return """No such File Found :("""


####### After request ########


@app.after_request
def after_request_func(response):

    """
    This function will run after a request, as long as no exceptions occur.
    It must take and return the same parameter - an instance of response_class.
    This is a good place to do some application cleanup.
    """

    username = g.username
    foo = session.get("foo")
    print("after_request is running!", username, foo)
    return response


@app.teardown_request
def teardown_request_func(error=None):

    """
    This function will run after a request, regardless if an exception occurs or not.
    It's a good place to do some cleanup, such as closing any database connections.
    If an exception is raised, it will be passed to the function.
    You should so everything in your power to ensure this function does not fail, so
    liberal use of try/except blocks is recommended.
    """

    print("teardown_request is running!")
    if error:
        # Log the error
        print(str(error))


################ Main ################

if __name__ == "__main__":
    try:
        printLog("Application Started")
        serve(app, host=FLASK_HOST, port=FLASK_PORT)
    except Exception as e:
        printLog(e)
        printLog("Exiting upgrade.py program...")
