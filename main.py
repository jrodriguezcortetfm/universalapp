from flask import Flask, render_template, request, redirect, url_for, session
from transformers import (
   AutoTokenizer,
   TFAutoModelForSequenceClassification,
)
import tensorflow as tf
import sys
import numpy as np
import sqlalchemy
from db import getconn

app = Flask(__name__)

app.secret_key = "3d6f45a5fc12445dbac2f59c3b6c7cb134" 

# Función que se encarga de realizar la predicción 
# se recibe el texto producto de la vectorización
# se devuelve el resultado del texto si es clasificado como positivo o negativo
def predict_model(input_text):
    # Lectura del mejor modelo
    tokenizer = AutoTokenizer.from_pretrained("model/tokenizer")
    model = TFAutoModelForSequenceClassification.from_pretrained("model/modelo")
    # Tokenizamos esa frase (encode)
    input_ids = tf.constant(tokenizer.encode(input_text, add_special_tokens=True))[None, :]
    # Predecimos
    pred = model.predict(input_ids)["logits"]
    # Indice del argumento máximo
    preds = np.argmax(pred,axis=1)
    # Resultado
    result = "Reseña positiva" if preds[0] == 1 else "Reseña negativa"
    return result

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password-field']
        pool = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )
        with pool.connect() as db_conn:
            # create ratings table in our sandwiches database
            login_query = sqlalchemy.text(
                "SELECT * from users "
                "WHERE users.email = :x "
                "AND users.password = :y "
                )
            
            result = db_conn.execute(login_query, {'x' : username, 'y' :password}).fetchall()
        if result:
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('index'))
        return render_template("login.html",error_message = "Usuario o password inválido")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)    
    return redirect(url_for('login'))

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        text = request.form['textpredict']
        predict_result = predict_model(text)
        if predict_result == "Reseña positiva":
            final_result = '<h4 >La reseña ha sido clasificada como: <b style="color:green !important">Positiva</b></h4>'
        else:
            final_result = '<h4 >La reseña ha sido clasificada como: <b style="color:red !important">Negativa</b></h4>'    
        return render_template("predict.html", result = final_result, review = text)
    return render_template("predict.html")