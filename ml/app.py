import base64
import threading
from pathlib import Path
import json
import re
import cv2
import numpy as np
import mediapipe as mp
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from features import normalize
from train import train, DATA, MODELS

app=FastAPI(title='ISL landmark recognition',version='1.0.0')
lock=threading.Lock()
detector=None
bundle=None
asset=Path(__file__).parent/'models'/'hand_landmarker.task'
if asset.exists():
    detector=mp.tasks.vision.HandLandmarker.create_from_options(mp.tasks.vision.HandLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(asset)),num_hands=2,min_hand_detection_confidence=.5))
def reload():
    global bundle
    path=MODELS/'alphabet.joblib'
    bundle=joblib.load(path) if path.exists() else None
reload()
class Frame(BaseModel):
    image: str = Field(max_length=1800000)
class Sample(BaseModel):
    features: list[float] = Field(min_length=128,max_length=128)
    label: str = Field(pattern=r'^[A-Z][A-Z ]{0,63}$')
    session: str = Field(min_length=1,max_length=100)
@app.get('/health')
def health():
    return {'available':True,'landmarker':detector is not None,'model':bundle is not None,'labels':bundle['labels'] if bundle else []}
@app.post('/frame')
def frame(body:Frame):
    if detector is None:
        raise HTTPException(503,'Download the hand landmark model: python ml/download_model.py; restart ML service.')
    try:
        raw=base64.b64decode(body.image.split(',')[-1],validate=True)
        img=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
        if img is None or img.shape[0]*img.shape[1]>1280*720:
            raise ValueError('Use a JPEG at most 1280x720')
    except Exception as e:
        raise HTTPException(400,'Invalid image: '+str(e))
    rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    with lock:
        result=detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb))
    hands=[[[p.x,p.y,p.z] for p in hand] for hand in result.hand_landmarks]
    features=normalize(hands)
    prediction={'label':None,'confidence':0.,'hands':hands,'features':features,'model':bundle is not None}
    if features is not None and bundle:
        scores=bundle['model'].predict_proba([features])[0];i=int(np.argmax(scores))
        prediction.update(label=str(bundle['model'].classes_[i]),confidence=float(scores[i]))
    return prediction
@app.post('/sample')
def sample(body:Sample):
    if not np.isfinite(body.features).all():
        raise HTTPException(400,'Features must be finite')
    DATA.parent.mkdir(parents=True,exist_ok=True)
    with lock:
        with DATA.open('a') as f:
            f.write(json.dumps(body.model_dump())+'\n')
    return {'saved':True,'label':body.label}
@app.post('/train')
def training():
    try:
        with lock:
            report=train();reload()
        return report
    except ValueError as e:
        raise HTTPException(400,str(e))
