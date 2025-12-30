import csv
import glob
import os

# =========================
# CONFIG
# =========================
PERCENT = 0.01
OUTPUT_SUFFIX = "_one_percent.csv"

# Addresses to EXCLUDE (one per line)
EXCLUDED_ADDRESSES = {
    # Examples — replace with real ones
    "",
}

# Normalize exclusions once
EXCLUDED_ADDRESSES = {addr.strip().upper() for addr in EXCLUDED_ADDRESSES}

# =========================
# FIND LATEST CSV
# =========================
csv_files = glob.glob("asa_*_holders.csv")


if not csv_files:
    raise FileNotFoundError("❌ No CSV files found in the current directory")

latest_csv = max(csv_files, key=os.path.getmtime)
print(f"📄 Using latest CSV: {latest_csv}")

# =========================
# READ + CALCULATE
# =========================
rows_out = []
excluded_count = 0

with open(latest_csv, newline="") as f:
    reader = csv.DictReader(f)

    if "address" not in reader.fieldnames or "amount" not in reader.fieldnames:
        raise ValueError("❌ CSV must contain 'address' and 'amount' columns")

    for row in reader:
        address = row["address"].strip().upper()

        if address in EXCLUDED_ADDRESSES:
            excluded_count += 1
            continue

        amount = int(row["amount"])
        one_percent = int(amount * PERCENT)

        if one_percent > 0:
            rows_out.append({
                "address": address,
                "one_percent_amount": one_percent
            })

# =========================
# WRITE OUTPUT CSV
# =========================
output_file = latest_csv.replace(".csv", OUTPUT_SUFFIX)

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["address", "one_percent_amount"]
    )
    writer.writeheader()
    writer.writerows(rows_out)

# =========================
# REPORT
# =========================
print(f"✅ Saved 1% allocation file: {output_file}")
print(f"📊 Addresses included: {len(rows_out)}")
print(f"🚫 Addresses excluded: {excluded_count}")
