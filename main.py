import pickle
from flask import Flask, render_template, request, flash, session, redirect, url_for
import sklearn
import sqlite3

app = Flask(__name__)
app.secret_key = "hello"


@app.route('/')
def home():
    if 'name' in session:
        session.pop('name', None)
    return render_template("home.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route("/login_validation", methods=['POST'])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("password")
    flag = 1
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS USER(name text, email text,password text)''')
    conn.commit()
    table = conn.execute("SELECT * FROM USER")
    for row in table:
        print(email + " " + password+" "+row[1]+" "+row[2])
        if email == row[1] and password == row[2]:
            uname = row[0]
            flag = 0
    if flag == 0:
        print(email+" "+password)
        session['name'] = uname
        print(session['name'])
        return redirect(url_for("predict"))
    else:
        flash("Please recheck your credentials")
        return render_template("login.html")


@app.route("/register_validation", methods=['POST'])
def register_validation():
    name = request.form.get("nameR")
    email = request.form.get("emailR")
    password = request.form.get("passwordR")
    specialsym = ['$', '@', '#', '%']
    val = True

    if len(password) < 6:
        flash('Length of password should be at least 6', 'info')
        return render_template("register.html")

    if len(password) > 20:
        flash('Length of password should be not be greater than 20')
        return render_template("register.html")

    if not any(char.isdigit() for char in password):
        flash('Password should have at least one number')
        return render_template("register.html")

    if not any(char.isupper() for char in password):
        flash('Password should have at least one uppercase letter')
        return render_template("register.html")

    if not any(char.islower() for char in password):
        flash('Password should have at least one lowercase letter')
        return render_template("register.html")

    if not any(char in specialsym for char in password):
        flash('Password should have at least one of the symbols $@#')
        return render_template("register.html")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS USER(name text, email text,password text)''')
    conn.commit()
    table = conn.execute("SELECT * FROM USER")
    for row in table:
        if row[1] == email:
            flash("You are already registered with this email.Try another")
            return render_template("register.html")

    sql = """INSERT INTO USER (NAME,EMAIL,PASSWORD) VALUES(?,?,?)"""
    cursor = conn.cursor()
    cursor.execute(sql, (name, email, password))
    conn.commit()
    print("Records Created")
    table = conn.execute("SELECT * FROM USER")
    for row in table:
        print(row[0]+" "+row[1]+"\n")
    conn.close()
    flash('Registration successful you can login with your credentials', 'info')
    return render_template("login.html")


@app.route('/predict')
def predict():
    if 'name' in session:
        print("hello")
        return render_template("predict.html")
    else:
        flash("Login in inorder to use predict")
        return redirect(url_for("login"))


@app.route('/predict_validation', methods=['POST'])
def predict_validation():

    attr1 = request.form.get("age")
    if request.form.get("sex") == "female":
        attr2 = "0"
    else:
        attr2 = "1"
    attr3 = request.form.get("chestpain")
    attr4 = request.form.get("bp")
    attr5 = request.form.get("cho")
    if request.form.get("sugar") == "false":
        attr6 = "0"
    else:
        attr6 = "1"
    attr7 = request.form.get("ecg")
    attr8 = request.form.get("hr")
    if request.form.get("angina") == "no":
        attr9 = "0"
    else:
        attr9 = "1"
    attr10 = request.form.get("ST")
    attr11 = request.form.get("slope")
    attr12 = request.form.get("vessels")
    attr13 = request.form.get("thal")
    attr = [[int(attr1), int(attr2), int(attr3), int(attr4), int(attr5), int(attr6), int(attr7), int(attr8), int(attr9), float(attr10), int(attr11), int(attr12), int(attr13)]]
    our_model = pickle.load(open('heart.pkl', 'rb'))
    prediction = our_model.predict(attr)[0]
    if prediction == 1:
        flash("You have high chances of having a cardio vascular disease.Please consult a doctor.")
        return render_template("result.html")
    else:
        flash("You have low chances of having a cardio vascular disease.You are good to go.")
        return render_template("result.html")


@app.route('/result')
def result():
    return render_template("result.html")


@app.route('/logout')
def logout():
    if 'name' in session:
        session.pop('name', None)
        return redirect(url_for("home"))
    else:
        flash("Login in inorder to logout")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)


