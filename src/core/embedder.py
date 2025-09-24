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
        return self.model.encode(text, batch_size=16,normalize_embeddings=True,device=DEVICE,convert_to_numpy=True)
