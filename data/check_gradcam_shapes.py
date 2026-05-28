import torch
import torchxrayvision as xrv
from models.xai_gradcam import XAIExplainer
import numpy as np
import cv2

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = xrv.models.DenseNet(weights="densenet121-res224-all")
model.to(device)
model.eval()

explainer = XAIExplainer(model=model)
print("Target layer:", explainer.target_layer)

input_tensor = torch.randn(1, 1, 224, 224).to(device)
orig_resized = np.zeros((224, 224, 3))

heatmap = explainer.generate_heatmap(input_tensor, orig_resized, target_category=7)
print("Heatmap min/max:", heatmap.min(), heatmap.max())
print("Feature map shape:", explainer.feature_map.shape)
print("Gradient shape:", explainer.gradient.shape)
