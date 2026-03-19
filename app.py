import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd
import json

st.set_page_config(page_title="Terminal Analyste Pro", layout="wide")

# --- CONFIGURATION API ---
try:
    AV_KEY = st.secrets["AV_API_KEY"]
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # On utilise 'gemini-pro', souvent plus robuste au déploiement initial
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error("Erreur de configuration des clés API dans les Secrets.")

# --- DATA FETCHING (Alpha Vantage) ---
@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    # Alpha Vantage supporte mieux les tickers sans suffixe pour le NASDAQ/NYSE
    # ou avec .PAR pour Paris.
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}'
    response = requests.get(url)
    data = response.json()
    if "Symbol" in data:
        return data
    return None

# --- AI ANALYSIS ---
def get_ai_insight(stock_info):
    prompt = f"""
    Analyse l'entreprise {stock_info.get('Name')} ({stock_info.get('Sector')}).
    Réponds UNIQUEMENT en JSON avec ce format exact :
    {{
        "bench_pe": "valeur",
        "bench_roe": "valeur",
        "risque": "bas/moyen/haut",
        "verdict": "ACHAT/VENTE/GARDE"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Nettoyage pour ne garder que le JSON
        res_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(res_text)
    except:
        return None

# --- UI ---
st.title("🚀 Terminal d'Arbitrage Final")

ticker = st.text_input("Entrez un Ticker (ex: AAPL, AI.PAR, MC.PAR)", "AAPL").upper()

if st.button("Lancer l'Audit"):
    with st.spinner("Interrogation des API sécurisées..."):
        data = get_stock_data(ticker)
        
        if data:
            ai = get_ai_insight(data)
            
            st.header(f"Analyse de {data['Name']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📊 Ratios Réels (Source: Alpha Vantage)")
                pe = data.get('PERatio', 'N/A')
                roe = data.get('ReturnOnEquityTTM', 'N/A')
                st.metric("P/E Ratio", f"{pe}x")
                st.metric("ROE", f"{roe}")
            
            with c2:
                if ai:
                    st.subheader("🤖 Diagnostic IA")
                    st.write(f"**Verdict :** {ai['verdict']}")
                    st.write(f"**Risque :** {ai['risque']}")
                    st.write(f"**Benchmark P/E Secteur :** {ai['bench_pe']}")
                else:
                    st.warning("L'IA n'a pas pu générer le diagnostic. Vérifiez votre quota Gemini.")
        else:
            st.error("Impossible de trouver ce ticker ou limite d'appels Alpha Vantage atteinte (5/min).")
