"""Media buyer morning briefing engine.

Designed to answer: "How are my campaigns doing, what should I kill,
what's winning, and should I scale?" All comparisons are relative
within the account's own data."""


def generate_insights(summary, campaigns, ads, daily_data, account_id, days):
    """Generate a morning briefing from performance data.

    Returns list of {priority, category, title, detail} dicts.
    Priority: HIGH = act on this now, MEDIUM = worth knowing, LOW/INFO = context.
    """
    insights = []

    if not ads and not campaigns:
        return insights

    total_spend = summary.get("spend", 0) if summary else 0

    if total_spend < 1:
        insights.append({
            "priority": "INFO",
            "category": "status",
            "title": "No meaningful spend yet",
            "detail": "Waiting for delivery data to generate insights.",
        })
        return insights

    # --- Morning briefing sections ---

    # 1. Overall campaign health status
    insights.extend(_campaign_status(summary, campaigns, days))

    # 2. The winner and why
    insights.extend(_winning_ad(ads))

    # 3. Kill list: ads that need cutting
    insights.extend(_kill_list(ads))

    # 4. CPM anomalies
    insights.extend(_cpm_flags(ads, campaigns))

    # 5. CTR red flags
    insights.extend(_ctr_flags(ads))

    # 6. Fatigue / frequency warnings
    insights.extend(_fatigue_flags(ads))

    # 7. Scaling readiness
    insights.extend(_scaling_assessment(summary, campaigns, ads, days))

    # 8. Budget waste
    insights.extend(_budget_efficiency(campaigns))

    # 9. Trend detection (multi-day only)
    if days >= 3 and len(daily_data) >= 3:
        insights.extend(_trend_detection(daily_data))

    # Sort: HIGH first
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    insights.sort(key=lambda x: order.get(x["priority"], 3))

    return insights


def _campaign_status(summary, campaigns, days):
    """Quick overall status line."""
    insights = []

    spend = summary.get("spend", 0)
    leads = summary.get("leads", 0)
    cpl = summary.get("cpl")
    ctr = summary.get("ctr", 0)

    period = "today" if days <= 1 else f"the last {days} days"
    cpl_str = f" at £{cpl:.2f}/lead" if cpl else " with no leads yet"

    active_campaigns = [c for c in campaigns if c.get("campaign_status") == "ACTIVE"]

    insights.append({
        "priority": "INFO",
        "category": "status",
        "title": f"£{spend:.2f} spent, {leads} lead{'s' if leads != 1 else ''}{cpl_str}",
        "detail": (
            f"{len(active_campaigns)} active campaign{'s' if len(active_campaigns) != 1 else ''} "
            f"running over {period}. "
            f"Account CTR: {ctr:.2f}%, "
            f"CPM: £{summary.get('cpm', 0):.2f}, "
            f"CPC: £{summary.get('cpc', 0):.2f}."
        ),
    })

    return insights


def _winning_ad(ads):
    """Identify the top performing ad and explain why it's winning."""
    insights = []

    with_leads = [a for a in ads if a.get("leads", 0) > 0 and a.get("cpl")]
    if not with_leads:
        return insights

    # Best by CPL
    best = min(with_leads, key=lambda a: a["cpl"])

    # Calculate how it compares
    if len(with_leads) > 1:
        others_cpl = [a["cpl"] for a in with_leads if a.get("ad_id") != best.get("ad_id")]
        avg_others = sum(others_cpl) / len(others_cpl) if others_cpl else best["cpl"]
        pct_better = ((avg_others - best["cpl"]) / avg_others * 100) if avg_others > 0 else 0
    else:
        avg_others = best["cpl"]
        pct_better = 0

    # Figure out WHY it's winning
    best_ctr = best.get("ctr", 0)
    best_cpm = best.get("cpm", 0)
    all_ctrs = [a.get("ctr", 0) for a in ads if a.get("spend", 0) > 3]
    avg_ctr = sum(all_ctrs) / len(all_ctrs) if all_ctrs else 0

    reasons = []
    if best_ctr > avg_ctr * 1.3 and avg_ctr > 0:
        reasons.append(f"CTR of {best_ctr:.2f}% is well above the {avg_ctr:.2f}% average, meaning the hook is resonating")
    if best.get("frequency", 0) < 2:
        reasons.append(f"frequency is still low at {best.get('frequency', 0):.1f}, so there's room to run")
    if best_cpm and best_cpm < 10:
        reasons.append(f"CPM is efficient at £{best_cpm:.2f}")

    why_str = ". ".join(reasons) + "." if reasons else ""

    detail = (
        f"£{best['cpl']:.2f}/lead from {best.get('leads', 0)} leads on £{best.get('spend', 0):.2f} spend."
    )
    if pct_better > 15 and len(with_leads) > 1:
        detail += f" That's {pct_better:.0f}% cheaper than the other converting ads."
    if why_str:
        detail += f" {why_str}"
    detail += " Consider creating variations of this angle."

    insights.append({
        "priority": "MEDIUM",
        "category": "winner",
        "title": f'Winner: "{best.get("ad_name", "Unknown")}"',
        "detail": detail,
        "ad_id": best.get("ad_id"),
    })

    return insights


def _kill_list(ads):
    """Ads that should be cut based on relative performance."""
    insights = []

    # Group ads by campaign
    by_campaign = {}
    for a in ads:
        cid = a.get("campaign_id", "unknown")
        by_campaign.setdefault(cid, []).append(a)

    kills = []

    for cid, camp_ads in by_campaign.items():
        if len(camp_ads) < 2:
            continue

        with_leads = [a for a in camp_ads if a.get("leads", 0) > 0 and a.get("cpl")]
        if not with_leads:
            continue

        best_cpl = min(a["cpl"] for a in with_leads)
        campaign_name = camp_ads[0].get("campaign_name", "")

        for a in camp_ads:
            spend = a.get("spend", 0)
            leads = a.get("leads", 0)
            cpl = a.get("cpl")
            name = a.get("ad_name", "Unknown")

            if spend < 5:
                continue

            reason = None

            # Zero leads while siblings convert
            if leads == 0 and spend > 15:
                reason = f"£{spend:.2f} spent, zero leads (best sibling: £{best_cpl:.2f}/lead)"

            # CPL 2x+ worse than best sibling
            elif cpl and cpl > best_cpl * 2 and leads > 0:
                ratio = cpl / best_cpl
                reason = f"£{cpl:.2f}/lead, {ratio:.1f}x more expensive than the best ad (£{best_cpl:.2f})"

            if reason:
                kills.append({"name": name, "reason": reason, "ad_id": a.get("ad_id"), "campaign": campaign_name})

    if kills:
        if len(kills) == 1:
            k = kills[0]
            insights.append({
                "priority": "HIGH",
                "category": "kill",
                "title": f'Kill "{k["name"]}"',
                "detail": f'{k["reason"]}. This spend is better off on your converting ads.',
                "ad_id": k.get("ad_id"),
            })
        else:
            lines = [f'"{k["name"]}": {k["reason"]}' for k in kills]
            insights.append({
                "priority": "HIGH",
                "category": "kill",
                "title": f"{len(kills)} ads to cut",
                "detail": ". ".join(lines) + ". Pause these and let the budget flow to your winners.",
            })

    return insights


def _cpm_flags(ads, campaigns):
    """Flag ads with unusually high CPM relative to the account."""
    insights = []

    spending_ads = [a for a in ads if a.get("spend", 0) > 3 and a.get("cpm")]
    if len(spending_ads) < 2:
        return insights

    cpms = [a["cpm"] for a in spending_ads]
    avg_cpm = sum(cpms) / len(cpms)

    # Flag ads 50%+ above average CPM
    high_cpm = [
        a for a in spending_ads
        if a["cpm"] > avg_cpm * 1.5 and a["cpm"] > avg_cpm + 3
    ]

    if high_cpm:
        for a in high_cpm[:3]:
            pct_above = ((a["cpm"] - avg_cpm) / avg_cpm) * 100
            insights.append({
                "priority": "MEDIUM",
                "category": "cpm",
                "title": f'High CPM: "{a.get("ad_name")}" at £{a["cpm"]:.2f}',
                "detail": (
                    f"{pct_above:.0f}% above the account average of £{avg_cpm:.2f}. "
                    "High CPM means Meta is charging more to show this ad, which could indicate "
                    "low relevance score, narrow audience, or the creative isn't engaging."
                ),
                "ad_id": a.get("ad_id"),
            })

    return insights


def _ctr_flags(ads):
    """Flag ads with unusually low CTR that may be dragging performance."""
    insights = []

    spending_ads = [a for a in ads if a.get("spend", 0) > 3 and a.get("ctr") is not None]
    if len(spending_ads) < 2:
        return insights

    ctrs = [a["ctr"] for a in spending_ads]
    avg_ctr = sum(ctrs) / len(ctrs)

    # Flag ads below 50% of average CTR (or below 0.5% absolute)
    threshold = max(avg_ctr * 0.5, 0.5)
    low_ctr = [a for a in spending_ads if a["ctr"] < threshold]

    if low_ctr:
        for a in low_ctr[:3]:
            insights.append({
                "priority": "MEDIUM",
                "category": "ctr",
                "title": f'Low CTR: "{a.get("ad_name")}" at {a["ctr"]:.2f}%',
                "detail": (
                    f"Account average is {avg_ctr:.2f}%. Low CTR means people are seeing "
                    "the ad but not clicking. The hook or creative isn't grabbing attention. "
                    "This also hurts your relevance score, which drives CPM up."
                ),
                "ad_id": a.get("ad_id"),
            })

    return insights


def _fatigue_flags(ads):
    """Flag creative fatigue based on frequency."""
    insights = []

    critical = [a for a in ads if a.get("frequency") and a["frequency"] > 5 and a.get("spend", 0) > 3]
    warning = [a for a in ads if a.get("frequency") and 3 < a["frequency"] <= 5 and a.get("spend", 0) > 3]

    for ad in critical:
        insights.append({
            "priority": "HIGH",
            "category": "fatigue",
            "title": f'Burned: "{ad.get("ad_name")}" (freq {ad["frequency"]:.1f})',
            "detail": (
                "Your audience has seen this ad too many times and performance will keep dropping. "
                "Replace this creative or pause it."
            ),
            "ad_id": ad.get("ad_id"),
        })

    if warning:
        names = [f'"{a.get("ad_name")}" ({a["frequency"]:.1f})' for a in warning[:4]]
        insights.append({
            "priority": "MEDIUM",
            "category": "fatigue",
            "title": f"{len(warning)} ad(s) approaching fatigue",
            "detail": f"{', '.join(names)}. Have replacement creatives ready.",
        })

    return insights


def _scaling_assessment(summary, campaigns, ads, days):
    """Assess whether the account is ready to scale."""
    insights = []

    # Need at least 3 days of data to make scaling calls
    if days < 3:
        return insights

    leads = summary.get("leads", 0) if summary else 0
    cpl = summary.get("cpl") if summary else None
    freq = summary.get("frequency", 0) if summary else 0

    if leads < 3 or not cpl:
        return insights

    # Check for scaling blockers
    blockers = []

    if freq and freq > 3.5:
        blockers.append(f"account frequency is {freq:.1f} (audience getting saturated)")

    critical_fatigue = [a for a in ads if a.get("frequency") and a["frequency"] > 5 and a.get("spend", 0) > 5]
    if len(critical_fatigue) > 0:
        blockers.append(f"{len(critical_fatigue)} ad(s) with burned-out creatives")

    # Count how many ads are actually converting
    converting_ads = [a for a in ads if a.get("leads", 0) > 0]
    if len(converting_ads) < 2:
        blockers.append("only 1 ad converting (single point of failure)")

    if blockers:
        insights.append({
            "priority": "MEDIUM",
            "category": "scaling",
            "title": "Not ready to scale yet",
            "detail": (
                "Blockers: " + "; ".join(blockers) + ". "
                "Fix these before increasing budget, otherwise you'll just spend more on the same problems."
            ),
        })
    else:
        # Green light for scaling
        active_campaigns = [c for c in campaigns if c.get("daily_budget")]
        if active_campaigns:
            total_daily = sum((c.get("daily_budget") or 0) / 100 for c in active_campaigns)
            suggested = total_daily * 1.2
            insights.append({
                "priority": "MEDIUM",
                "category": "scaling",
                "title": "Account looks healthy enough to scale",
                "detail": (
                    f"{len(converting_ads)} ads converting, frequency under control, "
                    f"no major blockers. Current daily budget: ~£{total_daily:.0f}. "
                    f"Safe to test £{suggested:.0f}/day (+20%). "
                    "Increase gradually, never more than 20-30% at once."
                ),
            })

    return insights


def _budget_efficiency(campaigns):
    """Flag campaigns eating budget without proportional results."""
    insights = []

    total_spend = sum(c.get("spend", 0) for c in campaigns)
    total_leads = sum(c.get("leads", 0) for c in campaigns)

    if total_spend < 20 or total_leads < 2 or len(campaigns) < 2:
        return insights

    for c in campaigns:
        spend = c.get("spend", 0)
        leads = c.get("leads", 0)
        name = c.get("campaign_name", "Unknown")

        if spend < 10:
            continue

        spend_pct = (spend / total_spend) * 100
        lead_pct = (leads / total_leads) * 100 if total_leads > 0 else 0

        if spend_pct > 30 and lead_pct < 10:
            insights.append({
                "priority": "HIGH",
                "category": "budget",
                "title": f'"{name}": {spend_pct:.0f}% of budget, {lead_pct:.0f}% of leads',
                "detail": (
                    f"£{spend:.2f} spent for {leads} lead{'s' if leads != 1 else ''}. "
                    "This campaign is consuming a disproportionate share of the budget "
                    "relative to what it's producing."
                ),
                "campaign_id": c.get("campaign_id"),
            })

    return insights


def _trend_detection(daily_data):
    """Detect performance direction over the period."""
    insights = []

    with_leads = [d for d in daily_data if d.get("leads", 0) > 0 and d.get("cpl")]
    if len(with_leads) < 4:
        return insights

    mid = len(with_leads) // 2
    first_avg = sum(d["cpl"] for d in with_leads[:mid]) / mid
    second_avg = sum(d["cpl"] for d in with_leads[mid:]) / (len(with_leads) - mid)

    if first_avg == 0:
        return insights

    change = ((second_avg - first_avg) / first_avg) * 100

    if change > 30:
        insights.append({
            "priority": "HIGH",
            "category": "trend",
            "title": f"CPL trending up {change:.0f}% over the period",
            "detail": (
                f"£{first_avg:.2f} average (first half) to £{second_avg:.2f} (second half). "
                "Something is deteriorating: check which ads are driving the increase, "
                "whether frequency is climbing, or if audience quality is dropping."
            ),
        })
    elif change < -25:
        insights.append({
            "priority": "INFO",
            "category": "trend",
            "title": f"CPL improving, down {abs(change):.0f}%",
            "detail": (
                f"£{first_avg:.2f} down to £{second_avg:.2f}. "
                "The account is finding its groove. Good time to consider scaling."
            ),
        })

    return insights
