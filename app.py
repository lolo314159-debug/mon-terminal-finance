import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Terminal Pro 2026", layout="wide")

try:
    AV_KEY = st.secrets["AV_API_KEY"]
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # On utilise la version la plus stable du modèle
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ Configurer AV_API_KEY et GEMINI_API_KEY dans les Secrets Streamlit.")

# --- FETCH DATA ---
@st.cache_data(ttl=3600)
def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}'
    r = requests.get(url)
    return r.json() if "Symbol" in r.json() else None

# --- UI ---
st.title("⚖️ Arbitrage & Comparaison Stratégique")

with st.sidebar:
    st.header("Sélection")
    main_ticker = st.text_input("Action principale (ex: AAPL, AI.PAR)", "AAPL").upper()
    comp_ticker = st.text_input("Comparer avec (ex: MSFT, LIN)", "MSFT").upper()
    btn = st.button("Lancer l'Analyse Comparative")

if btn:
    with st.spinner("Audit en cours..."):
        data1 = get_stock_data(main_ticker)
        data2 = get_stock_data(comp_ticker)
        
        if data1 and data2:
            # --- SECTION 1 : MATCH FACE À FACE ---
            st.subheader(f"⚔️ {data1['Name']} vs {data2['Name']}")
            
            comp_df = pd.DataFrame({
                "Indicateur": ["Secteur", "P/E Ratio", "ROE", "Marge Profite"],
                data1['Symbol']: [data1['Sector'], data1['PERatio'], data1['ReturnOnEquityTTM'], data1['ProfitMargin']],
                data2['Symbol']: [data2['Sector'], data2['PERatio'], data2['ReturnOnEquityTTM'], data2['ProfitMargin']]
            })
            st.table(comp_df)

            # --- SECTION 2 : L'AVIS DE L'IA ---
            st.divider()
            prompt = f"Analyse le match financier entre {data1['Name']} et {data2['Name']}. Qui a le meilleur profil de risque en 2026 ? Réponds en 3 points clés."
            
            try:
                response = model.generate_content(prompt)
                st.subheader("🤖 Analyse Comparative de l'IA")
                st.info(response.text)
            except:
                st.warning("L'IA est momentanément indisponible.")
                
        else:
            st.error("Un des tickers est introuvable (ou limite API 5/min atteinte).")
