import xml.etree.ElementTree as xml
from dateutil.parser import parse
import datetime as dt
import re
import pickle
from analise_sentistrength import analise_sentistr
from analise_vader import analise_vader
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from lxml import etree

# ano, mes, dia
DATA_INICIO = dt.datetime(2014, 1, 1)
DATA_FIM = dt.datetime(2019, 12, 31)
ano_atual = 2014

def remove_tags(texto):
    '''
    REMOVE TAGS HTML, EXCESSO DE ESPAÇO, URLs, ETC..
    '''
    texto = re.sub(r"http\S+", "", texto) #remove sites
    texto = re.sub(r'@[\w]*', "", texto) #remove menções
    texto = re.sub(r"\s+", " ", texto) #remove \n
    texto = re.sub(r"\+", "", texto)
    texto = re.sub(r'<.*?>','',texto) #remove códigos entre <>
    texto = re.sub(r'<.*?"','',texto) #remove códigos entre <>
    texto = re.sub(r'&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});',' ',texto)
    texto = re.sub(r'(\[)|(\])',' ', texto) #remove colchetes
    texto = re.sub(r'(\()|(\))',' ', texto) #remove parenteses
    #texto = re.sub(r'[0-9]','',texto) #fazer teste com numero e sem numero
    texto = re.sub(' +', ' ', texto) #remove espaços em branco
    texto = re.sub(r'-','',texto) #remove hifen
    texto = re.sub(r'\'','',texto) #remove \'

    return texto

def dicionario_perguntas_respostas():
    global ano_atual 
    context = etree.iterparse('Posts.xml', events=('end',), tag='row')
    dicionario = {}
    processed = 0
    for event, elem in context:
        processed += 1
        data = parse(elem.get('CreationDate', None))
        if processed % 100000 == 0:
            print("Processing ...",processed)
            print(data)
        
        # Sai cedo caso a data não seja de interesse
        if data < DATA_INICIO or data > DATA_FIM:
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]     
            continue
        
        if data.year > ano_atual:
            with open(f'datadump_{ano_atual}.dicionario', 'wb') as f:
                pickle.dump(dicionario, f)
            dicionario.clear()
            ano_atual += 1

        id_post = int(elem.get('PostTypeId', None))
        id = int(elem.get('Id', None))

        resposta_aceita = None
        if id_post == 1: # questão
            resposta_aceita = elem.get('AcceptedAnswerId', None)
            if resposta_aceita is not None:
                resposta_aceita = int(resposta_aceita)
        elif id_post == 2: # resposta
            resposta_aceita = int(elem.get('ParentId', None))
            
        body = elem.get('Body', None) 
        limpeza_body = remove_tags(body)
        
        dicionario[id] = (id_post,data,resposta_aceita,limpeza_body)

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]        

    return dicionario

def gera_dados(perguntas_respostas):

    # lista com textos de todas as respostas
    respostas = []
    # lista com 1 para respostas aceitas e 0 para não aceitas
    objetivo = []

    for post in perguntas_respostas.items():
        id = post[0]
        dados = post[1]
        if dados[0] == 1:
            continue

        # Verifica se a resposta atual é uma resposta aceita:
        id_pai = dados[2]
        if id_pai not in perguntas_respostas:
            # Não tem como saber se essa resposta foi aceita, pulando ...
            continue

        if perguntas_respostas[id_pai][2] != None and perguntas_respostas[id_pai][2] == id:
            objetivo.append(1)
        else:
            objetivo.append(0)
        
        respostas.append(dados[3])
    
    assert(len(respostas) == len(objetivo))

    print(f"Desses, {len(respostas)} são respostas")
    print(f"{sum(objetivo)} são respostas aceitas")
    print("-"*10)

    # respostas = respostas[:1000]
    # objetivo = objetivo[:1000]

    vader_X = analise_vader(respostas)
    # TODO: resolver gambiarra
    vader_X = [ [x] for x in vader_X ]

    senti_X = analise_sentistr(respostas)
    # TODO: resolver gambiarra
    senti_X = [ [x] for x in senti_X ]
    y = objetivo

    # VADER

    X_train, X_test, y_train, y_test = train_test_split(vader_X, y, test_size=0.3 , stratify=y, random_state = 47)
    regr = LogisticRegression(class_weight = 'balanced')
    regr.fit(X_train, y_train)

    Y_predict = regr.predict(X_test)
    #print(Y_predict[:100])
    print("Accuracy VADER score is: ", accuracy_score(y_test, Y_predict))
    print("Precision VADER score is: ", precision_score(y_test, Y_predict))
    print("Recall VADER score is: ", recall_score(y_test, Y_predict))
    print("F1-SCORE VADER score is: ", f1_score(y_test, Y_predict))
    print("AUC VADER score is: ", roc_auc_score(y_test, Y_predict))
    print("-"*10)

    # # Testing RF on VADER
    # clf_vader = RandomForestClassifier(max_depth=2, random_state=54, class_weight='balanced')
    # clf_vader.fit(X_train, y_train)
    # print("VADER on RF classifier",clf_vader.score(X_test,y_test))
    # Y_predict = clf_vader.predict(X_test)
    # print("ROC VADER RF score is: ", roc_auc_score(y_test, Y_predict))
    
    print("-"*10)

    # Senti

    X_train, X_test, y_train, y_test = train_test_split(senti_X, y, test_size=0.3, random_state = 54)
    regr_senti = LogisticRegression(class_weight = 'balanced')
    regr_senti.fit(X_train, y_train)

    Y_predict = regr_senti.predict(X_test)
    #print(Y_predict[:100])
    print("Accuracy SentiStr score is: ", accuracy_score(y_test, Y_predict))
    print("Precision SentiStr score is: ", precision_score(y_test, Y_predict))
    print("Recall SentiStr score is: ", recall_score(y_test, Y_predict))
    print("F1-SCORE SentiStr score is: ", f1_score(y_test, Y_predict))
    print("AUC SentiStr score is: ", roc_auc_score(y_test, Y_predict))

    print("-"*10)

    # # Testing RF on SentiStr
    # clf_senti = RandomForestClassifier(max_depth=2, random_state=54, class_weight='balanced')
    # clf_senti.fit(X_train, y_train)
    # print("SENTI on RF classifier",clf_senti.score(X_test,y_test))
    # Y_predict = clf_senti.predict(X_test)
    # print("ROC SENTI RF score is: ", roc_auc_score(y_test, Y_predict))

if __name__ == "__main__":
    # dicionario = dicionario_perguntas_respostas()
    # with open(f'datadump_{ano_atual}.dicionario', 'wb') as f:
    #     pickle.dump(dicionario, f)
    with open('datadump_2017.dicionario', 'rb') as f:
        dicionario_2017 = pickle.load(f)
    with open('datadump_2018.dicionario', 'rb') as f:
        dicionario_2018 = pickle.load(f)
    dicionario = {**dicionario_2017, **dicionario_2018}
    print(f"Foram coletadas em 2017 e 2018 juntos {len(dicionario)} perguntas/respostas")
    print("-"*10)
    gera_dados(dicionario)