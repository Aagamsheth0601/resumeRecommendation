from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import uuid


app = Flask(__name__)


# Session vaiable
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
        return json.dumps({'status': 'OK','job': position})




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
        jobsearchers = User.query.all()
        return render_template('companyprofile.html', user=user, jobsearchers=jobsearchers)
    return redirect(url_for('companylogin'))


# Logout
# Function to logout
@app.route("/logoutcompany")
def logoutcompany():
    if 'company' in session:
        session.pop('company', None)
    return redirect(url_for('companylogin'))


###################################### Common ######################################


# Function to go to home page
@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
