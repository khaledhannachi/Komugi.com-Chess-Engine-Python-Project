
from chess_engine import *


import chess
from utils import make_move

import torch
import re
from flask import Flask,render_template,redirect,request,session,flash
from flask_bcrypt import Bcrypt
from models.user_model import User
# input_string = "Hello, World! 123"
# result = re.sub(r'[A-Z]', '', input_string)
# print(result)  # Output will be: ", 123"


app = Flask(__name__)
bcrypt = Bcrypt(app)

app = Flask(__name__)
app.secret_key = "shhhhhh"
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



# @app.route('/move/<pgn>')
# def get_move(pgn):
#     print("Calculating...")
#     # engine = Engine(fen)
#     # move = engine.iterative_deepening(depth - 1)
 
#     start_chars = pgn[:2]
#     end_chars = pgn[-2:]
#     result = start_chars + end_chars
#     # bot_move = make_move(re.sub(r'[A-Z]', '', pgn))
#     bot_move = make_move(result)

    
#     print("5- Move found!", bot_move)
#     data = {"move":bot_move}
#     return bot_move


# @app.route('/test/<string:tester>')
# def test_get(tester):
#     return tester

@app.route('/')
def about():
    return render_template("about.html")



@app.route('/chess')
def chess():
    return render_template("index.html")


@app.route('/move/<pgn>')
def get_move(pgn):
    print("Calculating...")
    # engine = Engine(fen)
    # move = engine.iterative_deepening(depth - 1)
    result=re.sub(r'[+]', '', pgn)
    start_chars = result[:2]
    end_chars = result[-2:]
    result1 = start_chars + end_chars
    # bot_move = make_move(re.sub(r'[A-Z]', '', pgn))
    bot_move = make_move(result1)

    
    print("5- Move found!", bot_move)
    data = {"move":bot_move}
    return bot_move


@app.route('/test/<string:tester>')
def test_get(tester):
    return tester

#! ====display route sign up=====
@app.route('/sign_in')
def sign():
    return render_template("sign_in.html")

@app.route('/sign_up')
def sign_up():
    return render_template("sign_up.html")

@app.route('/show')
def show():
    return render_template("show.html")

@app.route('/support')
def support():
    return render_template("support.html")

@app.route('/learn')
def learn():
    return render_template("learn.html")

@app.route('/explore')
def explore():
    return render_template("explore.html")

@app.route('/FAQ')
def FAQ():
    return render_template("FAQ.html")

@app.route('/tips')
def tips():
    if "counter" in session:
        session["counter"] += 10
    else:
        session["counter"]=0
    return render_template("tips.html")
@app.route('/tips2')
def tips2():
    if "counter" in session:
        session["counter"] += 10
    else:
        session["counter"]=0
    return render_template("tips2.html")
@app.route('/tips3')
def tips3():
    if "counter" in session:
        session["counter"] += 10
    else:
        session["counter"]=0
    return render_template("tips3.html")
@app.route('/tips4')
def tips4():
    if "counter" in session:
        session["counter"] += 10
    else:
        session["counter"]=0
    return render_template("tips4.html")



@app.route('/courses')
def courses():
    return render_template("courses.html")

@app.route('/courses2')
def courses2():
    return render_template("courses2.html")

@app.route('/courses3')
def courses3():
    return render_template("courses3.html")



if __name__ == '__main__':
    app.run(debug=True)