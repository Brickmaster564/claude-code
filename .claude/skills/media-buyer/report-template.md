# Media Buyer Report Data Template

This document defines the JSON structure that `tools/meta_report.py` expects as input, and the decision rules used to generate verdicts.

## Data File Structure

The report data file (`.tmp/report-data.json`) should have this structure:

```json
{
  "account_id": "act_123456789",
  "account_name": "Client Network - Life Insurance",
  "period": "Mar 7 - Mar 14, 2026",
  "summary": {
    "spend": 1250.00,
    "impressions": 85000,
    "clicks": 2100,
    "cpc": 0.60,
    "ctr": 2.47,
    "reach": 45000,
    "frequency": 1.9,
    "leads": 72,
    "cpl": 17.36
  },
  "campaigns": [
    {
      "campaign_name": "LI - Broad US 35-65",
      "campaign_id": "123",
      "spend": 800.00,
      "impressions": 55000,
      "clicks": 1400,
      "ctr": 2.55,
      "frequency": 2.1,
      "leads": 48,
      "cpl": 16.67,
      "verdict": "SCALE"
    }
  ],
  "creatives": [
    {
      "ad_name": "Quiz Hook v3",
      "ad_id": "456",
      "spend": 250.00,
      "impressions": 18000,
      "clicks": 480,
      "ctr": 2.67,
      "frequency": 2.8,
      "leads": 16,
      "cpl": 15.63,
      "fatigue": "OK",
      "verdict": "SCALE"
    }
  ],
  "daily_data": [
    {
      "date_start": "2026-03-07",
      "spend": 175.00,
      "impressions": 12000,
      "clicks": 300,
      "leads": 10,
      "cpl": 17.50
    }
  ],
  "recommendations": "1. Scale 'LI - Broad US 35-65' by 20% ($800 > $960/day). CPL is $16.67 vs $20 target.\n2. Cut 'LI - Retarget Old' - CPL $42 is 2x over target with declining CTR.\n3. Replace 'Quiz Hook v1' - frequency 5.8 (CRITICAL fatigue). Swap with new creative."
}
```

## Decision Rules

### Verdict Assignment

**SCALE** (green) - all must be true:
- CPL below vertical target
- Spend > $20 in the period (enough data)
- Frequency < 3.0

**HOLD** (yellow) - any of:
- CPL within 20% of vertical target (above or below)
- Insufficient data (spend < $10)
- Frequency between 3.0 and 4.0

**CUT** (red) - any of:
- CPL > 2x vertical target
- Frequency > 5.0
- CTR < 0.5%
- Zero leads with > $30 spend

### Creative Fatigue Levels

| Frequency | Level | Action |
|---|---|---|
| < 3.0 | OK | No action needed |
| 3.0 - 5.0 | WARNING | Plan replacement creative |
| > 5.0 | CRITICAL | Replace immediately |

### CPL Targets by Vertical

| Vertical | Target CPL | Scale Below | Cut Above |
|---|---|---|---|
| Life Insurance | $20 | $16 | $40 |
| Senior Care | $16 | $13 | $32 |
| Home Security | $12 | $10 | $24 |
| Tax Relief | $14 | $11 | $28 |
| Gold IRA | $28 | $22 | $56 |

### Budget Recommendations

- **Scale:** Increase budget by 20% (never more than 30% per change, per campaign playbook)
- **Hold:** Maintain current budget. Monitor for 48h before re-evaluating.
- **Cut:** Reduce budget to minimum or pause. Reallocate to SCALE campaigns.
- **Neutral buffer rule:** For every aggressive creative, maintain 4-5 neutral ads at $1-2/day each.
