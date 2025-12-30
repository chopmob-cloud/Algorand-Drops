import csv
import glob
import os
import time

from dotenv import load_dotenv
from algosdk.v2client.algod import AlgodClient
from algosdk import mnemonic, account
from algosdk.transaction import AssetTransferTxn, wait_for_confirmation

# =========================
# LOAD .env
# =========================
load_dotenv()

# =========================
# CONFIG
# =========================
ALGOD_ADDRESS = "https://mainnet-api.algonode.cloud"
ALGOD_TOKEN = ""

ASA_ID =           # <-- YOUR ASA ID
WALLET_MNEMONIC = os.getenv("WALLET_MNEMONIC")

DELAY_BETWEEN_TXNS = 1.2     # seconds
DRY_RUN = True            # 🔒 SET False TO EXECUTE

# =========================
# VALIDATE WALLET
# =========================
if not WALLET_MNEMONIC:
    raise Exception("❌ WALLET_MNEMONIC not found in .env file")

sender_sk = mnemonic.to_private_key(WALLET_MNEMONIC)
sender_addr = account.address_from_private_key(sender_sk)

algod = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

print(f"🚀 Sender address: {sender_addr}")
print(f"📦 ASA ID: {ASA_ID}")
print(f"🧪 Dry-run mode: {DRY_RUN}")

# =========================
# FIND LATEST DAILY CSV
# =========================
csv_files = glob.glob("daily/*_one_percent.csv")

if not csv_files:
    raise FileNotFoundError("❌ No daily/*_one_percent.csv files found")

latest_csv = max(csv_files, key=os.path.getmtime)
print(f"📄 Using CSV: {latest_csv}")

# =========================
# LOAD RECIPIENTS
# =========================
recipients = []
total_required = 0

with open(latest_csv, newline="") as f:
    reader = csv.DictReader(f)

    if "address" not in reader.fieldnames or "one_percent_amount" not in reader.fieldnames:
        raise ValueError("❌ CSV must contain address, one_percent_amount")

    for row in reader:
        amount = int(row["one_percent_amount"])
        if amount > 0:
            recipients.append((row["address"], amount))
            total_required += amount

print(f"👥 Total recipients: {len(recipients)}")
print(f"🧮 Total ASA required: {total_required}")

# =========================
# BALANCE CHECK
# =========================
acct_info = algod.account_info(sender_addr)

asa_balance = 0
for asset in acct_info.get("assets", []):
    if asset["asset-id"] == ASA_ID:
        asa_balance = asset["amount"]
        break

print(f"💰 Sender ASA balance: {asa_balance}")

if asa_balance < total_required:
    raise Exception(
        f"❌ Insufficient ASA balance "
        f"(have {asa_balance}, need {total_required})"
    )

print("✅ ASA balance check passed")

# =========================
# DRY-RUN EXIT
# =========================
if DRY_RUN:
    print("\n🧪 DRY-RUN COMPLETE")
    print("➡️ No transactions were sent")
    print("➡️ Set DRY_RUN = False to execute the airdrop")
    exit(0)

# =========================
# SEND AIRDROP
# =========================
success = 0
failed = 0

for i, (receiver, amount) in enumerate(recipients, start=1):
    try:
        sp = algod.suggested_params()

        txn = AssetTransferTxn(
            sender=sender_addr,
            sp=sp,
            receiver=receiver,
            amt=amount,
            index=ASA_ID
        )

        signed_txn = txn.sign(sender_sk)
        txid = algod.send_transaction(signed_txn)

        wait_for_confirmation(algod, txid, 4)

        print(f"✅ [{i}/{len(recipients)}] Sent {amount} → {receiver}")
        success += 1
        time.sleep(DELAY_BETWEEN_TXNS)

    except Exception as e:
        print(f"❌ [{i}] Failed → {receiver}: {e}")
        failed += 1

# =========================
# SUMMARY
# =========================
print("\n🎉 AIRDROP COMPLETE")
print(f"✅ Successful transfers: {success}")
print(f"❌ Failed transfers: {failed}")
print(f"📄 Source CSV: {latest_csv}")
