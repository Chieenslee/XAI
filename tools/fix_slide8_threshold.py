from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path


PPTX = Path(r"D:\My\XAI\Doc\XAI_Medical_Sieu_Vip_PPT_Master_GroundTruth.pptx")
TMP = PPTX.with_suffix(".slide8fix.pptx")


def fix_slide8(xml: str) -> str:
    count_087 = {"n": 0}

    def repl(match: re.Match[str]) -> str:
        text = html.unescape(match.group(1))
        if text == "0.87":
            count_087["n"] += 1
            if count_087["n"] == 2:
                text = "6.82%"
        return f"<a:t>{html.escape(text, quote=False)}</a:t>"

    return re.sub(r"<a:t>(.*?)</a:t>", repl, xml)


def main() -> None:
    with zipfile.ZipFile(PPTX, "r") as zin, zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "ppt/slides/slide8.xml":
                data = fix_slide8(data.decode("utf-8")).encode("utf-8")
            zout.writestr(item, data)
    TMP.replace(PPTX)
    print(f"Fixed slide 8 threshold: {PPTX}")


if __name__ == "__main__":
    main()
