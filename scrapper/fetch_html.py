import requests
headers = {
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
  "Accept-Encoding": "gzip, deflate, br, zstd",
  "Accept-Language": "en-US,en;q=0.9",
  "Cache-Control": "max-age=0",
  "Connection": "keep-alive",
  "Host": "www.imsnsit.org",
  "Origin": "https://www.imsnsit.org",
  "Referer": "https://www.imsnsit.org/imsnsit/student_login.php?lo=1",
  "Sec-Fetch-Dest": "frame",
  "Sec-Fetch-Mode": "navigate",
  "Sec-Fetch-Site": "same-origin",
  "Sec-Fetch-User": "?1",
  "Sec-GPC": "1",
  "Upgrade-Insecure-Requests": "1",
  "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
  "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Brave\";v=\"140\"",
  "sec-ch-ua-mobile": "?1",
  "sec-ch-ua-platform": "\"Android\""
}
def fetch_notices_html(session):
    url="https://www.imsnsit.org/imsnsit/notifications.php"
    
    # We can use the headers from session_manager or update here if needed.
    # For now, let's use the session as is, assuming session_manager set it up.
    # But wait, session_manager sets minimal headers. 
    # The previous code in this file had specific headers.
    # Let's update the session with these headers if not present, OR just use them for this request.
    
    # Actually, session_manager.get_phpsessid sets the good headers on the session!
    # So we can just use session.get(url).
    
    response = session.get(url)
    response.raise_for_status()
    # encoding might be needed
    response.encoding = 'utf-8' 
    return response.text