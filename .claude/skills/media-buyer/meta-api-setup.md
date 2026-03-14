# Meta Marketing API Setup Guide

Follow these steps to connect the `/media-buyer` skill to your Meta ad accounts.

## Step 1: Create a Facebook App

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **My Apps** > **Create App**
3. Select **Other** > **Business** type
4. App name: `CN Media Buyer` (or whatever you prefer)
5. Link it to your Business Manager (CN & Nalu Group)

## Step 2: Add Marketing API

1. In the App Dashboard, go to **Add Products**
2. Find **Marketing API** and click **Set Up**
3. This unlocks access to the Ads Management and Insights APIs

## Step 3: Generate an Access Token

### Option A: System User Token (Recommended)

System User tokens don't expire. Best for automation.

1. Go to [Business Settings](https://business.facebook.com/settings/) > **Users** > **System Users**
2. Click **Add** > name it `media-buyer-bot` > set role to **Admin**
3. Click **Add Assets** > select your ad account(s) > grant **Full Control**
4. Click **Generate New Token**
5. Select your app (`CN Media Buyer`)
6. Check these permissions:
   - `ads_management` (create/edit campaigns, ad sets, ads, creatives)
   - `ads_read` (pull insights, read campaign structure)
   - `business_management` (access Business Manager assets)
7. Click **Generate Token** and copy it immediately (you won't see it again)

### Option B: User Access Token (Simpler, Expires in 60 Days)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app in the dropdown
3. Click **Generate Access Token**
4. Check permissions: `ads_management`, `ads_read`
5. Copy the short-lived token
6. Exchange for a long-lived token (60-day):
   ```
   curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
   ```
7. You'll need to repeat this every 60 days

## Step 4: Store Credentials

Add to `config/api-keys.json`:

```json
{
  "meta_access_token": "EAAxxxxxx..."
}
```

## Step 5: Install Python SDK

Already done if you followed the setup. If not:

```bash
pip3 install --break-system-packages facebook_business
```

## Step 6: Verify Connection

```bash
python3 tools/meta_ads.py --account-id act_XXXXXXXXX account-overview --days 1
```

Replace `act_XXXXXXXXX` with your actual ad account ID (find it in Ads Manager > Account Overview, or Business Settings > Ad Accounts).

If you see JSON with spend/impressions data, you're connected. If you get an error about permissions, double-check the token scopes in Step 3.

## Finding Your Ad Account ID

- **Ads Manager:** Look in the URL or Account Overview dropdown. Format: `act_123456789`
- **Business Settings:** Go to Accounts > Ad Accounts. The ID is shown next to each account name.
- **Always include the `act_` prefix** when passing to `meta_ads.py`

## Token Expiry

- **System User tokens (Option A):** Never expire. Recommended.
- **User tokens (Option B):** Expire after 60 days. When you see a "Token expired" error, regenerate following Step 3B.
