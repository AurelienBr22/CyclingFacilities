import streamlit as st
import requests
import pandas as pd

# Streamlit page configuration
st.title("Bike Accident Probability Prediction")

# Input fields for the user
address = st.text_input("Enter the address")
date = st.date_input("Select the date")
#hour = st.time_input("Select the hour")

if st.button("Predict Accident Probability"):
    # API endpoint
    url = "http://localhost:8000/predict"

    # Parameters to send to the FastAPI backend
    params = {
        "adr": address,
        "date": date
    }

    # Sending a request to the FastAPI server
    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Display the prediction result
        prediction = response.json()
        accident_probability = prediction['accident_probability']
        st.write(f"Predicted Accident Probability: {accident_probability}")

        lat, long = prediction['lat'], prediction['long']

        # map centered around the coordinates
        map_data = pd.DataFrame({'lat': [lat], 'lon': [long]})
        st.map(map_data)
    else:
        st.error("Error in API Call")
