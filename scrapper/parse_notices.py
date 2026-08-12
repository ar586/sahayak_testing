from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import convert_date_to_iso

BASE_URL = "https://imsnsit.org/"

def parse_notices(html):
    soup = BeautifulSoup(html, "html.parser")
    notices = []

    # 🔑 Select ONLY real notice cells
    notice_cells = soup.select("td.list-data-focus")

    print("Found notice cells:", len(notice_cells))  # debug, keep for now

    for cell in notice_cells:
        row = cell.parent
        tds = row.find_all("td")

        # DATE is in the first td of the same row
        raw_date = tds[0].get_text(strip=True) if len(tds) > 0 else None
        date = convert_date_to_iso(raw_date)

        # TITLE (always present here)
        title = cell.get_text(" ", strip=True)
        if not title or len(title) < 10:
            continue

        # LINK (may be redirect)
        link = None
        a = cell.find("a")
        if a and a.get("href"):
            link = urljoin(BASE_URL, a["href"])

        # PUBLISHER
        publisher = None
        b = cell.find("b")
        if b:
            publisher = b.get_text(strip=True).replace("Published By:", "").strip()

        notices.append({
            "date": date,
            "title": title,
            "link": link,
            "publisher": publisher
        })

    return notices
