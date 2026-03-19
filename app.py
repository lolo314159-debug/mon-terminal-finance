import streamlit as st
import yfinance as yf
import google.generativeai as genai
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Terminal Analyste Simple", layout="wide")

# Connexion à Gemini (via Secrets Streamlit)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Configurez votre GEMINI_API_KEY dans les Secrets.")

# --- RÉCUPÉRATION DES DONNÉES ---
@st.cache_data(ttl=3600)
def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # On extrait manuellement les ratios pour être sûr de ce qu'on envoie à l'IA
        stats = {
            "Nom": info.get('longName'),
            "Secteur": info.get('sector'),
            "Prix": info.get('currentPrice'),
            "P/E Ratio": info.get('trailingPE'),
            "ROE": info.get('returnOnEquity'),
            "Dette/Equity": info.get('debtToEquity')
        }
        return stats
    except:
        return None

# --- INTERFACE ---
st.title("📊 Diagnostic Financier : Yahoo + Gemini")

ticker_input = st.text_input("Entrez un Ticker (ex: AI.PA, AAPL, MC.PA)", "AI.PA").upper()

if st.button("Lancer l'Analyse"):
    data = get_data(ticker_input)
    
    if data and data['Nom']:
        st.header(f"Rapport : {data['Nom']}")
        
        # Affichage des chiffres
        col1, col2, col3 = st.columns(3)
        col1.metric("P/E Ratio", f"{data['P/E Ratio']:.2f}x" if data['P/E Ratio'] else "N/A")
        col2.metric("ROE", f"{data['ROE']*100:.2f}%" if data['ROE'] else "N/A")
        col3.metric("Dette/Equity", f"{data['Dette/Equity']:.2f}" if data['Dette/Equity'] else "N/A")

        # Interprétation IA
        st.subheader("🤖 L'avis de l'Analyste IA")
        prompt = f"Analyse ces chiffres pour {data['Nom']} ({data['Secteur']}) : P/E {data['P/E Ratio']}, ROE {data['ROE']}, Dette {data['Dette/Equity']}. Est-ce un bon investissement en 2026 ? Réponds en 3 points courts."
        
        with st.spinner("L'IA réfléchit..."):
            try:
                response = model.generate_content(prompt)
                st.write(response.text)
            except:
                st.warning("Gemini n'a pas pu répondre. Vérifiez votre clé.")
    else:
        st.error("Données introuvables. Yahoo Finance bloque peut-être la requête (Rate Limit). Réessayez avec un autre ticker.")
