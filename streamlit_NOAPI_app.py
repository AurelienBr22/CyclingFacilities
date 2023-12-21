import streamlit as st

import pandas as pd
import numpy as np
import folium
import requests

from streamlit_folium import folium_static
from folium.plugins import HeatMap, MeasureControl
from bikes.visualization.visual import create_heatmap
from bikes.ml_logic.model import load_model, predict_n_accidents
from bikes.services.risk_index import risk_index
from bikes.services.geolocation import get_lat_lon

# OLD FAST API

model = load_model()
df = pd.read_csv('clean_data/crado_velo_format.csv')[['lat', 'long']]
coords = [(el[0], el[1]) for el in zip(df['lat'].to_list(), df['long'].to_list())]

# defin predict endpoint
#@app.get('/predict')
def predict(adr, date):

    # converting adr to lat/long
    lat, long = get_lat_lon(adr)
    risk_idx = risk_index((lat, long), coords, 5)
    #breakpoint()
    # locals() gets us all of our arguments back as a dictionary
    X_pred = pd.DataFrame({"lat":lat,
                           "long":long,
                           "date":date }, index=[0])

    # processing input feature before prediction
    #X_processed = preprocess_features(X_pred)
    y_pred = predict_n_accidents(date, model)

    #breakpoint()
    score = y_pred * (1/risk_idx) * 1000

    return dict(accident_probability=y_pred,
                risk_idx=round(risk_idx, 2),
                risk_idx_inv=round((1/risk_idx), 2),
                score=round(score, 2),
                lat=lat,
                long=long)

# STREAMLIT

st.set_page_config(layout="wide")



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
lat1=48.8566
long1=2.3522
map = folium.Map(location=[lat1, long1], zoom_start=16, width='80%', height='100%')

#Initially display the heatmap
with map_section.container():
    col4, col5, col6 = st.columns([1,6,1])
    with col5:
        folium_static(map)

if st.button("Predict Accident Probability"):
        prediction = predict(address, date)
        accident_probability = prediction['accident_probability']
        risk_idx = prediction['risk_idx']
        score = prediction['score']
        st.write(f"Predicted number of accident : {accident_probability}")
        st.write(f"Local risk: {risk_idx}")
        st.write(f"Score: {score}")

        # Update the Folium heatmap with new data
        lat, long = prediction['lat'], prediction['long']
        heatmap = create_heatmap(locations, lat, long)

        # Clear the initial map and display the updated map
        map_section.empty()
        with map_section.container():
            col4, col5, col6 = st.columns([1,6,1])
            with col5:
                folium_static(heatmap)
