import re
from farasa import FarasaSegmenter   


farasa = FarasaSegmenter(interactive=True)

# Basic Arabic stopword list 
ARABIC_STOPWORDS = set([
    "في", "من", "على", "و", "الى", "إلى", "عن", "أن", "إن", "ما", "لا", 
    "لم", "لن", "قد", "كل", "كان", "كانت", "هو", "هي", "هم", "هن", 
    "هذا", "هذه", "ذلك", "تلك", "هناك", "هنا"
])

def normalize_arabic(text: str) -> str:
    """
    Basic normalization for Arabic text.
    """
    text = re.sub("[إأآا]", "ا", text)   # unify alef
    text = re.sub("ى", "ي", text)        # unify yaa
    text = re.sub("ؤ", "و", text)        # convert waw-hamza
    text = re.sub("ئ", "ي", text)        # convert yaa-hamza
    text = re.sub("ة", "ه", text)        # unify taa marbouta
    text = re.sub("ـ+", "", text)        # remove tatweel
    text = re.sub(r"(.)\1{2,}", r"\1", text)  # collapse elongations
    return text

def remove_diacritics(text: str) -> str:
    """
    Remove Arabic diacritics (tashkeel).
    """
    arabic_diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return re.sub(arabic_diacritics, '', text)

def remove_stopwords(words: list) -> list:
    """
    Remove common Arabic stopwords.
    """
    return [w for w in words if w not in ARABIC_STOPWORDS]

def clean_and_segment(text: str) -> str:
    """
    Full pipeline: normalize, remove diacritics, segment, remove stopwords.
    """
    if not text or not text.strip():
        return ""
    try:
        # Normalize & clean
        text = normalize_arabic(text)
        text = remove_diacritics(text)

        # Segment
        segmented = farasa.segment(text)

        # Stopword removal
        tokens = segmented.split()
        tokens = remove_stopwords(tokens)

        return " ".join(tokens)
    except Exception as e:
        print(f"[ERROR] Farasa failed on text: {text}\nReason: {e}")
        return text  # fallback

def ingestion_pipeline(raw_texts):
    """
    Ingests, cleans, and normalizes a list of texts.
    """
    processed = []
    for t in raw_texts:
        normalized = clean_and_segment(t)
        processed.append(normalized)
    return processed


# 🔹 Example usage
if __name__ == "__main__":
    raw_samples = [
        "وإلى اللقاء في القاهرةةة",
        "اللغة العربية جميلة جداً!!!",
        "كان هذا اختباراً للنظام."
    ]

    processed = ingestion_pipeline(raw_samples)
    for original, cleaned in zip(raw_samples, processed):
        print(f"Original: {original}")
        print(f"Processed: {cleaned}")
