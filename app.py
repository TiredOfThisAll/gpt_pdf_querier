from flask import Flask, render_template, request, redirect, url_for
import os
from uuid import uuid4
from ask_gpt import process_pdf

data = {}

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.isdir("uploads"):
    os.mkdir("uploads")


def allowed_file(filename):
    head, tail = os.path.splitext(filename)
    return tail == ".pdf"


@app.route('/', endpoint='root')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    filename = request.files['file'].filename
    if filename == '':
        return redirect(request.url)
    
    if file and allowed_file(filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        upload_id = str(uuid4())
        print("processing")
        responser = process_pdf(os.path.join("uploads", filename))
        print("done processing")
        data[upload_id] = {"responser": responser, "filename": filename}
        return upload_id, 200
    else:
        return redirect(request.url)


@app.route('/chat/<upload_id>', methods=['GET'])
def chat(upload_id):
    if upload_id not in data:
        return "Page not found", 404
    return render_template('chat.html', filename=data[upload_id]["filename"])


@app.route('/ask/<upload_id>', methods=['POST', 'GET'])
def ask(upload_id):
    if upload_id not in data:
        return "Page not found", 404
    if not request.form.get("query"):
        return redirect(request.url)
    
    query = request.form.get("query")
    response = data[upload_id]["responser"].invoke(query)

    return response, 200
    


if __name__ == '__main__':
    app.run(debug=True)