import os
from werkzeug.utils import secure_filename
from flask import Flask,request,redirect,send_file,render_template
import cv2
import random
import numpy as np
import threading

UPLOAD_FOLDER = 'uploads/'

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("upload.html")

@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = os.path.abspath(f"uploads/{filename}")
            
            img = cv2.imread(path)
            height, width = img.shape[0], img.shape[1]
            img = cv2.resize(img,dsize=(200,200))

            roi_list = []
            height_step, width_step = 40, 40
            for i in range(0,200,height_step):
                for j in range(0,200,width_step):
                    roi = img[i:i+height_step, j:j+width_step]
                    roi_list.append(roi)

            random.shuffle(roi_list)
            img_list = np.concatenate([np.concatenate(roi_list[5*i:5*(i+1)],axis=1) for i in range(5)],axis=0)

            image = cv2.resize(img_list, dsize=(width, height))
            cv2.imwrite(f"uploads/{filename}",image)

            print("saved file successfully")
      #send file name as parameter to downlad
            return redirect('/downloadfile/'+ filename)

    return render_template('upload.html')


# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    print(f"uploads/{filename}")
    def del_image():
        os.remove(f"uploads/{filename}")
    timer = threading.Timer(30, del_image, args = None, kwargs = None)
    timer.start()
    return render_template('download.html',value=filename)

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')

