import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd
from pydantic import BaseModel

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.utils.ml_utils.model.estimator import NetworkModel

class URLRequest(BaseModel):
    url_features: list


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()

# CORS Configuration - allow all origins for cloud deployments
# In production, you may want to restrict this to specific domains
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./networksecurity/templates")

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["monitoring"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {
        "status": "healthy",
        "service": "networksecurity-api",
        "version": "0.0.1"
    }

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
@app.post("/predict")
async def predict_route(request: Request,file: UploadFile = File(...)):
    try:
        df=pd.read_csv(file.file)
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        y_pred = network_model.predict(df)
        df['predicted_column'] = y_pred
        
        # Create prediction_output directory if it doesn't exist
        os.makedirs('prediction_output', exist_ok=True)
        df.to_csv('prediction_output/output.csv')
        
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html", {"request": request, "table": table_html})
        
    except Exception as e:
            raise NetworkSecurityException(e,sys)

@app.post("/predict_csv")
async def predict_csv_route(file: UploadFile = File(...)):
    """CSV prediction endpoint that returns JSON - for Streamlit Cloud compatibility"""
    try:
        df=pd.read_csv(file.file)
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        y_pred = network_model.predict(df)
        df['predicted_column'] = y_pred
        
        # Return JSON instead of HTML template
        return {"predictions": df.to_dict(orient='records')}
        
    except FileNotFoundError as e:
        logging.error(f"Model file not found: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Model files not found. Please ensure models are trained and available."
        )
    except Exception as e:
        logging.error(f"CSV Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.post("/predict_single")
async def predict_single_url(url_data: URLRequest):
    try:
        # Input validation
        if len(url_data.url_features) != 30:
            raise HTTPException(
                status_code=400,
                detail=f"Expected 30 features, got {len(url_data.url_features)}. Please provide all required URL features."
            )
        
        # Validate feature values (should be in [-1, 0, 1])
        for i, val in enumerate(url_data.url_features):
            if val not in [-1, 0, 1]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Feature at index {i} has invalid value {val}. All features must be -1, 0, or 1."
                )
        
        # Create DataFrame from single URL features
        feature_names = ['having_IP_Address','URL_Length','Shortining_Service','having_At_Symbol',
                        'double_slash_redirecting','Prefix_Suffix','having_Sub_Domain','SSLfinal_State',
                        'Domain_registeration_length','Favicon','port','HTTPS_token','Request_URL',
                        'URL_of_Anchor','Links_in_tags','SFH','Submitting_to_email','Abnormal_URL',
                        'Redirect','on_mouseover','RightClick','popUpWidnow','Iframe','age_of_domain',
                        'DNSRecord','web_traffic','Page_Rank','Google_Index','Links_pointing_to_page',
                        'Statistical_report']
        
        df = pd.DataFrame([url_data.url_features], columns=feature_names)
        
        preprocesor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocesor,model=final_model)
        
        y_pred = network_model.predict(df)
        result = "Phishing" if y_pred[0] == 1 else "Safe"
        
        return {"prediction": result, "confidence": float(y_pred[0])}
        
    except HTTPException:
        raise  # Re-raise HTTPException without wrapping
    except FileNotFoundError as e:
        logging.error(f"Model file not found: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Model files not found. Please ensure models are trained and available."
        )
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

    
if __name__=="__main__":
    # Use PORT environment variable for cloud deployments
    port = int(os.getenv("PORT", 8000))
    logging.info(f"Starting server on port {port}")
    app_run(app, host="0.0.0.0", port=port)
