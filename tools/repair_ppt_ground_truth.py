from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path


PPTX = Path(r"D:\My\XAI\Doc\XAI_Medical_Sieu_Vip_PPT_Master_GroundTruth.pptx")
TMP = PPTX.with_suffix(".repairing.pptx")


def replace_text_nodes(xml: str, mapper):
    index = {"i": 0}

    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        text = html.unescape(raw)
        new = mapper(text, index["i"])
        index["i"] += 1
        if new is None:
            new = text
        return f"<a:t>{html.escape(new, quote=False)}</a:t>"

    return re.sub(r"<a:t>(.*?)</a:t>", repl, xml)


def repair_slide3(xml: str) -> str:
    def mapper(text: str, idx: int):
        if text == "NIH NIH 112.120 + CheXpert 224.316 + MIMIC 377.110 + PadChest ~160.000 và PadChest trong weights all.":
            return "NIH ChestX-ray14, CheXpert, MIMIC-CXR và PadChest trong weights all."
        if text in {"o", "n"}:
            return ""
        return text

    return replace_text_nodes(xml, mapper)


def repair_slide4(xml: str) -> str:
    return xml.replace(
        "Hold-out test set Kaggle: Accuracy 81.46%, AUC 6.82%.",
        "Hold-out test set Kaggle: Accuracy 81.46%, AUC 0.87.",
    )


def repair_slide8(xml: str) -> str:
    seen = {"six": 0, "auc": 0}

    def mapper(text: str, idx: int):
        if text == "6.82%":
            seen["six"] += 1
            if seen["six"] == 1:
                return "0.87"
            return text
        if text == "AUC":
            seen["auc"] += 1
            if seen["auc"] == 3:
                return "Hold-out"
            return text
        if text == "AUC cao giúp giảm bỏ sót ca nghi ngờ. Threshold cân bằng giữa phát hiện và cảnh báo sai.":
            return "Ngưỡng 0.0682 được chọn bằng Youden's J trên ROC để giảm bỏ sót bệnh, không dùng 50% mặc định."
        if text.startswith("Metric đề xuất:"):
            return "Chưa có TP/FP/TN/FN export cứng; cần bổ sung confusion matrix và ROC artifact khi nghiệm thu học thuật."
        return text

    return replace_text_nodes(xml, mapper)


def main() -> None:
    with zipfile.ZipFile(PPTX, "r") as zin, zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "ppt/slides/slide3.xml":
                data = repair_slide3(data.decode("utf-8")).encode("utf-8")
            elif item.filename == "ppt/slides/slide4.xml":
                data = repair_slide4(data.decode("utf-8")).encode("utf-8")
            elif item.filename == "ppt/slides/slide8.xml":
                data = repair_slide8(data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    TMP.replace(PPTX)
    print(f"Repaired: {PPTX}")


if __name__ == "__main__":
    main()
