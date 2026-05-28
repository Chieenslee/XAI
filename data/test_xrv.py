import torch
import torchxrayvision as xrv

model = xrv.models.DenseNet(weights="densenet121-res224-all")
print("Model path:", xrv.__file__)
print("Has apply_sigmoid?", hasattr(model, 'apply_sigmoid'))
print("Classifier type:", type(model.classifier))
print("Last layer:", list(model.classifier.children()) if hasattr(model.classifier, 'children') else model.classifier)

dummy = torch.randn(10, 1, 224, 224) * 10
out = model(dummy)
print("Min output:", out.min().item(), "Max output:", out.max().item())
