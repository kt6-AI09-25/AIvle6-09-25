from typing import Union

from fastapi import FastAPI
import openai
import os
import emergency_ai26 as em
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/hospital_by_module")
def emergency(request:str, latitude:float, longitude:float):
    path = './'
    
    openai.api_key = em.load_keys(path + "api_key.txt")

    os.environ["OPENAI_API_KEY"] = openai.api_key

    map_key = em.load_keys(path + "map_key.txt")
    map_key = json.loads(map_key)
    c_id, c_key = map_key["c_id"], map_key["c_key"]

    emergency = pd.read_csv(path + "응급실 정보.csv")

    save_directory = path + "fine_tuned_bert_ai26"
    model = AutoModelForSequenceClassification.from_pretrained(save_directory)
    tokenizer = AutoTokenizer.from_pretrained(save_directory)

    # audio_path = path + "audio/"
    # filename = "audio1.mp3"

    # result = em.audio2text(audio_path, filename)
    result = em.text2summary(request)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    predicted_class, _ = em.predict(result, model, tokenizer, device)

    # 테스트 input --------------------
    # predicted_class = 2  # 테스트용
    # start_lat, start_lng = 35.548238, 129.307011
    # ---------------------------------

    if predicted_class <= 2:
        result = em.recommend_hospital(emergency, latitude, longitude, 0.1, c_id, c_key)
        print(result)
        result = result.to_dict(orient="records") 
    else:
        result = None
        
    return result

@app.get("/deploy_test")
def read_root():
    return {"deploy" : "success"}