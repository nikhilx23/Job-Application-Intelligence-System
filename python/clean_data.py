"""
clean_data.py — reads data/raw/applications_raw.csv (messy) and produces
data/clean/applications_clean.csv (analysis-ready): parses the three mixed
date formats, normalizes Status casing, strips stray whitespace, restores
real blanks from the literal "N/A" placeholder, and drops duplicate rows
that were logged twice.
"""
import csv
from datetime import datetime

DATE_FORMATS = ["%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y"]


def parse_any_date(value):
    value = value.strip()
    if value == "" or value.upper() == "N/A":
        return ""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value!r}")


def clean_row(row):
    row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
    row["Company"] = row["Company"].strip()
    row["Status"] = row["Status"].strip().title().replace(
        "No Response", "No Response"
    )
    # Title-case can mangle multi-word statuses; normalize explicitly
    status_map = {s.lower(): s for s in
                  ["Applied", "Rejected", "Interview", "Offer", "No Response"]}
    row["Status"] = status_map.get(row["Status"].lower(), row["Status"])
    row["Date Applied"] = parse_any_date(row["Date Applied"])
    row["Response Date"] = parse_any_date(row["Response Date"])
    row["Interview Date"] = parse_any_date(row["Interview Date"])
    if row["Response Time (Days)"].strip().upper() in ("", "N/A"):
        row["Response Time (Days)"] = ""
    return row


def main():
    with open("data/raw/applications_raw.csv", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = [clean_row(row) for row in reader]

    seen = set()
    deduped = []
    dropped = 0
    for row in rows:
        key = row["Application ID"]
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        deduped.append(row)

    deduped.sort(key=lambda r: r["Application ID"])

    with open("data/clean/applications_clean.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(f"Cleaned {len(rows)} raw rows -> {len(deduped)} unique applications "
          f"({dropped} duplicate rows dropped).")


if __name__ == "__main__":
    main()
