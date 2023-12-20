from fastapi import FastAPI
import pandas as pd
import numpy as np
from bikes.ml_logic.model import load_model, predict_n_accidents

from bikes.services.geolocation import get_lat_lon
#from bikes.ml_logic.preprocess import preprocess_features

# # library loading model
# import joblib

# from google.cloud import storage

# instantiating fastapi
app = FastAPI()

model = load_model()#np.random.uniform(0, 100)

# defin predict endpoint
@app.get('/predict')
def predict(adr, date):

    # converting adr to lat/long
    lat, long = get_lat_lon(adr)

    # locals() gets us all of our arguments back as a dictionary
    X_pred = pd.DataFrame({"lat":lat,
                           "long":long,
                           "date":date }, index=[0])

    # processing input feature before prediction
    #X_processed = preprocess_features(X_pred)
    y_pred = predict_n_accidents(date, model)

    return dict(accident_probability=y_pred,
                lat=lat,
                long=long)
