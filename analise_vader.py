import xml.etree.ElementTree as xml
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#inicializando VADER
svader = SentimentIntensityAnalyzer()

# Dada uma lista com as respostas, retorna uma lista com os valores de sentimento
# gerados pelo VADER
def analise_vader(respostas):
    return [ svader.polarity_scores(texto)['compound'] for texto in respostas ]