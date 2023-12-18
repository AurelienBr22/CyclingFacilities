# import streamlit as st
# import requests
# import pandas as pd

# # Streamlit page configuration
# st.set_page_config(page_title="Bike Accident Probability Prediction")

# st.title("Bike Accident Probability Prediction")

# # Function to handle map click
# def handle_map_click():
#     if "last_clicked_lat" in st.session_state and "last_clicked_lon" in st.session_state:
#         return st.session_state.last_clicked_lat, st.session_state.last_clicked_lon
#     return None, None

# # Display a map for user to click on
# map_clicked = st.empty()
# lat, lon = handle_map_click()

# if lat is not None and lon is not None:
#     # Show clicked location
#     map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
#     map_clicked.map(map_data, zoom=12)

# # Time input
# time = st.time_input("Time")

# # Button to make prediction
# if st.button("Predict Accident Probability"):
#     # Check if coordinates are selected
#     if lat is None or lon is None:
#         st.error("Please select a location on the map.")
#     else:
#         # API endpoint
#         url = "http://localhost:8000/predict"

#         # Parameters to send to the FastAPI backend
#         params = {
#             "lat": lat,
#             "long": lon,
#             "time": time.strftime("%H:%M")  # Format time as a string
#         }

#         # Sending a request to the FastAPI server
#         response = requests.get(url, params=params)

#         if response.status_code == 200:
#             # Display the prediction result
#             prediction = response.json()
#             st.write(f"Predicted Accident Probability: {prediction['accident_probability']}")
#         else:
#             st.error("Error in API Call")

# # Callback to store the last clicked position
# def on_map_click():
#     st.session_state.last_clicked_lat = st.session_state.map_last_clicked["lat"]
#     st.session_state.last_clicked_lon = st.session_state.map_last_clicked["lon"]

# # Event listener for map click
# map_clicked.map(on_click=on_map_click)
