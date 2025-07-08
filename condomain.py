from pathlib import Path
import uuid
import streamlit as st
from streamlit_js_eval import get_page_location, get_browser_language
from pages.tabella_millesimale import resdf
try:
    from helpers import (
        format_currency, 
        plot_barplot, plot_treemap, log_visit_to_cosmos,
        authenticate, 
        calculate_expenses, 
        collect_session_data
    )
except ImportError:
    import traceback
    print(traceback.format_exc())


# Hide Streamlit sidebar on first load
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True
)

session_data = collect_session_data()
if "streamlit_user" in session_data and session_data["streamlit_user"]:
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
with st.expander("Informazioni sull'applicazione", expanded=True):
    st.markdown(
        Path("./input_data/disclaimer.md").read_text(encoding="utf-8"),
        unsafe_allow_html=True
    )

cols = st.columns(2)
with cols[0]:
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

with cols[1]:
    mdcontent = Path("./input_data/notes.md").read_text(encoding="utf-8")
    try:
        base_url = get_page_location()["origin"]
    except Exception:
        base_url = ""
    ditte_url = f"{base_url.rstrip('/')}/ditte_manutenzione" if base_url else "ditte_manutenzione"
    mdcontent = mdcontent.format(ditte_url=ditte_url, base_url=base_url.rstrip('/'))
    st.markdown(mdcontent)


if st.button("Calcola ripartizione spese"):
    with st.container():
        st.subheader("Risultati")
        st.write(f"Spesa tetto (con IVA): {format_currency(roof_expense)}")
        st.write(f"Altre spese (con IVA): {format_currency(other_expense)}")
        total_expense = roof_expense + other_expense
        st.write(f"Totale spese condominiali: {format_currency(total_expense)}")

        st.write("### Ripartizione delle spese per unità immobiliare")
        st.write("Le spese sono calcolate in base ai millesimi di proprietà.")
        expenses_df = calculate_expenses(resdf, roof_expense, other_expense)

        st.dataframe(expenses_df, use_container_width=True)

        # Plots in tabs (no full page reload)
        tab1, tab2 = st.tabs(["Treemap", "Barplot"])
        with tab1:
            plot_treemap(expenses_df)
        with tab2:
            plot_barplot(expenses_df)
            

    

