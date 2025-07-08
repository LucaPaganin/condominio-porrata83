
from pathlib import Path
import uuid
import streamlit as st
from helpers import plot_barplot, plot_treemap, increment_visit_counter, log_visit_to_cosmos
from pages.tabella_millesimale import resdf
from helpers import format_currency, authenticate, calculate_expenses


# Hide Streamlit sidebar on first load
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)



# Track visits (file and CosmosDB)
# Collect session data for CosmosDB
session_data = {}
try:
    session_data["headers"] = dict(st.context.headers)
except Exception:
    session_data["headers"] = {}
session_data["query_params"] = st.query_params
session_data["session_id"] = st.session_state.get("_session_id", str(uuid.uuid4()))
session_data["user_agent"] = session_data["headers"].get("User-Agent")
log_visit_to_cosmos(session_data)

# Run authentication
if not authenticate():
    st.stop()


# Main App
st.title("Ripartizione millesimale spese straordinarie")

st.warning(
    """
    **Attenzione:** questa applicazione è destinata esclusivamente ai condomini di via Porrata 83.
    L'accesso non autorizzato è vietato e perseguito a norma di legge.
    """
)
st.markdown(
    Path("./disclaimer.md").read_text(encoding="utf-8"),
    unsafe_allow_html=True
)

roof_expense = st.number_input(
    f"Spesa per il tetto",
    min_value=0, step=100, 
    format="%d", value=int(2.04e5),
    help="1/3 a carico degli attici, normalizzati in base ai millesimi degli attici, 2/3 a carico degli altri, normalizzati in base ai millesimi degli altri"
)
other_expense = st.number_input(
    f"Cornicione e altre spese",
    min_value=0, step=100,
    format="%d", value=0,
    help="queste spese sono a carico di tutti i condomini, normalizzati in base ai millesimi di tutti"
)

# IVA checkbox
iva_included = st.checkbox("IVA inclusa", value=False, help="Seleziona se le spese includono l'IVA al 10%")
iva_val = 0.10
# Apply IVA if not included
roof_expense = roof_expense if iva_included else roof_expense * (1 + iva_val)
other_expense = other_expense if iva_included else other_expense * (1 + iva_val)

if st.button("Calcola ripartizione spese"):
    st.subheader("Risultati")
    st.write(f"Spesa tetto (con IVA): {format_currency(roof_expense)}")
    st.write(f"Altre spese (con IVA): {format_currency(other_expense)}")
    total_expense = roof_expense + other_expense
    st.write(f"Totale spese condominiali: {format_currency(total_expense)}")

    st.write("### Ripartizione delle spese per unità immobiliare")
    st.write("Le spese sono calcolate in base ai millesimi di proprietà.")
    expenses_df = calculate_expenses(resdf, roof_expense, other_expense)

    st.dataframe(expenses_df, use_container_width=True)

    plot_treemap(expenses_df)
            

    

