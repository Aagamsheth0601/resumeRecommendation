from flask import *
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Upload path of resumes
app.config['UPLOAD_FOLDER'] = os.getcwd() + '\\static\\resumes'

# Function to call Login Page
@app.route("/login")
def login():
    return render_template('login.html')

# Function to goto uploadfile 
@app.route("/uploadresume")
def uploadresume():
    return render_template('uploadresume.html')

# Function to keep file in folder
@app.route('/postresume', methods = ['POST'])  
def success():  
    if(request.method == 'POST'):
        resume = request.files['file']
        resume.filename = str(uuid.uuid4())+'.pdf'
        resume.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(resume.filename)))
        return json.dumps({'status':'OK','resume':resume.filename})

if __name__ == "__main__":
    app.run(debug=True)
