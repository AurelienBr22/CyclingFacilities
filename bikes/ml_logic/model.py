import pandas as pd
from prophet.serialize import model_to_json, model_from_json
from os.path import join

def predict_n_accidents(d: str, model=m) -> float:
    """
    Takes a date and returns the expected number of accident for this given day.
    """
    _df = pd.DataFrame({'ds': [pd.to_datetime(d).date()]})
    return round(model.predict(_df)['yhat'][0], 2)

def load_model(name, path):
    with open(join(name, path), 'r') as file:
        m = model_from_json(file.read())  # Load model
    return m
