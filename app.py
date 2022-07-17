import os
import easyocr
import json
import spacy
import PyPDF2
from pdf2image import convert_from_path
import numpy as np
from werkzeug.utils import secure_filename
from flask import Flask,flash,request,redirect,send_file,render_template
reader = easyocr.Reader(['en']) 

UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER='download/'

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Upload API
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
            print("saved file successfully")
            if filename[-3:]=='pdf' or filename[-3:]=='PDF':
                pdfFileObj = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') 
    
                # creating a pdf reader object 
                pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
                    
                # printing number of pages in pdf file 
                print(pdfReader.numPages) 
                    
                # creating a page object 
                pageObj = pdfReader.getPage(0) 
                    
                # extracting text from page 
                line= pageObj.extractText()
                print(line)
                # closing the pdf file object 
                pdfFileObj.close() 

            elif filename[-3:]=='jpg' or filename[-3:]=='JPG' or filename[-3:]=='png' or filename[-3:]=='PNG':    
                line=''
                text = reader.readtext(os.path.join(app.config['UPLOAD_FOLDER'], filename),detail=0)
                for tex in text:
                    line=line+' '+tex

            nlp_model=spacy.load('/Users/ritikalakdawala/Documents/Form16Extraction/model-last')
            doc=nlp_model(line)
            dict={}
            for i in doc.ents:
                dict[i.label_]=i.text
            with open(os.path.join(app.config['DOWNLOAD_FOLDER'], filename.rsplit('.',1)[0]+'.json'),'w') as outfile:
                json.dump(dict,outfile)
                FILENAME=filename.rsplit('.',1)[0]+'.json'
                app.config['FILENAME']=FILENAME

            #send file name as parameter to downlad
            return redirect('/downloadfile/'+ filename.rsplit('.',1)[0]+'.json')

    return render_template('index.html')

# Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = DOWNLOAD_FOLDER + filename.rsplit('.',1)[0]+'.json'
    print(file_path)
    return send_file(file_path, as_attachment=True, attachment_filename='')

if __name__ == "__main__":
    app.debug=True
    app.run()
