import io
import os
import base64
from pypdf import PdfReader
from mistralai import Mistral

def extract_text_from_pdf(pdf_bytes):
    """
    Extracts text from a PDF byte stream.
    Returns the extracted text or an empty string if extraction fails.
    """
    try:
        # Wrap bytes in a file-like object
        f = io.BytesIO(pdf_bytes)
        reader = PdfReader(f)
        
        text = []
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text.append(content)
        
        return "\n".join(text)
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def extract_text_from_image(image_bytes):
    """
    Extracts text from an image byte stream using Mistral OCR.
    """
    mistral_text = ""
    api_key = os.environ.get("MISTRAL_API_KEY")
    
    if api_key:
        try:
            client = Mistral(api_key=api_key)
            
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{base64_image}"

            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "image_url",
                    "image_url": image_url
                }
            )
            
            # Combine text from pages (usually just one for an image)
            for page in ocr_response.pages:
                mistral_text += page.markdown + "\n"
            
            mistral_text = mistral_text.strip()

        except Exception as e:
            print(f"Error extracting image text with Mistral: {e}")
            # Fallthrough to fallback
            
    if not mistral_text:
        return _extract_with_gemini(image_bytes)
        
    return mistral_text

def _extract_with_gemini(image_bytes):
    """
    Fallback extraction using Gemini 2.5 Pro.
    """
    import google.generativeai as genai
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found. Skipping Gemini fallback.")
        return ""

    try:
        print("Switching to Gemini fallback...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        response = model.generate_content([
            "You are a strict OCR engine. Your sole purpose is to extract text from the image exactly as it appears. Do not interpret, summarize, or describe the image. Output ONLY the extracted text.",
            {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
        ])
        
        return response.text.strip()
    except Exception as e:
        print(f"Error extraction with Gemini: {e}")
        return ""
