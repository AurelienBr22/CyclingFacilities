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
    # Radius of earth in meters is 6 371 000
    m = 6_371_000 * c
    return m

def risk_index(point: tuple, coords: list, n: int) -> float:
    """
    Compute the distance between one point and a list of other points.
    Take the distance of the n closest point and return the mean (in km).

    - point: tuple. First element is the latitude, second is the longitude.

    - coords: list. List of coordinates. Each coordinate must be a tuple, first element is the latitude
    and second element is the longitude.

    - n: number of closest points which will be used to compute the mean.
    """

    all_distances = [dist((point[0], point[1]), (coord[0], coord[1])) for coord in coords]
    all_distances_sorted = sorted(all_distances)
    all_distances_n = all_distances_sorted[:n]
    res = mean(all_distances_n)

    if res == 0:
        n = all_distances_sorted.count(0)
        return mean(all_distances_sorted[:n + 1])

    return res
