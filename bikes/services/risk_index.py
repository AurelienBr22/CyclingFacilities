import pandas as pd

from numpy import mean
from math import radians, cos, sin, asin, sqrt

def dist(point1: tuple, point2: tuple) -> float:
    """
    Replicating the same formula as mentioned in Wikipedia.

    - point1: tuple. First element is the latitude, second is longitude.

    - point2: tuple. First element is the latitude, second is longitude.
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [point1[0], point1[1], point2[0], point2[1]])
    # haversine formula 
    dlon = lon2 - lon1
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km

def risk_index(point: tuple, coords: list, n: int) -> float:
    """
    Compute the distance between one point and a list of other points.
    Take the distance of the n closest point and return the mean (in km).

    - point: tuple. First element is the latitude, second is the longitude.

    - coords: list. List of coordinates. Each coordinate must be a tuple, first element is the latitude
    and second element is the longitude.

    - n: number of closest points which will be used to compute the mean.
    """
    return mean(sorted([dist((point[0], point[1]), (coord[0], coord[1])) for coord in coords])[:n])