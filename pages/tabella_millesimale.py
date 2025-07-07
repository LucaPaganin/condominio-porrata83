import os
import pandas as pd
import streamlit as st
from helpers import authenticate, calculate_millesimal_fractions

# Load into DataFrame
milldf = pd.read_csv("./input_data/tabella_millesimale.csv")

# Calculate millesimal fractions
resdf = calculate_millesimal_fractions(milldf)

if __name__ == "__main__":
    authenticate()

    st.title("Tabella Millesimale")

    
    # Display the table optimized for mobile
    st.dataframe(resdf, use_container_width=True)