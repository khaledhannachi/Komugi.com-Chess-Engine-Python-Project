from flask_app.models.user_model import User

from flask_app import app
from flask import Flask,render_template,redirect,request,session,flash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)
DATABASE="chess_schema"

# @app.route('/')
# def index():
#     return render_template("index.html")

@app.route('/process' , methods=['POST'])
def save():
    if not User.validate(request.form):
        return redirect("/")
    pw_hashed=bcrypt.generate_password_hash(request.form["password"])
    data={
        **request.form,
        "password":pw_hashed
    }
    user_id=User.create(data)
    session["user_id"]=user_id
    return redirect("/chess")



# !Login - method - ACTION
@app.route("/users/login", methods=["POST"])
def user_login():
    data = {"email": request.form["email"]}
    user_in_db = User.get_by_email(data)
    # !if email not found
    if not user_in_db:
        flash("invalid credentials", "log")
        return redirect("/sign_in")
    # !now check the password
    if not bcrypt.check_password_hash(user_in_db.password, request.form["password"]):
        flash("invalid credentials", "log")
        return redirect("/sign_in")

    # * if all is good
    print(f"===> id = {user_in_db.id}")
    session["user_id"] = user_in_db.id
    return redirect("/chess")


# # !Display Route - Dashboard
@app.route("/dashboard")
def dash():
    # ! Route Guard
    # if "user_id" not in session:
    #     return redirect("/")
    data = {"id": session["user_id"]}
    user = User.get_by_id(data)
    
    return render_template("user_dashboard.html", user=user)


# ! ------- LOGOUT -------- action
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/chess")

