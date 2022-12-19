import json
import os

from spacy.lang.de.stop_words import STOP_WORDS
from spacy_iwnlp import spaCyIWNLP


class SentimentAnalyser:
    SENTIMENT_FILE = os.path.join(os.path.dirname(__file__), 'german_sentiment.json')
    LEMMA_FILE = os.path.join(os.path.dirname(__file__), 'IWNLP.Lemmatizer_20181001.json')

    def __init__(self, nlp):
        german_sentiment_file = open(SentimentAnalyser.SENTIMENT_FILE, "r", encoding="utf-8")
        self._dict = json.load(german_sentiment_file)
        self._nlp = nlp
        if 'spaCyIWNLP' not in [pipe[0] for pipe in nlp.pipeline]:
            iwnlp = spaCyIWNLP(lemmatizer_path=SentimentAnalyser.LEMMA_FILE)
            nlp.add_pipe(iwnlp)

    def lemmatize_iwnlp(self, texts: []):
        lemma_sentences = []
        pipelines = [pipe[0] for pipe in self._nlp.pipeline]
        for doc in self._nlp.pipe(texts, disable=[pipe for pipe in pipelines if pipe not in ['tagger', 'spaCyIWNLP']]):
            lemmas = [token._.iwnlp_lemmas[0] if token._.iwnlp_lemmas else token.text for token in doc]
            lemma_sentences.append(u' '.join(lemmas))
        return lemma_sentences

    def text(self, text: str):
        text = text.lower()
        lemma_text = self.lemmatize_iwnlp([text])
        words = [word.lower() for word in lemma_text[0].split() if word not in STOP_WORDS]
        word_scores = [self._dict.get(word, 0.0) for word in words]

        return float(sum(word_scores))
