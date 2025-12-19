import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import os
import shutil # Serve per cancellare la cartella vecchia
from transformers import pipeline # La libreria di Hugging Face per il sentiment

def indicizza_dati():
    # 0. Pulizia: Cancelliamo il vecchio DB per ricrearlo con i nuovi dati (Sentiment)
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        print("🗑️ Vecchio database eliminato per aggiornamento.")

    # 1. Carichiamo i dati grezzi
    if not os.path.exists("notizie_scaricate.csv"):
        print("❌ Errore: File 'notizie_scaricate.csv' non trovato.")
        return

    df = pd.read_csv("notizie_scaricate.csv")
    df = df.dropna(subset=['testo']) # Rimuovi righe vuote
    
    # --- NOVITÀ: Inizializziamo il modello di Sentiment Analysis ---
    print("🧠 Caricamento modello Sentiment (potrebbe richiedere un attimo)...")
    # Usiamo un modello standard molto veloce
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    # 2. Setup ChromaDB
    client = chromadb.PersistentClient(path="./chroma_db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(name="notizie_globali", embedding_function=sentence_transformer_ef)

    # 3. Preparazione dati ARRICCHITI
    documents = []
    metadatas = []
    ids = []

    print("⚙️ Analisi del sentiment in corso per ogni articolo...")
    
    # Iteriamo riga per riga per calcolare il sentiment
    for index, row in df.iterrows():
        testo = row['testo']
        
        # L'AI calcola il sentiment (tronchiamo a 512 caratteri perché il modello ha un limite)
        result = sentiment_pipeline(testo[:512])[0] 
        sentiment_label = result['label'] # "POSITIVE" o "NEGATIVE"
        sentiment_score = result['score'] # Quanto è sicuro (da 0 a 1)

        documents.append(testo)
        ids.append(f"id_{index}")
        
        # Salviamo il sentiment nei metadati così possiamo recuperarlo dopo!
        metadatas.append({
            "fonte": row['fonte'],
            "titolo": row['titolo'],
            "link": row['link'],
            "sentiment": sentiment_label,
            "score": sentiment_score
        })

    # 4. Caricamento
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Finito! {len(documents)} articoli indicizzati con Sentiment Analysis.")

if __name__ == "__main__":
    indicizza_dati()