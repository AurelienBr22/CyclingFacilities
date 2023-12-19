from fastapi import FastAPI
import pandas as pd
import numpy as np
from bikes.ml_logic.model import load_model

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

    # predict
    y_pred = round(np.random.uniform(0, 100), 2)

    return dict(accident_probability=float(y_pred),
                lat=lat,
                long=long)
