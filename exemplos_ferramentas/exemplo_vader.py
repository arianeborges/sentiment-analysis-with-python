from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

sentence1 = "The food here is GREAT!!"
sentence2 = "The food here is great."

senti1 = analyser.polarity_scores(sentence1)
senti2 = analyser.polarity_scores(sentence2)
print("Frase1:", senti1)
print("Frase2:", senti2)