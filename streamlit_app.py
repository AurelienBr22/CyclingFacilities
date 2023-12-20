import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap, MeasureControl
from bikes.visualization.visual import create_heatmap

# Streamlit page configuration
st.title("Bike Accident Probability Prediction")

# Input fields for the user
address = st.text_input("Enter the address")
date = st.date_input("Select the date")

# get data
locations = pd.read_csv('./raw_data/crado_velo_format.csv')[['lat', 'long']]
heatmap = create_heatmap(locations)

# Display the Folium map in Streamlit
folium_static(heatmap)

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
        heatmap = create_heatmap(lat, long)

        # Display the Folium map in Streamlit
        folium_static(heatmap)
    else:
        st.error("Error in API Call")
