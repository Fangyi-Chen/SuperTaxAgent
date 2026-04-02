---
name: tax-domain-crypto
description: Digital asset and cryptocurrency tax rules. Invoked by core skills when a 1099-DA is detected during document import or when the user reports cryptocurrency transactions.
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

## Trigger Conditions

Core skills invoke this domain skill when:
- `tax-start`: User mentions cryptocurrency, Bitcoin, Ethereum, NFT, DeFi, staking rewards, mining income, USDC, stablecoins, or "digital assets"
- `tax-import`: A 1099-DA document is detected; or 1099-MISC box 3 (other income) is present from a known crypto exchange
- `tax-calculate`: `domains.crypto` in tax-profile.json is non-null

## Interview Questions

Ask these questions when triggered. Ask 2-3 at a time.

1. "Did you buy, sell, trade, or dispose of any cryptocurrency or other digital assets in 2025? This includes converting one crypto to another (e.g., ETH → BTC), using crypto to pay for goods/services, and receiving crypto as payment."
2. "Which exchanges or wallets did you use? Did you receive a 1099-DA from any of them? (Starting in 2025, most major U.S. exchanges are required to issue 1099-DA.)"
3. "What cost basis method do you want to use: FIFO (first-in, first-out), HIFO (highest-in, first-out), or Specific Identification? Note: you must elect Specific ID at the time of sale and maintain adequate records."
4. "Did you receive any staking rewards in 2025? If yes, approximately what was the fair market value of the rewards at the time you received them?"
5. "Did you do any cryptocurrency mining in 2025? If yes, what was the approximate fair market value of the mined coins when you received them?"
6. "Did you participate in any DeFi (decentralized finance) activities — such as providing liquidity, yield farming, lending, or borrowing — in 2025?"
7. "Did you receive any crypto as a gift, in an airdrop, or as compensation for services?"
8. "Did you hold any stablecoins (USDC, USDT, DAI, etc.)? Did you redeem, swap, or transfer them in 2025?"
9. "Did you buy, sell, or trade any NFTs (non-fungible tokens) in 2025?"
10. "Did you use any crypto-to-crypto swaps or bridging transactions (e.g., wrapped tokens, Layer 2 bridges)?"

## Data Schema

Add under `domains.crypto` in `data/tax-profile.json`:

```json
{
  "domains": {
    "crypto": {
      "has1099DA": true,
      "exchanges": ["Coinbase", "Kraken"],
      "costBasisMethod": "FIFO",
      "form1040DigitalAssetCheckbox": true,
      "salesAndDisposals": [
        {
          "asset": "BTC",
          "saleDate": "2025-07-14",
          "proceeds": 28500,
          "costBasis": 18200,
          "gainLoss": 10300,
          "holdingPeriod": "long",
          "reportingCategory": "box-H-noncovered",
          "source1099DA": true
        }
      ],
      "ordinaryIncome": {
        "stakingRewards": 840,
        "miningIncome": 0,
        "airdrops": 120,
        "cryptoCompensation": 0,
        "defiIncome": 200
      },
      "stablecoinTransactions": {
        "hasStablecoinActivity": true,
        "aggregatedGainLoss": 0,
        "note": "USDC redeemed at $1.00; basis $1.00 per coin — de minimis gain/loss"
      },
      "nftTransactions": [],
      "summary": {
        "totalShortTermGainLoss": null,
        "totalLongTermGainLoss": null,
        "totalOrdinaryIncome": null
      }
    }
  }
}
```

## Calculation Rules

### Rule 1: Form 1040 Digital Asset Checkbox
Every taxpayer who received, sold, exchanged, or otherwise disposed of digital assets must check "Yes" on Form 1040, page 1, digital asset question. This applies even if no gain or loss resulted. Check "No" only if the taxpayer merely held digital assets without any transactions.

### Rule 2: Capital Gains/Losses — Sales and Exchanges
Every sale, trade, or exchange of cryptocurrency is a taxable event.

For each transaction:
  **Gain/Loss = Proceeds − Adjusted Cost Basis**

- **Short-term** (held ≤ 1 year): taxed at ordinary income rates.
- **Long-term** (held > 1 year): taxed at preferential capital gains rates (0%, 15%, 20%).
- Report on Form 8949; summarize on Schedule D.

### Rule 3: Crypto-to-Crypto Swaps
Converting one cryptocurrency to another (e.g., ETH → SOL) is a taxable disposal of the first asset.
- Proceeds = FMV of asset received at time of swap.
- Basis in new asset = FMV at acquisition date.

### Rule 4: 1099-DA Form 8949 Box
- 1099-DA transactions are generally reported in **Form 8949 Box H** (long-term) or **Box E** (short-term) for "noncovered" securities.
- Box B (short-term covered) or Box E (long-term covered) if basis IS reported to IRS by the broker.
- Verify: if 1099-DA Box 1e (cost basis) is populated, use Box A or D (covered); if $0 or blank, use Box B or E (noncovered).

### Rule 5: Cost Basis Methods
- **FIFO (First-In, First-Out):** Default method if no election made. Oldest lots sold first.
- **HIFO (Highest-In, First-Out):** Sell highest-cost lots first; maximizes loss recognition (or minimizes gains). Requires adequate records.
- **Specific Identification:** Identify exact lot at time of sale. Must be elected contemporaneously with the sale and records maintained per IRS guidelines. Most flexible but most demanding.
- Once a method is chosen for a given asset, it should be applied consistently (no formal lock-in rule, but IRS scrutinizes switches that appear tax-motivated).

### Rule 6: Staking Rewards and Mining Income
Per Rev. Rul. 2023-14, staking rewards are includible in gross income at **FMV when received**.
- Report as ordinary income on Schedule 1, Line 8z (other income).
- Basis in the received tokens = FMV at time of receipt.
- Subsequent sale of staking tokens is a capital gain/loss event.
- Mining income: same treatment — ordinary income at FMV when received.

### Rule 7: Stablecoin Transactions
Stablecoins (USDC, USDT, DAI, etc.) are treated as property, not currency, for U.S. tax purposes.
- Disposal of stablecoins is a taxable event.
- In practice, stablecoins pegged to $1 typically result in $0 gain/loss if held at stable peg.
- If 1099-DA reports stablecoin transactions, report on Form 8949; gains/losses likely de minimis.
- Aggregation rule: For stablecoin-to-stablecoin swaps or redemptions that are entirely at $1.00, enter as a single aggregated line if gain/loss is $0 — see IRS Notice 2014-21 (still applicable to stablecoin context).

### Rule 8: Airdrops and Hard Forks
- Airdrops: ordinary income at FMV when received (regardless of whether actively claimed).
- Hard forks resulting in new tokens: ordinary income at FMV when the taxpayer has dominion and control over the new tokens.
- Report on Schedule 1, Line 8z.

### Rule 9: DeFi — Providing Liquidity
- Depositing tokens into a liquidity pool: potentially a taxable exchange if LP tokens received differ from deposited tokens (FMV determines proceeds).
- Receiving liquidity pool rewards: ordinary income at FMV when received.
- Removing liquidity: taxable disposal at FMV of tokens received.

### Rule 10: NFT Sales
- NFTs are property; sales are capital gain/loss events.
- Short-term or long-term based on holding period.
- Collectible NFTs may be subject to 28% collectibles capital gains rate if they qualify as "collectibles" under IRC §408(m) — IRS guidance pending; flag to user.

## References

Read `skills/tax-domain-crypto/references/digital-asset-rules.md` for IRS notices, Rev. Rulings, Form 8949 examples, and cost basis method comparisons.
