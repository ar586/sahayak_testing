import re
import hashlib


def make_safe_public_id(title: str) -> str:
    """
    Converts a notice title into a Cloudinary-safe public_id.
    Removes special characters, shortens length, and adds a hash.
    """

    # Normalize
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "_", title)
    title = title.strip("_")

    # Hash to avoid collisions
    suffix = hashlib.md5(title.encode()).hexdigest()[:8]

    return f"sahayak/notices/{title[:40]}_{suffix}"


def drive_view_to_download(url: str) -> str | None:
    """
    Converts a Google Drive 'view' URL into a direct download URL.

    Example:
    https://drive.google.com/file/d/FILE_ID/view
    ->
    https://drive.google.com/uc?id=FILE_ID&export=download
    """
    try:
        if "/d/" not in url:
            return None

        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    except Exception:
        return None

def convert_date_to_iso(date_str: str) -> str | None:
    """
    Converts DD-MM-YYYY string to YYYY-MM-DD string (ISO 8601).
    Returns None if parsing fails.
    """
    if not date_str:
        return None
        
    try:
        parts = date_str.strip().split("-")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str # Return original if not in expected format
    except Exception:
        return date_str
