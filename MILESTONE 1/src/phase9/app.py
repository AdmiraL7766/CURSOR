"""Streamlit Frontend for Zomato AI Restaurant Recommendations."""

import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Zomato AI Recommendations",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

def fetch_locations():
    try:
        response = requests.get(f"{API_URL}/api/v1/locations", timeout=5)
        response.raise_for_status()
        return response.json().get("locations", [])
    except Exception as e:
        return []

def fetch_recommendations(payload):
    try:
        response = requests.post(f"{API_URL}/api/v1/recommendations", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return None

# Sidebar preferences
st.sidebar.title("🍔 Preferences")
st.sidebar.markdown("Find your next great meal.")

locations = fetch_locations()
location_options = [""] + locations if locations else ["Bellandur", "Indiranagar", "Koramangala", "BTM"]

selected_location = st.sidebar.selectbox("Location", location_options, help="Select a neighborhood")
if not selected_location:
    selected_location = st.sidebar.text_input("Or type location (e.g. Bellandur)")

cuisine = st.sidebar.selectbox(
    "Cuisine", 
    ["Any", "North Indian", "South Indian", "Chinese", "Italian", "Continental", "Mughlai", "Fast Food", "Cafe", "Biryani", "Street Food"]
)

budget = st.sidebar.selectbox(
    "Budget",
    options=["low", "medium", "high"],
    format_func=lambda x: {"low": "₹ Pocket Friendly", "medium": "₹₹ Mid Range", "high": "₹₹₹ Luxury"}[x]
)

min_rating = st.sidebar.selectbox(
    "Minimum Rating",
    options=["0", "3.0", "3.5", "4.0", "4.5"],
    format_func=lambda x: "Any rating" if x == "0" else f"{x}+"
)

additional_prefs_raw = st.sidebar.text_input("Extras (comma-separated)", placeholder="e.g. romantic, live music")

st.sidebar.markdown("---")
top_n = st.sidebar.slider("Number of recommendations", min_value=1, max_value=10, value=5)

# Main area
st.title("Discover the best food & drinks")
st.markdown("Personalized AI recommendations based on your mood and budget.")

if st.sidebar.button("Search", type="primary"):
    if not selected_location:
        st.sidebar.error("Please provide a location.")
    else:
        prefs_list = [p.strip() for p in additional_prefs_raw.split(",") if p.strip()]
        
        payload = {
            "location": selected_location,
            "cuisine": cuisine,
            "budget": budget,
            "min_rating": min_rating,
            "top_n": top_n,
            "additional_preferences": prefs_list
        }
        
        with st.spinner("Curating your perfect picks..."):
            result = fetch_recommendations(payload)
            
        if result:
            st.divider()
            
            if "summary" in result and result["summary"]:
                st.info(f"✨ **AI Summary:** {result['summary']}")
                
            recommendations = result.get("recommendations", [])
            
            if not recommendations:
                st.warning("No restaurants matched your preferences. Try broadening your filters.")
            else:
                st.subheader("Top Recommendations for you")
                
                for idx, rec in enumerate(recommendations):
                    with st.container():
                        st.markdown(f"### #{rec['rank']} {rec['title']}")
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            st.metric("Rating", f"⭐ {rec['rating']}")
                        with col2:
                            st.metric("Cost for two", f"₹{rec['estimated_cost_for_two']}")
                            
                        st.markdown(f"**Cuisine:** {rec['cuisine']}")
                        st.markdown(f"**Why we recommend it:** {rec['explanation']}")
                        
                        if rec.get("tags"):
                            tags_html = " ".join([f"<span style='background-color: #f0f2f6; padding: 2px 8px; border-radius: 12px; font-size: 14px; margin-right: 5px;'>{t}</span>" for t in rec['tags']])
                            st.markdown(tags_html, unsafe_allow_html=True)
                        st.divider()
else:
    st.info("👈 Use the sidebar to set your preferences and click Search!")
