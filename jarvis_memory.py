import chromadb
from chromadb.utils import embedding_functions
import os

# On s'assure que le dossier mémoire existe sur le disque externe
MEMORY_DIR = os.path.join(os.getcwd(), "memory")
if not os.path.exists(MEMORY_DIR): os.makedirs(MEMORY_DIR)

# Initialisation de la base de données (sur le disque)
chroma_client = chromadb.PersistentClient(path=MEMORY_DIR)

# On utilise un modèle léger pour transformer le texte en vecteurs
# all-MiniLM-L6-v2 est très rapide et tourne parfaitement en local
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Création (ou récupération) du bloc-notes principal
collection = chroma_client.get_or_create_collection(
    name="jarvis_core_memory",
    embedding_function=sentence_transformer_ef
)

def save_memory(fact, fact_id):
    """Sauvegarde un fait dans la mémoire."""
    collection.upsert(
        documents=[fact],
        ids=[fact_id] # Un ID unique pour ne pas créer de doublons (ex: "user_name")
    )
    print(f"🧠 Souvenir enregistré : {fact}")

def recall_memory(query, limit=2):
    """Recherche dans la mémoire les infos pertinentes par rapport à la question."""
    if collection.count() == 0:
        return ""
        
    results = collection.query(
        query_texts=[query],
        n_results=limit # On remonte les 2 souvenirs les plus proches
    )
    
    if results['documents'] and results['documents'][0]:
        memories = " ".join(results['documents'][0])
        return f"Souvenirs pertinents : {memories}"
    return ""

# Test rapide du module
if __name__ == "__main__":
    save_memory("Le projet actuel est de créer un système Jarvis local.", "current_project")
    print(recall_memory("Sur quoi travaillons-nous ?"))