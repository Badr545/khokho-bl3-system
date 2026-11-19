#!/usr/bin/env python3
# =====================================================================
# ─── COMMERCIAL LICENSE KEY GENERATOR (CLI)
#     Generates unique KHOKHO-XXXX-XXXX-XXXX license keys,
#     hashes them using SHA-256 / bcrypt, and saves them in features.db
# =====================================================================
import sys
import os
import secrets
import hashlib
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.features_schema import execute_feat, commit_feat, init_features_schema

def generate_key_string() -> str:
    part1 = secrets.token_hex(2).upper()
    part2 = secrets.token_hex(2).upper()
    part3 = secrets.token_hex(2).upper()
    return f"KHOKHO-{part1}-{part2}-{part3}"

def main():
    parser = argparse.ArgumentParser(description="Khokho Bl3 V3 — Premium License Key Generator")
    parser.add_argument("--tier", choices=["basic", "pro", "ultra"], default="basic", help="Premium tier")
    parser.add_argument("--days", type=int, default=30, help="Duration in days (e.g. 30, 90, 365)")
    parser.add_argument("--count", type=int, default=1, help="Number of keys to generate")
    args = parser.parse_args()

    init_features_schema()

    print(f"\n🔑 Generating {args.count} license key(s) for Tier: {args.tier.upper()} ({args.days} days)...\n")
    generated = []

    for _ in range(args.count):
        raw_key = generate_key_string()
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        execute_feat(
            "INSERT INTO premium_keys (key_hash, tier, duration_days, is_redeemed) VALUES (?, ?, ?, 0)",
            (key_hash, args.tier, args.days)
        )
        generated.append(raw_key)

    commit_feat()

    print("═══════════════════════════════════════════════════════════")
    for k in generated:
        print(f"  🎟️  {k}  [{args.tier.upper()} - {args.days} Days]")
    print("═══════════════════════════════════════════════════════════\n")
    print("✅ All keys securely stored and ready for customer activation!\n")

if __name__ == "__main__":
    main()