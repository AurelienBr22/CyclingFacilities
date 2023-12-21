import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap, MeasureControl
from bikes.visualization.visual import create_heatmap

st.set_page_config(layout="wide")

def page_accueil():
    st.write("Page d'accueil")

def page_model():
    st.write("Model")
    # # Streamlit page configuration
    st.title("Bike Accident Probability Prediction")

    # Input fields for the user
    col1, col2, col3= st.columns([1, 1, 1])  # Ajustez ces valeurs pour modifier la répartition de l'espace

    with col1:
        address = st.text_input("Enter the address")
    with col3:
        hr = st.time_input("Select the hour")
    with col2:
        date = st.date_input("Select the date")

    # get data
    locations = pd.read_csv('./clean_data/crado_velo_format.csv')[['lat', 'long']]

    heatmap = create_heatmap(locations)
    map_section = st.empty()

    # Initially display the heatmap
    with map_section.container():
        col4, col5, col6 = st.columns([1,6,1])
        with col5:
            folium_static(heatmap, width=1200, height=600)

    if st.button("Predict Accident Probability"):
        # API endpoint
        url = "http://localhost:8000/predict"

        # Parameters to send to the FastAPI backend
        params = {
            "adr": address,
            "date": date
        }

        # Sending a request to the FastAPI servers
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Display the prediction result
            prediction = response.json()
            accident_probability = prediction['accident_probability']
            st.write(f"Predicted Accident Probability: {accident_probability}")

            # Update the Folium heatmap with new data
            lat, long = prediction['lat'], prediction['long']
            heatmap = create_heatmap(locations, lat, long)

            # Clear the initial map and display the updated map
            map_section.empty()
            with map_section.container():
                col4, col5, col6 = st.columns([1,6,1])
                with col5:
                    folium_static(heatmap, width=1200, height=600)
        else:
            st.error("Error in API Call")


def page_secondaire():
    st.write("Page secondaire")
    st.title("Chams peux-tu travailler stp ?")

# Création de la barre latérale
choix_page = st.sidebar.selectbox("Choisissez une page :", ["Accueil","Model", "Page Secondaire"])

# Logique de redirection
if choix_page == "Accueil":
    page_accueil()
if choix_page == "Model":
    page_model()
elif choix_page == "Page Secondaire":
    page_secondaire()
