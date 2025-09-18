from rag_pipeline import create_vector_store
from utils import load_json, ensure_dir

if __name__ == "__main__":
    ensure_dir("backend/data/faiss_index")
    data = load_json("backend/data/scraped_data.json")
    create_vector_store(data)
    print("✅ Embeddings and FAISS index created.")


