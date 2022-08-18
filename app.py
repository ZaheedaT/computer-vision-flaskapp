from flask import Flask, render_template, request, jsonify
import os
import json
import pandas as pd
import io
import numpy as np
import nest_asyncio
from enum import Enum
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
from flask import Flask, render_template, request, jsonify, session
import os
import json
import pandas as pd

from utils import detect_and_draw_box , store_result , detect_video


app = Flask(__name__,  template_folder='templateFiles', static_folder='staticFiles')

UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'xyz'

# List available models using Enum for convenience. This is useful when the options are pre-defined.
class Model(str, Enum):
    yolov3tiny = "yolov3-tiny"
    yolov3 = "yolov3"

os.path.dirname("../templateFiles")
    
@app.route('/')
def main():
    return render_template("index.html")

def allowed_file(filename):

    fileExtension = filename.split(".")[-1] in ("jpg", "jpeg", "png", "webp", "mp4", "mov", "avi")

    if not fileExtension:
        raise HTTPException(status_code=415, detail="Unsupported file provided.")


@app.route('/', methods=("POST", "GET"))
def uploadFile():
    if not os.path.exists(app.config['UPLOAD_FOLDER']): # Create Directory for the uploaded staticFiles
        os.mkdir(app.config['UPLOAD_FOLDER'])

    if request.method == 'POST':
        _img = request.files['file-uploaded']
        filename = _img.filename
        allowed_file(filename)
        _img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        session['uploaded_img_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        return render_template('success.html')

@app.route('/show_image')
def displayImage():
    img_file_path = session.get('uploaded_img_file_path', None)
    if img_file_path.split(".")[-1] in ("mp4", "mov"):
        return render_template('show_video.html', user_image=img_file_path)
    else:

        return render_template('show_image.html', user_image = img_file_path)



@app.route('/detect_object')
def detectObject():
    uploaded_image_path = session.get('uploaded_img_file_path', None)

    output_image_path, response, file_type = detect_and_draw_box(uploaded_image_path)
    if file_type == "image":
        return render_template('show_image.html', jsonfile= response, user_image=output_image_path[0])
    else:
        return render_template('show_video.html',jsonfile= response, user_image=output_image_path[0])



if __name__ == '__main__':
    app.run(debug=True)
    
    