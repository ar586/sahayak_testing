from link_classifier import classify_link
from downloader import download_protected_resource
from cloudinary_client import upload_to_cloudinary
from utils import make_safe_public_id, drive_view_to_download
import requests

from session_manager import get_phpsessid
from summarizer import generate_summary
from tagger import extract_tags

def process_notice(session, notice):
    link = notice.get("link")
    link_type = classify_link(link)

    notice["link_type"] = link_type

    # 1️⃣ No attachment
    if link_type == "none":
        notice["status"] = "no_attachment"
        return notice

    # 2️⃣ Internal (session-protected)
    if link_type == "internal":
        phpsessid = get_phpsessid(session)
        content, content_type = download_protected_resource(session, link, phpsessid=phpsessid)

    # 3️⃣ Google Drive file
    elif link_type == "gdrive":
        download_url = drive_view_to_download(link)
        if not download_url:
            notice["status"] = "gdrive_unhandled"
            return notice

        resp = requests.get(download_url, stream=True, timeout=20)
        resp.raise_for_status()
        content = resp.content
        content_type = resp.headers.get("Content-Type", "")

    # 4️⃣ Google Docs / Sheets
    elif link_type == "gdocs":
        notice["status"] = "external_doc"
        notice["cached_url"] = link  # keep original
        return notice

    else:
        notice["status"] = "external_unknown"
        return notice

    # Upload downloadable content
    public_id = make_safe_public_id(notice["title"])
    cloud_url = upload_to_cloudinary(content, public_id)
    
    # Extract text if PDF
    extracted_text = ""
    if "pdf" in content_type.lower():
        from extractor import extract_text_from_pdf
        extracted_text = extract_text_from_pdf(content)
        # Truncate to avoid massive JSON files
        if len(extracted_text) > 5000:
            extracted_text = extracted_text[:5000] + "...[truncated]"

    # Extract text if Image
    elif "image" in content_type.lower():
        from extractor import extract_text_from_image
        extracted_text = extract_text_from_image(content)
        # Truncate to avoid massive JSON files
        if len(extracted_text) > 5000:
            extracted_text = extracted_text[:5000] + "...[truncated]"

    notice["cached_url"] = cloud_url
    notice["content_type"] = content_type
    notice["extracted_text"] = extracted_text
    notice["summary"] = generate_summary(extracted_text)
    notice["tags"] = extract_tags(extracted_text)
    notice["status"] = "cached"

    return notice
