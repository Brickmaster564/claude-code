#!/usr/bin/env python3
"""
Meta Ads PDF report generator.

Usage:
    python3 tools/meta_report.py generate --data-file .tmp/report-data.json --output output/media-buyer/2026-03-14.pdf
    python3 tools/meta_report.py generate --data-file .tmp/report-data.json --output report.pdf --email jasperkilic10@gmail.com

Reads a structured JSON file with campaign data and produces a visual PDF report.
Optionally emails the report via tools/gmail.py.

Expected data-file structure: see .claude/skills/media-buyer/report-template.md
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("ERROR: fpdf2 not installed. Run: pip3 install --break-system-packages fpdf2", file=sys.stderr)
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("ERROR: matplotlib not installed. Run: pip3 install --break-system-packages matplotlib", file=sys.stderr)
    sys.exit(1)

TOOLS_DIR = Path(__file__).parent
TMP_DIR = Path(__file__).parent.parent / ".tmp"

# Brand colors
PRIMARY = (24, 119, 242)     # Meta blue
SUCCESS = (34, 139, 34)      # Green (scale)
WARNING = (218, 165, 32)     # Gold (hold)
DANGER = (220, 53, 69)       # Red (cut)
LIGHT_GRAY = (245, 245, 245)
DARK_TEXT = (33, 37, 41)
MED_TEXT = (108, 117, 125)


class MediaBuyerReport(FPDF):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*MED_TEXT)
        self.cell(0, 8, "Jasper OS Media Buyer Report", align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MED_TEXT)
        self.cell(0, 10, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | Page {self.page_no()}/{{nb}}", align="C")

    def add_title_page(self):
        self.add_page()
        self.ln(40)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*DARK_TEXT)
        self.cell(0, 15, "Media Buyer Report", align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 14)
        self.set_text_color(*MED_TEXT)
        account = self.data.get("account_name", self.data.get("account_id", "Unknown"))
        self.cell(0, 10, account, align="C", new_x="LMARGIN", new_y="NEXT")

        period = self.data.get("period", "Last 7 days")
        self.cell(0, 10, period, align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 11)
        date_str = datetime.now().strftime("%B %d, %Y")
        self.cell(0, 10, date_str, align="C", new_x="LMARGIN", new_y="NEXT")

    def add_summary_card(self):
        summary = self.data.get("summary", {})
        if not summary:
            return

        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*DARK_TEXT)
        self.cell(0, 12, "Account Summary", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        metrics = [
            ("Spend", f"${summary.get('spend', 0):,.2f}"),
            ("Leads", f"{summary.get('leads', 0):,}"),
            ("CPL", f"${summary.get('cpl', 0):,.2f}" if summary.get("cpl") else "N/A"),
            ("CTR", f"{summary.get('ctr', 0):.2f}%"),
            ("CPC", f"${summary.get('cpc', 0):,.2f}" if summary.get("cpc") else "N/A"),
            ("Impressions", f"{summary.get('impressions', 0):,}"),
        ]

        col_width = (self.w - 20) / 3
        row_height = 28

        for i, (label, value) in enumerate(metrics):
            x = 10 + (i % 3) * col_width
            y = self.get_y() + (i // 3) * (row_height + 5)

            # Card background
            self.set_fill_color(*LIGHT_GRAY)
            self.rect(x, y, col_width - 3, row_height, style="F")

            # Value
            self.set_xy(x + 5, y + 3)
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(*DARK_TEXT)
            self.cell(col_width - 13, 10, value)

            # Label
            self.set_xy(x + 5, y + 15)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*MED_TEXT)
            self.cell(col_width - 13, 8, label)

        self.set_y(self.get_y() + (len(metrics) // 3 + 1) * (row_height + 5) + 5)

    def _verdict_color(self, verdict):
        v = (verdict or "").upper()
        if v == "SCALE":
            return SUCCESS
        elif v == "HOLD":
            return WARNING
        elif v == "CUT":
            return DANGER
        return MED_TEXT

    def add_campaign_table(self):
        campaigns = self.data.get("campaigns", [])
        if not campaigns:
            return

        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*DARK_TEXT)
        self.cell(0, 12, "Campaign Performance", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        # Table header
        headers = ["Campaign", "Spend", "Leads", "CPL", "CTR", "Freq", "Verdict"]
        widths = [55, 22, 18, 22, 18, 18, 22]

        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(*PRIMARY)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 8, h, border=1, fill=True, align="C")
        self.ln()

        # Table rows
        self.set_font("Helvetica", "", 8)
        for i, c in enumerate(campaigns):
            bg = LIGHT_GRAY if i % 2 == 0 else (255, 255, 255)
            self.set_fill_color(*bg)
            self.set_text_color(*DARK_TEXT)

            name = (c.get("campaign_name") or c.get("name", ""))[:25]
            spend = f"${c.get('spend', 0):,.2f}"
            leads = str(c.get("leads", 0))
            cpl = f"${c['cpl']:,.2f}" if c.get("cpl") else "N/A"
            ctr = f"{c.get('ctr', 0):.2f}%"
            freq = f"{c.get('frequency', 0):.1f}" if c.get("frequency") else "-"
            verdict = c.get("verdict", "")

            cells = [name, spend, leads, cpl, ctr, freq]
            for val, w in zip(cells, widths[:-1]):
                align = "L" if val == name else "C"
                self.cell(w, 7, val, border=1, fill=True, align=align)

            # Verdict with color
            self.set_text_color(*self._verdict_color(verdict))
            self.set_font("Helvetica", "B", 8)
            self.cell(widths[-1], 7, verdict.upper(), border=1, fill=True, align="C")
            self.set_font("Helvetica", "", 8)
            self.ln()

    def add_creative_scorecard(self):
        creatives = self.data.get("creatives", [])
        if not creatives:
            return

        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*DARK_TEXT)
        self.cell(0, 12, "Creative Scorecard", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        headers = ["Ad Name", "Spend", "Leads", "CPL", "CTR", "Freq", "Fatigue", "Verdict"]
        widths = [42, 20, 16, 20, 16, 16, 22, 22]

        self.set_font("Helvetica", "B", 7)
        self.set_fill_color(*PRIMARY)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, widths):
            self.cell(w, 8, h, border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 7)
        for i, c in enumerate(creatives[:20]):  # Top 20
            bg = LIGHT_GRAY if i % 2 == 0 else (255, 255, 255)
            self.set_fill_color(*bg)
            self.set_text_color(*DARK_TEXT)

            name = (c.get("ad_name") or c.get("name", ""))[:20]
            spend = f"${c.get('spend', 0):,.2f}"
            leads = str(c.get("leads", 0))
            cpl = f"${c['cpl']:,.2f}" if c.get("cpl") else "N/A"
            ctr = f"{c.get('ctr', 0):.2f}%"
            freq = f"{c.get('frequency', 0):.1f}" if c.get("frequency") else "-"
            fatigue = c.get("fatigue", "OK")
            verdict = c.get("verdict", "")

            cells = [name, spend, leads, cpl, ctr, freq]
            for val, w in zip(cells, widths[:6]):
                align = "L" if val == name else "C"
                self.cell(w, 7, val, border=1, fill=True, align=align)

            # Fatigue with color
            fatigue_color = DANGER if fatigue == "CRITICAL" else (WARNING if fatigue == "WARNING" else SUCCESS)
            self.set_text_color(*fatigue_color)
            self.set_font("Helvetica", "B", 7)
            self.cell(widths[6], 7, fatigue, border=1, fill=True, align="C")

            # Verdict with color
            self.set_text_color(*self._verdict_color(verdict))
            self.cell(widths[7], 7, verdict.upper(), border=1, fill=True, align="C")
            self.set_font("Helvetica", "", 7)
            self.ln()

    def add_charts(self):
        daily = self.data.get("daily_data", [])
        campaigns = self.data.get("campaigns", [])

        if not daily and not campaigns:
            return

        TMP_DIR.mkdir(exist_ok=True)
        chart_paths = []

        if daily:
            # Spend trend chart
            dates = [d.get("date_start", "")[-5:] for d in daily]  # MM-DD
            spends = [d.get("spend", 0) for d in daily]
            cpls = [d.get("cpl") for d in daily]

            fig, ax1 = plt.subplots(figsize=(8, 3))
            ax1.plot(dates, spends, color="#1877F2", linewidth=2, marker="o", markersize=4)
            ax1.fill_between(range(len(dates)), spends, alpha=0.1, color="#1877F2")
            ax1.set_ylabel("Spend ($)", color="#1877F2")
            ax1.tick_params(axis="y", labelcolor="#1877F2")
            ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
            ax1.set_xticks(range(len(dates)))
            ax1.set_xticklabels(dates, rotation=45, fontsize=7)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)

            # CPL on secondary axis if available
            if any(c is not None for c in cpls):
                ax2 = ax1.twinx()
                cpl_vals = [c if c is not None else 0 for c in cpls]
                ax2.plot(dates, cpl_vals, color="#DC3545", linewidth=2, linestyle="--", marker="s", markersize=3)
                ax2.set_ylabel("CPL ($)", color="#DC3545")
                ax2.tick_params(axis="y", labelcolor="#DC3545")
                ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.2f}"))
                ax2.spines["top"].set_visible(False)

            plt.title("Daily Spend & CPL Trend", fontsize=11, fontweight="bold")
            plt.tight_layout()
            spend_path = str(TMP_DIR / "spend_trend.png")
            plt.savefig(spend_path, dpi=150, bbox_inches="tight")
            plt.close()
            chart_paths.append(spend_path)

        if campaigns and len(campaigns) > 1:
            # Spend distribution pie chart
            names = [(c.get("campaign_name") or c.get("name", ""))[:20] for c in campaigns if c.get("spend", 0) > 0]
            spends = [c.get("spend", 0) for c in campaigns if c.get("spend", 0) > 0]

            if names:
                fig, ax = plt.subplots(figsize=(5, 4))
                colors = plt.cm.Set3(range(len(names)))
                wedges, texts, autotexts = ax.pie(
                    spends, labels=names, autopct="%1.0f%%",
                    colors=colors, textprops={"fontsize": 8},
                    pctdistance=0.8,
                )
                for t in autotexts:
                    t.set_fontsize(7)
                    t.set_fontweight("bold")
                ax.set_title("Spend Distribution by Campaign", fontsize=11, fontweight="bold")
                plt.tight_layout()
                pie_path = str(TMP_DIR / "spend_pie.png")
                plt.savefig(pie_path, dpi=150, bbox_inches="tight")
                plt.close()
                chart_paths.append(pie_path)

        # Add charts to PDF
        if chart_paths:
            self.add_page()
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(*DARK_TEXT)
            self.cell(0, 12, "Trends & Distribution", new_x="LMARGIN", new_y="NEXT")
            self.ln(5)

            for path in chart_paths:
                if os.path.exists(path):
                    self.image(path, x=10, w=self.w - 20)
                    self.ln(10)

    def add_recommendations(self):
        recs = self.data.get("recommendations", "")
        if not recs:
            return

        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*DARK_TEXT)
        self.cell(0, 12, "Recommendations", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 6, recs)

    def generate(self, output_path):
        """Generate the full PDF report."""
        self.alias_nb_pages()
        self.add_title_page()
        self.add_summary_card()
        self.add_campaign_table()
        self.add_creative_scorecard()
        self.add_charts()
        self.add_recommendations()

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.output(output_path)
        return output_path


def send_email(pdf_path, email_to, subject=None):
    """Send the PDF report via gmail.py with attachment."""
    if not subject:
        subject = f"Media Buyer Report - {datetime.now().strftime('%Y-%m-%d')}"

    cmd = [
        sys.executable, str(TOOLS_DIR / "gmail.py"),
        "send",
        "--to", email_to,
        "--subject", subject,
        "--body", f"Your daily Media Buyer report is attached.\n\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "--attachment", str(pdf_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": f"Email failed: {result.stderr}"}
    return json.loads(result.stdout) if result.stdout.strip() else {"message": "Email sent"}


def main():
    parser = argparse.ArgumentParser(description="Meta Ads PDF report generator")
    subparsers = parser.add_subparsers(dest="command")

    gen = subparsers.add_parser("generate", help="Generate a PDF report from data file")
    gen.add_argument("--data-file", required=True, help="Path to report data JSON file")
    gen.add_argument("--output", required=True, help="Output PDF file path")
    gen.add_argument("--email", help="Email address to send the report to")

    args = parser.parse_args()

    if args.command == "generate":
        data_path = Path(args.data_file)
        if not data_path.exists():
            print(f"ERROR: Data file not found: {args.data_file}", file=sys.stderr)
            sys.exit(1)

        with open(data_path) as f:
            data = json.load(f)

        report = MediaBuyerReport(data)
        output_path = report.generate(args.output)

        result = {"pdf": output_path, "message": "Report generated"}

        if args.email:
            email_result = send_email(output_path, args.email)
            result["email"] = email_result

        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
