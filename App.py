from mailbox import Message
import os
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
# if not os.path.isdir(UPLOAD_FOLDER):
#     os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['dcm', 'nii.gz', 'dicom', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/<path:path>')
def home(path):
  return render_template(path)

@app.route('/predict/v2/<path:path>', methods=['POST'])
def predictv2(path):

    print("inside ---",path)
    
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
        # nnUNetv2_predict -d Dataset219_AMOS2022_postChallenge_task2 -i ./input/ -o ./output/ -f  0 -tr nnUNetTrainer -c 3d_fullres
            # subprocess.check_output("/home/predict.sh", shell=True)
            o_put = subprocess.check_output(
                [
                "nnUNetv2_predict", 
                "-i", inputDir.name,
                "-o", outDir.name,
                "-f", "0",
                "-d",path,
                "-c", "3d_fullres",
                "-tr", "nnUNetTrainer",
                "-p" "nnUNetPlans",
                "--disable_tta"]
                )
        directory_path = outDir.name
        print(o_put)

# List all files in the directory and filter for files ending with '.nii.gz'
        files_with_extension = [f for f in os.listdir(directory_path) if f.endswith('.nii.gz')]

        print(files_with_extension)     

        # files = os.listdir(outDir.name)
        retFile = files_with_extension[0]
        return send_file(outDir.name +"/"+retFile, mimetype="application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip")

@app.route('/predict/ich', methods=['POST'])
def predict_ich():

    
    
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
        # nnUNetv2_predict -d Dataset219_AMOS2022_postChallenge_task2 -i ./input/ -o ./output/ -f  0 -tr nnUNetTrainer -c 3d_fullres
            # subprocess.check_output("/home/predict.sh", shell=True)
            o_put = subprocess.check_output(
                [
                "nnUNetv2_predict", 
                "-i", inputDir.name,
                "-o", outDir.name,
                "-f", "0",
                "-d","911",
                "-c", "3d_fullres",
                "-tr", "nnUNetTrainer",
                "-p" "nnUNetPlans"]
                )
        directory_path = outDir.name
        print(o_put)

# List all files in the directory and filter for files ending with '.nii.gz'
        files_with_extension = [f for f in os.listdir(directory_path) if f.endswith('.nii.gz')]

        print(files_with_extension)     

        # files = os.listdir(outDir.name)
        retFile = files_with_extension[0]
        return send_file(outDir.name +"/"+retFile, mimetype="application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip")



@app.route('/predict/<path:path>', methods=['POST'])
def predict(path):

    print("inside ---",path)
    
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
            o_put = subprocess.check_output(
                [
                "nnUNet_predict", 
                "-i", inputDir.name,
                "-o", outDir.name,
                "-t", path,
                "-m", "3d_fullres",
                "--disable_tta"]
                )
        directory_path = outDir.name
        print(o_put)

# List all files in the directory and filter for files ending with '.nii.gz'
        files_with_extension = [f for f in os.listdir(directory_path) if f.endswith('.nii.gz')]

        print(files_with_extension)     

        # files = os.listdir(outDir.name)
        retFile = files_with_extension[0]
        return send_file(outDir.name +"/"+retFile, mimetype="application/zip, application/octet-stream, application/x-zip-compressed, multipart/x-zip")
       
 
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False,threaded=True)
