# Tax Agent

AI-powered tax filing assistant for Claude Code. File your federal tax return through an interactive interview — import W2s and 1099s, calculate your refund, and generate a mail-ready IRS Form 1040 PDF. All locally on your machine.

## Quick Start

```
/tax-start          # begin the interview
/tax-import w2.pdf  # import a tax document
/tax-calculate      # compute your return
/tax-fill           # generate the 1040 PDF
```

## Installation

Add the marketplace, then install:

```
/plugin marketplace add fangyic/tax-agent-marketplace
/plugin install tax-agent@tax-agent-marketplace
```

Or install directly from GitHub:

```
/plugin install https://github.com/fangyic/tax-agent.git
```

## Skills

### Core Pipeline

| Command | Description |
|---------|-------------|
| `/tax-start [year]` | Interactive interview to collect all tax data (personal info, dependents, income, deductions, credits). Saves to `data/tax-profile.json`. |
| `/tax-import <file>` | Parse W2, 1099-B, 1099-DIV, 1099-INT, 1099-DA, 1099-MISC from PDF or image. Auto-detects document type and merges into your profile. |
| `/tax-calculate` | Compute your federal return — income, AGI, deductions, tax brackets, credits (CTC, EIC), refund or amount owed. Maps to Form 1040 line numbers. |
| `/tax-fill` | Fill the official IRS fillable Form 1040 PDF with your calculated data. Outputs a print-and-mail-ready PDF. |

### Domain Knowledge

These skills are automatically invoked by the core pipeline when relevant income types are detected.

| Skill | Triggers When... | What It Knows |
|-------|-------------------|---------------|
| `tax-domain-rsu` | W2 box 14 has RSU codes, or 1099-B has ESPP lots | RSU vesting taxation, cost basis = FMV at vest, ISO/NSO rules, ESPP qualifying dispositions |
| `tax-domain-rental` | User reports rental property income | Schedule E, MACRS 27.5-year depreciation, $25K passive loss allowance, active participation rules |
| `tax-domain-harvest` | 1099-B has wash sale adjustments | 30-day wash sale rule, adjusted basis, $3,000 net loss limit, carryforward |
| `tax-domain-crypto` | 1099-DA detected | Form 8949 reporting, FIFO/specific ID cost basis, staking income, DeFi, stablecoin rules |

### Self-Evolution

Help improve the tax agent for the community by comparing your output against TurboTax.

| Command | Description |
|---------|-------------|
| `/tax-compare <our.pdf> <turbotax.pdf>` | Diff two returns line by line. Identifies which fields match and which diverge. |
| `/tax-evolve` | Analyze discrepancies, classify root causes, generate skill fixes. |
| `/tax-publish [description]` | Submit improvements as a GitHub PR to the plugin repo. |

## How It Works

```
/tax-start ──> /tax-import ──> /tax-calculate ──> /tax-fill
     |              |                |                  |
     |         (detects type)   (applies rules)         |
     |              |                |                  |
     v              v                v                  v
 tax-profile.json  (merges)   tax-calculation.json   1040.pdf
                                                        |
                                                /tax-compare <── turbotax.pdf
                                                        |
                                                 /tax-evolve
                                                        |
                                                 /tax-publish ──> GitHub PR
```

## Privacy

All data stays **100% local** on your machine:
- Tax profile and calculations are stored in `data/` (gitignored)
- Imported PDFs are never uploaded anywhere
- The self-evolution system only submits anonymized rule fixes (no PII) — and only with your explicit review and approval

## Supported Tax Year

2025 (filing in 2026). Tax brackets, credits, and standard deduction amounts are specific to the 2025 tax year.

## Limitations (v1)

- Federal return only (no state returns)
- Form 1040 + Schedule B + Schedule D + Form 8949
- No e-filing (print and mail)
- No AMT calculation
- No Schedule C (self-employment) — coming soon

## Contributing

Found a bug or want to add a new domain skill? Run `/tax-publish "your description"` after making changes, or open a PR directly.

## License

MIT
