# Meta Advertising Infrastructure Handbook

Client Network's reference guide for Meta (Facebook) ad infrastructure, account architecture, and operational procedures.

Last updated: 2026-03-10

---

## 1. Target Architecture

The system uses a 5-layer model designed for resilience. If any single layer gets hit, the rest survive and you can recover quickly.

```
Layer 1: Pixel BM (Safehouse)        — Owns pixel data. Never runs ads.
Layer 2: Execution BM (Battleground) — Runs campaigns. Replaceable.
Layer 3: Aged US Profiles (Operators) — Day-to-day operations in AdsPower.
Layer 4: Personal Profile (Admin)     — Emergency access only.
Layer 5: Ad Accounts                  — Self-serve (warming) or Agency (scaled).
```

### Layer 1: Pixel BM (Safehouse)

- **Purpose:** Store and protect pixel data and conversion history
- **Current BM:** "CN & Nalu Group" (Pixel ID: 1820262881982518)
- **Rules:** Never run ads from this BM. Keep it clean. Its only job is to own the pixel and share it with the Execution BM.
- **Why it matters:** If your Execution BM gets restricted, your pixel data survives here. You reconnect a new Execution BM and keep all your conversion data.
- **Sharing status:** Currently too new to share pixel data with partners. Meta requires several weeks of compliant activity before enabling partner sharing. Keep the BM active to unlock this.

### Layer 2: Execution BM (Battleground)

- **Purpose:** House ad accounts, pages, and operational profiles. All campaign activity happens here.
- **Setup:** Separate BM from the Pixel BM. Receives shared pixel data.
- **Recovery:** If restricted, replace the entire BM. Reshare pixel from the Safehouse BM. Operational again in hours.
- **Future:** Home for agency ad accounts when ready to scale.

### Layer 3: Aged US Profiles (Operators)

- **Purpose:** Handle day-to-day campaign management so your personal profile stays untouched
- **Quantity:** 2 aged US profiles
- **Setup:** Each profile runs in its own AdsPower browser profile with a dedicated ISP proxy (geo-matched to the profile's country)
- **Buying criteria:**
  - ID-verified status preferred, or comes with ID documents for future verification
  - US-based with matching proxy geo
  - Genuine activity history (not freshly created then abandoned)
  - Fluent English profile presentation
- **Risk:** ID verification requests can kill a profile if you can't provide matching ID. Having ID docs mitigates this.
- **Replacement:** If one dies, buy a replacement and invite into the Execution BM. No critical data is lost because profiles are operators, not owners of important assets.

### Layer 4: Personal Profile (Emergency Admin)

- **Purpose:** Admin access on both BMs as a safety net
- **Rules:** Never use for routine ad operations. Only log into BMs if both aged profiles are compromised.
- **Why separate:** If Meta takes action on an operator profile, your personal Facebook account stays clean and unaffected.

### Layer 5: Ad Accounts

- **Current:** 3 self-serve ad accounts warming inside BM. Low spend limits, gradually increasing.
- **Future:** Agency ad accounts for stable, high-limit spend in restricted verticals (insurance, finance).
- See Section 2 for full agency ad account details.

---

## 2. Agency Ad Accounts

Agency ad accounts are ad accounts created under a Meta Business Partner's high-trust Business Manager. The agency shares them into your BM so you can run campaigns, but the account's stability comes from the agency's relationship with Meta.

### How They Work

1. You sign up with a provider (Uproas, Laurel Agency, SquareWave, etc.)
2. They create an ad account under their verified, high-trust BM
3. They share that account into your Execution BM
4. You run campaigns through Ads Manager as normal
5. The agency handles billing with Meta
6. If an account gets restricted, they reinstate or replace it in 1-3 days

### What They Solve

- **Stability:** High trust = fewer random bans, reviews, or restrictions
- **Spend limits:** Pre-approved $2,500-$5,000+/day (vs slowly warming from $25/day)
- **Restricted verticals:** Agencies specialising in finance/insurance get approvals that self-serve accounts can't
- **Replacement speed:** Days, not weeks of warming a new account
- **Meta support:** Direct escalation through the agency's partner status

### What They Don't Solve

- You still need a Facebook profile to operate your BM
- You still need your own BM to receive the shared ad accounts
- Profile vulnerability is a separate problem (solved by Layer 3)

### Cost

- **Flat fee:** $250-$500/month per account
- **Percentage model:** 4-7% of ad spend
- **Minimum deposit:** $200-$500
- **Setup time:** 1-3 days

### When to Get Agency Accounts

Get them when you're ready to scale beyond what self-serve accounts can handle, or when you need stable approvals in the insurance/finance vertical. Don't rush into them if you're still testing angles at low spend. Your self-serve warming accounts are fine for that.

---

## 3. Profile Management

### AdsPower Configuration

Each Facebook profile (aged or personal) must run in its own isolated AdsPower browser profile. Never share browser profiles between Facebook accounts.

**Per-profile setup:**
- Dedicated AdsPower browser profile
- Dedicated ISP proxy (geo-matched to the Facebook profile's country)
- Unique browser fingerprint (AdsPower handles this)
- Separate cookies and session data

**Rules:**
- Never log into multiple Facebook accounts from the same proxy
- Never log into multiple Facebook accounts from the same browser profile
- Never switch between accounts in the same session
- Each profile = one proxy = one browser = one identity

### Proxies

**Use static ISP proxies.** They are the best option for Facebook ad account management.

| Proxy Type | Best For | Facebook Ad Accounts? |
|---|---|---|
| **ISP (static)** | Ongoing account management, consistent logins | Yes (recommended) |
| **Residential (rotating)** | Account creation, warming, scraping | No. Rotating IPs look suspicious. |
| **Datacenter** | High-speed scraping, non-social tasks | No. Easily detected by Facebook. |
| **Mobile** | Account creation, high anonymity tasks | Overkill and expensive for ad management. |

**Why ISP proxies win for ad accounts:**
- Static IP stays the same every session. Facebook sees consistent login behavior.
- Registered as ISP addresses (not datacenter), so they look legitimate
- Fast and reliable
- Cheaper than residential proxies

**Rules:**
- 1 static ISP proxy per Facebook profile. Never share proxies between profiles.
- Proxy country must match the Facebook profile's registered country (US profiles = US proxies)
- IP mismatch between proxy and account country triggers security locks
- Keep the same IP for weeks/months. Never rotate during login, billing, or BM operations.
- If you must change a proxy, do it gradually (not mid-session) and expect a possible checkpoint.

### ID Verification Risk

Meta can request ID verification on any profile at any time. This is the primary risk with aged profiles.

**Mitigation:**
- Buy profiles that are already ID-verified
- Buy profiles that come with matching ID documents
- Maintain consistent, normal-looking activity on profiles (don't let them go dormant then spike)
- Avoid rapid changes to profile information (name, location, etc.)

**If a profile gets ID-checked and you can't verify:**
- That profile is lost. Do not attempt to bypass.
- Remove it from the BM
- Buy a replacement and set up fresh in AdsPower
- No critical data is lost because profiles are operators, not asset owners

---

## 4. Uproas Account Tiers

Reference for future scaling. Based on the Uproas "Bulletproof Facebook Account Structures" guide.

| Tier | BMs | Profiles | Pages | Agency Ad Accounts | Best For |
|---|---|---|---|---|---|
| **Standard** | 1 Execution + 1 Pixel | 3 | 1 | 1 | Getting started, low-to-mid spend |
| **Premium** | 1 Execution + 1 Pixel | 6 (2 admin + 4 staff) | 2 | 1+ | Spreading activity signals, mid spend |
| **Elite** | 2 Execution + 1 Pixel | 7 | 3 | 1+ | High-ban-rate verticals (insurance), high spend |

**Standard** is sufficient to start. Move to Premium or Elite when spend justifies it or if operating in high-restriction verticals like insurance.

---

## 5. Operational Rules

### What Triggers Flags

- Proxy geo mismatch with account country
- Dormant accounts suddenly spiking spend
- Rapid changes to BM information (name, address, contacts)
- Adding/removing multiple payment methods quickly
- Inviting lots of new people to a BM immediately after purchase
- Running ads that violate Meta's advertising policies (especially in finance/health)
- Multiple accounts sharing the same proxy or device fingerprint
- Inconsistent login patterns (different countries, different times, irregular frequency)

### Spend Warming

- New self-serve ad accounts start with low daily limits ($25-50/day)
- Increase spend gradually (20-30% increments every few days)
- Don't jump from $50/day to $500/day overnight
- Agency ad accounts come pre-warmed with higher limits, but still ramp responsibly
- Consistent daily spend is better than erratic spikes

### BM Hygiene

- Complete business verification when prompted
- Use legitimate, consistent payment methods aligned with account geo
- Don't make rapid structural changes to the BM
- Keep the BM active with regular, normal operations
- Avoid anything that looks like you're trying to evade detection

### Ad Content for Restricted Verticals

Life insurance and financial services are restricted categories on Meta:
- Avoid income claims or guaranteed returns
- Don't use before/after financial comparisons
- Include required disclaimers
- Use compliant landing pages
- Agency ad accounts from providers specialising in finance have better approval rates for these

---

## 6. Recovery Playbook

### Profile Gets ID-Checked (Can't Verify)

1. Accept the profile is lost
2. Remove it from the Execution BM
3. Buy a replacement aged US profile (ID-verified preferred)
4. Set up in new AdsPower browser profile with new dedicated ISP proxy
5. Invite into Execution BM
6. Resume operations. No data lost.

### Ad Account Gets Restricted

**If self-serve:**
1. Appeal through the standard Meta process
2. If appeal fails, the account is likely gone
3. Continue warming your other accounts
4. Consider this the signal to move to agency ad accounts

**If agency:**
1. Contact the agency provider immediately
2. They escalate through their Meta partnership
3. Account may be reinstated, or they create a replacement in 1-3 days
4. Reconnect to your pixel and resume

### Execution BM Gets Restricted

1. Pixel data is safe in the Safehouse BM
2. Set up a new Execution BM
3. Share pixel from Safehouse BM to new Execution BM
4. Invite aged profiles into new BM
5. Request new agency ad accounts (or move existing ones)
6. Reconnect pages and resume campaigns
7. Operational again in hours to days, not weeks

### Pixel BM Gets Restricted

This is the worst case and why the Pixel BM should never run ads or do anything risky.

1. If this happens, pixel data and conversion history are at risk
2. Create a new Pixel BM
3. Create a new pixel (conversion data from the old one is lost)
4. Reconnect to Execution BM
5. Campaigns will need to re-learn. This is painful but survivable.

**Prevention:** Keep the Pixel BM completely clean. No ads, no sketchy activity, no unnecessary profile additions.

---

## 7. Provider Directory

### Uproas
- **Specialty:** Full-stack account architecture + agency ad accounts
- **Scale:** $20M+ monthly spend managed, 1,750+ businesses
- **Offers:** Structured packages (Standard/Premium/Elite), verified BMs, agency ad accounts, antidetect guidance
- **Best for:** Comprehensive setup with built-in resilience
- **Website:** uproas.io

### Laurel Agency
- **Specialty:** High-risk verticals (finance, insurance, gambling, crypto, nutra)
- **Best for:** Insurance/finance vertical specifically, where standard accounts get banned quickly
- **Use case:** If you need agency ad accounts that are pre-approved for financial services

### SquareWave
- **Specialty:** Enterprise-level accounts, industry-specific packages
- **Base:** Estonia
- **Offers:** Structured onboarding with compliance reviews, vertical-specific setup
- **Budget requirement:** Minimum ~$500 spend, 2-5 day setup
- **Best for:** Larger-scale operations with compliance focus

---

## 8. Cost Reference

### Current Setup (DIY)

| Item | Cost | Frequency |
|---|---|---|
| Aged US profiles | $50-100 each | One-time (replace when they die) |
| AdsPower subscription | $10-50 | Monthly |
| ISP proxies (2) | $20-50 | Monthly |
| **Total ongoing** | **~$30-100** | **Monthly + replacement costs** |

Hidden cost: Time spent managing infrastructure, sourcing replacements, troubleshooting.

### Agency Setup (Future)

| Item | Cost | Frequency |
|---|---|---|
| Agency ad accounts (2) | $500-1,000 (or 4-7% of spend) | Monthly |
| AdsPower subscription | $10-50 | Monthly |
| ISP proxies | $20-50 | Monthly |
| **Total ongoing** | **~$530-1,100** | **Monthly** |

Higher monthly cost, but: stable ad accounts, pre-approved spend limits, faster approvals in restricted verticals, fast recovery, and less time on infrastructure.

**ROI threshold:** If agency accounts help you generate even a handful of leads that cover the ~$500 extra monthly cost, they pay for themselves.

---

## 9. Current Status & Migration Checklist

**As of 2026-03-10:**

- [x] Pixel BM created ("CN & Nalu Group", pixel: 1820262881982518)
- [x] Pixel created (no events received yet)
- [ ] Pixel BM matured enough for partner sharing (needs several weeks of activity)
- [ ] Buy 2 aged US profiles (ID-verified preferred)
- [ ] Set up each profile in AdsPower with dedicated ISP proxy
- [ ] Invite aged profiles into BM
- [ ] Create or acquire Execution BM (separate from Pixel BM)
- [ ] Share pixel from Pixel BM to Execution BM (once sharing unlocks)
- [ ] Move ad accounts to Execution BM (or create new ones there)
- [ ] Run test campaigns at $20-50/day to validate setup
- [ ] Research agency ad account providers (Uproas, Laurel Agency)
- [ ] Get agency ad accounts when ready to scale
- [ ] Scale spend gradually on agency accounts

---

## 10. Pixel Sharing Between BMs

### How to Share (Once Unlocked)

1. Log into the **Pixel BM** (the one that owns the pixel)
2. Go to **Business Settings > Data Sources > Datasets & pixels**
3. Select your pixel
4. Click the **Partners** tab
5. Click **Assign partner**
6. Enter the **Business ID** of your Execution BM
7. Set permissions (Manage dataset recommended)

### Finding a BM's Business ID

- Go to Business Settings in the target BM
- Look under **Business info** in the left sidebar
- The Business ID is displayed there (also visible in the URL)

### Limitations

- Only the owning BM can share the pixel. The receiving BM cannot reshare it.
- Ownership cannot be transferred, only access.
- New BMs must wait several weeks of compliant activity before sharing is enabled.
- The Pixel BM must remain active and in good standing for the sharing to persist.

---

## 11. Step-by-Step Setup Guide (Uproas Method)

### Step 1: Acquire Facebook Assets

Either build manually (slow, months of warming) or purchase pre-aged assets. Requirements:
- 2 aged US profiles (ID-verified preferred)
- 2 BMs (Pixel BM + Execution BM)
- Pages for the Execution BM

### Step 2: Install Anti-Detect Browser

**Dolphin Anty** is the recommended anti-detect browser (Uproas standard). AdsPower is an alternative. Free tier covers up to 5-10 profiles.

- Each Facebook profile gets its own isolated Dolphin Anty browser profile
- Unique browser fingerprint per profile (Dolphin Anty handles fingerprint generation)
- Separate cookies and session data per profile

### Step 3: Purchase ISP Proxies

Uproas recommends **Floxy** for ISP proxies. Buy one per profile, US geo.

- Static ISP proxies only (not residential, not datacenter, not mobile)
- 1 unique proxy per profile — never share proxies between profiles
- US proxies for US profiles

### Step 4: Configure Dolphin Anty Profiles

For each Facebook profile:
1. Create new browser profile in Dolphin Anty
2. Name it clearly (e.g. "Pixel BM Operator", "Execution BM Admin")
3. Copy proxy from Floxy dashboard
4. Select HTTP connection type
5. Create profile

### Step 5: Log Into Facebook Assets

- Open each profile in Dolphin Anty (never in a regular browser)
- Log into one Facebook account per browser profile
- Never log into multiple accounts from the same proxy or fingerprint — triggers pattern detection

### Step 6: Connect Everything

1. Share Pixel from Safe BM to Execution BM
2. Add Agency Ad Account to Execution BM (via BM ID sharing with the agency)
3. Assign Page inside Execution BM
4. Launch campaigns from Execution BM only
5. Keep Safe BM completely untouched

---

## Sources

- [Uproas: Bulletproof Facebook Account Structures](https://www.uproas.io/uproas-books/bulletproof-facebook-account-structures)
- [What is Facebook Agency Account: Ultimate Guide 2026](https://agencygdt.com/blog/what-is-facebook-agency-account/)
- [Why Top Advertisers Rely on Agency Ad Accounts](https://www.uproas.io/blog/what-are-agency-ad-accounts)
- [Facebook Agency Ad Account Prices in 2026](https://www.wetracked.io/post/facebook-agency-ad-account-prices)
- [Best Meta Agency Ad Accounts 2026](https://blog.zeropenny.co/p/best-meta-agency-ad-accounts-2026)
- [Meta Agency Ad Account: Everything You Need to Know](https://www.stackmatix.com/blog/meta-agency-ad-account)
- [Share Meta Pixel from Business Manager](https://support.smartly.io/hc/en-us/articles/360009113674-Share-Meta-Pixel-from-Business-Manager)
- [How to Share Facebook Pixel in Business Manager](https://www.paidmediapros.com/blog/how-to-share-facebook-pixel-in-business-manager/)
