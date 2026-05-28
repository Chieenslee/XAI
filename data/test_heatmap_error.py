import torch
import torchxrayvision as xrv
from models.xai_gradcam import XAIExplainer
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = xrv.models.DenseNet(weights="densenet121-res224-all")
model.to(device)
model.eval()

explainer = XAIExplainer(model=model)

input_tensor = torch.randn(1, 1, 224, 224).to(device)
orig_resized = np.random.rand(224, 224, 3)

try:
    heatmap = explainer.generate_heatmap(input_tensor, orig_resized, target_category=7)
    print("Heatmap generated successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
