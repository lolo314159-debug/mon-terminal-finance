import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Terminal Pro 2026", layout="wide")

# Récupération des clés dans les Secrets
AV_KEY = st.secrets["AV_API_KEY"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- FONCTION : DONNÉES RÉELLES (Alpha Vantage) ---
@st.cache_data(ttl=3600)
def get_hard_data(symbol):
    # Alpha Vantage utilise des tickers US ou globaux (ex: AI.PAR pour Air Liquide)
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}'
    r = requests.get(url)
    data = r.json()
    return data if data and "Name" in data else None

# --- FONCTION : ANALYSE IA (Gemini) ---
def get_ai_diagnostic(data):
    prompt = f"""
    Analyse cette entreprise : {data.get('Name')}. 
    Secteur : {data.get('Sector')}.
    Donne-moi UNIQUEMENT un JSON :
    {{
        "bench_roe": "moyenne %",
        "bench_pe": "moyenne x",
        "bench_gearing": "moyenne x",
        "verdict": "ACHAT/VENTE",
        "risque_score": 0-10
    }}
    """
    response = model.generate_content(prompt)
    try:
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except: return None

# --- INTERFACE ---
st.title("🛡️ Terminal d'Arbitrage (Flux API Sécurisé)")

with st.sidebar:
    # Note : Alpha Vantage demande souvent .PAR au lieu de .PA pour Paris
    ticker = st.text_input("Ticker (ex: AAPL, MC.PAR, AI.PAR)", "AAPL")
    btn = st.button("Lancer l'Analyse")

if btn:
    with st.spinner("Récupération via API officielle..."):
        stock_data = get_hard_data(ticker)
        
        if stock_data:
            ai_data = get_ai_diagnostic(stock_data)
            
            st.header(f"Rapport Financier : {stock_data['Name']}")
            
            # --- TABLEAU COMPARATIF ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Extraction des ratios (Alpha Vantage donne des strings, on les convertit)
                roe = float(stock_data.get('ReturnOnEquityTTM', 0)) * 100
                pe = float(stock_data.get('PERatio', 0))
                debt = float(stock_data.get('DebtToEquityRatio', 0))
                
                df = pd.DataFrame([
                    {"Ratio": "ROE", "Valeur": f"{roe:.2f}%", "Secteur (IA)": ai_data['bench_roe']},
                    {"Ratio": "P/E", "Valeur": f"{pe:.2f}x", "Secteur (IA)": ai_data['bench_pe']},
                    {"Ratio": "Dette/Equity", "Valeur": f"{debt:.2f}x", "Secteur (IA)": ai_data['bench_gearing']}
                ])
                st.table(df)
            
            with col2:
                st.metric("Verdict", ai_data['verdict'])
                st.write(f"**Score de Risque :** {ai_data['risque_score']}/10")
                st.progress(ai_data['risque_score']/10)
        else:
            st.error("Ticker non trouvé ou limite d'appels API atteinte (5/min pour la version gratuite Alpha Vantage).")
