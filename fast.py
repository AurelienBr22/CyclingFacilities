from fastapi import FastAPI
import pandas as pd
import numpy as np
from bikes.ml_logic.model import load_model, predict_n_accidents
from bikes.services.risk_index import risk_index

from bikes.services.geolocation import get_lat_lon
#from bikes.ml_logic.preprocess import preprocess_features

# # library loading model
# import joblib

# from google.cloud import storage

# instantiating fastapi
app = FastAPI()

model = load_model()#np.random.uniform(0, 100)
df = pd.read_csv('clean_data/crado_velo_format.csv')[['lat', 'long']]
coords = [(el[0], el[1]) for el in zip(df['lat'].to_list(), df['long'].to_list())]


# defin predict endpoint
@app.get('/predict')
def predict(adr, date):

    # converting adr to lat/long
    lat, long = get_lat_lon(adr)
    risk_idx = risk_index((lat, long), coords, 5)
    breakpoint()
    # locals() gets us all of our arguments back as a dictionary
    X_pred = pd.DataFrame({"lat":lat,
                           "long":long,
                           "date":date }, index=[0])

    # processing input feature before prediction
    #X_processed = preprocess_features(X_pred)
    y_pred = predict_n_accidents(date, model)

    # if risk_idx == 0:
    #     risk_idx = 0.001
    #print(risk_idx)

    #breakpoint()
    score = y_pred * (1/risk_idx)

    return dict(accident_probability=y_pred,
                risk_idx=round(risk_idx, 2),
                risk_idx_inv=round((1/risk_idx), 2),
                score=score,
                lat=lat,
                long=long)
