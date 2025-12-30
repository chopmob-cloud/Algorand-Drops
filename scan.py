from algosdk.v2client import indexer
import csv

# =========================
# CONFIG
# =========================
INDEXER_URL = "https://mainnet-idx.algonode.cloud"
ASA_ID =    # <-- replace with your ASA ID
OUTPUT_FILE = f"asa_{ASA_ID}_holders.csv"

# =========================
# INDEXER CLIENT
# =========================
idx = indexer.IndexerClient("", INDEXER_URL)

# =========================
# FETCH HOLDERS
# =========================
holders = []
next_token = None

while True:
    resp = idx.accounts(
        asset_id=ASA_ID,
        limit=1000,
        next_page=next_token
    )

    for acct in resp.get("accounts", []):
        for asset in acct.get("assets", []):
            if asset["asset-id"] == ASA_ID:
                holders.append({
                    "address": acct["address"],
                    "amount": asset["amount"]
                })

    next_token = resp.get("next-token")
    if not next_token:
        break

print(f"Fetched {len(holders)} holders")

# =========================
# WRITE CSV
# =========================
with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["address", "amount"])
    writer.writeheader()
    writer.writerows(holders)

print(f"Saved to {OUTPUT_FILE}")
