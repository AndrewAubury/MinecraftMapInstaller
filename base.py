import os
from flask import Flask
from flask import render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

from PterodactylControl import PterodactylControl

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__)
app.secret_key = b"'Z\tF\x84\xbf\xb5C\xcfk\xc3\x8c"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pc = PterodactylControl("./server/")
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
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
        if file and not allowed_file(file.filename):
            flash('Invalid file type')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #add andrew integration here
            status = pc.setupFromZIP(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if status:
                return render_template('Index.html', title='test page for now', status='Upload success')
            else:
                flash('Invalid file')
                return redirect(request.url)
    return render_template('Index.html', title='test page for now', status='Pending upload')