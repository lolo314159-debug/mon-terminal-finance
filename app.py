import streamlit as st
import yfinance as yf
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Terminal d'Analyse Financière", layout="wide")

st.title("📊 Terminal d'Analyste : Performance & Valorisation")
st.markdown("---")

# 1. Fonction de récupération des données avec CACHE (évite le ban IP)
@st.cache_data(ttl=3600)
def get_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # On récupère tout en un seul appel pour limiter les requêtes
        info = ticker.info
        hist = ticker.history(period="2y") # 2 ans pour voir la tendance
        # Pour les ratios complexes, on peut extraire le bilan si besoin :
        # balance = ticker.balance_sheet
        return info, hist
    except Exception as e:
        return None, None

# 2. Formulaire de recherche (Sécurité anti-spam)
with st.sidebar:
    st.header("Paramètres")
    with st.form("search_form"):
        ticker_input = st.text_input("Ticker Yahoo Finance", value="AI.PA")
        submit_button = st.form_submit_button("Lancer l'Analyse")
    
    st.info("💡 Indices Tickers :\n- Air Liquide : AI.PA\n- LVMH : MC.PA\n- Apple : AAPL\n- Total : TTE.PA")

# 3. Affichage des résultats
if submit_button:
    info, hist = get_data(ticker_input)
    
    if info and not hist.empty:
        # --- HEADER ---
        st.header(f"{info.get('longName', ticker_input)} ({info.get('currency', 'EUR')})")
        
        # --- BLOC 1 : VALORISATION ---
        st.subheader("1. Valorisation & Marché")
        col1, col2, col3, col4 = st.columns(4)
        
        pe = info.get('trailingPE', 'N/A')
        yield_div = info.get('dividendYield', 0) * 100
        mkt_cap = info.get('marketCap', 0) / 1e9 # En Milliards
        
        col1.metric("P/E Ratio", f"{pe:.2f}" if isinstance(pe, (int, float)) else "N/A")
        col2.metric("Rendement (Yield)", f"{yield_div:.2f} %")
        col3.metric("Capit. Boursière", f"{mkt_cap:.2f} Md")
        col4.metric("Prix Actuel", f"{info.get('currentPrice', 'N/A')} {info.get('currency', '')}")

        # --- BLOC 2 : RENTABILITÉ & STRUCTURE ---
        st.subheader("2. Santé Financière & Rentabilité")
        c1, c2, c3 = st.columns(3)
        
        roe = info.get('returnOnEquity', 0) * 100
        margin = info.get('ebitdaMargins', 0) * 100
        # Levier financier simplifié (Dette/Equité)
        debt_to_equity = info.get('debtToEquity', 'N/A')
        
        c1.metric("ROE (Rentabilité FP)", f"{roe:.2f} %")
        c2.metric("Marge EBITDA", f"{margin:.2f} %")
        c3.metric("Ratio d'endettement", f"{debt_to_equity}" if debt_to_equity == 'N/A' else f"{debt_to_equity:.2f}")

        # --- BLOC 3 : GRAPHIQUE ---
        st.subheader("3. Historique du Cours (2 ans)")
        st.line_chart(hist['Close'])
        
        # --- BLOC 4 : RÉSUMÉ ANALYSTE ---
        with st.expander("Voir le profil de l'entreprise"):
            st.write(info.get('longBusinessSummary', "Pas de résumé disponible."))
            
    else:
        st.error("Impossible de récupérer les données. Vérifiez le Ticker ou attendez quelques minutes (Limite API Yahoo).")

else:
    st.write("👈 Entrez un Ticker dans la barre latérale et cliquez sur 'Lancer l'Analyse'.")
