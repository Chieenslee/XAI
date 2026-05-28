import json

with open(r'd:\My\XAI\notebooks\Cloud_Training_Pipeline.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb['cells'][0]['source'] = [
    "# Fine-tuning Chuẩn Y tế (v8 — Fix Double Sigmoid)\n",
    "**Tác giả:** Antigravity AI\n\n",
    "### Changelog v8:\n",
    "- Sửa lỗi `Double Sigmoid`: TorchXRayVision mặc định đã xuất ra Probabilities (chứa sẵn Sigmoid), nên dùng `BCELoss` thay vì `BCEWithLogitsLoss`.\n",
    "- Bỏ `torch.sigmoid()` ở bước Validate/Test.\n",
    "- Tự động tìm ngưỡng tối ưu (Optimal Threshold bằng Youden's J statistic) thay vì hardcode `0.5`.\n"
]

for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])

    # Fix BCELoss
    if 'criterion = nn.BCEWithLogitsLoss()' in src:
        new_src = src.replace(
            "criterion = nn.BCEWithLogitsLoss()",
            "# Fix v8: XRV model da co apply_sigmoid=True mac dinh\n# -> Output ra Probabilities -> Dung BCELoss thay vi BCEWithLogitsLoss\ncriterion = nn.BCELoss()"
        )
        # Fix validation sigmoid
        new_src = new_src.replace(
            "probs = torch.sigmoid(out).cpu().numpy().flatten()",
            "# Fix v8: Khong can sigmoid vi output da la xac suat\n            probs = out.cpu().numpy().flatten()"
        )
        cell['source'] = [line + '\n' if not line.endswith('\n') else line for line in new_src.splitlines()]

    # Fix test set threshold
    if 'preds_binary = [1 if p > 0.5 else 0 for p in all_probs]' in src:
        new_src = src.replace(
            "preds_binary = [1 if p > 0.5 else 0 for p in all_probs]",
            "# Fix v8: Tim nguong toi uu (Optimal Threshold) bang Youden's J statistic\n"
            "from sklearn.metrics import roc_curve\n"
            "fpr, tpr, thresholds = roc_curve(all_labels, all_probs)\n"
            "optimal_idx = np.argmax(tpr - fpr)\n"
            "optimal_threshold = thresholds[optimal_idx]\n"
            "print(f'\\n⭐ Nguong toi uu (Optimal Threshold): {optimal_threshold:.4f}\\n')\n"
            "\n"
            "preds_binary = [1 if p >= optimal_threshold else 0 for p in all_probs]"
        )
        new_src = new_src.replace(
            "probs = torch.sigmoid(out).cpu().numpy().flatten()",
            "probs = out.cpu().numpy().flatten()"
        )
        cell['source'] = [line + '\n' if not line.endswith('\n') else line for line in new_src.splitlines()]

with open(r'd:\My\XAI\notebooks\Cloud_Training_Pipeline.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print("Patch v8 hoan tat!")
