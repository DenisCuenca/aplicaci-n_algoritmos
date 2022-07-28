

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
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

# algoritmo de MVS
vectorizerMVS = pickle.load(open('modelos/vectorizerMVS.sav', 'rb'))
classifierMVS = pickle.load(open('modelos/classifierMVS.sav', 'rb'))
report = pickle.load(open('modelos/reportMVS.sav', 'rb'))

# algoritmo de Naive Bayes
vectorizerNB = pickle.load(open('modelos/vectorizerBN.sav', 'rb'))
classifierNB = pickle.load(open('modelos/classifierBN.sav', 'rb'))

# algoritmo de knn
vectorizerKnn = pickle.load(open('modelos/vectorizerKNN.sav', 'rb'))
classifierKnn = pickle.load(open('modelos/classifierKNN.sav', 'rb'))



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
    rknn = ''
    text = ''
    p_MVS = ''

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

            d = report[resultMVS[0]]
            p_MVS = round(d['precision'], 3)

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

                            
     # Algoritmo de kNN:

           

            classifierKnn.predict([[len("comentario positivo")]])[0]

            if resultNB[0] == 1:
                rknn = '   :)   '
            elif resultNB[0] == -1:
                rknn = '   :(   '
            elif resultNB[0] == 0:
                rknn = '   :|   '
            elif resultNB[0] == 2:
                rknn = '   x   '                 


                            
    s = [text, rmvs, rknn, rnb]
    p = [p_MVS]

    return render_template('index.html', data = s, p = p)


app.config["data"] = "./datos"

@app.route('/graficas', methods=['POST'])
def graficas():
    if request.method == 'POST':
        da = request.files['file']
        alg = request.form['tipo']


        filename = secure_filename(da.filename)
        da.save(os.path.join(app.config["data"], filename))        
        df = pd.read_csv('./datos/{}'.format(filename), header=None)
        df = df.assign(sentiment = None)

        if alg == 'VMS':

            for i in range (len(df[0])):
                text_vectorMVS = vectorizerMVS.transform([df[0][i]])
                df['sentiment'][i] = classifierMVS.predict(text_vectorMVS)[0]

        if alg == 'nb':  
            for i in range (len(df[0])):

                text_vectorNB = vectorizerNB.transform([df[0][i]])

                if (classifierNB.predict(text_vectorNB)[0]  == -1):
                    df['sentiment'][i] = 'N'
        
                elif (classifierNB.predict(text_vectorNB)[0]  == 1):
                    df['sentiment'][i] = 'P'
                    
                elif (classifierNB.predict(text_vectorNB)[0]  == 0):
                    df['sentiment'][i] = 'NEU'

                elif (classifierNB.predict(text_vectorNB)[0]  == 2):
                    df['sentiment'][i] = 'NONE'         




        if alg == 'knn':  
            for i in range (len(df[0])):
                
                
                

                if (classifierKnn.predict([[len(df[0][i])]])[0]  == -1):
                    df['sentiment'][i] = 'N'
        
                elif (classifierKnn.predict([[len(df[0][i])]])[0]  == 1):
                    df['sentiment'][i] = 'P'
                    
                elif (classifierKnn.predict([[len(df[0][i])]])[0]  == 0):
                    df['sentiment'][i] = 'NEU'

                elif (classifierKnn.predict([[len(df[0][i])]])[0]  == 2):
                    df['sentiment'][i] = 'NONE'  


        

        # Generación de grafica PASTEL CON PLT:
        l = ['N', 'P', 'NONE', 'NEU']
        num = []
        for i in l:
            k = 0
            for j in df['sentiment']:
                if i == j:
                    k+=1
            num.append(k)

        plt.clf() 
        
        img = io.BytesIO()        
        fig, ax = plt.subplots()
        #Colocamos una etiqueta en el eje Y
        ax.set_ylabel('sentimiento')
        #Colocamos una etiqueta en el eje X
        ax.set_title('Cantidad')
        #Creamos la grafica de barras utilizando 'paises' como eje X y 'ventas' como eje y.
        plt.bar(l, num)
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()



    # Generación de nube de palabras
        texto = ''
        for i in df[0]:
            texto += i +' '

        nube = io.BytesIO()  
        wordcloud = WordCloud(width = 300, height=260,background_color="white" ,
                        stopwords = stopwords.words('spanish'), 
                        min_word_length = 5, max_words=50).generate(texto) 
    
        plt.figure() 
        plt.imshow(wordcloud, interpolation="bilinear") 
        plt.axis("off") 
        plt.margins(x=6, y=6) 

        plt.savefig(nube, format='png')
        img.seek(0)
        plot_url_nube = base64.b64encode(nube.getvalue()).decode()


    return render_template('grafica.html', imagen={ 'imagen': plot_url }, imagen1={ 'imagen': plot_url_nube }, cantidad = num)



if __name__ == '__main__':
   app.run(debug =  True, port = 4000)