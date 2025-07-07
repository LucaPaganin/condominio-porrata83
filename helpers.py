import os, sys
import streamlit as st
import locale

locale.setlocale(locale.LC_ALL, '')

def format_currency(value):
    try:
        return locale.currency(value, grouping=True, symbol=False) + " €"
    except Exception:
        return f"{value:,.2f} €".replace(",", ".")


# Authentication function
def authenticate():
    # Bypass authentication if environment variable is set
    if st.secrets.get("condo_auth_bypass", False):
        return True

    # Initialize auth state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Show full-width login form if not authenticated
    if not st.session_state.authenticated:
        st.markdown(
            """
            <style>
            .block-container { max-width: 100vw !important; padding-left: 10vw; padding-right: 10vw; }
            header, footer {display: none !important;}
            </style>
            """, unsafe_allow_html=True
        )
        st.title("Login")
        st.markdown("<h3 style='text-align:center;'>Accesso riservato ai condomini</h3>", unsafe_allow_html=True)
        password = st.text_input("Inserisci la password", type="password")
        cols = st.columns(5)
        with cols[2]:
            if st.button("Accedi", use_container_width=True):
                if password == st.secrets.get("condo_password"):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Password errata. Controlla e riprova.")
        st.stop()
    return True


def calculate_millesimal_fractions(df):
    resdf = df[df["incluso"]][["nominativo e interno", "civico", "millesimi", "attico", "incluso"]]
    millesimi_tot = resdf["millesimi"].sum()
    millesimi_tetto = resdf[resdf["attico"]]["millesimi"].sum()

    def calculate_roof_fraction(row):
        if row["attico"]:
            return (1/3) * row["millesimi"] / millesimi_tetto
        else:
            return (2/3) * row["millesimi"] / (1000 - millesimi_tetto)
    
    def calculate_general_fraction(row):
        return row["millesimi"] / millesimi_tot if row["incluso"] else 0
    
    resdf["frazione_tetto"] = resdf.apply(calculate_roof_fraction, axis=1)
    resdf["frazione_generale"] = resdf.apply(calculate_general_fraction, axis=1)

    return resdf

def calculate_expenses(df, roof_expense, general_expense):
    df["spesa_tetto"] = df["frazione_tetto"] * roof_expense
    df["spesa_generale"] = df["frazione_generale"] * general_expense
    df["spesa_totale"] = df["spesa_tetto"] + df["spesa_generale"]

    df["interno"] = df["nominativo e interno"].str.split(";").str[0]
    df["nominativo"] = df["nominativo e interno"].str.split(";").str[1]

    
    pivot = df.pivot_table(
        index=["nominativo"],
        values=["millesimi", "spesa_tetto", "spesa_generale", "spesa_totale"],
        aggfunc="sum"
    ).reset_index()

    # Format currency columns
    for col in ['spesa_tetto', 'spesa_generale', 'spesa_totale']:
        pivot[col] = pivot[col].apply(format_currency)

    return pivot
