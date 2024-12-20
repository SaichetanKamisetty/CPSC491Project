from flask import Flask, render_template, request, jsonify, url_for, Response, stream_with_context, send_file
import os
from werkzeug.utils import secure_filename
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))
import time
import json
import zipfile
import pathlib
import io
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("robloflow_api_key")

from Controller import TranslateManga

from roboflow import Roboflow
rf = Roboflow(api_key=f"{api_key}")
project = rf.workspace().project("segmetn")
model = project.version(3).model
from manga_ocr import MangaOcr 

is_translating = False

ocr = MangaOcr()
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def main_page():
    return render_template("index.html")

@app.route('/translation-progress')
def translation_progress():
    def generate():
        while True:
            if not hasattr(app, 'translation_status'):
                data = 'data: {"status": "waiting"}\n\n'
            else:
                data = f'data: {json.dumps(app.translation_status)}\n\n'
            yield data
            time.sleep(1) 
            
    return Response(stream_with_context(generate()), 
                   mimetype='text/event-stream')

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
        full_path = os.path.join(BASE_DIR, file_path.lstrip('/'))
        if os.path.exists(os.path.join(os.getcwd(), full_path)) and not is_translating:
            os.remove(os.path.join(os.getcwd(), full_path))
            return jsonify({'success': True, 'message':'File deleted'}), 200
        else:
            return jsonify({'success': False, 'message':'File not found/error'}), 400
        
    return jsonify({'success': False, 'message': 'File path not provided.'}), 400


@app.route('/translate', methods=['POST'])
def translate_request():
    global is_translating
    if is_translating:
        return jsonify({'success': False, 'message': 'Translation already in progress'}), 400
    
    apikey = request.form.get("gptInput")
    textsize = int(request.form.get("textSize"))
    checkbox = True if request.form.get("checkbox") == "true" else False

    is_translating = True
    try: 
        app.translation_status = {"status": "started"}
        def progress_callback(status):
            app.translation_status = {
                "status": status,
            }
        translator = TranslateManga(model=model, file_loc=UPLOAD_FOLDER, ocr=ocr, progress_callback=progress_callback, api_key=apikey, remove_text_only=checkbox, text_size=textsize)
        res = translator.TranslateManga()

        if res[0] == 1:
            file_urls = []
            for filename in os.listdir(UPLOAD_FOLDER):
                file_url = url_for('static', filename=f'uploads/{filename}')
                file_urls.append(file_url)

            return jsonify({'success': True, 'message': 'Translated Manga', 'fileUrls': file_urls}), 200
        else:
            app.translation_status = {"status": "waiting"}
            return jsonify({'success': False, 'message': f'Issue processing images: {res[1]}'}), 400
    except Exception as e:
        app.translation_status = {"status": "waiting"}
        return jsonify({'success': False, 'message': f'Something went wrong: {e}'}), 400
    finally:
        app.translation_status = {"status": "waiting"}
        is_translating = False


@app.route('/download', methods=['GET'])
def download_images():
    try:

        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify({'success': False, 'message': f"Image directory doesn't exist"}), 400
        

        images = [f for f in os.listdir(UPLOAD_FOLDER)]
        if not images:
            return jsonify({'success': False, 'message': f"No images in directory"}), 400


        base_path = pathlib.Path(UPLOAD_FOLDER)
        data = io.BytesIO()

        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in base_path.iterdir():
                z.write(f_name, arcname=f_name.name)
        data.seek(0)
        return send_file(
            data, 
            mimetype='application/zip',
            as_attachment=True,
            download_name="images.zip"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/deleteImages', methods=['POST'])
def delete_images():
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return jsonify({'success': False, 'message': f"Folder does not exist."}), 400
        images = [f for f in os.listdir(UPLOAD_FOLDER)]

        if not images:
            return jsonify({'success': False, 'message': f"No images in the directory"}), 400

        for image in images:
            os.remove(os.path.join(UPLOAD_FOLDER, image))
        
        return jsonify({'success': True, 'message': f"Images successfully deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


app.run(debug=True)



# npx tailwindcss -i ./app/static/src/input.css -o ./app/static/css/main.css -- watch | Run this command every time you start.