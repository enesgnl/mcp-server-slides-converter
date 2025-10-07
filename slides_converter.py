import base64
import fitz
from fpdf import FPDF
import os
import io
import tempfile
from fastmcp import FastMCP

mcp = FastMCP("SlideConverter")

# Dosya yolları yerine bellek içi işlemleri tercih etmek daha güvenli ve hızlıdır
def convert_pdf_in_memory(input_pdf_bytes, dpi=72) -> bytes:
    doc = fitz.open(stream=input_pdf_bytes, filetype="pdf")
    total_pages = len(doc)

    w, h = 210, 297  # A4 boyutları (mm)
    thumb_w, thumb_h = w / 2 - 10, h / 2 - 10
    positions = [
        (5, 5), (w / 2 + 5, 5),
        (5, h / 2 + 5), (w / 2 + 5, h / 2 + 5)
    ]

    pdf = FPDF(orientation='P', unit='mm', format='A4')

    for i in range(0, total_pages, 4):
        pdf.add_page()
        for j in range(4):
            if i + j >= total_pages:
                break
            page = doc.load_page(i + j)
            pix = page.get_pixmap(dpi=dpi)
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                pix.save(tmp_img.name)
                x, y = positions[j]
                pdf.image(tmp_img.name, x=x, y=y, w=thumb_w, h=thumb_h)
            os.remove(tmp_img.name)

    # fpdf2 farklı sürümlerde str/bytes/bytearray döndürebilir; güvenli şekilde bytes'a çevir
    output_data = pdf.output(dest='S')
    if isinstance(output_data, str):
        pdf_bytes = output_data.encode('latin1')
    elif isinstance(output_data, (bytes, bytearray)):
        pdf_bytes = bytes(output_data)
    else:
        raise TypeError(f"Unexpected output type from FPDF.output: {type(output_data)}")

    return pdf_bytes

@mcp.tool()
def convert_pdf_4up(input_pdf_base64: str = "", input_pdf_path: str = "", dpi: int = 72) -> dict:
    """Verilen PDF'i her sayfada 4 küçük slayt olacak şekilde yeni bir PDF'e dönüştürür.

    Girdi olarak base64 kodlu PDF verisi veya yerel dosya yolu alır; çıktı olarak base64 kodlu dönüştürülmüş PDF verir.

    - input_pdf_base64: Base64 kodlu orijinal PDF baytları
    - input_pdf_path: Yerel PDF dosya yolu (alternatif)
    - dpi: Render DPI (varsayılan 72)
    """
    try:
        if input_pdf_base64:
            input_bytes = base64.b64decode(input_pdf_base64)
        elif input_pdf_path:
            if not os.path.exists(input_pdf_path):
                return {"error": f"PDF not found at path: {input_pdf_path}"}
            with open(input_pdf_path, "rb") as f:
                input_bytes = f.read()
        else:
            return {"error": "Provide either input_pdf_base64 or input_pdf_path"}

        output_bytes = convert_pdf_in_memory(input_bytes, dpi=dpi)
        output_b64 = base64.b64encode(output_bytes).decode('ascii')
        return {
            "filename": "converted_4slayt.pdf",
            "pdf_base64": output_b64,
            "mime_type": "application/pdf"
        }
    except Exception as exc:
        return {"error": f"PDF conversion failed: {str(exc)}"}


if __name__ == '__main__':
    mcp.run() 