

from asyncio import Task
from crypt import methods
import pickle
import os
from flask import Flask, jsonify, make_response, request, url_for
from flask import render_template, request, redirect
from werkzeug.utils import secure_filename
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

    
app.config["data"] = "./datos"

@app.route('/', methods=['GET', 'POST'])

def home():

    return render_template('home.html')

@app.route('/columnas', methods=['POST'])
def columnas():
    if request.method == 'POST':
        da = request.files['file']
        filename = secure_filename(da.filename)
        da.save(os.path.join(app.config["data"], filename))
        df = pd.read_csv('./datos/{}'.format(filename))
        columnas = { 
            'columnas': df.columns.tolist(),
            'filename': filename
        }

        
        return render_template('generador.html', columnas=columnas)   

@app.route('/grafica', methods=['POST'])
def grafica():
    if request.method == 'POST':
        columna = request.form['columna']
        grafica = request.form['tipo']
        filename = request.form['filename']
        df = pd.read_csv('./datos/{}'.format(filename))[columna]
        
        plt.clf() 
        if grafica == 'puntos':
            img = io.BytesIO()
            plt.title("la grafica por: "+columna)
            plt.plot(df.head(10),'--')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('grafica.html', imagen={ 'imagen': plot_url })
        elif grafica == 'lineas':
            print('lineas')
            img = io.BytesIO()
            plt.title("la grafica por: "+columna)
            plt.plot(df.head(10))
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('grafica.html', imagen={ 'imagen': plot_url })
        elif grafica == 'pastel':
            img = io.BytesIO()
            plt.title("la grafica por: "+columna)
            datos = df.head(10).tolist()
            plt.pie(datos, autopct="%0.1f %%")
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('grafica.html', imagen={ 'imagen': plot_url })
        else:
            img = io.BytesIO()
            
            datos = df.head(10).tolist()
            for i in range(len(datos)):
                plt.bar(i, datos[i], align = 'center')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('grafica.html', imagen={ 'imagen': plot_url })



if __name__ == '__main__':
   app.run(debug =  True, port = 4000)