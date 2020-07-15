# Here we have to write our Machine Learning Algorithm to impliment the problem solution and create the model ...

def main(wind_speed,theory_power):
    import pandas as pd
    # This scripts is used to train the data into a ML model and dump the model into a pickle file ...
    import numpy as np
    import xgboost as xgb
    import pickle


    # Getting data from 'Data_preprocessing' folder ...
    df = pd.read_csv('./Data_Processing/data_for_training.csv')

    x = df.iloc[:,1:]
    y = df.iloc[:,0]

    xgbr = xgb.XGBRegressor(gamma=0.10137883109108962, learning_rate=0.02, max_depth=2, min_child_weight=20, missing=float('nan'), 
    n_estimators=707, n_jobs=2, random_state=33, reg_alpha=0.9575998867944943, 
    silent=True, subsample=0.05498233327011234, verbosity=0)

    xgbr.fit(x,y)

    with open('model.pkl','wb') as file:
        pickle.dump(xgbr, file)
    file.close()

    model = pickle.load(open('model.pkl', 'rb'))
    series = {
    'Wind Speed (m/s)':[wind_speed],
    'Theoretical_Power_Curve (KWh)':[theory_power]
    }
    vector = pd.DataFrame(series)
    result = model.predict(vector[['Wind Speed (m/s)','Theoretical_Power_Curve (KWh)']].iloc[[0]])

    return result




if __name__ == "__main__":
    # Manually define the values of wind_speed,theory_power
    wind_speed,theory_power = 5,1520

    result = main(wind_speed,theory_power)
    print(result)

