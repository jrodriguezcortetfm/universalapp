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
    print('abrió archivo pickle de vectorización', file=sys.stderr)
    new_data_vec = vectorizer.transform([text])
    print('realizó la vectorización', file=sys.stderr)
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
    result = "Positivo" if prediction[0] == 1 else print("Negativa")
    return result

# Función que permite iniciar sesión al usuario
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password-field']
        print(request.form['username'], file=sys.stderr)
        print(request.form['password-field'], file=sys.stderr)
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
            print(result, file=sys.stderr)
        if result:
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('index'))
        return render_template("login.html",error_message = "Usuario o password inválido")
    return render_template("login.html")

# Función que realiza el logout del usuario
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)    
    return redirect(url_for('login'))

# Muestra el contenido de la página inicial
@app.route('/index')
def index():
    return render_template("index.html")

# Muestra el contenido de la sección de Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

# Permite ingresar el texto a predecir y obtener el resultado de la predicción
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    print(request.method, file=sys.stderr)
    if request.method == 'POST':
        text = request.form['textpredict']
        print(text, file=sys.stderr)
        data_vec = vectorizar(text)
        print('pasó vectorización',file=sys.stderr)
        predict_result = predict_model(data_vec)
        print(predict_result, file=sys.stderr)
        if predict_result == "Positivo":
            final_result = '<h4>La reseña ha sido clasificada como: <b style="color:green">Positiva</b></h4>'
        else:
            final_result = '<h4>La reseña ha sido clasificada como: <b style="color:red">Negativa</b></h4>'    
        print('resultados predict:',file=sys.stderr)
        print(final_result,file=sys.stderr)
        print(text,file=sys.stderr)
        return render_template("predict.html", result = final_result, review = text)
    return render_template("predict.html")

