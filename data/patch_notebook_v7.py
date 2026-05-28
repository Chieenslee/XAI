import json

with open(r'd:\My\XAI\notebooks\Cloud_Training_Pipeline.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# FIX 1: Title v7
nb['cells'][0]['source'] = [
    "# Fine-tuning Chuan Y te (v7 - Production Ready)\n",
    "**Tac gia:** Antigravity AI\n\n",
    "### Changelog v7:\n",
    "- Pin `torchxrayvision==1.4.0` tranh API break khi Colab update\n",
    "- Gan `Path` truc tiep (khong for-loop) - het SettingWithCopyWarning\n",
    "- Bo `verbose=True` (deprecated PyTorch 2.x) - LR in thu cong trong log\n"
]

for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])

    # FIX 2: Pin torchxrayvision==1.4.0
    if '!pip install kaggle torchxrayvision scikit-image' in src:
        new_src = src.replace(
            '!pip install kaggle torchxrayvision scikit-image scikit-learn tqdm',
            '# Pin version de tranh API break\n!pip install kaggle "torchxrayvision==1.4.0" scikit-image scikit-learn tqdm'
        )
        # FIX 3: Thay for-loop bang 3 dong truc tiep
        new_src = new_src.replace(
            "# FIX: Dung .copy() va gan lai de tranh SettingWithCopyWarning\nfor df_part in [df_train, df_val, df_test]:\n    df_part['Path'] = df_part['Image Index'].map(extracted.get)\n",
            "# FIX v7: Gan truc tiep tung bien, khong qua for-loop - het SettingWithCopyWarning\ndf_train['Path'] = df_train['Image Index'].map(extracted.get)\ndf_val['Path']   = df_val['Image Index'].map(extracted.get)\ndf_test['Path']  = df_test['Image Index'].map(extracted.get)\n"
        )
        cell['source'] = [line + '\n' if not line.endswith('\n') else line for line in new_src.splitlines()]
        cell['source'] = [new_src]

    # FIX 4: Bo verbose=True trong ReduceLROnPlateau
    if 'verbose=True' in src:
        new_src = src.replace(
            "    optimizer, mode='max', patience=2, factor=0.5, verbose=True\n",
            "    # Bo verbose=True (deprecated PyTorch 2.x) - LR da in thu cong qua lr_now\n    optimizer, mode='max', patience=2, factor=0.5\n"
        ).replace(
            "# Scheduler theo AUC (tang tot hon) voi verbose=True\n",
            "# Scheduler theo AUC - bo verbose=True vi deprecated o PyTorch 2.x\n"
        )
        cell['source'] = [new_src]

with open(r'd:\My\XAI\notebooks\Cloud_Training_Pipeline.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=2)

print("Notebook v7 cap nhat thanh cong!")
print("Fix 1: Title v7")
print("Fix 2: Pin torchxrayvision==1.4.0")
print("Fix 3: Gan Path truc tiep (khong for-loop)")
print("Fix 4: Bo verbose=True trong scheduler")
