from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle
import sys
import sqlalchemy
from db import getconn

app = Flask(__name__)

app.secret_key = "3d6f45a5fc12445dbac2f59c3b6c7cb122" 

# Función que se encarga de aplizar TfidfVectorizer sobre el texto 
# se recibe el texto enviado por el usuario
# se devuelve la sparse matrix asociada
def vectorizar(text):
    # Lectura del vectorizador 
    vectorizer = pickle.load(open('pickle/tfidf.pkl', 'rb'))
    # Transformación del texto de entrada
    new_data_vec = vectorizer.transform([text])
    return new_data_vec

# Función que se encarga de realizar la predicción 
# se recibe el texto producto de la vectorización
# se devuelve el resultado del texto si es clasificado como positivo o negativo
def predict_model(data_vec):
    # Lectura del mejor modelo
    loaded_model = pickle.load(open('pickle/machine_learning_best_model.pkl', 'rb'))
    # Predicción
    prediction = loaded_model.predict(data_vec)
    # Resultado
    result = "Reseña positiva" if prediction[0] == 1 else "Reseña negativa"
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
        data_vec = vectorizar(text)
        predict_result = predict_model(data_vec)
        if predict_result == "Reseña positiva":
            final_result = '<h4 >La reseña ha sido clasificada como: <b style="color:green !important">Positiva</b></h4>'
        else:
            final_result = '<h4 >La reseña ha sido clasificada como: <b style="color:red !important">Negativa</b></h4>'    
        return render_template("predict.html", result = final_result, review = text)
    return render_template("predict.html")