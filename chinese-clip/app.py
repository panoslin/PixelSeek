import os
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from fastapi import FastAPI, UploadFile, File, Form, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Optional, Union, Dict, Any
import time
import sys
import json
import logging
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Add Weaviate vectorizer module compatibility endpoints
@app.post("/modules/chinese-clip/vectorize")
async def vectorize_module(data: Dict[str, Any] = Body(...)):
    """
    Vectorizer module endpoint compatible with Weaviate v4.11.3.
    This endpoint handles both image and text vectorization requests from Weaviate.
    
    Expects a JSON body with this structure:
    {
        "fields": ["field1", "field2", ...],
        "objects": [{"field1": "value1", "field2": "value2"}, ...]
    }
    
    Image fields are expected to be base64 encoded.
    """
    try:
        start_time = time.time()
        fields = data.get("fields", [])
        objects = data.get("objects", [])
        
        if not fields or not objects:
            raise HTTPException(status_code=400, detail="Missing fields or objects in request")
        
        # Get module config
        config = data.get("config", {})
        image_fields = config.get("imageFields", [])
        
        results = []
        
        # Process each object
        for obj in objects:
            # Initialize vectors
            vectors = {}
            
            # Process text fields
            text_to_vectorize = []
            text_fields = []
            
            for field in fields:
                if field in obj:
                    # Skip image fields in text processing
                    if field in image_fields:
                        continue
                        
                    field_value = obj[field]
                    if isinstance(field_value, str) and field_value:
                        text_to_vectorize.append(field_value)
                        text_fields.append(field)
            
            # Generate text vectors if there are text fields
            if text_to_vectorize:
                with torch.no_grad():
                    text_tokens = clip.tokenize(text_to_vectorize).to(device)
                    text_features = model.encode_text(text_tokens)
                    
                text_embeddings = text_features.cpu().numpy()
                text_embeddings = text_embeddings / np.linalg.norm(text_embeddings, axis=1, keepdims=True)
                
                # Assign vectors to their fields
                for i, field in enumerate(text_fields):
                    vectors[field] = text_embeddings[i].tolist()
            
            # Process image fields
            for field in image_fields:
                if field in obj and obj[field]:
                    try:
                        # Decode base64 image
                        img_data = base64.b64decode(obj[field])
                        pil_image = Image.open(BytesIO(img_data)).convert("RGB")
                        processed_image = preprocess(pil_image)
                        
                        # Get image embedding
                        with torch.no_grad():
                            image_input = processed_image.unsqueeze(0).to(device)
                            image_features = model.encode_image(image_input)
                            
                        image_embedding = image_features.cpu().numpy()[0]
                        image_embedding = image_embedding / np.linalg.norm(image_embedding)
                        
                        # Assign vector to field
                        vectors[field] = image_embedding.tolist()
                    except Exception as e:
                        logger.error(f"Error processing image field {field}: {str(e)}")
                        # If image processing fails, provide a zero vector
                        vector_dim = model.visual.output_dim
                        vectors[field] = [0.0] * vector_dim
            
            # Combine vectors if needed or use field-specific vectors
            if not vectors and (text_to_vectorize or any(field in obj for field in image_fields)):
                # If we got here but have no vectors, there was a problem
                vector_dim = model.visual.output_dim
                combined_vector = [0.0] * vector_dim
            else:
                # Combine all vectors into one if multiple fields were vectorized
                all_vectors = list(vectors.values())
                if len(all_vectors) > 1:
                    # Average the vectors
                    combined_vector = np.mean(all_vectors, axis=0).tolist()
                elif len(all_vectors) == 1:
                    # Just use the single vector
                    combined_vector = all_vectors[0]
                else:
                    # No vectors were generated
                    vector_dim = model.visual.output_dim
                    combined_vector = [0.0] * vector_dim
            
            # Format result for Weaviate
            result = {
                "object": combined_vector,
                "fields": vectors
            }
            
            results.append(result)
        
        processing_time = time.time() - start_time
        logger.info(f"Processed {len(objects)} objects in {processing_time:.2f} seconds")
        
        return {
            "vectors": results
        }
        
    except Exception as e:
        logger.error(f"Error in vectorize_module: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vectorization failed: {str(e)}")

@app.get("/modules/chinese-clip/meta")
async def module_meta():
    """
    Return module metadata for Weaviate v4.11.3 compatibility
    """
    return {
        "name": "chinese-clip",
        "version": "1.0.0",
        "type": "vectorizer",
        "supported_media_types": ["text", "image"],
        "dimensions": model.visual.output_dim,
        "model": MODEL_NAME,
        "device": device
    }

@app.get("/modules/chinese-clip/models")
async def module_models():
    """
    Return available models for Weaviate v4.11.3 compatibility
    """
    return {
        "models": available_models(),
        "current_model": MODEL_NAME
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
