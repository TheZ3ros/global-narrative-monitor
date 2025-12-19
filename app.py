import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

# Configurazione della pagina (titolo tab browser, layout)
st.set_page_config(page_title="Global Narrative Monitor", layout="wide")

# TITOLO E INTRODUZIONE
st.title("🌍 Global Narrative Monitor")
st.markdown("""
Questa dashboard utilizza **Vector Embeddings** per cercare notizie basate sul **concetto** e non solo sulle parole chiave.
Analizza come diverse fonti (CNN, BBC, Al Jazeera) riportano gli stessi eventi.
""")

# --- FUNZIONI DI BACKEND (Con Caching) ---

# @st.cache_resource è FONDAMENTALE in Streamlit.
# Significa: "Esegui questa funzione una volta sola e tieni il risultato in memoria".
# Senza questo, ogni volta che clicchi un bottone, ricaricherebbe il modello AI (lento!).
@st.cache_resource
def load_db():
    client = chromadb.PersistentClient(path="./chroma_db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_collection(name="notizie_globali", embedding_function=sentence_transformer_ef)
    return collection

# Carichiamo il DB
try:
    collection = load_db()
    st.success("✅ Sistema AI caricato e pronto.", icon="🧠")
except Exception as e:
    st.error(f"Errore nel caricamento del DB: {e}. Hai eseguito processor.py?")
    st.stop()

# --- INTERFACCIA UTENTE (UI) ---

# Sidebar laterale per i filtri
with st.sidebar:
    st.header("⚙️ Impostazioni")
    n_results = st.slider("Numero di risultati", min_value=1, max_value=10, value=3)

# Barra di ricerca principale
query = st.text_input("Di cosa vuoi sapere oggi?", placeholder="Es: Tensioni in medio oriente, Crisi climatica...")

if st.button("Analizza Narrazione"):
    if not query:
        st.warning("Inserisci un testo per cercare.")
    else:
        with st.spinner('L\'AI sta analizzando i vettori semantici...'):
            # Eseguiamo la query sul Vector DB
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            st.divider()
            st.subheader(f"Risultati semantici per: '{query}'")
            
            # I risultati di Chroma sono liste di liste. Dobbiamo iterarli.
            # results['documents'][0] contiene la lista dei testi trovati
            num_found = len(results['documents'][0])
            
            # Usiamo le colonne per mostrare i risultati in modo ordinato
            # Se ci sono molti risultati, li mostriamo uno sotto l'altro
            for i in range(num_found):
                meta = results['metadatas'][0][i]
                text = results['documents'][0][i]
                source = meta['fonte']
                
                # Creiamo una "Card" visiva per ogni notizia
                with st.container():
                    # Intestazione con Fonte
                    emoji_fonte = "📰"
                    if "CNN" in source: emoji_fonte = "🇺🇸"
                    elif "BBC" in source: emoji_fonte = "🇬🇧"
                    elif "Al Jazeera" in source: emoji_fonte = "🇶🇦"
                    
                    st.markdown(f"### {emoji_fonte} {meta['titolo']}")
                    
                    # --- NOVITÀ: VISUALIZZAZIONE SENTIMENT ---
                    sentiment = meta['sentiment'] # POSITIVE o NEGATIVE
                    score = meta['score']
                    
                    # Colore dinamico
                    colore = "green" if sentiment == "POSITIVE" else "red"
                    emoji_mood = "😊" if sentiment == "POSITIVE" else "😠"
                    
                    # Mostriamo un badge
                    st.caption(f"Fonte: **{source}** | Sentiment: :{colore}[**{sentiment} {emoji_mood}**] ({score:.2f})")
                    # -----------------------------------------

                    st.info(text)
                    st.markdown(f"[Leggi articolo completo]({meta['link']})")
                    st.divider()