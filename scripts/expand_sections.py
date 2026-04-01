"""
expand_sections.py
------------------
Queries NotebookLM for each module section and writes the expanded
content into the corresponding docs/module-XX-.../index.md file.

Run from the project root:
    python scripts/expand_sections.py

Requires:
    pip install notebooklm-py
"""

import asyncio
import os
import re
import time

from notebooklm import NotebookLMClient  # pip install notebooklm-py

NOTEBOOK_ID = "089061de-5c74-411f-9315-af4717aef843"
DELAY_SECONDS = 3  # between queries — respect rate limits

# ──────────────────────────────────────────────────────────────────────────────
# MODULE DEFINITIONS
# Each module has a slug (folder suffix), title, and list of sections.
# Each section has an id, title, and the query sent to NotebookLM.
# ──────────────────────────────────────────────────────────────────────────────

MODULES = [
    {
        "module": 1,
        "slug": "foundations-of-islamic-finance",
        "title": "Foundations of Islamic Finance",
        "sections": [
            {
                "id": "1.1",
                "title": "Core Philosophy and Operating Principles",
                "query": (
                    "Expand comprehensively on the core philosophy and operating principles of "
                    "Islamic finance. Cover: Shariah derivation (Quran, Sunnah, scholarly consensus, "
                    "analogy), alignment with ethical/social/economic justice, prohibition of "
                    "exploitation, promotion of risk-sharing, linkage to real productive activity. "
                    "Explain how Islamic finance is NOT merely 'interest-free banking' but a distinct "
                    "philosophy requiring asset ownership/possession, legitimate profit from "
                    "trade/partnership, and avoidance of zero-sum speculation. Explain the "
                    "two-component framework: (i) prohibitions and (ii) positive requirements. "
                    "Cite all sources from the notebook."
                ),
            },
            {
                "id": "1.2",
                "title": "The Three Core Prohibitions",
                "query": (
                    "Expand in full detail on the three core prohibitions in Islamic finance. "
                    "For RIBA: define precisely, explain why conventional interest-bearing loans and "
                    "bonds are excluded, note universal acceptance across all major schools. "
                    "For GHARAR: define ambiguity in subject matter/delivery/price, explain major vs "
                    "minor gharar, why selling what you do not own is prohibited. "
                    "For MAYSIR: define chance-based contracts, distinguish from productive risk-taking. "
                    "Also cover HALAL/HARAM SCREENING: prohibited activities and financial-ratio-level "
                    "screening for listed equities. Cite all sources."
                ),
            },
            {
                "id": "1.3",
                "title": "Positive Structuring Principles",
                "query": (
                    "Expand on the positive structuring principles: (1) Real economy linkage — returns "
                    "tied to trade/lease/investment; (2) Ownership and risk transfer — profit requires "
                    "bearing related risk, rules on possession (qabd), title, AAOIFI Shariah Standard 8; "
                    "(3) Fair dealing and clarity — clear terms, no hidden leverage; (4) Debt vs trade "
                    "vs partnership — pure debt only as Qard Hasan or trade context. Cite all sources."
                ),
            },
            {
                "id": "1.4",
                "title": "Asset Linkage and Commercial Legitimacy",
                "query": (
                    "Expand on asset linkage: 'asset-backing' requires identifiable assets with defined "
                    "rights and risk flows. Cover asset-based vs asset-backed distinction (credit reliance "
                    "vs true sale). Discuss debt-like hybrid instruments such as commodity murabaha and "
                    "IFSB Stability Report observations. Cite all sources."
                ),
            },
            {
                "id": "1.5",
                "title": "Practical Commercial Application",
                "query": (
                    "Expand on practical commercial application for senior executives. Show how a "
                    "conventional loan can be redesigned as Murabaha or Ijara. Explain the four Islamic "
                    "structuring primitives: (1) Sale — trade profit; (2) Lease — rental income; "
                    "(3) Partner — P&L share; (4) Agency — service income. Cite all sources."
                ),
            },
            {
                "id": "1.6",
                "title": "Risks and Limitations",
                "query": (
                    "Expand on risks and limitations: over-reliance on debt-like structures (Tawarruq), "
                    "jurisdictional divergence (Malaysia vs GCC), operational complexity as the cost of "
                    "compliance, and how cosmetic replication fails long-term as substance scrutiny "
                    "intensifies. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 2,
        "slug": "islamic-finance-vs-conventional-finance",
        "title": "Islamic Finance vs Conventional Finance",
        "sections": [
            {
                "id": "2.1",
                "title": "Common Misconceptions",
                "query": (
                    "Expand on the four common misconceptions: (1) 'no debt' — incorrect; "
                    "(2) 'all sukuk are asset-backed' — incorrect; (3) 'just no-interest banking' — "
                    "incorrect; (4) 'always more expensive' — not necessarily. Cite all sources."
                ),
            },
            {
                "id": "2.2",
                "title": "Side-by-Side Comparison",
                "query": (
                    "Provide a comprehensive side-by-side comparison across: pricing of time value, "
                    "core constraints, uncertainty treatment, speculation, documentation focus, risk "
                    "allocation, ethical screening, leverage, and crisis resilience. Cite all sources."
                ),
            },
            {
                "id": "2.3",
                "title": "Economic Substance vs Legal Form",
                "query": (
                    "Expand on the economic substance vs legal form debate: recurring critique of form "
                    "over substance; what is genuinely different vs economically similar; the two-layer "
                    "analysis framework (Layer 1: Shariah form; Layer 2: meaningful substance). "
                    "Cite all sources."
                ),
            },
            {
                "id": "2.4",
                "title": "Where Islamic Finance Is Strong vs Contested",
                "query": (
                    "Expand on strong areas (resilience, ethical appeal, ESG alignment, Muslim investor "
                    "access) and contested areas (standardisation gaps, scholar concentration, "
                    "interpretive divergence). Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 3,
        "slug": "core-islamic-contracts-and-structuring-toolkit",
        "title": "Core Islamic Contracts and Structuring Toolkit",
        "sections": [
            {
                "id": "3.1",
                "title": "Contract Family Map",
                "query": (
                    "Provide the complete contract family map: Sale-based (Murabaha, Tawarruq, Salam, "
                    "Istisna), Lease-based (Ijara, IMB), Equity/PLS (Musharaka, DM, Mudaraba), "
                    "Agency/support (Wakala, Kafala, Qard Hasan), Capital markets (Sukuk, Wa'ad, SPVs). "
                    "Explain when each is used. Cite all sources."
                ),
            },
            {
                "id": "3.2",
                "title": "Murabaha (Cost-Plus Sale)",
                "query": (
                    "Expand comprehensively on Murabaha: definition, full transaction logic, AAOIFI SS 8, "
                    "use cases (trade finance, inventory, commodity murabaha for liquidity), key risks, "
                    "and executive takeaway ('credit via trade'). Cite all sources."
                ),
            },
            {
                "id": "3.3",
                "title": "Tawarruq / Commodity Murabaha",
                "query": (
                    "Expand on Tawarruq/Commodity Murabaha: definition, full transaction flow, market "
                    "practice vs OIC Fiqh Academy debate, GCC vs Malaysia divergence, governance "
                    "sensitivity (genuine third-party trading, clean contract separation, documented "
                    "ownership). Cite all sources."
                ),
            },
            {
                "id": "3.4",
                "title": "Ijara and Ijara Muntahia Bittamleek",
                "query": (
                    "Expand on Ijara and IMB: definitions, AAOIFI SS 9, full transaction flow, use "
                    "cases (real estate, aircraft, equipment, sukuk — UK 2014), key risks (maintenance/"
                    "insurance, notional ownership). Executive takeaway: 'return via renting use'. "
                    "Cite all sources."
                ),
            },
            {
                "id": "3.5",
                "title": "Musharaka and Diminishing Musharaka",
                "query": (
                    "Expand on Musharaka and DM: AAOIFI SS 12, mechanics, DM for home finance (bank "
                    "progressively exits), private markets relevance, challenge of aligning VC economics "
                    "with Shariah partnership rules. Cite all sources."
                ),
            },
            {
                "id": "3.6",
                "title": "Mudaraba (Profit-Sharing Partnership)",
                "query": (
                    "Expand on Mudaraba: AAOIFI SS 13, Rab al-Mal vs Mudarib, LP/GP analogy but no "
                    "capital guarantee, use cases (investment funds, deposit structures, PE/VC). "
                    "Cite all sources."
                ),
            },
            {
                "id": "3.7",
                "title": "Salam and Istisna",
                "query": (
                    "Expand on Salam (AAOIFI SS 10, agricultural/commodity) and Istisna (AAOIFI SS 11, "
                    "construction/manufacturing, parallel Istisna, project finance). Cite all sources."
                ),
            },
            {
                "id": "3.8",
                "title": "Wakala, Kafala, and Qard Hasan",
                "query": (
                    "Expand on Wakala (AAOIFI SS 46, agency backbone), Kafala (AAOIFI SS 5, "
                    "guarantee rules), Qard Hasan (AAOIFI SS 19, benevolent loan). Cite all sources."
                ),
            },
            {
                "id": "3.9",
                "title": "Wa'ad, SPVs, and Modern Structuring Tools",
                "query": (
                    "Expand on modern structuring tools: Wa'ad (unilateral promise, purchase "
                    "undertakings in sukuk, ISDA/IIFM Tahawwut Master Agreement), SPVs and trust "
                    "certificates (beneficial interests, UK Sovereign Sukuk), Arbun. "
                    "Cite all sources."
                ),
            },
            {
                "id": "3.10",
                "title": "Contract Application Matrix",
                "query": (
                    "Provide the complete contract application matrix (Murabaha, Tawarruq, Ijara, "
                    "Musharaka, Mudaraba, Salam, Istisna, Wakala, Sukuk) with core use, risk profile, "
                    "tradability, and criticism level. Explain contract selection. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 4,
        "slug": "shariah-governance-and-institutional-framework",
        "title": "Shariah Governance and Institutional Framework",
        "sections": [
            {
                "id": "4.1",
                "title": "The Multi-Tier Governance Model",
                "query": (
                    "Expand on the three-tier Shariah governance model: Tier 1 National Authority "
                    "(UAE HSA, Malaysia BNM SAC), Tier 2 Institutional Shariah Board (IFSB-10), "
                    "Tier 3 Transaction-Level Review. Cite all sources."
                ),
            },
            {
                "id": "4.2",
                "title": "AAOIFI and IFSB: The Global Standard Setters",
                "query": (
                    "Expand on AAOIFI (62+ standards, SS 62 debate), IFSB (prudential/governance, IFSI "
                    "Stability Report), and IIFM (ISDA/IIFM Tahawwut Master Agreement). "
                    "Cite all sources."
                ),
            },
            {
                "id": "4.3",
                "title": "Jurisdictional Divergence",
                "query": (
                    "Expand on jurisdictional divergence: GCC (conservative, tawarruq restrictions), "
                    "Malaysia (permissive hybrids, codified framework), UK (structuring hub, no "
                    "dedicated Shariah layer). Cite all sources."
                ),
            },
            {
                "id": "4.4",
                "title": "Scholar Concentration and Governance Risks",
                "query": (
                    "Expand on scholar concentration risks, conflicts of interest, insufficient "
                    "independence, lack of standardised qualifications, inconsistent audit practices, "
                    "and 'scholar shopping'. Cite all sources."
                ),
            },
            {
                "id": "4.5",
                "title": "Standardisation vs Innovation",
                "query": (
                    "Expand on standardisation vs innovation tension: AAOIFI Standard 62 debate, "
                    "cost/liquidity impacts, rating agency warnings about fragmentation, permanent "
                    "tension. Cite all sources."
                ),
            },
            {
                "id": "4.6",
                "title": "The Fatwa Process",
                "query": (
                    "Expand on the fatwa process in Islamic finance: definition, typical process "
                    "(product review, conditional approval, ongoing monitoring), and how fatwa "
                    "quality directly affects product defensibility. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 5,
        "slug": "islamic-banking-treasury-and-liquidity",
        "title": "Islamic Banking, Treasury, and Liquidity",
        "sections": [
            {
                "id": "5.1",
                "title": "Balance Sheet Structure",
                "query": (
                    "Expand on Islamic financial institution balance sheet: trading/PLS business models, "
                    "profit-sharing investment accounts (PSIA), contract-specific operational risks. "
                    "Cite all sources."
                ),
            },
            {
                "id": "5.2",
                "title": "Core Application Areas",
                "query": (
                    "Expand on core applications: retail/corporate banking, trade finance, project "
                    "finance, asset management/funds (IFSB-6), and Takaful (Tabarru pool, Wakeel). "
                    "Cite all sources."
                ),
            },
            {
                "id": "5.3",
                "title": "Treasury and Liquidity Management",
                "query": (
                    "Expand on treasury/liquidity as a key differentiator: cannot use conventional "
                    "money-market instruments, structural inefficiencies, instruments (Commodity Murabaha "
                    "placements, short-term Wakala deposits, IILM sukuk, Malaysian repo tools, "
                    "collateralised Murabaha, IIFM master agreements). Cite all sources."
                ),
            },
            {
                "id": "5.4",
                "title": "Family Office Relevance",
                "query": (
                    "Expand on family office relevance: how Islamic structuring affects liquidity tools, "
                    "leverage limits, deal documentation, governance, private market pacing, exit timing, "
                    "and portfolio financing. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 6,
        "slug": "sukuk-and-public-capital-markets",
        "title": "Sukuk and Public Capital Markets",
        "sections": [
            {
                "id": "6.1",
                "title": "Sukuk Definition and Economic Role",
                "query": (
                    "Expand on sukuk definition, AAOIFI SS 17, distinction from bonds, market scale "
                    "(IIFM USD 205 billion 2024 issuances, international USD 65.6 billion record, "
                    "outstanding >USD 900 billion), sovereign sukuk as anchor. Cite all sources."
                ),
            },
            {
                "id": "6.2",
                "title": "Asset-Based vs Asset-Backed: The Critical Distinction",
                "query": (
                    "Expand on the most important structural distinction: asset-based (dominant, credit "
                    "reliance) vs asset-backed (true sale, genuine risk transfer). Cover AAOIFI "
                    "Standard 62 debate and 2008 AAOIFI Sukuk Statement. Cite all sources."
                ),
            },
            {
                "id": "6.3",
                "title": "Sukuk Structure Menu",
                "query": (
                    "Expand on the full sukuk structure menu: Ijara (tradable, sovereign), Wakala "
                    "(flexible pools), Murabaha/Salam (tradability constraints, AAOIFI SS 59), "
                    "Musharaka/Mudaraba (equity-based, genuine P&L), Hybrid (33-51% tangible assets). "
                    "Cite all sources."
                ),
            },
            {
                "id": "6.4",
                "title": "Secondary Market Issues",
                "query": (
                    "Expand on secondary market: AAOIFI SS 59 on sale of debt, tradability requirement "
                    "for tangible assets/usufruct interests, how this shapes portfolio composition and "
                    "limits certain structures. Cite all sources."
                ),
            },
            {
                "id": "6.5",
                "title": "Equity Screening and Listed Products",
                "query": (
                    "Expand on Shariah equity screening: business activity screens, financial ratio "
                    "screens, MSCI Islamic Index, S&P Shariah, Dow Jones Islamic Market. USD 4.3 trillion "
                    "screened universe. Cite all sources."
                ),
            },
            {
                "id": "6.6",
                "title": "Islamic REITs and ETFs",
                "query": (
                    "Expand on Islamic REITs (Malaysia guidance, Shariah-compliant tenants/financing) "
                    "and ETFs (iShares Sukuk UCITS ETF). Cite all sources."
                ),
            },
            {
                "id": "6.7",
                "title": "ESG and Sustainable Sukuk",
                "query": (
                    "Expand on ESG/sustainable sukuk: ICMA/IsDB/LSEG guidance, Malaysia SC SRI sukuk, "
                    "green sukuk exceeding USD 15 billion in 2024, convergence with Islamic principles, "
                    "dual risk of greenwashing and Shariah-washing. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 7,
        "slug": "islamic-finance-in-private-markets",
        "title": "Islamic Finance in Private Markets",
        "sections": [
            {
                "id": "7.1",
                "title": "Why Private Markets Are the Natural Home",
                "query": (
                    "Expand on why private markets suit Islamic finance: direct ownership, real-economy "
                    "linkage, risk-sharing; and friction from conventional norms (liquidation preferences, "
                    "preferred returns, interest-based leverage). Cite all sources."
                ),
            },
            {
                "id": "7.2",
                "title": "Structuring the Fund: GP/LP Dynamics",
                "query": (
                    "Expand on Shariah-compliant fund structuring (Mudaraba or Wakala), GP as Mudarib/"
                    "Wakeel, fee constraints, LPs as Rab al-Mal, IFSB-6 principles. Cite all sources."
                ),
            },
            {
                "id": "7.3",
                "title": "The 'Halal Waterfall' and Carry Mechanics",
                "query": (
                    "Expand on the halal waterfall: conventional 8% hurdle vs 'priority in profit "
                    "distribution', catch-up mechanics, carry under AAOIFI SS 46 as performance "
                    "incentive, 'excuse' provisions for Islamic investors in mixed funds. "
                    "Cite all sources."
                ),
            },
            {
                "id": "7.4",
                "title": "The Leverage Challenge",
                "query": (
                    "Expand on the leverage challenge: conventional 60-70% LBO debt vs Islamic "
                    "alternatives, fund-level leverage (Murabaha/Musharaka), portfolio company level "
                    "(debt <33% total assets), practical responses (growth equity, commodity Murabaha "
                    "facilities). Cite all sources."
                ),
            },
            {
                "id": "7.5",
                "title": "Private Credit and Acquisition Finance",
                "query": (
                    "Expand on Islamic private credit as a 'huge white space': Murabaha/Ijara/Wakala "
                    "alternatives, commodity Murabaha/Tawarruq for drawdown facilities (PwC/DIFC 2025), "
                    "governance defensibility warning. Cite all sources."
                ),
            },
            {
                "id": "7.6",
                "title": "Infrastructure and Real Estate",
                "query": (
                    "Expand on infrastructure/real estate compatibility: Ijara and DM for ownership/"
                    "rental, Istisna for construction, Islamic REITs, private credit funds using "
                    "Murabaha delivering 8-12% returns. Cite all sources."
                ),
            },
            {
                "id": "7.7",
                "title": "Restructurings and Special Situations",
                "query": (
                    "Expand on restructurings: AAOIFI SS 3 (default/late payment), AAOIFI SS 59 "
                    "(sale of debt constraints on distressed strategies), different enforcement paths "
                    "for Murabaha vs Ijara vs conventional loans. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 8,
        "slug": "case-study-compendium",
        "title": "Case Study Compendium",
        "sections": [
            {
                "id": "8.1",
                "title": "UK Sovereign Sukuk (Ijara, 2014)",
                "query": (
                    "Expand on UK Sovereign Sukuk: GBP 200 million, first Western sovereign sukuk, "
                    "Ijara structure, HM Treasury/SPV/HSBC/Standard Chartered, government property "
                    "assets, tax neutrality legislation, lessons. Cite all sources."
                ),
            },
            {
                "id": "8.2",
                "title": "UAE Treasury Sukuk Programme",
                "query": (
                    "Expand on UAE Treasury Sukuk Programme: Ministry of Finance/Central Bank HSA, "
                    "multi-contract structure, programme format for repeat issuance, lessons on "
                    "centralised governance. Cite all sources."
                ),
            },
            {
                "id": "8.3",
                "title": "Saudi PIF International Sukuk Programme",
                "query": (
                    "Expand on Saudi PIF International Sukuk Programme: multi-currency, LSE ISM "
                    "listing, programme flexibility, lesson on efficiency for sovereign-backed issuers. "
                    "Cite all sources."
                ),
            },
            {
                "id": "8.4",
                "title": "ADNOC Murban Debut Sukuk (2025)",
                "query": (
                    "Expand on ADNOC Murban Sukuk: USD 1.5 billion 10-year, Standard Chartered sole "
                    "global coordinator, Islamic investor demand alongside conventional, lessons on "
                    "corporate sukuk as bond complement. Cite all sources."
                ),
            },
            {
                "id": "8.5",
                "title": "Tadau Energy Green Sukuk (Malaysia, 2017)",
                "query": (
                    "Expand on Tadau Energy Green Sukuk: world's first Green Sukuk, USD 59 million "
                    "50MW solar, Wakala + commodity Murabaha, oversubscribed, spurred Quantum Solar "
                    "follow-on, Malaysia SRI framework lesson. Cite all sources."
                ),
            },
            {
                "id": "8.6",
                "title": "Republic of Indonesia Sovereign Green Sukuk (2018)",
                "query": (
                    "Expand on Indonesia Sovereign Green Sukuk: World Bank partnership, USD 1.25 "
                    "billion Wakala, rail and renewable energy, 29% new investors, green/Islamic "
                    "convergence lesson. Cite all sources."
                ),
            },
            {
                "id": "8.7",
                "title": "Majid Al Futtaim Corporate Green Sukuk (UAE, 2019)",
                "query": (
                    "Expand on MAF Corporate Green Sukuk: first benchmark corporate green sukuk "
                    "Middle East, USD 600 million Wakala, green buildings Dubai and Egypt. "
                    "Cite all sources."
                ),
            },
            {
                "id": "8.8",
                "title": "Malaysia SRI Sukuk Ecosystem",
                "query": (
                    "Expand on Malaysia SRI Sukuk ecosystem: SC leadership, Cagamas first ASEAN "
                    "Social SRI Sukuk, KPI/reporting credibility risks, regulatory clarity lesson. "
                    "Cite all sources."
                ),
            },
            {
                "id": "8.9",
                "title": "Emirates Islamic EmFIN Platform",
                "query": (
                    "Expand on Emirates Islamic EmFIN Platform: Shariah-compliant private financing "
                    "platform, Wakala charges, digital onboarding, evergreen features, governance "
                    "risks. Cite all sources."
                ),
            },
            {
                "id": "8.10",
                "title": "Dana Gas Sukuk Restructuring (2017-2018)",
                "query": (
                    "Expand comprehensively on Dana Gas Sukuk Restructuring: USD 700 million Mudaraba "
                    "sukuk, issuer declared sukuk unlawful, BlackRock dispute, English/UAE law, "
                    "purchase undertaking enforceability, settlement via new structure, lessons on "
                    "form-versus-substance and Shariah validity as credit risk. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 9,
        "slug": "market-landscape-and-ecosystem",
        "title": "Market Landscape and Ecosystem",
        "sections": [
            {
                "id": "9.1",
                "title": "Global Market Size",
                "query": (
                    "Expand on global Islamic finance market size: IFSB (USD 3.88 trillion, 14.9% YoY), "
                    "LSEG/ICD (USD 5.98 trillion, 21% YoY), sukuk outstanding (>USD 900bn–1tn), "
                    "2024 issuance (USD 205bn IIFM, international USD 65.6bn record), projection to "
                    "USD 9.7 trillion by 2029. Cite all sources."
                ),
            },
            {
                "id": "9.2",
                "title": "The Three Major Hubs",
                "query": (
                    "Expand on the three hubs: Malaysia 'The Laboratory' (regulatory innovation, IFSB "
                    "host, SRI pioneer, SC/BNM), Saudi Arabia 'The Powerhouse' (PIF, Vision 2030, SAMA), "
                    "UAE 'The Bridge' (DIFC/ADGM, HSA, digital assets). Also: UK, Indonesia, Pakistan, "
                    "Bahrain. Cite all sources."
                ),
            },
            {
                "id": "9.3",
                "title": "Key Ecosystem Players",
                "query": (
                    "Expand on the full ecosystem: AAOIFI, IFSB, IIFM, IILM, IsDB, IMF, World Bank, "
                    "BNM, SC Malaysia, CBUAE, SAMA, Al Rajhi, Dubai Islamic Bank, KFH, 300+ fintechs, "
                    "Dow Jones Islamic, FTSE Shariah, MSCI Islamic (~USD 4.3tn). Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "sections": [
            {
                "id": "10.1",
                "title": "Form vs Substance (Still Central)",
                "query": (
                    "Expand on form vs substance debate: academic criticism of excessive 'Islamisation "
                    "of conventional products', calls for community banking/social investment, impact on "
                    "product acceptability and regulatory direction. Cite specific academic works. "
                    "Cite all sources."
                ),
            },
            {
                "id": "10.2",
                "title": "AAOIFI Standard 62 and Standardisation Pressure",
                "query": (
                    "Expand on AAOIFI Standard 62 debate: cost/liquidity impacts, delayed implementation "
                    "risk, impact on existing asset-based sukuk, rating agency fragmentation warnings. "
                    "Cite all sources."
                ),
            },
            {
                "id": "10.3",
                "title": "Digitisation and Tokenisation",
                "query": (
                    "Expand on tokenisation in Islamic finance: Malaysia SC/Khazanah tokenised sukuk, "
                    "Wethaq and ADIB Smart Sukuk platforms, fractional 'micro-sukuk' from USD 10,000, "
                    "traditional vs digital issuance costs (USD 500K-1.5M), 5-10 year outlook. "
                    "Cite all sources."
                ),
            },
            {
                "id": "10.4",
                "title": "ESG and Sustainable Sukuk Convergence",
                "query": (
                    "Expand on ESG/sustainable sukuk convergence: ICMA/IsDB/LSEG guidance, green sukuk "
                    ">USD 15bn in 2024, climate as highest natural convergence point, Malaysia SRI "
                    "leadership. Cite all sources."
                ),
            },
            {
                "id": "10.5",
                "title": "AI-Driven Shariah Compliance",
                "query": (
                    "Expand on AI-driven Shariah compliance: real-time transaction monitoring replacing "
                    "annual audits, automated screening, revenue purification, document review, "
                    "operational risk reduction. Cite all sources."
                ),
            },
            {
                "id": "10.6",
                "title": "The Authenticity Movement",
                "query": (
                    "Expand on the authenticity movement: backlash against synthetic Tawarruq, future "
                    "of 'authentic' Musharaka and utility-based fintech, strongest in academic circles "
                    "and next-generation scholars. Cite all sources."
                ),
            },
            {
                "id": "10.7",
                "title": "Private Market Innovation",
                "query": (
                    "Expand on private market innovation: Shariah-compliant private credit strategies, "
                    "DIFC-based funds (PwC/DIFC 2025), tokenised real assets, Shariah-compliant VC, "
                    "cross-border co-investment platforms. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 11,
        "slug": "product-development-and-opportunity-mapping",
        "title": "Product Development and Opportunity Mapping",
        "sections": [
            {
                "id": "11.1",
                "title": "White Space Map",
                "query": (
                    "Expand on white space opportunities: (1) Shariah-compliant private credit; "
                    "(2) Family office co-investment; (3) SME fintech distribution; (4) Tokenised "
                    "infrastructure sukuk; (5) Musharaka REIT; (6) Green/sustainable sukuk platform. "
                    "For each: market gap, target investors, structure, barriers, attractiveness. "
                    "Cite all sources."
                ),
            },
            {
                "id": "11.2",
                "title": "Decision Matrix for Platform Launch",
                "query": (
                    "Expand on the decision matrix: market gap size, target investor base, proposed "
                    "structure, execution barriers (regulatory/Shariah/technology), attractiveness "
                    "(economics + branding), jurisdictional complexity. Cite all sources."
                ),
            },
        ],
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "sections": [
            {
                "id": "12.1",
                "title": "The Five-Question Robustness Test",
                "query": (
                    "Expand on the Five-Question Robustness Test: (1) Asset Linkage; (2) Risk-Sharing; "
                    "(3) Substance Over Form; (4) Governing Law Enforceability; (5) Shariah Board "
                    "Consensus. Cite all sources."
                ),
            },
            {
                "id": "12.2",
                "title": "Checklist for Structure Robustness",
                "query": (
                    "Expand on the robustness checklist: ownership proof, cash-flow mapping, red flags "
                    "for debt mimicry (guaranteed returns, no asset risk, circular trades), scholar "
                    "shopping indicators, jurisdictional enforcement, tax neutrality. Cite all sources."
                ),
            },
            {
                "id": "12.3",
                "title": "Red Flags",
                "query": (
                    "Expand on all red flags: Wa'ad dependency without genuine asset backing, scholar "
                    "concentration reliance, guaranteed returns in equity structures, circular commodity "
                    "trades, purely notional asset link, purchase undertakings at nominal value in "
                    "Musharaka/Mudaraba sukuk (post-AAOIFI 2008). Cite all sources."
                ),
            },
            {
                "id": "12.4",
                "title": "Questions to Ask Key Parties",
                "query": (
                    "Expand on questions to ask: Shariah advisors (juristic basis, contested points?), "
                    "Lawyers (title/security/trust/insolvency, Wa'ad enforceability?), Arrangers "
                    "(real value vs replication, secondary market plan?), Sponsors/Issuers (why "
                    "Islamic, target investor base?). Cite all sources."
                ),
            },
            {
                "id": "12.5",
                "title": "Evaluating an Islamic PE Opportunity",
                "query": (
                    "Expand on evaluating Islamic PE: Mudaraba or Wakala fund? Fee justification? Carry "
                    "under partnership/agency? Hurdle as priority distribution vs guaranteed rate? "
                    "Leverage source? Portfolio screening? Exit structuring. Cite all sources."
                ),
            },
            {
                "id": "12.6",
                "title": "Platform Decision Framework",
                "query": (
                    "Expand on the platform decision framework: market gap vs execution barriers vs ROI, "
                    "jurisdictional complexity, Shariah board capacity, investor education, "
                    "documentation standardisation, regulatory pathway, competitive landscape. "
                    "Cite all sources."
                ),
            },
        ],
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# TEMPLATE HELPERS
# ──────────────────────────────────────────────────────────────────────────────

EXECUTIVE_REFRESHER_TEMPLATE = """
---

<div class="executive-refresher">
<h3>Executive Refresher</h3>

{bullet_points}
</div>
"""

QUIZ_TEMPLATE = """
<div class="quiz-section">
<h3>Knowledge Check Quiz</h3>

{questions}
</div>
"""


def build_module_header(module: dict) -> str:
    """Return the YAML front-matter and H1 heading for a module index."""
    return (
        f"---\n"
        f"title: \"Module {module['module']}: {module['title']}\"\n"
        f"description: \"Executive course module on {module['title']}\"\n"
        f"---\n\n"
        f"# Module {module['module']}: {module['title']}\n\n"
    )


def slugify_section(title: str) -> str:
    """Convert a section title to a URL-safe anchor."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def build_section_header(section: dict) -> str:
    return f"\n## {section['id']} {section['title']}\n\n"


def build_fallback_content(section: dict) -> str:
    """Return placeholder content if NotebookLM query fails."""
    return (
        f"!!! warning \"Content Pending\"\n"
        f"    This section will be populated by the NotebookLM expansion script.\n"
        f"    Query: *{section['query'][:120]}...*\n"
    )


def extract_refresher_bullets(content: str) -> str:
    """Heuristically pull 3–5 key sentences for the Executive Refresher."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", content) if len(s.strip()) > 40]
    bullets = sentences[:5] if sentences else ["Key takeaways from this section will appear here."]
    return "\n".join(f"- {b}" for b in bullets)


def build_quiz_for_section(section_id: str, title: str, content: str) -> str:
    """Generate 3 basic quiz questions from section content."""
    # We scaffold 3 questions; the generate_quizzes.py script will enrich these.
    q = [
        f"1. What is the primary Shariah principle underpinning **{title}**?\n\n"
        f"    <details class='quiz-answer'><summary>Show answer</summary>\n"
        f"    See the section body above for a full explanation.\n"
        f"    </details>\n",
        f"2. Describe the key regulatory or governance consideration relevant to **{title}**.\n\n"
        f"    <details class='quiz-answer'><summary>Show answer</summary>\n"
        f"    Refer to AAOIFI/IFSB standards cited in the section.\n"
        f"    </details>\n",
        f"3. What is the main practical challenge an executive faces when applying **{title}** in a transaction?\n\n"
        f"    <details class='quiz-answer'><summary>Show answer</summary>\n"
        f"    See risk analysis in the section body.\n"
        f"    </details>\n",
    ]
    return QUIZ_TEMPLATE.format(questions="\n".join(q))


# ──────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────────────────────────────────────

async def expand_module(client, module: dict) -> None:
    module_num = str(module["module"]).zfill(2)
    slug = module["slug"]
    module_dir = f"docs/module-{module_num}-{slug}"
    os.makedirs(module_dir, exist_ok=True)
    output_path = os.path.join(module_dir, "index.md")

    print(f"\n{'='*60}")
    print(f"MODULE {module['module']}: {module['title']}")
    print(f"{'='*60}")

    content = build_module_header(module)

    for section in module["sections"]:
        print(f"  [{section['id']}] {section['title']} ...", end=" ", flush=True)

        section_body = ""
        try:
            result = await client.chat.ask(NOTEBOOK_ID, section["query"])
            section_body = result.answer if hasattr(result, "answer") else str(result)
            print("OK")
        except Exception as exc:
            print(f"FAILED ({exc})")
            section_body = build_fallback_content(section)

        content += build_section_header(section)
        content += section_body.strip() + "\n\n"

        # Add Executive Refresher after last section only (per-section version available via flag)
        time.sleep(DELAY_SECONDS)

    # Append module-level Executive Refresher
    content += "\n---\n\n"
    content += EXECUTIVE_REFRESHER_TEMPLATE.format(
        bullet_points=(
            "- Review the key contract types covered in this module before any deal review.\n"
            "- Always apply the five-question robustness test (Module 12) to structures encountered here.\n"
            "- Note any jurisdictional divergences flagged — they create cross-border execution risk.\n"
            "- The substance vs form distinction is critical: Shariah form without economic substance "
            "invites both reputational and legal risk.\n"
            "- Keep AAOIFI/IFSB standard references handy for due diligence conversations."
        )
    )

    # Append Knowledge Check Quiz (one question per section, capped at 5)
    quiz_questions = []
    for i, section in enumerate(module["sections"][:5], 1):
        quiz_questions.append(
            f"{i}. Explain the significance of **{section['title']}** for an Islamic finance practitioner.\n\n"
            f"    <details class='quiz-answer'><summary>Show answer</summary>\n"
            f"    See Section {section['id']} for the full treatment.\n"
            f"    </details>\n"
        )
    content += QUIZ_TEMPLATE.format(questions="\n".join(quiz_questions))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  -> Written: {output_path}")


async def main():
    print("Connecting to NotebookLM...")
    async with await NotebookLMClient.from_storage() as client:
        print("Connected.\n")
        for module in MODULES:
            await expand_module(client, module)
    print("\nAll modules expanded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
