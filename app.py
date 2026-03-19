import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 Mon Terminal d'Analyste Financier 2026")

# 1. Sélection de l'entreprise (Ticker Yahoo Finance)
ticker_symbol = st.text_input("Entrez le Ticker (ex: AI.PA pour Air Liquide, MC.PA pour LVMH)", "AI.PA")
ticker = yf.Ticker(ticker_symbol)

# 2. Récupération des données
info = ticker.info
balance_sheet = ticker.balance_sheet
cash_flow = ticker.cashflow

# 3. Calcul des ratios clés
st.subheader("Indicateurs de Performance")
col1, col2, col3 = st.columns(3)

with col1:
    pe_ratio = info.get('trailingPE', 'N/A')
    st.metric("P/E Ratio", f"{pe_ratio:.2f}" if isinstance(pe_ratio, float) else "N/A")

with col2:
    # Calcul simplifié du Gearing (Dette Totale / Capitaux Propres)
    total_debt = balance_sheet.loc['Total Debt'][0]
    equity = balance_sheet.loc['Stockholders Equity'][0]
    gearing = total_debt / equity
    st.metric("Gearing", f"{gearing:.2%}")

with col3:
    # Calcul du Free Cash Flow Yield
    fcf = cash_flow.loc['Free Cash Flow'][0]
    mkt_cap = info.get('marketCap', 1)
    fcf_yield = fcf / mkt_cap
    st.metric("FCF Yield", f"{fcf_yield:.2%}")

# 4. Graphique du cours de bourse
st.subheader("Évolution du Cours")
hist = ticker.history(period="1y")
st.line_chart(hist['Close'])
