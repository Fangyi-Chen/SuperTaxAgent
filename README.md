<div align="center">

# 🧾 SuperTaxAgent

**AI-powered US federal tax filing, right inside Claude Code.**
**在 Claude Code 里用 AI 报美国联邦税 — 免费、本地、开源。**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-8A4FFF.svg)](https://claude.com/claude-code)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing--招募合作者)

*Import your W2. Ask Claude to prepare your return. Get a mail-ready 1040 PDF. Local-first, open-source, no subscription.*

</div>

---

## 🌍 Why this project · 为什么做这个项目

> **"征税没有征到最应该被征税的人身上，而是征到最容易被征税的人身上。"**
>
> Taxes don't fall on those who *should* pay them most — they fall on those who are *easiest* to tax: wage earners, immigrants, working families. Meanwhile, commercial tax software costs $100–$300 a year, even for a simple W2 filing.

This project is built on a simple belief: **AI should serve the many, not the few.** With a capable model and a well-designed agent, preparing a straightforward return shouldn't require an expensive annual subscription. Your data should stay on your laptop. The rules should be open. And if the agent gets something wrong, the whole community should be able to fix it — permanently, for everyone.

这个项目的初衷，是基于 **"AI 造福最广大人民"** 的思想：让普通工薪家庭、留学生、新移民、小业主，都能免费、私密、体面地完成自己的报税准备工作，不必再被昂贵的年费软件反复收割。你的数据留在自己电脑上，规则全部开源，社区一起让它越来越准。

---

## 📦 Installation · 安装

Install from the Claude Code plugin marketplace:

```
/plugin marketplace add Fangyi-Chen/tax-marketplace
/plugin install super-tax-agent@tax-marketplace
```

Or install directly from GitHub:

```
/plugin install https://github.com/Fangyi-Chen/SuperTaxAgent.git
```

> Requires [Claude Code](https://claude.com/claude-code). Works on macOS, Linux, and Windows.

---

## 🚀 Quick Start · 快速上手

The easiest way — **just ask Claude in plain language**:

```
help me do tax 2025
帮我报 2025 年的税
```

Claude will walk you through the interview, ask for your documents, and handle the rest.

Prefer explicit commands? Use the pipeline directly:

```
/tax-start            # begin the interactive interview
/tax-import w2.pdf    # import a W2 / 1099 / brokerage PDF
/tax-calculate        # compute refund or amount owed
/tax-fill             # produce a mail-ready IRS 1040 PDF
```

---

## 🧠 Skills

### Core pipeline · 核心流程

| Command | Description |
|---|---|
| `/tax-start [year]` | Interactive interview — personal info, dependents, income, deductions, credits. Saves to `data/tax-profile.json`. |
| `/tax-import <file>` | Parse W2, 1099-B, 1099-DIV, 1099-INT, 1099-DA, 1099-MISC from PDF or image. Auto-detects type. |
| `/tax-calculate` | Compute income, AGI, deductions, brackets, credits (CTC, EIC), refund or amount owed. Maps to Form 1040 line numbers. |
| `/tax-fill` | Fill the official IRS fillable Form 1040 PDF. Outputs a print-and-mail-ready PDF. |

### Domain knowledge · 领域规则

Automatically invoked by the core pipeline when relevant income types appear.

| Skill | Triggers when... | What it knows |
|---|---|---|
| `tax-domain-rsu` | W2 box 14 has RSU codes, or 1099-B has ESPP lots | RSU vesting, cost basis = FMV at vest, ISO/NSO, ESPP qualifying dispositions |
| `tax-domain-rental` | User reports rental income | Schedule E, MACRS 27.5-yr depreciation, $25K passive loss allowance |
| `tax-domain-harvest` | 1099-B has wash sale adjustments | 30-day wash sale rule, adjusted basis, $3,000 net loss limit, carryforward |
| `tax-domain-crypto` | 1099-DA detected | Form 8949, FIFO / specific-ID cost basis, staking, DeFi, stablecoin rules |

### Self-evolution · 自进化

Help make the agent smarter for everyone by comparing your output against TurboTax.

| Command | Description |
|---|---|
| `/tax-compare <our.pdf> <turbotax.pdf>` | Diff two returns line by line. |
| `/tax-evolve` | Classify discrepancies, generate skill fixes. |
| `/tax-publish [description]` | Submit improvements as an anonymized GitHub PR. |

---

## 🔁 How it works · 工作流程

```
/tax-start ──> /tax-import ──> /tax-calculate ──> /tax-fill
     │              │                │                 │
     │        (detects type)    (applies rules)        │
     ▼              ▼                ▼                 ▼
tax-profile.json  (merges)    tax-calculation.json   1040.pdf
                                                       │
                                              /tax-compare ◄── turbotax.pdf
                                                       │
                                                /tax-evolve
                                                       │
                                                /tax-publish ──> GitHub PR
```

---

## 🔒 Privacy · 隐私

All data stays **100% local** on your machine.
所有数据 **100% 留在你自己电脑上**。

- Tax profile and calculations live in `data/` (gitignored)
- Imported PDFs are never uploaded anywhere
- Self-evolution PRs contain only anonymized rule fixes — **no PII**, and only with your explicit review

---

## 📅 Supported tax year · 支持年度

**2025 tax year** (filing in 2026). Brackets, credits, and standard deduction amounts are specific to TY2025.

## ⚠️ Limitations · 当前限制 (v1)

- Federal return only (no state returns yet)
- Form 1040 + Schedule B + Schedule D + Form 8949
- No e-filing — print and mail
- No AMT calculation
- No Schedule C (self-employment) — coming soon

---

## ⚖️ Legal Notice · 法律声明

**Not tax, legal, or accounting advice.** SuperTaxAgent is an open-source software tool for **individuals preparing their own tax returns**. It is provided for informational purposes only and does **not** constitute tax, legal, or accounting advice, and it does **not** create any professional-client relationship. You are solely responsible for reviewing your return for accuracy and for any filing you submit to the IRS or any state authority. For advice specific to your situation, consult a licensed tax professional (CPA, Enrolled Agent, or tax attorney).

**Self-prep use only.** This tool is intended for self-preparation of your own return. If you prepare returns for others **for compensation**, you must obtain an IRS PTIN and comply with IRS Circular 230 as well as any applicable state registration requirements (e.g., CTEC in California, OBTP in Oregon, MD, NY). SuperTaxAgent does not grant, represent, or substitute for any such credential.

**No affiliation.** SuperTaxAgent is an independent open-source project. It is not affiliated with, endorsed by, or sponsored by the Internal Revenue Service, Intuit Inc., TurboTax, H&R Block, or any certified public accountant, state board of accountancy, or government agency. All trademarks belong to their respective owners.

**本工具不构成税务、法律或会计建议。** SuperTaxAgent 是一个供 **个人为自己准备税表** 使用的开源软件，仅供参考，不构成任何形式的税务、法律或会计专业意见，也不建立任何专业委托关系。您需对所提交税表的准确性和合法性自行负责。如需针对您具体情况的专业建议，请咨询持证税务专业人士（CPA、EA 或税务律师）。

**仅限自用准备。** 若您 **以收取报酬的方式** 为他人报税，必须依法取得 IRS PTIN 并遵守 Circular 230 及各州相关注册要求（如加州 CTEC、俄勒冈 OBTP 等）。本项目不提供、不代表、也不能替代上述任何专业资质。

**无官方关联。** 本项目为独立开源项目，与 IRS、Intuit、TurboTax、H&R Block 及任何 CPA、州注册会计师委员会或政府机构 **均无任何关联、背书或赞助关系**。所有商标归其各自所有者。

---

## 🤝 Contributing · 招募合作者

**This project is looking for collaborators.** 本项目正在招募长期合作者。

Whether you are a CPA, tax attorney, software engineer, designer, student, or just someone who cares about making tax filing fair and free — **I'd love to work with you.** 无论你是注册会计师、税务律师、工程师、设计师、学生，还是单纯认同 "让报税公平、免费、开源" 这件事的人，**欢迎加入，一起把它做下去。**

Ways to contribute:

- 🧩 **Add domain skills** — Schedule C, state returns, AMT, foreign income (Form 2555 / 1116), K-1s
- 📚 **Improve tax rules** — cite the IRC section or IRS publication when you fix a rule
- 🌐 **Translate** — more languages, more accessible
- 🎨 **Design & docs** — make the interview flow friendlier
- 💼 **Long-term collaborators** — email me if you want to co-own a module or domain area

Quick path: after making changes, run `/tax-publish "your description"` to open an anonymized PR automatically.

---

## 📮 Contact · 联系方式

[fangyic@alumni.cmu.edu](mailto:fangyic@alumni.cmu.edu)

Email me for collaboration, bug reports you don't want public, or just to say hi. 欢迎来信交流合作、反馈问题，或者只是打个招呼。

---

## 📄 License · 许可证

Licensed under the **Apache License 2.0** — free for personal and **commercial** use, modification, and distribution.

本项目采用 **Apache License 2.0** 协议，**允许免费商用**、修改、再分发。

> **Attribution required.** Any redistribution, fork, derivative work, or commercial product **must credit this project** — preserve the `LICENSE` and `NOTICE` files, and clearly state that the work is based on *SuperTaxAgent* (https://github.com/Fangyi-Chen/SuperTaxAgent).
>
> **必须署名。** 任何二次分发、fork、衍生作品或商业产品都 **必须注明本项目出处** — 保留 `LICENSE` 与 `NOTICE` 文件，并明确标注作品基于 *SuperTaxAgent*（https://github.com/Fangyi-Chen/SuperTaxAgent）。

See [`LICENSE`](./LICENSE) for the full text.

---

<div align="center">

**⭐ If this project attracts you, please star it — hope we all have a free tax agent in 2027.**
**⭐ 如果这个项目吸引到了你，请点个 Star。希望我们明年报税从从容容游刃有余**

</div>
