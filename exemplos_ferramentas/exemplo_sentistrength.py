from sentistrength import PySentiStr

#inicializando sentistrength
senti = PySentiStr()
senti.setSentiStrengthPath("SentiStrength.jar")
senti.setSentiStrengthLanguageFolderPath("SentiStrength_Data")

frase1 = senti.getSentiment('The food here is GREAT!!', score='dual')
frase2 = senti.getSentiment('The food here is GREAT!!', score='binary')
frase3 = senti.getSentiment('The food here is GREAT!!', score='trinary')
frase4 = senti.getSentiment('The food here is GREAT!!', score='scale')
print("Frase1 na saída dual:", frase1)
print("Frase2 na saída binary:", frase2)
print("Frase3 na saída trinary:", frase3)
print("Frase4 na saída scale:", frase4)





