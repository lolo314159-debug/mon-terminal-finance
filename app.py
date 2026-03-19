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
    """Interroge Gemini pour obtenir des benchmarks et une analyse"""
    prompt = f"""
    En tant qu'analyste financier senior, analyse cette entreprise : {ticker_info.get('longName')}.
    Secteur : {ticker_info.get('sector')}.
    Donne-moi UNIQUEMENT un objet JSON avec les moyennes de son secteur pour 2026 :
    {{
        "bench_roe": "valeur en %",
        "bench_pe": "valeur x",
        "bench_gearing": "valeur x",
        "analyse_risque": "une phrase courte sur le risque principal"
    }}
    """
    response = model.generate_content(prompt)
    try:
        # Nettoyage de la réponse pour ne garder que le JSON
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except:
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
