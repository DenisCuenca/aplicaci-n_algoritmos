

from asyncio import Task
from crypt import methods
import pickle
import os
from flask import Flask, jsonify, make_response, request, redirect
from flask import render_template, request
from werkzeug.utils import secure_filename
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

# algoritmo de MVS
vectorizerMVS = pickle.load(open('modelos/vectorizerMVS.sav', 'rb'))
classifierMVS = pickle.load(open('modelos/classifierMVS.sav', 'rb'))

# algoritmo de Naive Bayes
vectorizerNB = pickle.load(open('modelos/vectorizerBN.sav', 'rb'))
classifierNB = pickle.load(open('modelos/classifierBN.sav', 'rb'))



@app.route('/show-text', methods = ['POST'])
def analice():

    
    text = request.form['content']

    if text:
            
        # algoritmo de MVS
            
        text_vectorMVS = vectorizerMVS.transform([text])
        resultMVS = classifierMVS.predict(text_vectorMVS)
                                                
        if resultMVS[0] == 'P':
            rmvs = '   :)   '
        elif resultMVS[0] == 'N':
            rmvs = '   :(   '
        elif resultMVS[0] == 'NEU':
            rmvs = '   :|   '
        elif resultMVS[0] == 'NONE':
            rmvs = '   x   ' 

            # algoritmo de NB
        text_vectorNB = vectorizerNB.transform([text])
        resultNB = classifierNB.predict(text_vectorNB)
                                                
        if resultNB[0] == 1:
            rnb = '   :)   '
        elif resultNB[0] == -1:
            rnb = '   :(   '
        elif resultNB[0] == 0:
            rnb = '   :|   '
        elif resultNB[0] == 2:
            rnb = '   x   '                 

                        
        return make_response(jsonify({'sentiment': rmvs, 'text': text, 'Algorithm': 'MVS'},
                                            {'sentiment': rnb, 'text': text, 'Algorithm': 'NB'},
                                            {'sentiment': 'None', 'text': text, 'Algorithm': 'kNN'}))

            
    else:
        return make_response(jsonify({'error':'Lo siento ocurrio un errror', 'status_code':500}), 500)    

    





@app.route('/', methods=['GET', 'POST'])

def template_test():

    rmvs = ''
    rnb = ''
    text = ''

    if request.method == 'POST':
        text = request.form['content']    



        if text:
            
        # algoritmo de MVS
                
            text_vectorMVS = vectorizerMVS.transform([text])
            resultMVS = classifierMVS.predict(text_vectorMVS)
                                                    
            if resultMVS[0] == 'P':
                rmvs = '   :)   '
            elif resultMVS[0] == 'N':
                rmvs = '   :(   '
            elif resultMVS[0] == 'NEU':
                rmvs = '   :|   '
            elif resultMVS[0] == 'NONE':
                rmvs = '   x   ' 

                # algoritmo de NB
            text_vectorNB = vectorizerNB.transform([text])
            resultNB = classifierNB.predict(text_vectorNB)
                                                    
            if resultNB[0] == 1:
                rnb = '   :)   '
            elif resultNB[0] == -1:
                rnb = '   :(   '
            elif resultNB[0] == 0:
                rnb = '   :|   '
            elif resultNB[0] == 2:
                rnb = '   x   '                 

                            
    s = [text, rmvs, 'None', rnb]

    return render_template('index.html', data = s)


app.config["data"] = "./datos"

@app.route('/graficas', methods=['POST'])
def graficas():
    if request.method == 'POST':
        da = request.files['file']
        filename = secure_filename(da.filename)
        da.save(os.path.join(app.config["data"], filename))        
        df = pd.read_csv('./datos/{}'.format(filename), header=None)
        df = df.assign(sentiment = None)
        for i in range (len(df[0])):
            text_vectorMVS = vectorizerMVS.transform([df[0][i]])
            df['sentiment'][i] = classifierMVS.predict(text_vectorMVS)[0]
    

        # Generación de grafica:
        plt.clf() 
        img = io.BytesIO()
        
        img = io.BytesIO()        
        datos = df['sentiment'].value_counts().head(10).tolist()
        plt.pie(datos, autopct="%0.1f %%")
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('grafica.html', imagen={ 'imagen': plot_url })



if __name__ == '__main__':
   app.run(debug =  True, port = 4000)