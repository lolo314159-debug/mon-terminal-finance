import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Terminal Expert", layout="wide")

@st.cache_data(ttl=3600)
def get_full_data(symbol):
    try:
        t = yf.Ticker(symbol)
        return t.info
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    ticker = st.text_input("Ticker", "AI.PA").upper()
    analyze = st.button("Lancer le Diagnostic")

# --- LOGIQUE D'INTERPRÉTATION ---
def diagnostic(value, threshold, mode="sup"):
    if value == "N/A": return "⚪ Donnée manquante", "grey"
    if mode == "sup": # Plus c'est haut, mieux c'est (ex: ROE)
        if value > threshold: return "✅ Solide", "green"
        return "⚠️ À surveiller", "orange"
    else: # Plus c'est bas, mieux c'est (ex: Gearing)
        if value < threshold: return "✅ Sain", "green"
        return "🚨 Risqué", "red"

# --- AFFICHAGE ---
if analyze:
    data = get_full_data(ticker)
    if data:
        st.header(f"Analyse de {data.get('longName')} - {ticker}")
        
        # Préparation des ratios
        ratios = {
            "ROE (Rentabilité)": (data.get('returnOnEquity', 0) * 100, 15, "sup", "%"),
            "Gearing (Endettement)": (data.get('debtToEquity', 0) / 100, 1.2, "inf", "x"),
            "Marge Opé.": (data.get('operatingMargins', 0) * 100, 10, "sup", "%"),
            "P/E (Valorisation)": (data.get('trailingPE', 0), 20, "inf", "x"),
            "Current Ratio (Liquidité)": (data.get('currentRatio', 0), 1, "sup", "x")
        }

        # --- TABLEAU DE BORD (Le "Tableur" automatisé) ---
        st.subheader("📋 Tableau de Bord de l'Analyste")
        
        rows = []
        for name, (val, thresh, mode, unit) in ratios.items():
            status, color = diagnostic(val, thresh, mode)
            rows.append({
                "Indicateur": name,
                "Valeur": f"{val:.2f} {unit}" if isinstance(val, (int, float)) else "N/A",
                "Seuil Critique": f"{thresh} {unit}",
                "Verdict": status
            })
        
        df = pd.DataFrame(rows)
        st.table(df) # Utilisation de st.table pour le look "Spreadsheet"

        # --- INTERPRÉTATION GLOBALE ---
        st.markdown("---")
        st.subheader("🧐 Synthèse de l'Expert")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**Points Forts :**")
            if ratios["ROE (Rentabilité)"][0] > 15:
                st.write("- Capacité d'autofinancement élevée (ROE > 15%).")
            if ratios["Gearing (Endettement)"][0] < 1:
                st.write("- Structure financière saine, peu de dépendance à la dette.")
        
        with col2:
            st.warning("**Points de Vigilance :**")
            if ratios["P/E (Valorisation)"][0] > 25:
                st.write("- L'action semble chère payée par rapport aux bénéfices.")
            if ratios["Current Ratio (Liquidité)"][0] < 1:
                st.write("- Attention : l'entreprise pourrait manquer de cash à court terme.")

    else:
        st.error("Ticker non trouvé.")
