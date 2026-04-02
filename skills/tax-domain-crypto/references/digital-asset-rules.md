# Digital Asset Tax Rules — IRS Reference

## Governing Law and IRS Guidance

- **IRC §61** — Gross income from all sources, including virtual currency.
- **IRC §1001** — Gain/loss on sale or exchange of property.
- **IRC §1221/1222** — Capital asset definitions and holding periods.
- **IRS Notice 2014-21** — Virtual currency is property; general tax principles apply; mining income = ordinary income at FMV when received.
- **Rev. Rul. 2019-24** — Hard forks result in ordinary income when taxpayer has dominion and control over new tokens.
- **Rev. Rul. 2023-14** — Staking rewards are includible in gross income at FMV when received; overrides Jarrett v. United States (M.D. Tenn. 2022) which ruled staking rewards were not immediately taxable.
- **IRS FAQ on Virtual Currency (IRS.gov)** — Updated guidance on airdrops, DeFi, NFTs (check for updates as of filing date).
- **Form 1099-DA (introduced 2025)** — Digital Asset Proceeds from Broker Transactions.
- **Form 8949 Instructions** — Capital asset sales and exchanges.
- **IRS Publication 544** — Sales and Other Dispositions of Assets.

## Form 1040 Digital Asset Question

The digital asset question on Form 1040 page 1 must be answered by all taxpayers:

**"At any time during 2025, did you: (a) receive (as a reward, award, or payment for property or services); or (b) sell, exchange, or otherwise dispose of a digital asset (or a financial interest in a digital asset)?"**

- Answer **Yes** if any of the following occurred: received crypto as payment, staking/mining rewards, airdrops, sold/traded crypto, converted crypto to fiat, used crypto to purchase goods/services, gifted crypto.
- Answer **No** if you only HELD digital assets with zero transactions. Checking "No" falsely when transactions occurred is a compliance risk.

## 1099-DA — New for Tax Year 2025

### Background
The Infrastructure Investment and Jobs Act (2021) expanded broker reporting to include digital asset brokers. The IRS finalized regulations requiring brokers (centralized exchanges, hosted wallet providers, and certain DeFi protocols) to issue Form 1099-DA starting for transactions in calendar year 2025.

### Key Fields
| Box | Description |
|-----|-------------|
| 1a | Description of property (asset name/ticker) |
| 1b | Date acquired |
| 1c | Date sold or disposed |
| 1d | Proceeds |
| 1e | Cost or other basis |
| 1f | Accrued market discount |
| 1g | Wash sale loss disallowed |
| 2 | Short-term (Box 2a) or long-term (Box 2b) gain/loss indicator |
| 3 | If checked: basis NOT reported to IRS (noncovered) |
| 4 | Federal income tax withheld |
| 5 | Type of gain or loss |

### Reporting on Form 8949

| 1099-DA Situation | Form 8949 Box |
|-------------------|---------------|
| Short-term, basis reported to IRS | Box A |
| Short-term, basis NOT reported | Box B |
| Long-term, basis reported to IRS | Box D |
| Long-term, basis NOT reported | Box E |

For "basis not reported" entries: enter proceeds in column (d), YOUR calculated basis in column (e), and no adjustment needed in column (g) unless there is a wash sale or other adjustment.

## Cost Basis Methods — Comparison

### FIFO (First-In, First-Out)
- Default if no other election made.
- Oldest lots consumed first on any sale.
- Generally produces the largest gain (or smallest loss) because early crypto purchases often have low basis.
- Simple and defensible.

### HIFO (Highest-In, First-Out)
- Highest-cost lots consumed first.
- Minimizes current-year gain (or maximizes loss recognition).
- Requires detailed records of all purchases with dates and prices.
- No IRS rule explicitly authorizes HIFO by name, but Specific Identification (which allows HIFO-equivalent lot selection) is permitted.

### Specific Identification
- Taxpayer designates exact lots at time of sale.
- Requires contemporaneous documentation: date, amount, price of the specific lot being sold.
- Most tax-efficient but most record-keeping intensive.
- For centralized exchanges: many provide lot selection tools; export trade history as documentation.
- IRS Rev. Proc. 2024-28 provides a safe harbor for taxpayers who have been using a universal method and wish to transition to Specific ID, allowing them to allocate remaining basis to specific lots using a reasonable method.

### Consistency Requirement
Once a method is chosen, the IRS expects consistent application within an asset class. Switching methods to maximize current-year tax benefit (especially if the switch is retroactive) is not permitted.

## Staking and Mining Income — Rev. Rul. 2023-14

### Staking
- When a taxpayer receives staking rewards, they have ordinary income equal to the FMV of the tokens on the date of receipt.
- FMV = price of the token on a reputable exchange at the date/time of receipt (spot price).
- Basis in received tokens = FMV at receipt.
- Reporting: Schedule 1, Line 8z ("Other income" — describe as "Staking rewards").

### Mining
- Same treatment as staking: ordinary income at FMV when coins are received.
- If mining rises to the level of a trade or business (Schedule C), self-employment tax also applies. For occasional/hobby mining, report on Schedule 1.
- Mining equipment may be depreciable (out of scope for v1).

## DeFi Transaction Tax Analysis

### Liquidity Providing
1. **Deposit:** Depositing Token A and Token B into a pool and receiving LP tokens is likely a taxable exchange. Proceeds = FMV of LP tokens received. Gain/loss on disposed Token A and B.
2. **Fees/Rewards:** Periodic fees or reward tokens are ordinary income at FMV when received.
3. **Withdrawal:** Redeeming LP tokens for Token A and Token B is a taxable event. Proceeds = FMV of tokens received. Gain/loss on LP tokens.

Note: IRS has not issued specific DeFi guidance as of 2025; the above analysis follows Notice 2014-21 general property principles.

### Wrapped Tokens
Wrapping ETH → WETH is likely a taxable exchange per property rules (two different tokens). However, many practitioners treat wrapping/unwrapping as non-taxable on the theory that the assets are economically equivalent. Use caution and document the position taken.

### Bridges and Layer 2 Transfers
Moving native ETH to a Layer 2 (e.g., Arbitrum, Optimism) via a bridge where you receive a "bridged" version may be treated as an exchange. The IRS has not issued specific guidance. Document transactions and basis at time of bridge.

## NFT Tax Treatment

### Sales of NFTs
- NFTs are property; gain/loss = sale proceeds − basis.
- Basis = price paid to acquire (including gas fees, which are capitalized into basis).
- Holding period determines short-term or long-term.

### Collectibles Rate
- Under IRC §1(h)(4), "collectibles" gains are taxed at a maximum 28% rate (not the standard 20% long-term rate).
- Collectibles include: works of art, rugs, antiques, metals, gems, stamps, coins, and "any other tangible personal property that the IRS determines is a collectible."
- Whether NFTs constitute collectibles is unresolved. IRS Notice 2023-27 requested public comments. Until further guidance, many practitioners default to treating NFTs as capital assets subject to standard rates unless the underlying asset (e.g., digital art) is clearly a collectible. Flag this uncertainty to user.

## Stablecoin Tax Treatment

- Stablecoins are property under Notice 2014-21.
- Each transfer, swap, or redemption is a taxable event.
- In practice, USDC redeemed at $1.00 with a $1.00 basis yields $0 gain/loss.
- If a stablecoin depegs (e.g., LUNA/UST collapse), losses may be recognizable — either as capital loss on disposal, or potentially as worthless security (IRC §165) if the token becomes worthless.
- Stablecoin-to-stablecoin swaps (e.g., USDC → USDT) are taxable exchanges. If both are at $1.00 parity, the gain/loss is de minimis.

## Gifts of Cryptocurrency

### Recipient's Basis
- Carryover basis: recipient takes donor's basis.
- If FMV at date of gift < donor's basis: basis for loss = FMV at date of gift; basis for gain = donor's original basis.
- Recipient's holding period includes donor's holding period.

### Gift Tax (Donor)
- Gifts of crypto are subject to gift tax rules (annual exclusion $19,000 per recipient in 2025).
- Donor does NOT recognize gain at time of gift.

### Charitable Donation of Crypto
- Deduction = FMV at date of donation (for long-term capital gain property donated to a public charity, within AGI limits).
- No capital gain recognized by donor.
- File Form 8283 if donation > $500.
