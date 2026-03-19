import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
import json

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Analyste IA 2026", layout="wide")

# Récupération sécurisée de la clé API via les Secrets Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Clé API Gemini manquante dans les Secrets Streamlit.")

# --- FONCTIONS LOGIQUES ---

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    """Récupère les données avec gestion d'erreur Rate Limit"""
    try:
        t = yf.Ticker(ticker)
        return t.info
    except Exception as e:
        return None

def get_ai_analysis(info):
    """Prompt optimisé pour analyse sectorielle 2026"""
    prompt = f"""
    En tant qu'analyste CFA senior en mars 2026, analyse {info.get('longName')} 
    (Secteur: {info.get('sector')}, Industrie: {info.get('industry')}).
    
    Fournis UNIQUEMENT un JSON structuré avec ces clés exactes :
    {{
        "bench_roe": "valeur %",
        "bench_pe": "valeur x",
        "bench_gearing": "valeur x",
        "risk_score": 0 à 10 (10 = risque max),
        "analyse_courte": "avis stratégique 20 mots max",
        "verdict": "ACHAT/VENTE/CONSERVER"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Nettoyage du JSON reçu
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except:
        return None

# --- INTERFACE UTILISATEUR ---
st.title("🚀 Terminal d'Arbitrage IA - Édition 2026")

with st.sidebar:
    st.header("Analyseur")
    target_ticker = st.text_input("Ticker (ex: AI.PA, AAPL)", "AI.PA").upper()
    start_btn = st.button("Lancer l'audit complet")

if start_btn:
    with st.spinner("Extraction des données et consultation de l'IA..."):
        data = get_stock_data(target_ticker)
        
        if not data or 'longName' not in data:
            st.error("Erreur Yahoo Finance (Rate Limit). Réessayez dans 5 min ou changez de ticker.")
        else:
            ai_data = get_ai_analysis(data)
            
            # --- AFFICHAGE DES RÉSULTATS ---
            st.header(f"Rapport : {data.get('longName')}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Comparaison avec les Benchmarks IA")
                # On prépare les données pour le tableau
                comp_table = pd.DataFrame([
                    {"Indicateur": "ROE (%)", "Entreprise": f"{data.get('returnOnEquity',0)*100:.1f}%", "Secteur (IA)": ai_data.get('bench_roe')},
                    {"Indicateur": "P/E Ratio", "Entreprise": f"{data.get('trailingPE',0):.1f}x", "Secteur (IA)": ai_data.get('bench_pe')},
                    {"Indicateur": "Gearing", "Entreprise": f"{data.get('debtToEquity',0)/100:.2f}x", "Secteur (IA)": ai_data.get('bench_gearing')}
                ])
                st.table(comp_table)
            
            with col2:
                st.subheader("🛡️ Évaluation du Risque")
                score = ai_data.get('risk_score', 5)
                # Barre de progression couleur
                color = "green" if score < 4 else "orange" if score < 7 else "red"
                st.progress(score / 10)
                st.markdown(f"**Score de Risque : {score}/10**")
                
                st.subheader("💡 Verdict IA")
                st.code(ai_data.get('verdict', 'N/A'))
                st.write(ai_data.get('analyse_courte', ''))

            # Graphique final
            st.subheader("📈 Évolution du titre")
            st.line_chart(yf.Ticker(target_ticker).history(period="1y")['Close'])
