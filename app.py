from flask import Flask, render_template

app = Flask(__name__)

# Function to call Login Page


@app.route("/login")
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
