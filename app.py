from flask import Flask, send_file, request,render_template, make_response
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

@app.route('/', methods=['GET', 'POST'])
def home():
	allfiles = os.listdir(app.config['UPLOAD_FOLDER'])
	return render_template('index.html', baseurl = request.host_url, name="Mehul", uploaded_files = allfiles)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	try:
		file = request.files['f']
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	except Exception as e:
		print(e)
		return """Failed"""
	return """File uploaded successfully :)"""

@app.route('/download', methods=['GET', 'POST'])
def download():
    filename = request.args.get('filename')
    print(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
    	return send_file(file_path, attachment_filename=filename, as_attachment=True)
    return """No such File Found :("""

if __name__ == '__main__':
    app.run(debug=True, threaded=False)