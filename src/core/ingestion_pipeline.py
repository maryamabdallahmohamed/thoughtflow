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
    text= re.sub("[*#]","").replace("\n"," ")
    text= re.sub("\n\n"," ")
    text= re.sub("\n"," ")
    text= re.sub("\n*"," ")
    

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
    Full pipeline: normalize, remove diacritics, segment, remove stopwords,
    and strip Farasa '+' symbols.
    """
    if not text or not text.strip():
        return ""
    try:
        # Normalize & clean
        text = normalize_arabic(text)
        text = remove_diacritics(text)

        # Use Farasa to segment
        segmented = farasa.segment(text)

        # Remove Farasa "+" markers
        segmented = segmented.replace("+", " ")

        # Tokenize
        tokens = segmented.split()

        # Stopword removal
        tokens = remove_stopwords(tokens)

        return " ".join(tokens)

    except Exception as e:
        print(f"[ERROR] Farasa failed on text: {text}\nReason: {e}")
        return text


def split_into_sentences(text: str) -> list:
    """
    Split Arabic text into sentences using common punctuation.
    """
    # Split on common sentence endings
    sentences = re.split(r'[.!?؟।\n]+', text)
    
    # Clean, filter, and remove extra symbols from each sentence
    sentences = [
        remove_extra_symbols(s.strip()) 
        for s in sentences 
        if s.strip() and len(s.strip()) > 10
    ]
    
    return sentences

def remove_extra_symbols(text: str) -> str:
    text = re.sub(r"[\[\]\*\n\.+،,:;”“\"\'\-–—_]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ingestion_pipeline(raw_texts):
    if isinstance(raw_texts, str):
        sentences = split_into_sentences(raw_texts)
        raw_texts = sentences

    processed = []
    for idx, t in enumerate(raw_texts):
        normalized = clean_and_segment(t)
        if normalized.strip():  
            processed.append({
                "index": idx,
                "original": t,
                "cleaned": normalized
            })
    return processed


# # 🔹 Example usage
# if __name__ == "__main__":
#     raw_samples = [
#         "وإلى اللقاء في القاهرةةة",
#         "اللغة العربية جميلة جداً!!!",
#         "كان هذا اختباراً للنظام."
#     ]

#     processed = ingestion_pipeline(raw_samples)
#     for original, cleaned in zip(raw_samples, processed):
#         print(f"Original: {original}")
#         print(f"Processed: {cleaned}")
