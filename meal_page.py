# streamlit_client/meal_page.py

import os
import streamlit as st
import requests, os, time, base64
import pandas as pd

def render():
    BACKEND = os.getenv("BACKEND_URL")
    st.markdown("<h1 style='color:#766A8F;'>My Meal — Daily Summary</h1>", unsafe_allow_html=True)

    if "meals" not in st.session_state or not st.session_state["meals"]:
        st.info("No meals added yet. Go to Scan & Analyze to add your first meal!")
        return

    df = pd.DataFrame(st.session_state["meals"])
    st.subheader("Today's Meals")
    st.dataframe(df, use_container_width=True)

    total = df[["cal", "protein", "fat", "carb"]].sum()
    st.markdown("### Daily Totals")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories (kcal)", f"{total['cal']:.0f}")
    c2.metric("Protein (g)", f"{total['protein']:.1f}")
    c3.metric("Fat (g)", f"{total['fat']:.1f}")
    c4.metric("Carbs (g)", f"{total['carb']:.1f}")



