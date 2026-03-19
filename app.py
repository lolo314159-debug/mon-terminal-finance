import streamlit as st
import yfinance as yf

# 1. On crée une fonction de récupération avec CACHE
@st.cache_data(ttl=3600) # Cache les données pendant 1h (3600 sec)
def get_financial_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # On ne demande que les infos essentielles pour éviter le ban
        return ticker.info, ticker.history(period="1y")
    except Exception as e:
        return None, None

st.title("📊 Terminal d'Analyste (Mode Sécurisé)")

symbol = st.text_input("Ticker (ex: AI.PA, MC.PA, AAPL)", "AI.PA")

# 2. Utilisation de la fonction cachée
info, hist = get_financial_data(symbol)

if info:
    st.success(f"Données chargées pour {info.get('longName')}")
    
    # Affichage des metrics
    col1, col2 = st.columns(2)
    col1.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
    col2.metric("Yield (%)", f"{info.get('dividendYield', 0)*100:.2f}%")
    
    st.line_chart(hist['Close'])
else:
    st.error("Erreur de récupération : Trop de requêtes. Attendez quelques minutes.")
