from fastapi import FastAPI
import pandas as pd
from bikes.services.geolocation import get_lat_lon

# library loading model
import pickle

# instantiating fastapi
app = FastAPI()

# pre-loading model when uvicorn server starts
with open('model_filename.pkl', 'rb') as file:
    model = pickle.load(file)

# defin predict endpoint
@app.get('/predict')
def predict(adr, date):

    # converting adr to lat/long
    lat, long = get_lat_lon(adr)

    # locals() gets us all of our arguments back as a dictionary
    X_pred = pd.DataFrame({"lat":lat, "long":long, "date":date }, index=[0])

    # processing input feature before prediction
    X_processed = preprocess_features(X_pred)

    # predict
    y_pred = model.predict(X_processed)

    return dict(accident_probability=float(y_pred))
