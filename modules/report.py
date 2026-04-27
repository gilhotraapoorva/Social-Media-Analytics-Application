"""Final report generation — HTML and PDF."""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from flask import render_template
from xhtml2pdf import pisa

from config import Config


def render_html_report(case, analytics: Dict[str, Any]) -> str:
    return render_template(
        "report.html",
        case=case,
        analytics=analytics,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    )


def write_html_report(case, analytics: Dict[str, Any]) -> Path:
    html = render_html_report(case, analytics)
    out_dir = Config.REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"report_case_{case.id}.html"
    path.write_text(html, encoding="utf-8")
    return path


def write_pdf_report(case, analytics: Dict[str, Any]) -> Path:
    html = render_html_report(case, analytics)
    out_dir = Config.REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"report_case_{case.id}.pdf"
    with open(path, "wb") as f:
        pisa.CreatePDF(src=html, dest=f)
    return path
