import re
import stanza
import spacy
from nltk.corpus import stopwords
import nltk


nltk.download("stopwords")

stopwords_ar = set(stopwords.words("arabic"))
stopwords_en = set(stopwords.words("english"))

# Load Stanza (Arabic)
stanza.download("ar")
nlp_ar = stanza.Pipeline("ar", processors="tokenize,pos,lemma", verbose=False)

# Load SpaCy (English)
nlp_en = spacy.load("en_core_web_sm")

# --- POS tags to keep ---
# (Focus on content words: nouns, verbs, adjectives, adverbs)
KEEP_TAGS_AR = {"NOUN", "VERB", "ADJ", "ADV"}
KEEP_TAGS_EN = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}


def clean_text(text: str):
    """Basic text normalization and character filtering."""
    text = text.strip()
    text = re.sub(r"[\n\t\r]+", " ", text)
    text = " ".join(re.findall(r"[ء-ي]+|[a-zA-Z]+", text))
    return text


def preprocess(text: str, lang="ar"):
    """Full preprocessing pipeline: clean, lemmatize, POS-filter, remove stopwords."""
    text = clean_text(text)

    if lang == "ar":
        doc = nlp_ar(text)
        tokens = []
        for sent in doc.sentences:
            for word in sent.words:
                if (
                    word.upos in KEEP_TAGS_AR
                    and word.lemma not in stopwords_ar
                    and len(word.lemma) > 1
                ):
                    tokens.append(word.lemma)
    else:
        doc = nlp_en(text)
        tokens = [
            token.lemma_.lower()
            for token in doc
            if (
                token.pos_ in KEEP_TAGS_EN
                and token.text.lower() not in stopwords_en
                and len(token.lemma_) > 1
            )
        ]

    return " ".join(tokens)

