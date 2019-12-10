import xml.etree.ElementTree as xml
from sentistrength import PySentiStr

#inicializando sentistrength
sstrength = PySentiStr()
sstrength.setSentiStrengthPath("SentiStrength.jar")
sstrength.setSentiStrengthLanguageFolderPath("SentiStrength_Data")

# Dada uma lista com as respostas, retorna uma lista com os valores de sentimento
# gerados pelo SentiStr
def analise_sentistr(respostas):
    return sstrength.getSentiment( respostas )