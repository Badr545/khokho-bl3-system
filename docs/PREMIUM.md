# 💎 Commercial Licensing & Stripe Integration

## Generating License Keys
To generate keys for hosted customers or one-off sales:
`ash
python scripts/generate_keys.py --tier pro --days 30 --count 5
`

## Stripe Subscription Sync
1. Setup webhook pointing to https://your-domain.com/api/v1/premium/webhook.
2. Listen for checkout.session.completed to auto-credit tiers into eatures.db.