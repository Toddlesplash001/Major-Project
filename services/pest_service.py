# services/pest_service.py
import io
import os
import threading
from PIL import Image
import torch
from torchvision import transforms
import pandas as pd

# Paths — update as needed
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root when services/ is inside project
MODEL_PATH = os.path.join(BASE_DIR, "models", "plant_disease_model_1_latest.pt")
DISEASE_CSV = os.path.join(BASE_DIR, "data", "disease_info.csv")
SUPP_CSV = os.path.join(BASE_DIR, "data", "supplement_info.csv")

# Lazy-loaded globals
_model = None
_model_lock = threading.Lock()
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load CSVs (safe to load at import)
disease_info = pd.read_csv(DISEASE_CSV, encoding="cp1252")
supplement_info = pd.read_csv(SUPP_CSV, encoding="cp1252")

# preprocessing transform: match training
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp"}


def _load_model():
    """Thread-safe lazy model loader."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                # Import the model class here so module import is lightweight
                from CNN import CNN as CNNModel  # adjust import path if needed
                print("Loading pest/disease model to", _device)
                model = CNNModel(39)  # be consistent with how you instantiate in training
                model.to(_device)
                # load state
                state = torch.load(MODEL_PATH, map_location=_device)
                # if you saved a dict with "model_state_dict", adapt accordingly
                if isinstance(state, dict) and "model_state_dict" in state:
                    model.load_state_dict(state["model_state_dict"])
                else:
                    model.load_state_dict(state)
                model.eval()
                _model = model
    return _model


def _allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXT


def predict_from_pil(img_pil):
    """
    Accepts a PIL Image, returns (pred_index, probs array)
    """
    model = _load_model()
    img = img_pil.convert("RGB")
    x = _transform(img).unsqueeze(0).to(_device)  # shape (1,3,224,224)
    with torch.no_grad():
        out = model(x)  # raw logits (1, C)
        probs = torch.softmax(out, dim=1).cpu().numpy()[0]
        pred_idx = int(probs.argmax())
    return pred_idx, probs


def predict_disease(file_storage):
    """
    Public function for Flask routes. Accepts a Werkzeug FileStorage (request.files['image']).
    Returns a dict with useful fields for templates / API:
      { 'pred_index': int, 'label': str, 'prob': float, 'description': str, ... }
    """
    filename = getattr(file_storage, "filename", None)
    if not filename or not _allowed_file(filename):
        raise ValueError("Unsupported file type")

    # read into PIL without saving to disk (optional saving below)
    file_bytes = file_storage.read()
    img = Image.open(io.BytesIO(file_bytes))

    pred_idx, probs = predict_from_pil(img)
    prob = float(probs[pred_idx])

    # assemble metadata (guard against index errors)
    label = disease_info['disease_name'].iloc[pred_idx] if pred_idx < len(disease_info) else f"class_{pred_idx}"
    description = disease_info['description'].iloc[pred_idx] if pred_idx < len(disease_info) else ""
    prevent = disease_info['Possible Steps'].iloc[pred_idx] if pred_idx < len(disease_info) else ""
    image_url = disease_info['image_url'].iloc[pred_idx] if pred_idx < len(disease_info) else ""
    supplement_name = supplement_info['supplement name'].iloc[pred_idx] if pred_idx < len(supplement_info) else ""
    supplement_image_url = supplement_info['supplement image'].iloc[pred_idx] if pred_idx < len(supplement_info) else ""
    supplement_buy_link = supplement_info['buy link'].iloc[pred_idx] if pred_idx < len(supplement_info) else ""

    # Optionally save uploaded image to static/uploads for later review
    uploads_dir = os.path.join(BASE_DIR, "static", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    save_path = os.path.join(uploads_dir, filename)
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    return {
        "pred_index": pred_idx,
        "label": label,
        "probability": prob,
        "description": description,
        "prevention": prevent,
        "image_url": image_url,
        "supplement_name": supplement_name,
        "supplement_image_url": supplement_image_url,
        "supplement_buy_link": supplement_buy_link,
        "saved_path": save_path
    }
