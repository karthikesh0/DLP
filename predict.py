# predict_utils.py

import os
import torch
from torchvision import models, transforms
from PIL import Image, ImageEnhance
import json
from collections import OrderedDict

def build_transforms():
    def add_tint(img):
        img = img.convert("RGB")
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.2)
        return img

    return transforms.Compose([
        transforms.Lambda(add_tint),
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])

def predict_single_image(image_path):
    # Assume model and config are in project root /model folder
    root_dir = os.path.dirname(os.path.abspath(__file__))  # this file's folder
    model_path = os.path.join(root_dir, 'fine_tuned_model.bin')
    config_path = os.path.join(root_dir, 'config.json')

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(config_path, "r") as f:
        config = json.load(f)

    model_name = config.get("model_name", "resnet50")

    if model_name == "resnet50":
        model = models.resnet50(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, 2)
    elif model_name == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, 2)
    else:
        raise ValueError(f"Unsupported model name: {model_name}")

    model.to(device)

    checkpoint = torch.load(model_path, map_location=device)
    new_state_dict = OrderedDict()
    for k, v in checkpoint.items():
        name = k[7:] if k.startswith("module.") else k
        new_state_dict[name] = v

    model.load_state_dict(new_state_dict, strict=False)
    model.eval()

    transform = build_transforms()
    image = Image.open(image_path)
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image_tensor)
        probs = torch.nn.functional.softmax(output, dim=1)
        pred_idx = torch.argmax(probs, dim=1).item()
        confidence = probs[0][pred_idx].item()

    class_names = ["neg", "pos"]  # Hardcoded classes
    pred_label = class_names[pred_idx]
    return {"label": pred_label, "confidence": round(confidence, 2)}
