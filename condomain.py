
import streamlit as st
from helpers import plot_barplot, plot_treemap
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

# Run authentication
if not authenticate():
    st.stop()

# Main App
st.title("Calcolo ripartizione lavori straordinari via Porrata 83")

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
            

    

