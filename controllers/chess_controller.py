from flask_app import app
from flask import Flask,render_template,redirect,request,session,flash,jsonify
import chess
# from ...utils import make_move
import torch
import re
# from chess_engine import *
# from ...utils import *




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
 
    start_chars = pgn[:2]
    end_chars = pgn[-2:]
    result = start_chars + end_chars
    # bot_move = make_move(re.sub(r'[A-Z]', '', pgn))
    bot_move = make_move(result)

    
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
