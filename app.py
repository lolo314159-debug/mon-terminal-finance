import streamlit as st
import yfinance as yf
import google.generativeai as genai
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Terminal AI Analyst", layout="wide")

# Configurez votre clé ici (ou via st.secrets en ligne)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
