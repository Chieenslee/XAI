import torch
import torchxrayvision as xrv
import numpy as np

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")

model = xrv.models.DenseNet(weights="densenet121-res224-all")
effusion_idx = model.pathologies.index('Effusion')

# Test raw baseline model
dummy_input = torch.randn(2, 1, 224, 224)
model.eval()
with torch.no_grad():
    out_baseline = model(dummy_input)

print("BASELINE output (raw):", out_baseline[:, effusion_idx])

# Load our fine-tuned weights
model_path = r"d:\My\XAI\models\pleural_effusion_model_best_v6.pth"
if __import__('os').path.exists(model_path):
    print("Found v6 model. Loading...")
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    with torch.no_grad():
        out_finetuned = model(dummy_input)
    print("FINETUNED output (raw):", out_finetuned[:, effusion_idx])
    print("FINETUNED sigmoid:", torch.sigmoid(out_finetuned[:, effusion_idx]))
else:
    print("Model file not found:", model_path)
