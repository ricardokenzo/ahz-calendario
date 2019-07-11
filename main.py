import os
import urllib.request
from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore
import json
import csv
import uuid
import datetime
from datetime import timedelta
ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			if (not len(firebase_admin._apps)):
				cred = credentials.Certificate('./ServiceAccountKey.json')
				default_app = firebase_admin.initialize_app(cred)
			db = firestore.client()

			with open(filename, encoding='UTF-8') as excel:
			    reader = list(csv.reader(excel))
			    row_count = sum(1 for row in reader)
			    s = 3
			    d = 0
			    i = 3
			    row = 2
			    col = 1
			    while (col < 8):
			        while (s<row_count):
			            time = reader[1][col]
			            segmento = reader[s][0]
			            nome = reader[2][col]
			            post_id=reader[i][col]
			            date = datetime.datetime.strptime(reader[0][col], "%d/%m/%Y")
			            modified_date = date + timedelta(days=1)
			            s+=1
			            i+=1
			            if post_id=='':
			                continue
			            else:
			                doc_ref = db.collection('calendar_update').document(segmento).collection('list').document(str(uuid.uuid4()))
			                doc_ref.set({ #set is to create, update is to update, use set and merge=true to merge
			                    "date":modified_date,
			                    "id_posts":[post_id],
			                    "times_to_post":int(time),
			                    "title":str(nome)
			            }, merge=True)
			        s=3
			        i=3
			        col+=1
			flash('File successfully uploaded')
			os.remove(filename)
			return redirect('/')
		else:
			flash('Allowed file type is csv ')
			return redirect(request.url)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001)