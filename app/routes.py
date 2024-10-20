from flask import Flask, render_template, request, jsonify, url_for, g
import os
from werkzeug.utils import secure_filename

from roboflow import Roboflow
# rf = Roboflow(api_key="")
# project = rf.workspace().project("segmetn")
# model = project.version(3).model
from manga_ocr import MangaOcr 

# ocr = MangaOcr()
app = Flask(__name__)

UPLOAD_FOLDER = 'app/static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def main_page():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def uploadFiles():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files in the request.'}), 400
    
    files = request.files.getlist('files[]')
    file_urls = []

    for file in files:
        if file and check_file_ext(file.filename):
            filename = secure_filename(filename=file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_url = url_for('static', filename=f'uploads/{filename}')
            file_urls.append(file_url)
        
    return jsonify({'files_urls': file_urls})

def check_file_ext(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']


@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_path = data.get('file_path', None)

    if file_path:
        full_path = os.path.join('app/', file_path.lstrip('/'))

        if os.path.exists(os.path.join(os.getcwd(), full_path)):
            os.remove(os.path.join(os.getcwd(), full_path))
            return jsonify({'success': True, 'message':'File deleted'}), 200
        else:
            return jsonify({'success': True, 'message':'File not found/error'}), 400
        
    return jsonify({'success': False, 'message': 'File path not provided.'}), 400


app.run(debug=True)



# npx tailwindcss -i ./app/static/src/input.css -o ./app/static/css/main.css -- watch | Run this command every time you start.