import os
from pathlib import Path
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
assert api_key, "MISTRAL_API_KEY manquante"

PDF_PATH = Path("pdf/02_a.pdf").resolve()
assert PDF_PATH.is_file(), f"Fichier introuvable: {PDF_PATH}"

client = Mistral(api_key=api_key)

# 1) Upload
uploaded = client.files.upload(
    file={"file_name": PDF_PATH.name, "content": open(PDF_PATH, "rb")},
    purpose="ocr",
)
print("✅ Upload OK. file_id =", uploaded.id)

# 2) URL signée
signed = client.files.get_signed_url(file_id=uploaded.id)
print("🔗 Signed URL =", signed.url)

# 3) OCR
resp = client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "document_url", "document_url": signed.url},
    include_image_base64=False,      # passe à True si tu veux récupérer les images
)

# 4) Concaténer le markdown de toutes les pages
all_md = "\n\n".join(page.markdown for page in resp.pages)
out_md = PDF_PATH.with_suffix(".md")
out_md.write_text(all_md, encoding="utf-8")
print(f"📄 {len(resp.pages)} page(s) OCRisées → {out_md}")
