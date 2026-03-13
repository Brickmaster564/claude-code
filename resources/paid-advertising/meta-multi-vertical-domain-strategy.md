# Meta Multi-Vertical Domain & Pixel Strategy

**Use case:** Running multiple subverticals (e.g. life, auto, commercial insurance) inside one Meta ad account without triggering domain inconsistency flags.

---

## The Rule

One Meta ad account = one root domain. Never send traffic from a single ad account to multiple unrelated root domains. Meta monitors domain patterns and inconsistency raises flags.

## The Solution: Subdomains

For umbrella verticals like insurance, use one root domain with subdomains per subvertical:

| Subvertical | Landing Page |
|---|---|
| Life Insurance | `life.rootdomain.com` |
| Auto Insurance | `auto.rootdomain.com` |
| Commercial Insurance | `commercial.rootdomain.com` |

Meta treats these as the same root domain. You get separation at the funnel level without triggering domain mismatch signals.

## Pixel Strategy: One Per Subvertical

Each subvertical gets its own pixel, even though they share one ad account and root domain.

| Subvertical | Pixel | Tracks |
|---|---|---|
| Life Insurance | Pixel A | `life.rootdomain.com` |
| Auto Insurance | Pixel B | `auto.rootdomain.com` |
| Commercial Insurance | Pixel C | `commercial.rootdomain.com` |

**Why separate pixels:**
- Different subverticals target different demographics (age, income, life stage)
- Clean audience data per vertical. No cross-contamination between a 25-year-old looking for auto quotes and a 55-year-old looking for whole life
- Each pixel builds its own lookalike audiences and retargeting pools independently
- Optimization signals stay pure. Meta learns what a "good lead" looks like for each subvertical separately

## Summary

| Layer | Rule |
|---|---|
| Ad Account | One per umbrella vertical (e.g. "Insurance") |
| Root Domain | One shared root domain across all subverticals |
| Subdomains | One per subvertical (`life.`, `auto.`, `commercial.`) |
| Pixels | One per subvertical (separate demographic data) |
| Audiences | Built independently per pixel. No sharing across subverticals |
