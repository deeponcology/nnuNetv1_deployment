from mailbox import Message
import os
import sys
from pathlib import Path
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import subprocess
import json
import shutil
import tempfile
from flask import jsonify, send_file
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024 * 1024

# Get current path
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = "./input"
# os.path.join(path, 'uploads')

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

if not os.path.isdir("./output"):
    os.mkdir("./output")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['dcm', 'nii.gz', 'dicom', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/config')
def get_home():
    if "TOTALSEG_HOME_DIR" in os.environ:
        totalseg_dir = Path(os.environ["TOTALSEG_HOME_DIR"])
    else:
        # in docker container finding home not properly working therefore map to /tmp
        home_path = Path("/tmp") if str(Path.home()) == "/" else Path.home()
        totalseg_dir = home_path / ".totalsegmentator"
    # return totalseg_dir
    return jsonify({"message": totalseg_dir})


@app.route('/<path:path>')
def home(path):
  return render_template(path)

@app.route('/predict/totalseg/<path:path>', methods=['POST'])
def predict(path):

    
    
    # os.mkdir(app.config['UPLOAD_FOLDER'])
    if request.method == 'POST':

        
        print("inside ---")
        files = request.files.getlist('files[]')
        inputDir = tempfile.TemporaryDirectory(dir="./input")
        
        outDir = tempfile.TemporaryDirectory(dir="./output")
        print(inputDir.name)
        print(outDir.name)

        for file in files:
            filename = secure_filename(file.filename)
            print(filename)
            file.save(inputDir.name +"/" +filename)
            

       
            my = os.listdir(app.config['UPLOAD_FOLDER'])
            print("input dir = ",my)
            # nnUNet_predict -i $inputDir -o $outDir --task_name $1 --model 2d --disable_tta
        # 
            # subprocess.check_output("/home/predict.sh", shell=True)
            subprocess.check_output(
                [
                "TotalSegmentator", 
                "-i", inputDir.name +"/" +filename,
                "-o", outDir.name+"/" +"output.nii.gz",
                # "--fast",
                "--task",path,
                "--ml"]
                )
        files = os.listdir(outDir.name)
        # retFile = files[0]
        print("output files",files)
        retFile = files
        return send_file(outDir.name+"/" +"output.nii.gz", mimetype="application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip")
       
 
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False,threaded=True)
