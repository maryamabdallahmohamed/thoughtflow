from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from embedder import Embedder  


if __name__ == "__main__":
    embedder = Embedder()


    texts = [
        "اللغة العربية جميلة.",
        "أحب قراءة الكتب كل يوم.",
        "الذكاء الاصطناعي يغير العالم.",
        "أدرس اللغة العربية في الجامعة.",
        "الكتب مصدر مهم للمعرفة.",
        "الذكاء الاصطناعي يساعد في الطب.",
        "أحب الذهاب إلى المكتبة."
    ]


    embeddings = embedder.encode(texts)

    # 🔹 Estimate clusters (here: 3 clusters → language/reading vs AI vs misc.)
    estimated_clusters = 3
    kmeans = KMeans(n_clusters=estimated_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    # 🔹 Silhouette Score
    silhouette_avg = silhouette_score(embeddings, labels)
    print(f"Silhouette Score: {silhouette_avg:.3f}")

    # Manual inspection threshold:
    if silhouette_avg > 0.5:
        print("✅ Excellent clustering — stick with pretrained.")
    elif 0.3 <= silhouette_avg <= 0.5:
        print("⚠️ Good clustering — consider fine-tuning if critical.")
    else:
        print("❌ Weak clustering — fine-tuning is recommended.")
