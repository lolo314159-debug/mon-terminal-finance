import streamlit as st
import yfinance as yf
import google.generativeai as genai
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Terminal AI Analyst", layout="wide")

# Configurez votre clé ici (ou via st.secrets en ligne)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')import streamlit as st
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

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    t = yf.Ticker(ticker)
    return t.info

def get_ai_insight(ticker_info):
    """Interroge Gemini avec un prompt structuré pour éviter les hallucinations"""
    
    # On prépare les données réelles pour nourrir l'IA
    nom = ticker_info.get('longName')
    secteur = ticker_info.get('sector')
    industrie = ticker_info.get('industry')
    
    prompt = f"""
    CONTEXTE : Nous sommes en mars 2026. Tu es un analyste financier expert (CFA).
    ENTREPRISE : {nom} (Secteur: {secteur}, Industrie: {industrie}).
    
    MISSION : Fournis des benchmarks sectoriels précis pour cette industrie en 2026.
    
    RÈGLES STRICTES :
    1. Réponds UNIQUEMENT au format JSON.
    2. Ne commente pas, ne salue pas.
    3. Si une donnée est incertaine, fournis une estimation basée sur les leaders du secteur.
    
    STRUCTURE JSON ATTENDUE :
    {{
        "bench_roe": "moyenne en %",
        "bench_pe": "multiple moyen x",
        "bench_gearing": "ratio moyen Dette/Equity",
        "bench_fcf_margin": "marge de Free Cash Flow moyenne en %",
        "analyse_dividende": "avis court sur la pérennité du dividende",
        "risk_score": "note de 1 à 10 du risque de refinancement en 2026",
        "verdict_ia": "Acheter/Conserver/Vendre (expliquer en 10 mots)"
    }}
    """
    
    response = model.generate_content(prompt)
    try:
        # Nettoyage du texte pour extraire le JSON proprement
        res_text = response.text.strip()
        if "```json" in res_text:
            res_text = res_text.split("```json")[1].split("```")[0]
        return json.loads(res_text)
    except Exception as e:
        st.error(f"Erreur d'analyse IA : {e}")
        return None

# --- INTERFACE ---
st.title("🤖 Terminal Financier Augmenté par l'IA")

with st.sidebar:
    ticker = st.text_input("Ticker Yahoo Finance", "AI.PA").upper()
    btn = st.button("Lancer le Diagnostic IA")

if btn:
    with st.spinner("L'IA analyse le secteur..."):
        data = get_stock_data(ticker)
        ai_data = get_ai_insight(data)
        
        if data and ai_data:
            st.header(f"Analyse de {data.get('longName')}")
            
            # --- LE TABLEAU COMPARATIF DYNAMIQUE ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Comparaison Réelle vs Secteur (IA)")
                df_comp = pd.DataFrame([
                    {"Indicateur": "ROE (%)", "Entreprise": f"{data.get('returnOnEquity',0)*100:.2f}%", "Moyenne Secteur (IA)": ai_data['bench_roe']},
                    {"Indicateur": "P/E Ratio", "Entreprise": f"{data.get('trailingPE',0):.2f}x", "Moyenne Secteur (IA)": ai_data['bench_pe']},
                    {"Indicateur": "Gearing", "Entreprise": f"{data.get('debtToEquity',0)/100:.2f}x", "Moyenne Secteur (IA)": ai_data['bench_gearing']}
                ])
                st.table(df_comp)
            
            with col2:
                st.subheader("🚩 Diagnostic IA")
                st.warning(ai_data['analyse_risque'])
                
            # --- GRAPH ---
            st.line_chart(yf.Ticker(ticker).history(period="1y")['Close'])
