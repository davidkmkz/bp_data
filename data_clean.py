import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim

ciudades = pd.read_csv("ciudades.csv")

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")

def coordenadas(row):
    ciudad = row["Municipio"]
    location = geolocator.geocode(ciudad)
    row["Latitude"] = location.latitude
    row["Longitude"] = location.longitude
    return row



if __name__ == '__main__':
    ciudades = ciudades.apply(coordenadas,axis=1)
    ciudades.to_csv("ciudades_final_test.csv")
