import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd
import json
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Terminal Pro 2026", layout="wide")

# Chargement sécurisé des clés
try:
    AV_KEY = st.secrets["AV_API_KEY"]
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Utilisation du nom de modèle le plus universel
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ Erreur : Vérifiez AV_API_KEY et GEMINI_API_KEY dans vos Secrets Streamlit.")

# --- FETCH DATA (Alpha Vantage) ---
@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}'
    r = requests.get(url)
    data = r.json()
    
    # Gestion de la limite d'API (5/min)
    if "Note" in data:
        st.warning("⏳ Limite API Alpha Vantage atteinte (5/min). Patientez 60 secondes...")
        return "LIMIT"
    return data if "Symbol" in data else None

# --- UI ---
st.title("🛡️ Terminal d'Analyse Robuste")
st.info("💡 Rappel : 5 recherches max par minute (version gratuite Alpha Vantage).")

with st.sidebar:
    ticker = st.text_input("Action (ex: AAPL, AI.PAR, MC.PAR)", "AAPL").upper()
    btn = st.button("Lancer l'Audit")

if btn:
    with st.spinner("Consultation des bases de données..."):
        data = get_stock_data(ticker)
        
        if data == "LIMIT":
            st.info("Veuillez cliquer de nouveau sur le bouton dans une minute.")
        elif data:
            st.header(f"Rapport : {data['Name']}")
            
            # --- BLOC CHIFFRES ---
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Ratios de Marché")
                # On gère les valeurs potentiellement vides (None)
                pe = data.get('PERatio', 'N/A')
                roe = data.get('ReturnOnEquityTTM', 'N/A')
                st.metric("P/E Ratio", f"{pe}x")
                st.metric("ROE", roe)

            # --- BLOC IA ---
            with col2:
                st.subheader("🤖 Diagnostic IA")
                prompt = f"Analyse {data['Name']} ({data['Sector']}). Verdict 2026 : Acheter, Vendre ou Conserver ? 2 phrases max."
                try:
                    response = model.generate_content(prompt)
                    st.success(response.text)
                except Exception as e:
                    st.error("L'IA n'a pas pu répondre. Vérifiez si votre clé Gemini est active.")
        else:
            st.error("Ticker inconnu ou erreur serveur. Essayez AI.PAR pour Air Liquide.")
