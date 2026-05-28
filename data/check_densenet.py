import torch
import torchxrayvision as xrv

model = xrv.models.DenseNet(weights="densenet121-res224-all")
print("Features children:")
for name, module in model.features.named_children():
    print(name, module.__class__.__name__)
