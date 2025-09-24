from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
load_dotenv()

DEVICE= os.getenv("DEVICE")
CACHE_DIR = os.getenv("CACHE_DIR")
class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/gtr-t5-base',
                                         device=DEVICE,
                                         cache_folder=CACHE_DIR)
    def encode(self,text):
        return self.model.encode(text)



if __name__ == "__main__":
    embedder = Embedder()
    
    # 🔹 Arabic sentences to test
    sentences = [
        "اللغة العربية جميلة.",
        "أحب قراءة الكتب كل يوم.",
        "الذكاء الاصطناعي يغير العالم."
    ]
    
    for s in sentences:
        embedding = embedder.encode(s)
        print(f"Sentence: {s}")
        print(f"Embedding (first 5 dims): {embedding[:5]}\n")