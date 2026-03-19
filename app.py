import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Terminal IA", layout="wide")

# --- CONNEXION GEMINI ---
# On utilise .strip() pour éviter qu'un espace caché dans les Secrets ne casse la clé
try:
    api_key = st.secrets["GEMINI_API_KEY"].strip()
    genai.configure(api_key=api_key)
    
    # SOLUTION AU MESSAGE "NOT FOUND" : 
    # On utilise le nom complet du modèle 'models/gemini-1.5-flash' 
    # ou 'gemini-pro' si le premier échoue.
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erreur de configuration : {e}")

# --- RÉCUPÉRATION YFINANCE ---
@st.cache_data(ttl=3600)
def get_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.info

# --- INTERFACE ---
st.title("📈 Analyse Financière & IA")

ticker = st.text_input("Ticker Yahoo Finance", "AI.PA").upper()

if st.button("Lancer l'analyse"):
    info = get_data(ticker)
    
    if info and 'longName' in info:
        st.header(f"{info['longName']}")
        
        # Affichage des données yfinance
        pe = info.get('trailingPE', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        
        col1, col2 = st.columns(2)
        col1.metric("P/E Ratio", f"{pe}")
        col2.metric("ROE", f"{roe}")

        # --- PARTIE GEMINI ---
        st.subheader("🤖 Interprétation de l'IA")
        
        # On construit un message simple
        prompt = f"Analyse cette action : {info['longName']}. Son P/E est de {pe} et son ROE est de {roe}. Donne un avis rapide."
        
        try:
            # Test d'appel direct
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            # Si gemini-1.5-flash échoue encore, on tente automatiquement gemini-pro
            st.warning("Tentative avec le modèle de secours (Gemini Pro)...")
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(prompt)
                st.write(response.text)
            except Exception as e2:
                st.error(f"Erreur Gemini persistante : {e2}")
                st.info("Vérifiez que votre clé API n'a pas de restrictions de région.")
    else:
        st.error("Données Yahoo introuvables pour ce ticker.")
