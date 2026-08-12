def download_protected_resource(session, url, phpsessid=None):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,en-IN;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "imsnsit.org",
        "Referer": "https://imsnsit.org/imsnsit/student.htm",
        "Sec-Fetch-Dest": "frame",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36 Edg/134.0.0.0",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Microsoft Edge\";v=\"134\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android"
    }

    if phpsessid:
        headers["Cookie"] = f"PHPSESSID={phpsessid}"
    
    # We use a fresh request instead of the session to ensure exact headers if needed, 
    # or we can update the session. The user requirement said "pass it as a header".
    # Since we are passing explicit headers, using session.get with headers kwarg 
    # will merge/override.
    
    response = session.get(url, headers=headers, stream=True, timeout=20)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    content = response.content

    return content, content_type
