import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ditte Manutenzione", layout="wide")
st.title("Ditte di Manutenzione e Ristrutturazione")

csv_path = "./input_data/ditte.csv"
df = pd.read_csv(csv_path)

# Make 'Sito Web' column clickable
def make_clickable(val):
    if pd.isna(val) or not str(val).strip():
        return ""
    return f'<a href="{val}" target="_blank">{val}</a>'

if "Sito Web" in df.columns:
    df["Sito Web"] = df["Sito Web"].apply(make_clickable)

st.markdown(
    """
    <style>
    th, td { text-align: left !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("Elenco di aziende che offrono servizi di manutenzione, ristrutturazione e rifacimento tetti/cornicioni.")

st.write(
    df.to_html(escape=False, index=False),
    unsafe_allow_html=True
)

st.markdown("""
    <p style="text-align: center; font-size: 0.8em;">
        La ricerca corrispondente si trova [qui](https://www.perplexity.ai/search/fai-una-ricerca-di-ditte-che-e-0JjB5ESKS0CrJ48cSYlnLg).
    </p>
""", unsafe_allow_html=True)
