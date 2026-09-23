#!/usr/bin/env python3
"""Build the two bilingual public Parliament attendance datasets."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sqlite3
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TOOLS = ROOT / "tools"
PUBLIC = ROOT / "data.mn" / "public" / "datasets"
RAW = HERE / "raw"
sys.path.insert(0, str(TOOLS))

from registry import Dataset, Registry, Version  # noqa: E402


COMMITTEE_EN = {
    "Аюулгүй байдал, гадаад бодлогын байнгын хороо": "Standing Committee on Security and Foreign Policy",
    "Байгаль орчин, хүнс, хөдөө аж ахуйн байнгын хороо": "Standing Committee on Environment, Food and Agriculture",
    "Төрийн байгуулалтын байнгын хороо": "Standing Committee on State Structure",
    "Төсвийн байнгын хороо": "Standing Committee on Budget",
    "Хууль зүйн байнгын хороо": "Standing Committee on Legal Affairs",
    "Хүний хөгжил, нийгмийн бодлогын байнгын хороо": "Standing Committee on Human Development and Social Policy",
    "Эдийн засгийн байнгын хороо": "Standing Committee on Economy",
    "Өргөдлийн байнгын хороо": "Standing Committee on Petitions",
}

SESSION_KIND = {
    "SPRING": ("Spring regular session", "Хаврын ээлжит чуулган"),
    "AUTUMN": ("Autumn regular session", "Намрын ээлжит чуулган"),
    "EXTRAORDINARY": ("Extraordinary session", "Ээлжит бус чуулган"),
}

MP_METRICS = [
    ("sittings", "Sittings", "Хуралдаан", "count", "тоо"),
    ("physical_attendance", "Physically attended", "Биеэр оролцсон", "count", "тоо"),
    ("physical_attendance_rate", "Physical attendance rate", "Биеэр оролцсон хувь", "percent", "хувь"),
    ("official_on_time", "Officially on time", "Албан ёсоор цагтаа ирсэн", "count", "тоо"),
    ("official_late", "Officially late", "Албан ёсоор хоцорсон", "count", "тоо"),
    ("official_on_time_rate", "Official on-time rate among appearances", "Биеэр оролцсон үеийн албан ёсны цагтаа ирэлтийн хувь", "percent", "хувь"),
    ("scheduled_observations", "Arrivals with a published scheduled start", "Товлосон цаг нийтлэгдсэн ирэлт", "count", "тоо"),
    ("scheduled_on_time", "Arrived by scheduled start", "Товлосон цагт багтаж ирсэн", "count", "тоо"),
    ("scheduled_late", "Arrived after scheduled start", "Товлосон цагаас хойш ирсэн", "count", "тоо"),
    ("scheduled_on_time_rate", "Scheduled-start on-time rate", "Товлосон цагтаа ирэлтийн хувь", "percent", "хувь"),
    ("median_late_minutes", "Median minutes late after actual start", "Бодит эхлэлээс хоцорсон медиан минут", "minutes", "минут"),
    ("average_late_minutes", "Average minutes late after actual start", "Бодит эхлэлээс хоцорсон дундаж минут", "minutes", "минут"),
    ("unexplained_absence", "Unexplained absences", "Тайлбаргүй тасалсан", "count", "тоо"),
    ("unexplained_absence_rate", "Unexplained absence rate", "Тайлбаргүй таслалтын хувь", "percent", "хувь"),
    ("general_leave", "General leave", "Чөлөөтэй", "count", "тоо"),
    ("medical_leave", "Medical leave", "Эмнэлгийн чөлөө", "count", "тоо"),
    ("domestic_mission", "Domestic official assignments", "Орон нутгийн томилолт", "count", "тоо"),
    ("foreign_mission", "Foreign official assignments", "Гадаад томилолт", "count", "тоо"),
]

SESSION_METRICS = [
    ("agenda_count", "Agenda items", "Хэлэлцэх асуудал", "count", "тоо"),
    ("start_delay_minutes", "Sitting start delay", "Хуралдаан эхэлсэн хоцролт", "minutes", "минут"),
    ("on_time", "Officially on time", "Албан ёсоор цагтаа ирсэн", "count", "тоо"),
    ("late", "Officially late", "Албан ёсоор хоцорсон", "count", "тоо"),
    ("general_leave", "General leave", "Чөлөөтэй", "count", "тоо"),
    ("medical_leave", "Medical leave", "Эмнэлгийн чөлөө", "count", "тоо"),
    ("domestic_mission", "Domestic official assignments", "Орон нутгийн томилолт", "count", "тоо"),
    ("foreign_mission", "Foreign official assignments", "Гадаад томилолт", "count", "тоо"),
    ("unexplained_absence", "Unexplained absences", "Тайлбаргүй тасалсан", "count", "тоо"),
    ("physical_attendance", "Physically attended", "Биеэр оролцсон", "count", "тоо"),
    ("physical_attendance_rate", "Physical attendance rate", "Биеэр оролцсон хувь", "percent", "хувь"),
    ("official_on_time_rate", "Official on-time rate among appearances", "Биеэр оролцсон үеийн албан ёсны цагтаа ирэлтийн хувь", "percent", "хувь"),
]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> int | float | None:
    if value in (None, ""):
        return None
    parsed = float(value)
    return int(parsed) if parsed.is_integer() else parsed


def rate(numerator: int, denominator: int) -> float | None:
    return round(numerator * 100 / denominator, 1) if denominator else None


def rounded_median(values: list[int]) -> float | None:
    return round(statistics.median(values), 1) if values else None


def rounded_mean(values: list[int]) -> float | None:
    return round(statistics.mean(values), 1) if values else None


def mandate_en(member: dict) -> str:
    if member["district"] != "0":
        return f"District {member['district']}"
    order = member["mandate_label_mn"].split("№", 1)[-1]
    return f"Party list #{order}"


def timing_status(session: dict, lang: str) -> str:
    scheduled = bool(session["scheduled_start_time"])
    actual = bool(session["actual_start_time"])
    delay = number(session["start_delay_minutes"])
    labels = {
        "complete": ("Complete", "Бүрэн"),
        "actual_before": ("Actual start precedes scheduled start", "Бодит эхлэл товлосон цагаас өмнө"),
        "actual_only": ("Actual start only", "Зөвхөн бодит эхлэлтэй"),
        "scheduled_only": ("Scheduled start only", "Зөвхөн товлосон цагтай"),
        "missing": ("No timing published", "Цаг нийтлээгүй"),
    }
    if scheduled and actual and delay is not None and delay < 0:
        key = "actual_before"
    elif scheduled and actual:
        key = "complete"
    elif actual:
        key = "actual_only"
    elif scheduled:
        key = "scheduled_only"
    else:
        key = "missing"
    return labels[key][0 if lang == "en" else 1]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def build_mp(members: list[dict], attendance: list[dict]) -> None:
    history = defaultdict(list)
    for row in attendance:
        history[row["member_id"]].append(row)

    chart_en, chart_mn, full_en, full_mn = [], [], [], []
    for member in sorted(members, key=lambda row: int(row["ordinal"])):
        rows = history[member["member_id"]]
        counts = Counter(row["status"] for row in rows)
        physical = counts["present"] + counts["late"]
        scheduled_on_time = sum(row["scheduled_arrival_class"] == "on_time" for row in rows)
        scheduled_late = sum(row["scheduled_arrival_class"] == "late" for row in rows)
        scheduled_observations = scheduled_on_time + scheduled_late
        late_minutes = [
            int(row["minutes_from_actual_start"])
            for row in rows
            if row["status"] == "late" and row["minutes_from_actual_start"] != ""
        ]
        values = {
            "sittings": len(rows),
            "physical_attendance": physical,
            "physical_attendance_rate": rate(physical, len(rows)),
            "official_on_time": counts["present"],
            "official_late": counts["late"],
            "official_on_time_rate": rate(counts["present"], physical),
            "scheduled_observations": scheduled_observations,
            "scheduled_on_time": scheduled_on_time,
            "scheduled_late": scheduled_late,
            "scheduled_on_time_rate": rate(scheduled_on_time, scheduled_observations),
            "median_late_minutes": rounded_median(late_minutes),
            "average_late_minutes": rounded_mean(late_minutes),
            "unexplained_absence": counts["absent_unexplained"],
            "unexplained_absence_rate": rate(counts["absent_unexplained"], len(rows)),
            "general_leave": counts["excused_general"],
            "medical_leave": counts["excused_medical"],
            "domestic_mission": counts["mission_local"],
            "foreign_mission": counts["mission_foreign"],
        }
        chart_en.append(
            {
                "member": member["name_mn"],
                "party": member["party_name_en"],
                "physical_attendance_rate": values["physical_attendance_rate"],
                "official_on_time_rate": values["official_on_time_rate"],
                "scheduled_on_time_rate": values["scheduled_on_time_rate"],
                "unexplained_absence_rate": values["unexplained_absence_rate"],
                "median_late_minutes": values["median_late_minutes"],
            }
        )
        chart_mn.append(
            {
                "гишүүн": member["name_mn"],
                "нам": member["party_name_mn"],
                "биеэр_оролцсон_хувь": values["physical_attendance_rate"],
                "албан_ёсны_цагтаа_ирэлтийн_хувь": values["official_on_time_rate"],
                "товлосон_цагтаа_ирэлтийн_хувь": values["scheduled_on_time_rate"],
                "тайлбаргүй_таслалтын_хувь": values["unexplained_absence_rate"],
                "хоцролтын_медиан_минут": values["median_late_minutes"],
            }
        )
        for key, label_en, label_mn, unit_en, unit_mn in MP_METRICS:
            full_en.append(
                {
                    "member_id": member["member_id"],
                    "member": member["name_mn"],
                    "party": member["party_name_en"],
                    "mandate": mandate_en(member),
                    "committee": COMMITTEE_EN[member["committee_name_mn"]],
                    "metric": label_en,
                    "value": values[key],
                    "unit": unit_en,
                }
            )
            full_mn.append(
                {
                    "гишүүний_id": member["member_id"],
                    "гишүүн": member["name_mn"],
                    "нам": member["party_name_mn"],
                    "мандат": member["mandate_label_mn"],
                    "байнгын_хороо": member["committee_name_mn"],
                    "үзүүлэлт": label_mn,
                    "утга": values[key],
                    "нэгж": unit_mn,
                }
            )

    write_csv(PUBLIC / "mp-parliament-attendance-en.csv", list(chart_en[0]), chart_en)
    write_csv(PUBLIC / "mp-parliament-attendance-mn.csv", list(chart_mn[0]), chart_mn)
    write_csv(PUBLIC / "mp-parliament-attendance-all-en.csv", list(full_en[0]), full_en)
    write_csv(PUBLIC / "mp-parliament-attendance-all-mn.csv", list(full_mn[0]), full_mn)


def build_sessions(sessions: list[dict]) -> None:
    chart_en, chart_mn, full_en, full_mn = [], [], [], []
    previous_date = None
    period = 1
    for session in sorted(sessions, key=lambda row: row["date"]):
        sitting_date = date.fromisoformat(session["date"])
        if previous_date is not None and (sitting_date - previous_date).days > 14:
            period += 1
        previous_date = sitting_date
        on_time = int(session["on_time"])
        late = int(session["late"])
        leave = int(session["excused_general"]) + int(session["excused_medical"])
        mission = int(session["mission_local"]) + int(session["mission_foreign"])
        absent = int(session["absent_unexplained"])
        physical = on_time + late
        delay = number(session["start_delay_minutes"])
        groups = [
            ("On time", "Цагтаа ирсэн", on_time),
            ("Late", "Хоцорсон", late),
            ("Approved leave", "Зөвшөөрөгдсөн чөлөө", leave),
            ("Official mission", "Албан томилолт", mission),
            ("Unexplained absence", "Тайлбаргүй тасалсан", absent),
        ]
        for status_en, status_mn, count in groups:
            chart_en.append(
                {
                    "date": session["date"],
                    "year": sitting_date.year,
                    "period": f"period-{period}",
                    "status": status_en,
                    "count": count,
                    "scheduled_start": session["scheduled_start_time"],
                    "actual_start": session["actual_start_time"],
                    "start_delay_minutes": delay,
                }
            )
            chart_mn.append(
                {
                    "огноо": session["date"],
                    "он": sitting_date.year,
                    "үе": f"period-{period}",
                    "төлөв": status_mn,
                    "тоо": count,
                    "товлосон_цаг": session["scheduled_start_time"],
                    "эхэлсэн_цаг": session["actual_start_time"],
                    "эхлэлтийн_хоцролт_минут": delay,
                }
            )
        values = {
            "agenda_count": number(session["agenda_count"]),
            "start_delay_minutes": delay,
            "on_time": on_time,
            "late": late,
            "general_leave": int(session["excused_general"]),
            "medical_leave": int(session["excused_medical"]),
            "domestic_mission": int(session["mission_local"]),
            "foreign_mission": int(session["mission_foreign"]),
            "unexplained_absence": absent,
            "physical_attendance": physical,
            "physical_attendance_rate": rate(physical, int(session["total_members"])),
            "official_on_time_rate": rate(on_time, physical),
        }
        kind_en, kind_mn = SESSION_KIND[session["session_kind"]]
        for key, label_en, label_mn, unit_en, unit_mn in SESSION_METRICS:
            full_en.append(
                {
                    "date": session["date"],
                    "session": kind_en,
                    "scheduled_start": session["scheduled_start_time"],
                    "actual_start": session["actual_start_time"],
                    "timing_status": timing_status(session, "en"),
                    "data_status": "Provisional" if session["data_provisional"] == "True" else "Final",
                    "source_article_url": session["source_article_url"],
                    "source_attachment_url": session["source_attachment_url"],
                    "metric": label_en,
                    "value": values[key],
                    "unit": unit_en,
                }
            )
            full_mn.append(
                {
                    "огноо": session["date"],
                    "чуулган": kind_mn,
                    "товлосон_цаг": session["scheduled_start_time"],
                    "эхэлсэн_цаг": session["actual_start_time"],
                    "цагийн_мэдээллийн_төлөв": timing_status(session, "mn"),
                    "өгөгдлийн_төлөв": "Түр" if session["data_provisional"] == "True" else "Эцсийн",
                    "эх_сурвалжийн_нийтлэл": session["source_article_url"],
                    "эх_файлын_холбоос": session["source_attachment_url"],
                    "үзүүлэлт": label_mn,
                    "утга": values[key],
                    "нэгж": unit_mn,
                }
            )

    write_csv(PUBLIC / "parliament-session-attendance-en.csv", list(chart_en[0]), chart_en)
    write_csv(PUBLIC / "parliament-session-attendance-mn.csv", list(chart_mn[0]), chart_mn)
    write_csv(PUBLIC / "parliament-session-attendance-all-en.csv", list(full_en[0]), full_en)
    write_csv(PUBLIC / "parliament-session-attendance-all-mn.csv", list(full_mn[0]), full_mn)


def register_split(registry: Registry, dataset: Dataset, data_date: str) -> None:
    existing = registry.get_dataset(dataset.id)
    if existing is None:
        registry.add_dataset(dataset)
    elif existing.source_id != "parliament" or existing.parent_id != dataset.parent_id:
        raise SystemExit(f"Unexpected existing registry row: {dataset.id}")

    connection = sqlite3.connect(registry.db_path)
    connection.execute(
        """
        UPDATE datasets
        SET name_en = ?, name_mn = ?, description_en = ?, description_mn = ?,
            category_en = ?, category_mn = ?, tags = ?, keywords_en = ?,
            keywords_mn = ?, source_ref = ?, source_path = ?, definition_path = ?,
            status = 'active', data_file = ?, mdx_file_en = ?, mdx_file_mn = ?,
            chart_spec = ?, data_as_of = ?, last_checked_at = datetime('now'),
            last_fetched_at = datetime('now'), auto_publish = 0,
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (
            dataset.name_en, dataset.name_mn, dataset.description_en,
            dataset.description_mn, dataset.category_en, dataset.category_mn,
            json.dumps(dataset.tags), json.dumps(dataset.keywords_en),
            json.dumps(dataset.keywords_mn), dataset.source_ref, dataset.source_path,
            dataset.definition_path, dataset.data_file, dataset.mdx_file_en,
            dataset.mdx_file_mn, dataset.chart_spec, data_date, dataset.id,
        ),
    )
    connection.commit()
    connection.close()


def register(data_date: str) -> None:
    registry = Registry()
    if registry.get_source("parliament") is None:
        raise SystemExit(
            "Parliament source is not registered; run "
            "`uv run python tools/sources/parliament/register.py` first"
        )
    parent = registry.get_dataset("parliament-attendance-records")
    if parent is None or not parent.is_parent:
        raise SystemExit(
            "Parliament parent dataset is not registered; run "
            "`uv run python tools/sources/parliament/register.py` first"
        )
    register_split(
        registry,
        Dataset(
            id="mp-parliament-attendance",
            source_id="parliament",
            parent_id="parliament-attendance-records",
            name_en="Attendance and Punctuality by Member of Parliament",
            name_mn="Улсын Их Хурлын гишүүдийн ирц ба цаг баримтлалт",
            description_en="Current-Parliament physical attendance, official and scheduled-start punctuality, leave, assignments, and unexplained absences by MP.",
            description_mn="Одоогийн Улсын Их Хурлын гишүүн бүрийн биеэр оролцсон ирц, албан ёсны болон товлосон цагийн цаг баримтлалт, чөлөө, томилолт, тайлбаргүй таслалт.",
            category_en="Government & Politics",
            category_mn="Засаглал ба улс төр",
            definition_path="sources/parliament/datasets/mp-parliament-attendance.md",
            tags=["parliament", "attendance", "punctuality", "MPs"],
            keywords_en=["mongolia parliament attendance", "MP punctuality Mongolia"],
            keywords_mn=["УИХ гишүүдийн ирц", "гишүүдийн цаг баримтлалт"],
            source_ref="https://att.parliament.mn/members",
            source_path="sources/parliament/raw/parliament-attendance.csv",
            status="active",
            data_file="data.mn/public/datasets/mp-parliament-attendance-all-en.csv",
            mdx_file_en="data.mn/src/data/data/en/mp-parliament-attendance.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/mp-parliament-attendance.mdx",
            chart_spec="data.mn/public/charts/mp-parliament-attendance-en.json",
            auto_publish=False,
        ),
        data_date,
    )
    register_split(
        registry,
        Dataset(
            id="parliament-session-attendance",
            source_id="parliament",
            parent_id="parliament-attendance-records",
            name_en="Mongolian Parliament Attendance by Plenary Sitting",
            name_mn="Монгол Улсын Их Хурлын нэгдсэн хуралдаан бүрийн ирц",
            description_en="Attendance composition and scheduled-versus-actual start timing for each plenary sitting of the current Parliament.",
            description_mn="Одоогийн Улсын Их Хурлын нэгдсэн хуралдаан бүрийн ирцийн бүтэц, товлосон болон бодит эхлэх цаг.",
            category_en="Government & Politics",
            category_mn="Засаглал ба улс төр",
            definition_path="sources/parliament/datasets/parliament-session-attendance.md",
            tags=["parliament", "attendance", "plenary", "sittings"],
            keywords_en=["mongolia parliament sittings", "plenary attendance Mongolia"],
            keywords_mn=["УИХ нэгдсэн хуралдааны ирц", "чуулганы эхлэх цаг"],
            source_ref="https://att.parliament.mn/sessions",
            source_path="sources/parliament/raw/parliament-sessions.csv",
            status="active",
            data_file="data.mn/public/datasets/parliament-session-attendance-all-en.csv",
            mdx_file_en="data.mn/src/data/data/en/parliament-session-attendance.mdx",
            mdx_file_mn="data.mn/src/data/data/mn/parliament-session-attendance.mdx",
            chart_spec="data.mn/public/charts/parliament-session-attendance-en.json",
            auto_publish=False,
        ),
        data_date,
    )


def create_initial_version(
    registry: Registry,
    dataset_id: str,
    data_date: str,
    files: list[str],
) -> None:
    version_dir = TOOLS / "versions" / dataset_id / "v1"
    if not version_dir.exists():
        version_dir.mkdir(parents=True)
        for filename in files:
            shutil.copy2(PUBLIC / filename, version_dir / filename)
        (version_dir / "VERSION.md").write_text(
            f"# {dataset_id} — Version 1\n\n"
            f"- Data as of: {data_date}\n"
            "- Source: State Great Khural official attendance dashboard\n"
            "- Coverage: current Parliament plenary sittings\n"
            "- Build: `uv run python tools/sources/parliament/build_public.py`\n",
            encoding="utf-8",
        )

    if registry.get_versions(dataset_id):
        registry.update_dataset(dataset_id, current_version=1)
        return

    primary_name = next(
        (name for name in files if name.endswith("-all-en.csv")),
        files[0],
    )
    primary_path = version_dir / primary_name
    with primary_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        row_count = sum(1 for _ in reader)
        column_count = len(reader.fieldnames or [])

    registry.add_version(
        Version(
            id=0,
            dataset_id=dataset_id,
            version=1,
            data_hash=hashlib.sha256(primary_path.read_bytes()).hexdigest(),
            data_path=str(primary_path.relative_to(TOOLS)),
            row_count=row_count,
            column_count=column_count,
            change_type="initial",
            change_summary="Initial Parliament attendance publication",
            source_updated_at=data_date,
            source_raw_files=[
                "sources/parliament/raw/parliament-members.csv",
                "sources/parliament/raw/parliament-sessions.csv",
                "sources/parliament/raw/parliament-attendance.csv",
                "sources/parliament/raw/parliament-archive.csv",
                "sources/parliament/raw/parliament-pull.meta.json",
            ],
        )
    )
    registry.update_dataset(dataset_id, current_version=1)


def main() -> None:
    members = read_csv(RAW / "parliament-members.csv")
    sessions = read_csv(RAW / "parliament-sessions.csv")
    attendance = read_csv(RAW / "parliament-attendance.csv")
    metadata = json.loads((RAW / "parliament-pull.meta.json").read_text(encoding="utf-8"))
    if len(attendance) != len(members) * len(sessions):
        raise SystemExit("Incomplete MP × sitting matrix")
    build_mp(members, attendance)
    build_sessions(sessions)
    data_date = metadata["coverage"]["last_sitting"]
    register(data_date)
    registry = Registry()
    create_initial_version(
        registry,
        "mp-parliament-attendance",
        data_date,
        [
            "mp-parliament-attendance-en.csv",
            "mp-parliament-attendance-mn.csv",
            "mp-parliament-attendance-all-en.csv",
            "mp-parliament-attendance-all-mn.csv",
        ],
    )
    create_initial_version(
        registry,
        "parliament-session-attendance",
        data_date,
        [
            "parliament-session-attendance-en.csv",
            "parliament-session-attendance-mn.csv",
            "parliament-session-attendance-all-en.csv",
            "parliament-session-attendance-all-mn.csv",
        ],
    )
    print(
        f"Built public Parliament datasets: {len(members)} MPs, "
        f"{len(sessions)} sittings, data through {metadata['coverage']['last_sitting']}"
    )


if __name__ == "__main__":
    main()
