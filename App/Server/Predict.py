#  First before that we have to load the ML model from pickle file (model.pkl) ... 
# This python file/function used to predict the output power from the inputs in WeatherAPI.py file...
import pandas as pd
import pickle


def predict(wind_speed,theoreticalPower):

    model = pickle.load(open('./App/Server/model.pkl', 'rb'))
    series = {
        'Wind Speed (m/s)': wind_speed,
        'Theoretical_Power_Curve (KWh)': theoreticalPower
        }

    vector = pd.DataFrame(series)
    actualPower = model.predict(vector)

    return list(actualPower)

