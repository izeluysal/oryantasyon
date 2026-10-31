"""Dağıtım paketlerini üretir: dist/ klasörüne SCORM 1.2 zip'i ve şirket içi web zip'i.

Kullanım:  python program/package.py
"""
import os
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "..", "dist")
CORE = ["index.html", "style.css", "app.js", "content.js"]
AUDIO = sorted(f for f in os.listdir(os.path.join(ROOT, "audio")) if f.endswith(".mp3"))

MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="tr.com.ecekalibrasyon.oryantasyon" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="org1">
    <organization identifier="org1">
      <title>Ece Kalibrasyon Oryantasyon Programı</title>
      <item identifier="item1" identifierref="res1"><title>Hassas Metroloji Yolculuğu</title></item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="res1" type="webcontent" adlcp:scormtype="sco" href="index.html">
{files}
    </resource>
  </resources>
</manifest>
"""


def main():
    os.makedirs(DIST, exist_ok=True)
    files = CORE + ["audio/" + a for a in AUDIO]
    manifest = MANIFEST.format(files="\n".join(f'      <file href="{f}"/>' for f in files))
    scorm = os.path.join(DIST, "ece-oryantasyon-scorm12.zip")
    with zipfile.ZipFile(scorm, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("imsmanifest.xml", manifest)
        for f in files:
            z.write(os.path.join(ROOT, f), f)
    web = os.path.join(DIST, "ece-oryantasyon-web.zip")
    with zipfile.ZipFile(web, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files + ["yonetici.html", "README.md"]:
            z.write(os.path.join(ROOT, f), "oryantasyon/" + f)
    for p in (scorm, web):
        print(os.path.basename(p), round(os.path.getsize(p) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
