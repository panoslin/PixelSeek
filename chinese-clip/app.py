import os
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from transformers import CLIPProcessor, CLIPModel
import uvicorn
from typing import List, Optional, Union
import time

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

# Load Chinese-CLIP model
MODEL_NAME = "OFA-Sys/chinese-clip-vit-base-patch16"
model = CLIPModel.from_pretrained(MODEL_NAME)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)

# Move model to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

@app.get("/")
def read_root():
    return {"status": "running", "model": MODEL_NAME}

@app.post("/vectorize/text")
async def vectorize_text(text: List[str] = Form(...)):
    start_time = time.time()
    
    # Preprocess text
    inputs = processor(text=text, return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get text embeddings
    with torch.no_grad():
        text_outputs = model.get_text_features(**inputs)
        
    # Convert to numpy and normalize
    embeddings = text_outputs.cpu().numpy()
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
    pil_images = []
    for image_file in images:
        content = await image_file.read()
        pil_image = Image.open(BytesIO(content)).convert("RGB")
        pil_images.append(pil_image)
    
    # Process images
    inputs = processor(images=pil_images, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get image embeddings
    with torch.no_grad():
        image_outputs = model.get_image_features(**inputs)
    
    # Convert to numpy and normalize
    embeddings = image_outputs.cpu().numpy()
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
    pil_images = []
    for b64_str in image_base64:
        img_data = base64.b64decode(b64_str)
        pil_image = Image.open(BytesIO(img_data)).convert("RGB")
        pil_images.append(pil_image)
    
    # Process images
    inputs = processor(images=pil_images, return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get image embeddings
    with torch.no_grad():
        image_outputs = model.get_image_features(**inputs)
    
    # Convert to numpy and normalize
    embeddings = image_outputs.cpu().numpy()
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    processing_time = time.time() - start_time
    
    return {
        "vectors": embeddings.tolist(),
        "dimensions": embeddings.shape[1],
        "processing_time": processing_time
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
