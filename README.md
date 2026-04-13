<div align="center">

# 🧾 Super CPA · US Tax

**AI-powered US federal tax filing, right inside Claude Code.**
**在 Claude Code 里用 AI 报美国联邦税 — 免费、本地、开源。**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-8A4FFF.svg)](https://claude.com/claude-code)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing--招募合作者)

*Import your W2. Ask Claude to do your taxes. Get a mail-ready 1040 PDF. No uploads, no subscriptions, no $400 CPA bill.*

</div>

---

## 🌍 Why this project · 为什么做这个项目

> **"征税没有征到最应该被征税的人身上，而是征到最容易被征税的人身上。"**
>
> Taxes don't fall on those who *should* pay them most — they fall on those who are *easiest* to tax: wage earners, immigrants, working families. Meanwhile, tax software costs $100–$300 a year and a CPA costs $400+ per return, even for a simple W2 filing.

This project is built on a simple belief: **AI should serve the many, not the few.** With a capable model and a well-designed agent, you shouldn't need TurboTax or a CPA to file a straightforward return. Your data should stay on your laptop. The rules should be open. And if the agent gets something wrong, the whole community should be able to fix it — permanently, for everyone.

这个项目的初衷，是基于 **"AI 造福最广大人民"** 的思想：让普通工薪家庭、留学生、新移民、小业主，都能免费、私密、体面地完成自己的报税，不必再依赖昂贵的报税软件和会计师。你的数据留在自己电脑上，规则全部开源，社区一起让它越来越准。

---

## 📦 Installation · 安装

Install from the Claude Code plugin marketplace:

```
/plugin marketplace add Fangyi-Chen/tax-marketplace
/plugin install super-cpa-us-tax@tax-marketplace
```

Or install directly from GitHub:

```
/plugin install https://github.com/Fangyi-Chen/super-cpa-us-tax.git
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

> **Attribution required.** Any redistribution, fork, derivative work, or commercial product **must credit this project** — preserve the `LICENSE` and `NOTICE` files, and clearly state that the work is based on *Super CPA · US Tax* (https://github.com/Fangyi-Chen/super-cpa-us-tax).
>
> **必须署名。** 任何二次分发、fork、衍生作品或商业产品都 **必须注明本项目出处** — 保留 `LICENSE` 与 `NOTICE` 文件，并明确标注作品基于 *Super CPA · US Tax*（https://github.com/Fangyi-Chen/super-cpa-us-tax）。

See [`LICENSE`](./LICENSE) for the full text.

---

<div align="center">

**⭐ If this project attracts you, please star it — hope we all have a free tax agent in 2027.**
**⭐ 如果这个项目吸引到了你，请点个 Star。希望我们明年报税从从容容游刃有余**

</div>
