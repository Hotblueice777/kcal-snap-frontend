# app.py

import streamlit as st
import scan_page, meal_page, assistant_page
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

st.set_page_config(page_title="KcalSnap", layout="centered")

st.markdown("""
        <style>
            
        div.stAlert {
            background-color: #F7F5FA !important; 
            border: 1px solid #E0DAEB !important; 
            color: #6E5B8B !important;            
            border-radius: 10px !important;
            padding: 12px 16px !important;
        }

        div.stAlert [data-testid="stMarkdownContainer"] p,
        div.stAlert svg {
            color: #6E5B8B !important;
            fill: #6E5B8B !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.radio("KcalSnap", ["Scan & Analyze", "My Meal", "AI Assistant"])

st.markdown("""
        <style>
            
        section[data-testid="stSidebar"] {
            background-color: #F9F9F9 !important;
            padding-top: 50px !important;
        }

        div[data-testid="stSidebar"] [data-baseweb="radio"] svg {
            display: none !important;
        }

        div[data-testid="stSidebar"] label[data-baseweb="radio"] {
            padding: 8px 14px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease-in-out;
        }

        /* hover */
        div[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
            background-color: rgba(155, 93, 229, 0.08) !important;
        }

        div[data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] {
            background-color: rgba(155, 93, 229, 0.20) !important;
        }

        div[data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] p {
            color: #5A2D9D !important;
            font-weight: 600 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# Page switching
if page == "Scan & Analyze":
    scan_page.render()
elif page == "My Meal":
    meal_page.render()
elif page == "AI Assistant":
    assistant_page.render()
