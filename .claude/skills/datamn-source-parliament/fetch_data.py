#!/usr/bin/env python3
"""Pull and normalize official Mongolian Parliament attendance data."""

from __future__ import annotations

import argparse
import csv
import html as html_lib
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DASHBOARD_BASE = "https://att.parliament.mn"
SESSIONS_URL = f"{DASHBOARD_BASE}/sessions"
ARCHIVE_URL = "https://www.parliament.mn/nc/635/"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = REPO_ROOT / "tools" / "sources" / "parliament" / "raw"
USER_AGENT = "data.mn Parliament attendance collector/0.1 (+https://data.mn)"

KNOWN_STATUSES = {
    "present",
    "late",
    "excused_general",
    "excused_medical",
    "mission_local",
    "mission_foreign",
    "absent_unexplained",
}


def build_http() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "gzip, deflate, br",
        }
    )
    return session


def fetch_text(http: requests.Session, url: str, delay: float) -> str:
    response = http.get(url, timeout=60)
    response.raise_for_status()
    if delay:
        time.sleep(delay)
    return response.content.decode("utf-8")


def json_constant(page: str, name: str):
    match = re.search(rf"\bconst\s+{re.escape(name)}\s*=\s*", page)
    if not match:
        raise ValueError(f"Embedded JSON constant not found: {name}")
    value, _ = json.JSONDecoder().raw_decode(page, match.end())
    return value


def parse_session_list(page: str) -> list[dict]:
    soup = BeautifulSoup(page, "html.parser")
    sessions = []
    for row in soup.select("tr.sess-row[data-date]"):
        year_kind = row.get("data-chuulgan", "").split("-", 1)
        sessions.append(
            {
                "date": row["data-date"],
                "parliamentary_year": year_kind[0] if year_kind else "",
                "session_kind": year_kind[1] if len(year_kind) == 2 else "",
                "agenda_count": integer_attr(row, "data-sort-agenda"),
                "list_on_time": integer_attr(row, "data-sort-ontime"),
                "list_late": integer_attr(row, "data-sort-late"),
                "list_excused": integer_attr(row, "data-sort-excused"),
                "list_missed": integer_attr(row, "data-sort-missed"),
            }
        )
    if not sessions:
        raise ValueError("No session rows found on the sessions page")
    return sessions


def integer_attr(tag, name: str) -> int | None:
    value = tag.get(name)
    return int(value) if value not in (None, "") else None


def parse_detail(page: str, date: str) -> dict:
    marker = re.search(
        rf"{re.escape(date)}\s*"
        rf"·\s*(?P<scheduled>\d{{2}}:\d{{2}})\s*цагт товлогдсон"
        rf"(?:\s*·\s*(?P<actual>\d{{2}}:\d{{2}})\s*цагт эхэлсэн)?",
        page,
    )
    if not marker:
        marker = re.search(
            rf"{re.escape(date)}\s*"
            rf"·\s*(?P<actual>\d{{2}}:\d{{2}})\s*цагт эхэлсэн",
            page,
        )
    if not marker:
        raise ValueError(f"Could not parse sitting timing header for {date}")
    title_match = re.search(r"<h2[^>]*>(.*?)</h2>", page[marker.end() :], re.S)
    title = ""
    if title_match:
        title = re.sub(r"<[^>]+>", "", title_match.group(1))
        title = " ".join(html_lib.unescape(title).split())
    return {
        "scheduled_start_time": marker.groupdict().get("scheduled") or "",
        "actual_start_time": marker.group("actual") or "",
        "title_mn": title,
    }


def parse_archive_page(page: str, page_number: int) -> tuple[list[dict], int | None, int]:
    soup = BeautifulSoup(page, "html.parser")
    rows = []
    for anchor in soup.select('h3 a[href^="/nn/"]'):
        container = anchor.find_parent("div", class_="grid-inner")
        date_node = container.select_one(".entry-meta span") if container else None
        rows.append(
            {
                "publication_date": date_node.get_text(strip=True) if date_node else "",
                "title_mn": " ".join(anchor.get_text(" ", strip=True).split()),
                "article_url": urljoin(ARCHIVE_URL, anchor["href"]),
                "archive_page": page_number,
            }
        )
    text = soup.get_text(" ", strip=True)
    total_match = re.search(r"Нийт:\s*(\d+)", text)
    reported_total = int(total_match.group(1)) if total_match else None
    pages = [
        int(match.group(1))
        for anchor in soup.select('a[href*="page="]')
        if (match := re.search(r"[?&]page=(\d+)", anchor.get("href", "")))
    ]
    return rows, reported_total, max(pages, default=1)


def parse_attachment_url(page: str) -> str:
    soup = BeautifulSoup(page, "html.parser")
    candidates = []
    for anchor in soup.select('a[href*="/files/"]'):
        href = urljoin("https://www.parliament.mn/", anchor.get("href", ""))
        label = " ".join(anchor.get_text(" ", strip=True).split()).lower()
        candidates.append(("татах" in label or "download" in label, href))
    if not candidates:
        return ""
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    return candidates[0][1]


def time_minutes(value: str) -> int | None:
    if not value:
        return None
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def difference_minutes(value: str, base: str) -> int | None:
    value_minutes = time_minutes(value)
    base_minutes = time_minutes(base)
    if value_minutes is None or base_minutes is None:
        return None
    return value_minutes - base_minutes


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def pull(args: argparse.Namespace) -> dict:
    http = build_http()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    list_page = fetch_text(http, SESSIONS_URL, args.delay)
    list_rows = parse_session_list(list_page)
    dates = sorted(row["date"] for row in list_rows)
    latest_date = dates[-1]

    latest_page = fetch_text(http, f"{SESSIONS_URL}/{latest_date}", args.delay)
    members = json_constant(latest_page, "members")
    parties = json_constant(latest_page, "parties")
    history_by_member = json_constant(latest_page, "historyByMember")
    recent_sessions = json_constant(latest_page, "recentSessions")

    member_ids = {member["id"] for member in members}
    if set(history_by_member) != member_ids:
        raise ValueError("Member IDs and history payload IDs disagree")

    histories = []
    history_dates = set()
    unknown_statuses = set()
    for member_id, entries in history_by_member.items():
        if len(entries) != len(dates):
            raise ValueError(
                f"{member_id} has {len(entries)} records; expected {len(dates)}"
            )
        for entry in entries:
            history_dates.add(entry["date"])
            unknown_statuses.add(entry["status"])
            histories.append({"member_id": member_id, **entry})
    unknown_statuses -= KNOWN_STATUSES
    if unknown_statuses:
        raise ValueError(f"Unknown attendance statuses: {sorted(unknown_statuses)}")
    if history_dates != set(dates):
        raise ValueError("Session-list dates and member-history dates disagree")

    by_date = defaultdict(list)
    session_id_by_date = {}
    for row in histories:
        by_date[row["date"]].append(row)
        previous = session_id_by_date.setdefault(row["date"], row["sessionId"])
        if previous != row["sessionId"]:
            raise ValueError(f"Multiple session IDs found for {row['date']}")
    for date, rows in by_date.items():
        if len(rows) != len(members):
            raise ValueError(f"{date} has {len(rows)} MP rows; expected {len(members)}")

    details = {latest_date: parse_detail(latest_page, latest_date)}
    if not args.skip_session_details:
        for position, date in enumerate(dates, start=1):
            if date not in details:
                page = fetch_text(http, f"{SESSIONS_URL}/{date}", args.delay)
                details[date] = parse_detail(page, date)
            if position % 25 == 0 or position == len(dates):
                print(f"Fetched sitting details: {position}/{len(dates)}", flush=True)

    archive_rows = []
    archive_reported_total = None
    if not args.skip_archive:
        first_archive = fetch_text(http, ARCHIVE_URL, args.delay)
        first_rows, archive_reported_total, archive_page_count = parse_archive_page(
            first_archive, 1
        )
        archive_rows.extend(first_rows)
        for page_number in range(2, archive_page_count + 1):
            page = fetch_text(http, f"{ARCHIVE_URL}?page={page_number}", args.delay)
            rows, _, _ = parse_archive_page(page, page_number)
            archive_rows.extend(rows)
        archive_by_url = {row["article_url"]: row for row in archive_rows}
        archive_rows = sorted(
            archive_by_url.values(), key=lambda row: (row["publication_date"], row["article_url"])
        )
        if archive_reported_total is not None and len(archive_rows) != archive_reported_total:
            raise ValueError(
                f"Archive returned {len(archive_rows)} unique posts; "
                f"reported total is {archive_reported_total}"
            )

    party_by_id = {party["id"]: party for party in parties}
    recent_by_date = {row["date"]: row for row in recent_sessions}
    archive_url_by_title = {row["title_mn"]: row["article_url"] for row in archive_rows}
    article_url_by_date = {}
    for date in dates:
        detail = details.get(date, {})
        recent = recent_by_date.get(date, {})
        title = detail.get("title_mn", "")
        article_url_by_date[date] = (
            recent.get("sourceUrl") or archive_url_by_title.get(title, "")
        )

    attachment_by_article = {}
    if not args.skip_attachments:
        article_urls = sorted({url for url in article_url_by_date.values() if url})
        for position, article_url in enumerate(article_urls, start=1):
            article_page = fetch_text(http, article_url, args.delay)
            attachment_by_article[article_url] = parse_attachment_url(article_page)
            if position % 25 == 0 or position == len(article_urls):
                print(
                    f"Fetched article attachments: {position}/{len(article_urls)}",
                    flush=True,
                )
    member_rows = []
    for member in sorted(members, key=lambda row: row["ord"]):
        party = party_by_id.get(member.get("party"), {})
        member_rows.append(
            {
                "member_id": member["id"],
                "ordinal": member.get("ord", ""),
                "name_mn": member.get("name", ""),
                "surname_initial_mn": member.get("surname", ""),
                "given_name_mn": member.get("given", ""),
                "party_code": member.get("party", ""),
                "party_name_mn": party.get("fullMn", ""),
                "party_name_en": party.get("fullEn", ""),
                "district": member.get("district", ""),
                "district_label_mn": member.get("districtLabel", ""),
                "mandate_label_mn": member.get("mandateLabel", ""),
                "committee_code": member.get("committee", ""),
                "committee_name_mn": member.get("committeeMn", ""),
                "profile_url": (
                    f"https://www.parliament.mn/cv/{member['cvId']}/"
                    if member.get("cvId")
                    else ""
                ),
                "photo_url": member.get("photoUrl", ""),
                "is_flagged": member.get("flagged", False),
            }
        )

    list_by_date = {row["date"]: row for row in list_rows}
    session_rows = []
    attendance_rows = []
    for session_number, date in enumerate(dates, start=1):
        list_row = list_by_date[date]
        detail = details.get(date, {})
        recent = recent_by_date.get(date, {})
        status_counts = Counter(row["status"] for row in by_date[date])
        provisional = any(row.get("lateProvisional", False) for row in by_date[date])
        scheduled = detail.get("scheduled_start_time", "")
        actual = detail.get("actual_start_time", "")
        title = detail.get("title_mn", "")
        article_url = article_url_by_date[date]
        session_rows.append(
            {
                "session_id": session_id_by_date[date],
                "session_number": session_number,
                "date": date,
                "parliamentary_year": list_row["parliamentary_year"],
                "session_kind": list_row["session_kind"],
                "scheduled_start_time": scheduled,
                "actual_start_time": actual,
                "start_delay_minutes": difference_minutes(actual, scheduled),
                "title_mn": title,
                "agenda_count": list_row["agenda_count"],
                "on_time": status_counts["present"],
                "late": status_counts["late"],
                "excused_general": status_counts["excused_general"],
                "excused_medical": status_counts["excused_medical"],
                "mission_local": status_counts["mission_local"],
                "mission_foreign": status_counts["mission_foreign"],
                "absent_unexplained": status_counts["absent_unexplained"],
                "total_members": len(members),
                "data_provisional": provisional,
                "dashboard_url": f"{SESSIONS_URL}/{date}",
                "source_article_url": article_url,
                "source_attachment_url": (
                    recent.get("excelUrl")
                    or attachment_by_article.get(article_url, "")
                ),
            }
        )
        for row in sorted(by_date[date], key=lambda item: item["member_id"]):
            arrival = row.get("arrivalTime") or ""
            scheduled_delta = difference_minutes(arrival, scheduled)
            actual_delta = difference_minutes(arrival, actual)
            attendance_rows.append(
                {
                    "session_id": row["sessionId"],
                    "date": date,
                    "member_id": row["member_id"],
                    "status": row["status"],
                    "arrival_time": arrival,
                    "official_arrival_class": (
                        "on_time"
                        if row["status"] == "present"
                        else "late" if row["status"] == "late" else ""
                    ),
                    "scheduled_arrival_class": (
                        "on_time"
                        if row["status"] in {"present", "late"}
                        and scheduled_delta is not None
                        and scheduled_delta <= 0
                        else "late"
                        if row["status"] in {"present", "late"}
                        and scheduled_delta is not None
                        else ""
                    ),
                    "scheduled_start_time": scheduled,
                    "actual_start_time": actual,
                    "minutes_from_scheduled_start": scheduled_delta,
                    "minutes_from_actual_start": actual_delta,
                    "late_provisional": row.get("lateProvisional", False),
                    "did_not_convene": row.get("didNotConvene", False),
                }
            )

    write_csv(
        output / "parliament-members.csv",
        [
            "member_id", "ordinal", "name_mn", "surname_initial_mn",
            "given_name_mn", "party_code", "party_name_mn", "party_name_en",
            "district", "district_label_mn", "mandate_label_mn",
            "committee_code", "committee_name_mn", "profile_url", "photo_url",
            "is_flagged",
        ],
        member_rows,
    )
    write_csv(
        output / "parliament-sessions.csv",
        [
            "session_id", "session_number", "date", "parliamentary_year",
            "session_kind", "scheduled_start_time", "actual_start_time",
            "start_delay_minutes", "title_mn", "agenda_count", "on_time", "late",
            "excused_general", "excused_medical", "mission_local",
            "mission_foreign", "absent_unexplained", "total_members",
            "data_provisional", "dashboard_url", "source_article_url",
            "source_attachment_url",
        ],
        session_rows,
    )
    write_csv(
        output / "parliament-attendance.csv",
        [
            "session_id", "date", "member_id", "status", "arrival_time",
            "official_arrival_class", "scheduled_arrival_class",
            "scheduled_start_time", "actual_start_time",
            "minutes_from_scheduled_start", "minutes_from_actual_start",
            "late_provisional", "did_not_convene",
        ],
        attendance_rows,
    )
    write_csv(
        output / "parliament-archive.csv",
        ["publication_date", "title_mn", "article_url", "archive_page"],
        archive_rows,
    )

    metadata = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "dashboard": DASHBOARD_BASE,
            "sessions": SESSIONS_URL,
            "publication_archive": ARCHIVE_URL,
        },
        "coverage": {"first_sitting": dates[0], "last_sitting": dates[-1]},
        "counts": {
            "members": len(member_rows),
            "sessions": len(session_rows),
            "attendance_records": len(attendance_rows),
            "archive_posts": len(archive_rows),
        },
        "status_counts": dict(Counter(row["status"] for row in attendance_rows)),
        "session_details_complete": not args.skip_session_details,
        "archive_complete": not args.skip_archive,
        "attachments_complete": not args.skip_attachments,
        "archive_reported_total": archive_reported_total,
        "attachment_links": sum(bool(value) for value in attachment_by_article.values()),
    }
    write_json(output / "parliament-pull.meta.json", metadata)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--delay", type=float, default=0.25,
        help="Seconds to wait after each request (default: 0.25)",
    )
    parser.add_argument(
        "--skip-session-details", action="store_true",
        help="Skip per-sitting pages; timing/title fields will be incomplete",
    )
    parser.add_argument(
        "--skip-archive", action="store_true",
        help="Skip the parliament.mn publication archive catalog",
    )
    parser.add_argument(
        "--skip-attachments", action="store_true",
        help="Skip attendance-article pages used to discover source attachments",
    )
    args = parser.parse_args()
    if args.delay < 0:
        parser.error("--delay cannot be negative")
    return args


if __name__ == "__main__":
    result = pull(parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2))
