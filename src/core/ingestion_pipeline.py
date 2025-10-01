import re
import stanza
import spacy
from nltk.corpus import stopwords
import nltk


# # NLTK stopwords RUN ONCE
# nltk.download("stopwords")
stopwords_ar = set(stopwords.words("arabic"))
stopwords_en = set(stopwords.words("english"))

# Stanza for Arabic
stanza.download("ar")
nlp_ar = stanza.Pipeline("ar", processors="tokenize,pos,lemma", verbose=False)

# SpaCy for English
nlp_en = spacy.load("en_core_web_sm")


def clean_text(text: str):
    text = text.strip()
    text = re.sub(r"[\n\t\r]+", " ", text)
    text = " ".join(re.findall(r"[ء-ي]+|[a-zA-Z]+", text))
    return text

def preprocess(text: str, lang="ar"):
    text = clean_text(text)
    if lang == "ar":
        doc = nlp_ar(text)
        tokens = [word.lemma for sent in doc.sentences for word in sent.words if word.lemma not in stopwords_ar]
    else:
        doc = nlp_en(text)
        tokens = [token.lemma_.lower() for token in doc if token.text.lower() not in stopwords_en]
    return " ".join(tokens)

