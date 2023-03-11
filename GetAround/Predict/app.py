from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import json
import numpy as np
import uvicorn
import pandas as pd

description = """
Welcome to  my fast API 🏃
## Introduction Endpoints
"""
tags_metadata = [
    {
        "name": "Introduction Endpoints",
        "description": "Simple endpoints to try out!",
    },
    {
        "name": "Machine Learning",
        "description": "Car Price Prediction."
    }
]

# instanciate FastAPI class
app = FastAPI(
    title="GetAround",
    description=description,
    version="0.1",
    contact={
        "name": "GetAround Price Prediction",
        "url": "https://predict-getaround-nico.herokuapp.com/",
    },
    openapi_tags=tags_metadata
)


class PredictionFeatures(BaseModel):
    model_key: str = "Fiat"
    mileage: int = 146980
    engine_power: int = 150
    fuel: str = "diesel"
    paint_color: str = "black"
    car_type: str = "hatchback"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = True
    winter_tires: bool = True

@app.get("/", tags=["Introduction Endpoints"])
async def index():
    """
    Welcome message
    """
    message = "Hello There! This `/` is the default Endpoint. For more informations, check out the documentation on `/docs`"
    return message


@app.post("/predict", tags=["Car Price"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Rental Price Per Day Prediction.
    """

    price_day = pd.DataFrame(dict(predictionFeatures), index=[0])

    filename = 'finalized_model.joblib'
    loaded_model = joblib.load(open(filename, 'rb'))

    preprocessor = joblib.load(open('preprocessor.joblib', 'rb'))

    X = preprocessor.transform(price_day)
    prediction = loaded_model.predict(X)

    response = prediction.tolist()[0]
    response = round(response)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)