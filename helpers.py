# --- Cosmos DB visit logger ---
import os
import datetime
import uuid
import streamlit as st
from streamlit_js_eval import get_page_location, get_browser_language, streamlit_js_eval

def collect_session_data():
    session_data = {}
    try:
        session_data["headers"] = dict(st.context.headers)
    except Exception:
        session_data["headers"] = {}
    session_data["query_params"] = {str(k): str(v) for k, v in st.query_params.items()}
    session_data["id"] = st.session_state.get("_session_id", str(uuid.uuid4()))
    session_data["user_agent"] = session_data["headers"].get("User-Agent")
    session_data["language"] = get_browser_language() or "unknown"
    session_data["origin"] = session_data["headers"].get("Origin", "")
    session_data["referrer"] = session_data["headers"].get("Referer", "")
    # Persistent anonymous user id from localStorage
    anon_id = streamlit_js_eval(
        js_expressions="localStorage.anon_id || (localStorage.anon_id = crypto.randomUUID())",
        key="anon_id"
    )
    session_data["anon_id"] = anon_id
    return session_data


def log_visit_to_cosmos(session_data):
    try:
        from azure.cosmos import CosmosClient
    except ImportError:
        return False
    # Get credentials from Streamlit secrets or env
    url = st.secrets.get("cosmosdb_url") or os.environ.get("COSMOSDB_URL")
    key = st.secrets.get("cosmosdb_key") or os.environ.get("COSMOSDB_KEY")
    db_name = st.secrets.get("cosmosdb_db") or os.environ.get("COSMOSDB_DB")
    container_name = st.secrets.get("cosmosdb_container") or os.environ.get("COSMOSDB_CONTAINER")
    if not all([url, key, db_name, container_name]):
        return False
    client = CosmosClient(url, credential=key)
    db = client.get_database_client(db_name)
    container = db.get_container_client(container_name)
    # Add timestamp
    session_data["timestamp"] = datetime.datetime.utcnow().isoformat()
    # Insert
    container.create_item(session_data)
    return True
# --- Simple visit counter ---
import threading
def increment_visit_counter(filepath="visit_count.txt"):
    lock = threading.Lock()
    with lock:
        try:
            with open(filepath, "r+") as f:
                count = int(f.read().strip() or 0) + 1
                f.seek(0)
                f.write(str(count))
                f.truncate()
        except FileNotFoundError:
            with open(filepath, "w") as f:
                count = 1
                f.write(str(count))
    return count
# --- Plotting functions for Streamlit ---
import plotly.express as px
import streamlit as st
import locale

locale.setlocale(locale.LC_ALL, '')

def plot_barplot(df_plot):
    import plotly.colors
    bar_height = max(400, 30 * len(df_plot))  # 30px per person, min 400px
    # Use a qualitative color palette from plotly for unique colors
    palette = plotly.colors.qualitative.Plotly
    if len(df_plot) > len(palette):
        # Extend with D3 or other qualitative palette if needed
        palette = plotly.colors.qualitative.Plotly + plotly.colors.qualitative.D3
    color_map = {name: palette[i % len(palette)] for i, name in enumerate(df_plot["nominativo"])}
    fig = px.bar(
        df_plot,
        x="spesa_totale",
        y="nominativo",
        orientation="h",
        labels={"spesa_totale": "Spese Totali (€)", "nominativo": "Nominativo"},
        title="Ripartizione Spese Totali per famiglia",
        color="nominativo",
        color_discrete_map=color_map
    )
    fig.update_layout(
        height=bar_height,
        showlegend=False,
        xaxis_showgrid=True,
        yaxis_showgrid=True,
        xaxis_gridcolor="#cccccc",
        yaxis_gridcolor="#cccccc"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_treemap(df_plot):
    import plotly.colors
    palette = plotly.colors.qualitative.Plotly
    if len(df_plot) > len(palette):
        palette = plotly.colors.qualitative.Plotly + plotly.colors.qualitative.D3
    color_map = {name: palette[i % len(palette)] for i, name in enumerate(df_plot["nominativo"])}
    fig = px.treemap(
        df_plot,
        path=["nominativo"],
        values="spesa_totale",
        color="nominativo",
        color_discrete_map=color_map,
        labels={"spesa_totale": "Spese Totali (€)", "nominativo": "Nominativo"},
        title="Ripartizione Spese Totali per famiglia (Treemap)"
    )
    fig.update_traces(textinfo="label+value")
    fig.update_layout(height=700)  # Increased height
    st.plotly_chart(fig, use_container_width=True)


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
        pivot[col] = pivot[col].apply(lambda x: round(x, 2))

    return pivot
