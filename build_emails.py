"""Build one ready-to-send HTML email per company.

Reads companies.csv and logistics-email-v5.html, writes emails/NN-company.html.
Each file carries its recipient and plain-text version for send-from-drive.gs,
which strips both before sending.

Usage: python build_emails.py
"""
import csv
import html
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "logistics-email-v5.html"
COMPANIES = HERE / "companies.csv"
OUT = HERE / "emails"

PASS_ON = "If this is better handled by your general manager or head of operations, I would be grateful if you could pass it on."

PLAIN = """{greeting}

{opening}

Every logistics company runs two operations: one moves the freight, the other moves the information about it. I help established companies explore where customized AI could support that second one, without needing a technical department or an AI team of their own.

If a 20-minute conversation would be useful, reply with a day that suits you. If not, reply "No thanks" and I will not contact you again.

Hala Al-Attiyat
Software Engineer | AI Solutions & Business Automation"""


def esc(value):
    return html.escape(value, quote=False)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def build(template, row):
    company = row["company"].strip()
    contact = row["contact_name"].strip()
    opening = row["opening"].strip()

    greeting = f"Dear {contact}," if contact else f"Dear {company} team,"
    full_opening = opening if contact else f"{opening} {PASS_ON}"

    page = re.sub(r"\[PERSONAL OPENING:.*?\"\]", lambda _: esc(full_opening), template, flags=re.S)
    page = page.replace("Dear [First Name],", esc(greeting))
    page = page.replace("[Company Name]", esc(company))

    plain = PLAIN.format(greeting=greeting, opening=full_opening)
    header = (
        f'<meta name="x-send-to" content="{html.escape(row["email"].strip())}">\n'
        f"<!--PLAINTEXT\n{plain}\nPLAINTEXT-->\n"
    )
    return page.replace("</title>\n", "</title>\n" + header, 1)


def main():
    template = TEMPLATE.read_text(encoding="utf-8")
    rows = list(csv.DictReader(COMPANIES.read_text(encoding="utf-8-sig").splitlines()))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    problems = []
    for number, row in enumerate(rows, start=1):
        page = build(template, row)
        name = f"{number:02d}-{slug(row['company'])}.html"
        (OUT / name).write_text(page, encoding="utf-8", newline="\n")

        left = re.findall(r"\[[A-Z][^\]]*\]|yourdomain", page)
        if left or "--" in page.split("<!--PLAINTEXT")[1].split("PLAINTEXT-->")[0]:
            problems.append(f"{name}: {left or 'double hyphen in plain text'}")
        print(f"{name:42} {row['email'].strip()}")

    print(f"\n{len(rows)} files in {OUT}")
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
