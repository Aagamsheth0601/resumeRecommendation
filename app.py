from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.sql.schema import ForeignKey
from werkzeug.utils import secure_filename
import os
import uuid


app = Flask(__name__)


# Session variable
app.secret_key = 'AJSKHFVIAUBVGNSDKFHUIUHFASHF'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Upload path of resumes
app.config['UPLOAD_FOLDER'] = os.getcwd() + '\\static\\resumes'


# For database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)







###################################### Important ######################################

# PDF to text
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def pdftotext(path):
    output_string = StringIO()
    with open(os.getcwd() + path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()

# Percentage Matche
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def cosine(companyjobreq, userresume):
    # Create vectors for cosine similarity
    cv = CountVectorizer()
    vectors = cv.fit_transform([companyjobreq, userresume])
    # print(vectors)
    print(cosine_similarity(vectors))
    return str("{:.2f}".format(cosine_similarity(vectors)[0][1]*100))+"%"
    
def percentagematch(companyjobreq, userresume):
    companyjobreq = pdftotext("\\static\\companyJobRequiement\\"+companyjobreq)
    userresume = pdftotext("\\static\\resumes\\"+userresume)
    return cosine(companyjobreq, userresume)


###################################### User ######################################

# User object
class User(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), nullable=False)
    resume = db.Column(db.String(200), nullable=True)
    position = db.Column(db.String(200), nullable=True)


# Signup
# Function to check User Signup Details
@app.route("/usersignupcheck", methods=['POST'])
def usersignupcheck():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirmpassword = request.form['confirm-password']
        if password != confirmpassword:
            return json.dumps({'status': 'fail', 'message': 'Password and confirm password do not match'})
        # To check if user already exists
        exists = db.session.query(User.sno).filter_by(
            username=username).first() is not None
        if exists:
            return json.dumps({'status': 'fail', 'message': 'User already exists. Try different loginID or goto login'})
        user = User(name=name, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return json.dumps({'status': 'success', 'message': 'You registered successfully'})

# Function to call User Signup Page


@app.route("/usersignup")
def usersignup():
    if 'username' in session:
        return redirect(url_for('profile'))
    return render_template('usersignup.html')


# Login
# Function to check User Login Details
@app.route("/userlogincheck", methods=['POST'])
def userlogincheck():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            return json.dumps({'status': 'fail', 'message': 'You need to first Signup'})
        # Check if password matches
        if not user.password == password:
            return json.dumps({'status': 'fail', 'message': 'Wrong password'})
        session['username'] = username
        return json.dumps({'status': 'success'})

# Function to call User Login Page


@app.route("/userlogin")
def userlogin():
    if 'username' in session:
        return redirect(url_for('profile'))
    return render_template('userlogin.html')


# Profile
# Function to goto user profile
@app.route("/profile")
def profile():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        return render_template('profile.html', user=user)
    return redirect(url_for('userlogin'))

# Function to keep file in folder


@app.route('/postresume', methods=['POST'])
def postresume():
    if(request.method == 'POST'):
        resume = request.files['file']
        resume.filename = str(uuid.uuid4())+'.pdf'
        resume.save(os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(resume.filename)))
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user.resume:
            os.remove(os.getcwd() + '/static/resumes/'+user.resume)
        user.resume = resume.filename
        db.session.commit()
        return json.dumps({'status': 'OK', 'resume': resume.filename})


# Function to update position
@app.route('/updatejobpositionuser', methods=['POST'])
def updatejobpositionuser():
    if(request.method == 'POST'):
        position = request.form['position']
        username = session['username']
        user = User.query.filter_by(username=username).first()
        user.position = position
        db.session.commit()
        return json.dumps({'status': 'OK', 'job': position})


@app.route("/searchcompany")
def searchcompany():
    if 'username' in session:
        company = Company.query.all()
        return render_template('searchcompany.html', company=company)
    return redirect(url_for('userlogin'))



# Profile
# Function to goto company profile
@app.route("/userfavourites")
def userfavourites():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        favourite = Companyfavourite.query.filter_by(usersno = user.sno)
        return render_template('userfavourites.html', favourite=favourite)
    return redirect(url_for('userlogin'))

def companydetailsincompanyfavourite(companysno):
    return Company.query.filter_by(sno=companysno).first()


# Logout
# Function to call Company Signup Page
@app.route("/logoutuser")
def logoutuser():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('userlogin'))


###################################### Company ######################################

# Company object
class Company(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), nullable=False)
    jobTitle = db.Column(db.String(200), nullable=True)
    pdf = db.Column(db.String(200), nullable=True)

# Upload Job Description
@app.route("/companyRequirement", methods=['POST'])
def companyRequirement():
    if 'company' in session:
        if request.method == 'POST':
            username = session['company']
            companyDetails = Company.query.filter_by(username=username).first()
            jobTitle = request.form['position']
            pdf = request.files['pdf']
            pdf.filename = str(uuid.uuid4())+'.pdf'
            pdf.save(os.path.join(os.getcwd() + "\\static\\companyJobRequiement", secure_filename(pdf.filename)))
            if companyDetails.pdf:
                os.remove(os.getcwd() + '/static/companyJobRequiement/'+companyDetails.pdf)
            companyDetails.pdf = pdf.filename
            companyDetails.jobTitle = jobTitle
            db.session.commit()
            return json.dumps({'status': 'OK', 'pdf': pdf.filename, 'job' : jobTitle})
    return redirect(url_for('companylogin'))


# Function to call Company Description Page
@app.route("/companyJobRequirement")
def companyJobRequirement():
    if 'company' in session:
        username = session['company']
        companyDetails = Company.query.filter_by(username=username).first()
        return render_template('companyJobRequirement.html', companyDetails=companyDetails)
    return redirect(url_for('companylogin'))


# Signup
# Function to check company Signup Details


@app.route("/companysignupcheck", methods=['POST'])
def companysignupcheck():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirmpassword = request.form['confirm-password']
        if password != confirmpassword:
            return json.dumps({'status': 'fail', 'message': 'Password and confirm password do not match'})
        # To check if user already exists
        exists = db.session.query(Company.sno).filter_by(
            username=username).first() is not None
        if exists:
            return json.dumps({'status': 'fail', 'message': 'User already exists. Try different loginID or goto login'})
        user = Company(name=name, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return json.dumps({'status': 'success', 'message': 'You registered successfully'})

# Function to call company Signup Page


@app.route("/companysignup")
def companysignup():
    if 'company' in session:
        return redirect(url_for('companyprofile'))
    return render_template('companysignup.html')


# Login
# Function to check Company Login Details
@app.route("/companylogincheck", methods=['POST'])
def companylogincheck():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Company.query.filter_by(username=username).first()
        if not user:
            return json.dumps({'status': 'fail', 'message': 'You need to first Signup'})
        # Check if password matches
        if not user.password == password:
            return json.dumps({'status': 'fail', 'message': 'Wrong password'})
        session['company'] = username
        return json.dumps({'status': 'success'})

# Function to call company Login Page


@app.route("/companylogin")
def companylogin():
    if 'company' in session:
        return redirect(url_for('companyprofile'))
    return render_template('companylogin.html')


# Profile
# Function to goto company profile
@app.route("/companyprofile")
def companyprofile():
    if 'company' in session:
        username = session['company']
        user = Company.query.filter_by(username=username).first()
        companyfavourite = Companyfavourite.query.filter_by(companysno = user.sno)
        return render_template('companyprofile.html', user=user, companyfavourite=companyfavourite)
    return redirect(url_for('companylogin'))


@app.route('/searchuser')
def searchuser():
    if 'company' in session:
        jobsearchers = User.query.all()
        return render_template('searchuser.html', jobsearchers=jobsearchers)
    return redirect(url_for('companylogin'))

# Logout
# Function to logout
@app.route("/logoutcompany")
def logoutcompany():
    if 'company' in session:
        session.pop('company', None)
    return redirect(url_for('companylogin'))


# Company object
class Companyfavourite(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    companysno = db.Column(db.Integer, ForeignKey("company.sno"), nullable=False)
    usersno = db.Column(db.Integer, ForeignKey("user.sno"), nullable=False)


def userincompanyfavourite(usersno):
    username = session['company']
    company = Company.query.filter_by(username=username).first()
    return Companyfavourite.query.filter_by(usersno = usersno, companysno = company.sno).count()

def userdetailsincompanyfavourite(usersno):
    return User.query.filter_by(sno=usersno).first()

def companyjobreq():
    if 'company' in session:
        companyusername = session['company']
        company = Company.query.filter_by(username=companyusername).first()
        return company.pdf

@app.context_processor
def context_processor():
    return dict(userincompanyfavourite = userincompanyfavourite, userdetailsincompanyfavourite = userdetailsincompanyfavourite, companyjobreq=companyjobreq, percentagematch = percentagematch, companydetailsincompanyfavourite=companydetailsincompanyfavourite)


@app.route("/addcompanyfavourite", methods=['POST'])
def addcompanyfavourite():
    if 'company' in session:
        companyusername = session['company']
        company = Company.query.filter_by(username=companyusername).first()
        companysno = company.sno
        usersno = request.form['usersno']
        companyfavourite = Companyfavourite(companysno=companysno, usersno=usersno)
        db.session.add(companyfavourite)
        db.session.commit()
        return json.dumps({'status': 'success'})

@app.route("/deletecompanyfavourite", methods=['POST'])
def deletecompanyfavourite():
    if 'company' in session:
        usersno = request.form['usersno']
        companyusername = session['company']
        company = Company.query.filter_by(username=companyusername).first()
        companysno = company.sno
        companyfavourite = Companyfavourite.query.filter_by(usersno = usersno, companysno = companysno).first()
        db.session.delete(companyfavourite)
        db.session.commit()
        return json.dumps({'status': 'success'})


###################################### Common ######################################


# Function to go to home page
@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
