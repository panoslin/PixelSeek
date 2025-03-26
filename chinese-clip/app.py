import os
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Optional, Union
import time
import sys
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use environment variable or default to RN50 model
MODEL_NAME = os.environ.get("CLIP_MODEL_NAME", "RN50")
assert MODEL_NAME in available_models(), f"Model {MODEL_NAME} not found in available models: {available_models()}"

# Load CN-CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = load_from_name(MODEL_NAME, device=device)

@app.get("/")
def read_root():
    return {"status": "running", "model": MODEL_NAME}

@app.post("/vectorize/text")
async def vectorize_text(text: List[str] = Form(...)):
    start_time = time.time()
    
    # Tokenize and encode text
    with torch.no_grad():
        text_tokens = clip.tokenize(text).to(device)
        text_features = model.encode_text(text_tokens)
        
    # Convert to numpy and normalize
    embeddings = text_features.cpu().numpy()
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    processing_time = time.time() - start_time
    
    return {
        "vectors": embeddings.tolist(),
        "dimensions": embeddings.shape[1],
        "processing_time": processing_time
    }

@app.post("/vectorize/image")
async def vectorize_image(images: List[UploadFile] = File(...)):
    start_time = time.time()
    
    # Load and preprocess images
    processed_images = []
    for image_file in images:
        content = await image_file.read()
        pil_image = Image.open(BytesIO(content)).convert("RGB")
        processed_image = preprocess(pil_image)
        processed_images.append(processed_image)
    
    # Stack images into a batch
    image_input = torch.stack(processed_images).to(device)
    
    # Get image embeddings
    with torch.no_grad():
        image_features = model.encode_image(image_input)
    
    # Convert to numpy and normalize
    embeddings = image_features.cpu().numpy()
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    processing_time = time.time() - start_time
    
    return {
        "vectors": embeddings.tolist(),
        "dimensions": embeddings.shape[1],
        "processing_time": processing_time
    }

@app.post("/vectorize/base64")
async def vectorize_base64(image_base64: List[str] = Form(...)):
    start_time = time.time()
    
    # Decode base64 images
    processed_images = []
    for b64_str in image_base64:
        img_data = base64.b64decode(b64_str)
        pil_image = Image.open(BytesIO(img_data)).convert("RGB")
        processed_image = preprocess(pil_image)
        processed_images.append(processed_image)
    
    # Stack images into a batch
    image_input = torch.stack(processed_images).to(device)
    
    # Get image embeddings
    with torch.no_grad():
        image_features = model.encode_image(image_input)
    
    # Convert to numpy and normalize
    embeddings = image_features.cpu().numpy()
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    processing_time = time.time() - start_time
    
    return {
        "vectors": embeddings.tolist(),
        "dimensions": embeddings.shape[1],
        "processing_time": processing_time
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
