from urllib.parse import urlparse

def classify_link(url):
    if not url:
        return "none"

    netloc = urlparse(url).netloc.lower()

    if "imsnsit.org" in netloc:
        return "internal"

    if "drive.google.com" in netloc:
        return "gdrive"

    if "docs.google.com" in netloc:
        return "gdocs"

    return "external"
