#!/usr/bin/env python3
"""
Build the Client Network lead magnet PDF: "The Insurance Agent's Guide to Better Leads"
Branded with CN colours, logo, and typography. Target: 4 pages A4.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ── Paths ──
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANDING = os.path.join(BASE, "resources", "client-network", "cn-branding")
OUTPUT = os.path.join(BASE, "output")
LOGO_PATH = os.path.join(BRANDING, "Logo.jpeg")
PDF_PATH = os.path.join(OUTPUT, "Client-Network-Insurance-Agents-Guide-to-Better-Leads.pdf")

# ── Brand Colours ──
TEAL = HexColor("#6BBFAB")
TEAL_DARK = HexColor("#4A9E8A")
TEAL_LIGHT = HexColor("#E8F5F1")
DARK = HexColor("#1A1A1A")
GREY = HexColor("#4A4A4A")
GREY_LT = HexColor("#888888")
CTA_BG = HexColor("#1A1A1A")

PAGE_W, PAGE_H = A4
ML = 18 * mm
MR = 18 * mm
MT = 14 * mm
MB = 14 * mm
USABLE = PAGE_W - ML - MR


def S():
    """Build all paragraph styles (compact for 4-page fit)."""
    d = {}
    d["cover_title"] = ParagraphStyle(
        "ct", fontName="Helvetica-Bold", fontSize=26, leading=31,
        textColor=DARK, spaceAfter=6)
    d["cover_sub"] = ParagraphStyle(
        "cs", fontName="Helvetica", fontSize=11, leading=16,
        textColor=GREY, spaceAfter=4)
    d["cover_tag"] = ParagraphStyle(
        "cg", fontName="Helvetica", fontSize=9, leading=12,
        textColor=TEAL_DARK, spaceAfter=2)
    d["h1"] = ParagraphStyle(
        "h1", fontName="Helvetica-Bold", fontSize=16, leading=20,
        textColor=DARK, spaceBefore=2, spaceAfter=6)
    d["h2"] = ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=TEAL_DARK, spaceBefore=8, spaceAfter=3)
    d["h3"] = ParagraphStyle(
        "h3", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
        textColor=DARK, spaceBefore=6, spaceAfter=2)
    d["body"] = ParagraphStyle(
        "b", fontName="Helvetica", fontSize=8.5, leading=12.5,
        textColor=GREY, spaceAfter=5)
    d["bb"] = ParagraphStyle(
        "bb", fontName="Helvetica-Bold", fontSize=8.5, leading=12.5,
        textColor=DARK, spaceAfter=3)
    d["bul"] = ParagraphStyle(
        "bu", fontName="Helvetica", fontSize=8.5, leading=12.5,
        textColor=GREY, leftIndent=10, spaceAfter=3, bulletIndent=0)
    d["callout"] = ParagraphStyle(
        "co", fontName="Helvetica-Oblique", fontSize=8.5, leading=12.5,
        textColor=TEAL_DARK, leftIndent=8, rightIndent=8,
        spaceBefore=4, spaceAfter=6)
    d["cta_h"] = ParagraphStyle(
        "ch", fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=white, alignment=TA_CENTER, spaceAfter=2)
    d["cta_b"] = ParagraphStyle(
        "cb", fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=HexColor("#CCCCCC"), alignment=TA_CENTER, spaceAfter=1)
    d["cta_l"] = ParagraphStyle(
        "cl", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
        textColor=TEAL, alignment=TA_CENTER, spaceBefore=3)
    d["ft"] = ParagraphStyle(
        "ft", fontName="Helvetica", fontSize=7, leading=9,
        textColor=GREY_LT, alignment=TA_CENTER)
    d["th"] = ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=8.5, leading=12,
        textColor=white, alignment=TA_CENTER)
    d["tc"] = ParagraphStyle(
        "tc", fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=GREY, alignment=TA_CENTER)
    d["tcb"] = ParagraphStyle(
        "tcb", fontName="Helvetica-Bold", fontSize=8.5, leading=12,
        textColor=DARK, alignment=TA_CENTER)
    d["tcl"] = ParagraphStyle(
        "tcl", fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=GREY, alignment=TA_LEFT)
    d["num"] = ParagraphStyle(
        "nm", fontName="Helvetica-Bold", fontSize=18, leading=22,
        textColor=TEAL, alignment=TA_CENTER)
    d["ask"] = ParagraphStyle(
        "ak", fontName="Helvetica-Bold", fontSize=8, leading=11,
        textColor=TEAL_DARK, spaceBefore=2, spaceAfter=4)
    return d


def tline():
    return HRFlowable(width="35%", thickness=2, color=TEAL,
                       spaceBefore=2, spaceAfter=5, hAlign="LEFT")

def fline():
    return HRFlowable(width="100%", thickness=0.4, color=HexColor("#DDDDDD"),
                       spaceBefore=3, spaceAfter=3)

def cta(s, heading, lines, link="Book Your Free Strategy Call"):
    content = [Paragraph(heading, s["cta_h"])]
    for ln in lines:
        content.append(Paragraph(ln, s["cta_b"]))
    content.append(Spacer(1, 2))
    content.append(Paragraph(
        f'<a href="https://start.clientnetworkpartners.com/call-booking" color="#6BBFAB">'
        f'{link} &rarr;</a>', s["cta_l"]))
    t = Table([[content]], colWidths=[USABLE - 8 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CTA_BG),
        ("ROUNDEDCORNERS", [5, 5, 5, 5]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def nitem(s, num, title, paras, ask=None):
    els = []
    np = Paragraph(str(num), s["num"])
    tp = Paragraph(title, s["h3"])
    ht = Table([[np, tp]], colWidths=[28, USABLE - 28 - 6 * mm])
    ht.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    els.append(ht)
    els.append(Spacer(1, 2))
    for p in paras:
        els.append(Paragraph(p, s["body"]))
    if ask:
        els.append(Paragraph(f"<b>Ask your provider:</b> {ask}", s["ask"]))
    els.append(fline())
    return els


def build():
    s = S()
    story = []

    # ════════ PAGE 1: COVER + INTRO ════════
    if os.path.exists(LOGO_PATH):
        story.append(RLImage(LOGO_PATH, width=50, height=50))
        story.append(Spacer(1, 18))

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "The Insurance Agent's<br/>Guide to Better Leads", s["cover_title"]))
    story.append(tline())
    story.append(Paragraph(
        "How to stop wasting money on leads that never pick up, "
        "and start building a pipeline that actually converts.", s["cover_sub"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Presented by Client Network", s["cover_tag"]))
    story.append(Paragraph(
        "Pre-Qualified Prospects  |  Pay Per Result  |  Scale On Demand", s["cover_tag"]))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Introduction", s["h2"]))
    story.append(Paragraph(
        "If you have been buying leads for more than a few months, you already know the "
        "frustration. You pay $20, $30, sometimes $50 or more for a single lead. You call "
        "within minutes. The number is disconnected, or the person has no idea why you are "
        "calling, or they have already spoken to three other agents before you even dialled.", s["body"]))
    story.append(Paragraph(
        "You are not imagining it. The lead generation industry has a serious quality problem, "
        "and most agents are paying the price for it without realising there is a better way.", s["body"]))
    story.append(Paragraph(
        "This guide breaks down why most leads underperform, what separates a high-quality "
        "lead from a waste of money, and what to look for when choosing a lead generation "
        "partner who actually delivers results. Whether you are a new agent building your "
        "first pipeline or a seasoned producer looking to scale, this will save you time, "
        "money, and a lot of headaches.", s["body"]))

    story.append(Spacer(1, 10))

    # Inline "what's inside" list
    story.append(Paragraph("What you will learn:", s["bb"]))
    items = [
        "Why shared leads are destroying your conversion rates",
        "The four main lead source types and what you are really paying for",
        "Five things to check before choosing any lead generation partner",
        "The exclusive lead advantage (with real cost-per-sale comparison)",
    ]
    for it in items:
        story.append(Paragraph(f"\u2022  {it}", s["bul"]))

    story.append(PageBreak())

    # ════════ PAGE 2: SHARED LEADS + LEAD SOURCES ════════
    story.append(Paragraph("Why Shared Leads Are Killing Your Conversion Rates", s["h1"]))
    story.append(tline())
    story.append(Paragraph(
        "The average contact rate on shared internet leads sits between 30% and 40%. "
        "For every 10 leads you buy, six or seven people will never pick up the phone. "
        "And for the ones who do answer, many have already spoken to another agent.", s["body"]))
    story.append(Paragraph(
        "This is the shared lead model: a single prospect fills out a form and their "
        "information gets sold to multiple agents at once. The result is a race to the phone "
        "where the fastest caller wins, and everyone else burns their money.", s["body"]))

    story.append(Paragraph("The real cost goes beyond the sticker price:", s["bb"]))
    bul = [
        ("<b>Lower contact rates.</b> Prospects bombarded with calls stop answering entirely. "
         "Your lead becomes a dead number within hours."),
        ("<b>Worse conversion rates.</b> Shared leads are already fatigued from multiple "
         "conversations. Their guard is up, their patience is thin, and they are far less "
         "likely to sit through a full needs analysis."),
        ("<b>Higher true cost per sale.</b> If you pay $15 per shared lead and close 1 in 50, "
         "your real cost per sale is $750. An exclusive lead at $30 with a 1-in-10 close rate "
         "gives you a cost per sale of $300. The \"cheaper\" lead costs twice as much."),
        ("<b>Damaged reputation.</b> When a prospect gets five calls in ten minutes from "
         "different agents, the entire industry looks bad, and that reflects on you."),
    ]
    for b in bul:
        story.append(Paragraph(f"\u2022  {b}", s["bul"]))

    story.append(Spacer(1, 6))

    # ── Lead sources ──
    story.append(Paragraph("Understanding Your Lead Sources", s["h2"]))
    story.append(Paragraph(
        "Before you spend another dollar, it helps to understand where leads actually come "
        "from and what you are really paying for.", s["body"]))

    story.append(Paragraph("Lead Aggregators", s["h3"]))
    story.append(Paragraph(
        "These companies generate leads at scale through comparison websites and search ads, "
        "then distribute them to multiple agents. Volume and convenience are the upside. The "
        "downside: most leads are shared, quality varies month to month, and agents often report "
        "strong results early on followed by a steady decline. Contact rates typically hover "
        "around 30-40%, with close rates between 1% and 5%.", s["body"]))

    story.append(Paragraph("Lead Brokers", s["h3"]))
    story.append(Paragraph(
        "Brokers buy leads in bulk and resell them, sometimes multiple times. This is where "
        "ultra-cheap \"aged leads\" come from ($1-$5 each). The data is old, often months past "
        "the original inquiry. Calling aged leads is essentially cold calling with extra steps, "
        "and for most agents the return on time and energy is poor.", s["body"]))

    story.append(Paragraph("Self-Generated Leads (Your Own Ads)", s["h3"]))
    story.append(Paragraph(
        "Running your own Facebook or Google campaigns gives you full control over targeting, "
        "messaging, and exclusivity. The catch is that doing this well requires real marketing "
        "expertise, ongoing testing, and a willingness to spend money learning what works. "
        "For those who figure it out it can be profitable, but it is not a plug-and-play solution.", s["body"]))

    story.append(Paragraph("Dedicated Lead Generation Agencies", s["h3"]))
    story.append(Paragraph(
        "A specialised company runs advertising campaigns on your behalf, generates leads "
        "exclusively for you, and delivers them in real time. The key difference from aggregators "
        "is exclusivity and accountability: your lead is never sold to another agent, the "
        "prospect's information is verified before delivery, and leads that do not meet spec are "
        "replaced. The cost per lead is typically higher, but the conversion economics are "
        "dramatically better because you are the only agent calling.", s["body"]))

    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "<i>If you want higher-quality conversations with prospects who are expecting your "
        "call and have not spoken to four other agents already, an exclusive lead generation "
        "partner will deliver a better cost per sale in almost every scenario.</i>", s["callout"]))

    story.append(Spacer(1, 4))
    story.append(cta(s,
        "Tired of chasing leads that never pick up?",
        ["Talk to Client Network about exclusive, phone-verified life insurance leads.",
         "One lead. One agent. Every time."]))

    story.append(PageBreak())

    # ════════ PAGE 3: 5-POINT CHECKLIST ════════
    story.append(Paragraph(
        "5 Things Every Agent Should Look For in a Lead Generation Partner", s["h1"]))
    story.append(tline())
    story.append(Paragraph(
        "Not all lead providers are built the same. Before you commit your budget, here are "
        "five things that separate a reliable partner from a vendor who will leave you chasing "
        "dead numbers.", s["body"]))

    story.extend(nitem(s, 1, "Exclusivity That Is Actually Enforced", [
        "\"Exclusive leads\" is the most overused promise in the industry. Many vendors claim "
        "exclusivity but define it loosely, selling the same lead to one agent per state, or "
        "recycling leads after 30 days. True exclusivity means one lead is generated for one "
        "buyer, full stop. It is never resold, recycled, or shared with anyone else, at any point."
    ], "\"Is this lead sold to anyone else, ever?\" If the answer involves caveats or "
       "timeframes, it is not exclusive."))

    story.extend(nitem(s, 2, "Real-Time Delivery While Intent Is Warm", [
        "The single biggest factor in whether a lead converts is speed. Contacting a prospect "
        "within the first five minutes of their inquiry increases conversion rates dramatically "
        "compared to waiting even 30 minutes. Your provider should deliver leads the moment the "
        "prospect submits their information, not batch them into a spreadsheet."
    ], "\"How quickly will I receive the lead after the prospect fills out the form?\" If "
       "the answer is not measured in seconds or minutes, that is a red flag."))

    story.extend(nitem(s, 3, "Phone Verification Before Delivery", [
        "Disconnected numbers, wrong numbers, and fake information are solvable problems, but "
        "most providers do not bother because verification costs money. A quality-focused "
        "provider will verify phone numbers via OTP (one-time password) before the lead reaches "
        "you, where the prospect enters a code sent to their phone to confirm the number is "
        "real and active. This single step eliminates a huge percentage of junk leads."
    ], "\"Do you verify phone numbers before delivery? How?\" If the answer is vague, "
       "that is not real verification."))

    story.extend(nitem(s, 4, "A Clear Replacement Policy for Bad Leads", [
        "Even with the best systems, some leads will fall outside spec. What matters is how "
        "your provider handles it. A trustworthy partner has a transparent replacement policy "
        "where leads that do not meet criteria are credited or replaced without a fight. You "
        "should not need to argue or threaten to cancel to get a fair outcome."
    ], "\"What is your return or replacement policy?\" Get it in writing before you start."))

    story.extend(nitem(s, 5, "Transparency About How Leads Are Generated", [
        "You have a right to know where your leads come from. A prospect who clicked a "
        "targeted ad about life insurance and filled out a detailed form is a very different "
        "conversation from someone cold-called by an overseas telemarketing room. A good "
        "provider will happily show you their ads, landing pages, and qualification process. "
        "If they refuse to share how leads are sourced, that usually means there is something "
        "they do not want you to see."
    ], "\"Can you show me the ad creative and landing page my leads come from?\" A provider "
       "who is proud of their process will say yes without hesitation."))

    story.append(Spacer(1, 4))
    story.append(cta(s,
        "Client Network checks every box.",
        ["100% exclusive. OTP phone-verified. Real-time delivery.",
         "Transparent process. Pay per result, no setup fees, no retainers."]))

    story.append(PageBreak())

    # ════════ PAGE 4: EXCLUSIVE ADVANTAGE + CN + FINAL CTA ════════
    story.append(Paragraph("The Exclusive Lead Advantage", s["h1"]))
    story.append(Paragraph("Why One Lead, One Agent Changes Everything", s["h2"]))
    story.append(tline())

    story.append(Paragraph(
        "When a lead is truly exclusive to you, the entire dynamic of the sales conversation "
        "shifts in your favour.", s["body"]))

    pts = [
        ("<b>You are calling someone who expects one call, not five.</b> There is no competition, "
         "no fatigue, no \"I already spoke to someone.\" The prospect is open and ready to talk."),
        ("<b>Your contact rate goes up significantly.</b> The prospect is not being bombarded by "
         "multiple agents, so they are far more likely to answer. And because the lead has been "
         "verified, you are not wasting time on disconnected or fake numbers."),
        ("<b>Your conversion rate improves because trust starts higher.</b> When a prospect only "
         "deals with one agent, they build rapport faster and share more about their situation. "
         "That depth of conversation is what turns a lead into a policy."),
    ]
    for p in pts:
        story.append(Paragraph(f"\u2022  {p}", s["bul"]))

    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Your cost per sale drops, even if the cost per lead is higher. This is the part most "
        "agents miss when comparing prices:", s["bb"]))

    # ── Comparison table ──
    cw = USABLE / 3
    td = [
        ["", Paragraph("Shared Leads", s["th"]), Paragraph("Exclusive Leads", s["th"])],
        [Paragraph("Cost per lead", s["tcl"]), Paragraph("$12", s["tc"]),
         Paragraph("$30", s["tc"])],
        [Paragraph("Close rate", s["tcl"]), Paragraph("2%", s["tc"]),
         Paragraph("12%", s["tc"])],
        [Paragraph("Leads per sale", s["tcl"]), Paragraph("50", s["tc"]),
         Paragraph("~8", s["tc"])],
        [Paragraph("Cost per sale", s["tcl"]), Paragraph("<b>$600</b>", s["tcb"]),
         Paragraph("<b>$250</b>", s["tcb"])],
    ]
    ct = Table(td, colWidths=[cw, cw, cw])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, TEAL_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 3))
    story.append(Paragraph(
        "The \"expensive\" lead is less than half the cost when you follow it through "
        "to a closed policy.", s["bb"]))

    story.append(Spacer(1, 8))

    # ── How CN Works ──
    story.append(Paragraph("How Client Network Works", s["h2"]))
    story.append(Paragraph(
        "Client Network is a lead generation partner built for insurance agents, brokers, "
        "and agencies who are done wasting money on shared, unverified leads.", s["body"]))

    cn = [
        "<b>100% exclusive leads.</b> Every lead is delivered to one buyer only. Never shared, never recycled, never resold.",
        "<b>OTP phone-verified before delivery.</b> Every prospect confirms their phone number via a one-time passcode before the lead reaches you.",
        "<b>Real-time delivery.</b> Leads arrive the moment the prospect completes the qualification process.",
        "<b>Pay per result, not per promise.</b> No setup fees, no monthly retainers, no ad spend risk. Fixed price per qualified lead.",
        "<b>Adjustable daily volume.</b> 5 leads per day or 50. Scale based on your capacity, consistent CPL regardless.",
        "<b>Replacement guarantee.</b> If a lead does not meet spec, it gets replaced. No arguments, no fine print.",
    ]
    for c in cn:
        story.append(Paragraph(f"\u2022  {c}", s["bul"]))

    story.append(Spacer(1, 10))

    # ── Final CTA ──
    story.append(cta(s,
        "Ready to See the Difference?",
        ["No pressure, no hard sell. Just a straightforward conversation about",
         "whether we can help you write more policies.",
         "One lead. One agent. Real-time delivery. Pay per result."],
        "Book Your Free Strategy Call"))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Client Network  |  clientnetwork.io  |  @clientnetwork", s["ft"]))
    story.append(Paragraph(
        "Pre-Qualified Prospects  |  Pay Per Result  |  Scale On Demand", s["ft"]))

    # ── Build ──
    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(TEAL)
        canvas.rect(0, PAGE_H - 5, PAGE_W, 5, fill=1, stroke=0)
        canvas.setStrokeColor(TEAL)
        canvas.setLineWidth(0.4)
        canvas.line(ML, MB - 4, PAGE_W - MR, MB - 4)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(GREY_LT)
        canvas.drawCentredString(PAGE_W / 2, MB - 12, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        PDF_PATH, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
        title="The Insurance Agent's Guide to Better Leads",
        author="Client Network")
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    print(f"PDF created: {PDF_PATH}")


if __name__ == "__main__":
    build()
