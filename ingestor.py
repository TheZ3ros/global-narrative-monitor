import feedparser
import pandas as pd
from datetime import datetime

# 1. Definiamo le fonti (Useremo RSS feed pubblici)
# Nota: Alcuni link RSS potrebbero cambiare nel tempo, questi sono solitamente stabili.
FONTI = {
    "CNN (US)": "http://rss.cnn.com/rss/edition_world.rss",
    "BBC (UK)": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Al Jazeera (Middle East)": "https://www.aljazeera.com/xml/rss/all.xml",
}

def scarica_notizie():
    print(f"📡 Inizio download notizie: {datetime.now()}")
    lista_articoli = []

    for nome_fonte, url in FONTI.items():
        print(f"   Scaricando da: {nome_fonte}...")
        try:
            # feedparser fa tutto il lavoro sporco di scaricare e leggere l'XML
            feed = feedparser.parse(url)
            
            # Prendiamo solo i primi 5 articoli per fonte per ora
            for entry in feed.entries[:5]:
                lista_articoli.append({
                    "fonte": nome_fonte,
                    "titolo": entry.title,
                    "link": entry.link,
                    # Alcuni feed mettono il riassunto in 'summary', altri in 'description'
                    "testo": entry.get('summary', entry.get('description', ''))
                })
        except Exception as e:
            print(f"⚠️ Errore con {nome_fonte}: {e}")

    # Creiamo un DataFrame (tabella) con i dati
    df = pd.DataFrame(lista_articoli)
    print(f"✅ Download completato. Trovati {len(df)} articoli.\n")
    return df

if __name__ == "__main__":
    # Questo blocco viene eseguito solo se lanci il file direttamente
    news_df = scarica_notizie()
    
    # Stampiamo le prime 3 righe per vedere se ha funzionato
    print(news_df.head(3))
    
    # Salviamo in un file CSV per comodità (così possiamo vederlo con Excel/Notepad)
    news_df.to_csv("notizie_scaricate.csv", index=False)
    print("📁 Dati salvati in 'notizie_scaricate.csv'")