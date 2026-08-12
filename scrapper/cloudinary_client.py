# scraper/cloudinary_client.py
import cloudinary
import cloudinary.uploader

import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)
def upload_to_cloudinary(file_bytes, filename):
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",   # REQUIRED for PDFs
        public_id=f"sahayak/notices/{filename}",
        overwrite=True
    )
    return result["secure_url"]
def process_notice(session, notice):
    content, content_type = download_protected_resource(
        session,
        notice["link"]
    )

    # Decide filename
    safe_title = notice["title"][:50].replace(" ", "_")
    filename = f"{safe_title}.pdf" if "pdf" in content_type.lower() else f"{safe_title}.html"

    cloud_url = upload_to_cloudinary(content, filename)

    notice["cached_url"] = cloud_url
    notice["content_type"] = content_type

    return notice
