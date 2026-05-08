from __future__ import annotations

import re
from urllib.parse import urlparse


DIRECT_AFFILIATE_DOMAINS = [
    "a8.net",
    "px.a8.net",
    "a8cv.jp",
    "af.moshimo.com",
    "t.afi-b.com",
    "acs.valuecommerce.com",
    "ck.jp.ap.valuecommerce.com",
    "accesstrade.net",
    "valuecommerce.com",
    "rentracks.jp",
]
URL_RE = re.compile(r"https?://[^\s)）]+|www\.[^\s)）]+", re.IGNORECASE)
AFFILIATE_HINT_RE = re.compile(r"(?:affiliate|aff|ref|ad|afs|afi|asp|banner|linkshare)", re.IGNORECASE)


def _normalize_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


def _host_matches(url: str, domain: str) -> bool:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    host = parsed.netloc.lower().removeprefix("www.")
    return host == domain or host.endswith(f".{domain}")


def detect_direct_affiliate_link(text: str, registered_urls: list[str] | None = None) -> dict[str, object]:
    if not text:
        return {"detected": False, "matches": [], "notes": []}

    matches: list[str] = []
    notes: list[str] = []
    lowered = text.lower()

    for domain in DIRECT_AFFILIATE_DOMAINS:
        if domain in lowered:
            matches.append(domain)
            notes.append(f"{domain} を含むためASP直リンクの可能性があります")

    urls = URL_RE.findall(text)
    for url in urls:
        if any(_host_matches(url, domain) for domain in DIRECT_AFFILIATE_DOMAINS):
            matches.append(url)
        if AFFILIATE_HINT_RE.search(url):
            notes.append(f"{url} はaffiliate/ref/ad系パラメータを含む可能性があります")

    for registered_url in registered_urls or []:
        normalized = _normalize_url(registered_url)
        if not normalized:
            continue
        if normalized in lowered or registered_url.lower() in lowered:
            matches.append(registered_url)
            notes.append("登録済みアフィリエイトURLが本文に含まれています")

    unique_matches = list(dict.fromkeys(matches))
    unique_notes = list(dict.fromkeys(notes))
    detected = bool(unique_matches) or any("affiliate/ref/ad" in note for note in unique_notes)
    return {"detected": detected, "matches": unique_matches, "notes": unique_notes}

