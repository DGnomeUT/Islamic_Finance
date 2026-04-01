"""
build_reading_list.py
---------------------
Generates docs/essential-reading-list.md from the curated reading
list data defined below.

Run:
    python scripts/build_reading_list.py
"""

import os

OUTPUT_PATH = "docs/essential-reading-list.md"

# ──────────────────────────────────────────────────────────────────────────────
# READING LIST DATA
# ──────────────────────────────────────────────────────────────────────────────

READING_LIST = [
    {
        "category": "Foundational Texts",
        "items": [
            {
                "title": "An Introduction to Islamic Finance: Theory and Practice",
                "author": "Zamir Iqbal & Abbas Mirakhor",
                "publisher": "Wiley Finance (3rd ed.)",
                "relevance": "Definitive academic foundation — Shariah principles, contract theory, banking and capital markets overview.",
                "level": "Core",
            },
            {
                "title": "Islamic Finance: Law, Economics, and Practice",
                "author": "Mahmoud A. El-Gamal",
                "publisher": "Cambridge University Press",
                "relevance": "Critical economic analysis of form vs substance — essential for understanding the mainstream academic critique.",
                "level": "Core",
            },
            {
                "title": "Principles of Islamic Finance",
                "author": "Muhammad Taqi Usmani",
                "publisher": "IDARATUL MA'ARIF",
                "relevance": "Authoritative scholarly perspective from one of the world's most prominent Shariah scholars.",
                "level": "Core",
            },
        ],
    },
    {
        "category": "Standards and Regulatory Frameworks",
        "items": [
            {
                "title": "AAOIFI Shariah Standards (complete set, 62+ standards)",
                "author": "Accounting and Auditing Organisation for Islamic Financial Institutions",
                "publisher": "AAOIFI",
                "relevance": "Primary reference for all contract structures — SS 8 (Murabaha), SS 9 (Ijara), SS 12 (Musharaka), SS 13 (Mudaraba), SS 17 (Sukuk), SS 59 (sale of debt), SS 62 (sukuk). Mandatory practitioner reference.",
                "level": "Practitioner Reference",
            },
            {
                "title": "IFSB Guiding Principles on Shariah Governance Systems (IFSB-10)",
                "author": "Islamic Financial Services Board",
                "publisher": "IFSB",
                "relevance": "Defines institutional Shariah governance framework — board composition, independence, competence, and reporting.",
                "level": "Practitioner Reference",
            },
            {
                "title": "IFSB Guiding Principles on Governance for Islamic Collective Investment Schemes (IFSB-6)",
                "author": "Islamic Financial Services Board",
                "publisher": "IFSB",
                "relevance": "Essential for fund structuring — governance of Mudaraba/Wakala-based collective investment vehicles.",
                "level": "Practitioner Reference",
            },
            {
                "title": "IFSB Islamic Financial Services Industry Stability Report (Annual)",
                "author": "Islamic Financial Services Board",
                "publisher": "IFSB (annual publication)",
                "relevance": "Best authoritative source for global market size data, structural trends, and systemic risk analysis.",
                "level": "Annual Reference",
            },
            {
                "title": "IIFM Sukuk Report and ISDA/IIFM Tahawwut Master Agreement",
                "author": "International Islamic Financial Market",
                "publisher": "IIFM",
                "relevance": "Primary documentation framework for sukuk and Islamic hedging. Critical for treasury and capital markets practitioners.",
                "level": "Practitioner Reference",
            },
        ],
    },
    {
        "category": "Sukuk and Capital Markets",
        "items": [
            {
                "title": "Sukuk Markets: A Practitioner's Guide",
                "author": "Andreas A. Jobst & Juan Sole",
                "publisher": "IMF Working Paper",
                "relevance": "Best concise practitioner-level treatment of sukuk structuring, asset-based vs asset-backed distinction, and regulatory implications.",
                "level": "Core",
            },
            {
                "title": "UK Government Sukuk Prospectus (2014)",
                "author": "HM Treasury / UK Debt Management Office",
                "publisher": "UK DMO",
                "relevance": "Primary document for the landmark first Western sovereign sukuk. Essential case study reference.",
                "level": "Case Study",
            },
            {
                "title": "IIFM Global Sukuk Market Report (Annual)",
                "author": "International Islamic Financial Market",
                "publisher": "IIFM",
                "relevance": "Authoritative annual data on global sukuk issuance volumes, structures, and market trends.",
                "level": "Annual Reference",
            },
            {
                "title": "Green Sukuk Guidance: A Framework for Sustainable Islamic Finance",
                "author": "ICMA / IsDB / LSEG",
                "publisher": "ICMA",
                "relevance": "Key framework for understanding green and sustainable sukuk convergence with ESG principles.",
                "level": "Practitioner Reference",
            },
        ],
    },
    {
        "category": "Private Markets and Structured Finance",
        "items": [
            {
                "title": "Islamic Finance in Private Equity and Venture Capital",
                "author": "Various / DIFC / ADGM Publications",
                "publisher": "DIFC",
                "relevance": "Practical treatment of fund structuring, halal waterfall mechanics, and leverage alternatives in Islamic PE.",
                "level": "Core",
            },
            {
                "title": "Islamic Private Credit: Emerging Strategies and Structures (PwC/DIFC, 2025)",
                "author": "PwC / Dubai International Financial Centre",
                "publisher": "PwC / DIFC",
                "relevance": "Most current practitioner analysis of commodity Murabaha-based drawdown facilities, digital onboarding, and evergreen credit strategies.",
                "level": "Core",
            },
            {
                "title": "AAOIFI Shariah Standard 3: Default in Payment",
                "author": "AAOIFI",
                "publisher": "AAOIFI",
                "relevance": "Critical reference for restructurings — defines penalty clause treatment and charity requirements for late payment.",
                "level": "Practitioner Reference",
            },
            {
                "title": "AAOIFI Shariah Standard 59: Sale of Debt",
                "author": "AAOIFI",
                "publisher": "AAOIFI",
                "relevance": "Governs constraints on distressed debt strategies and sukuk secondary market trading of receivable-heavy portfolios.",
                "level": "Practitioner Reference",
            },
        ],
    },
    {
        "category": "Innovation, Digitalisation, and ESG",
        "items": [
            {
                "title": "Tokenisation of Islamic Financial Instruments",
                "author": "Securities Commission Malaysia / Khazanah",
                "publisher": "SC Malaysia",
                "relevance": "Foundational regulatory framework for digital sukuk and tokenised Islamic instruments in Malaysia — the most advanced jurisdiction.",
                "level": "Forward-Looking",
            },
            {
                "title": "LSEG / ICD Islamic Finance Development Report (Annual)",
                "author": "London Stock Exchange Group / ICD",
                "publisher": "LSEG / ICD",
                "relevance": "Comprehensive annual market intelligence: USD 5.98 trillion market estimate, growth projections to USD 9.7 trillion by 2029.",
                "level": "Annual Reference",
            },
            {
                "title": "Malaysia SC Sustainable and Responsible Investment (SRI) Sukuk Framework",
                "author": "Securities Commission Malaysia",
                "publisher": "SC Malaysia",
                "relevance": "Regulatory framework enabling green, social, and sustainability-linked sukuk — template widely adopted regionally.",
                "level": "Practitioner Reference",
            },
        ],
    },
    {
        "category": "Governance and Critical Analysis",
        "items": [
            {
                "title": "Islamic Finance and the New Financial System",
                "author": "Tariq Al-Rifai",
                "publisher": "Wiley",
                "relevance": "Accessible executive-level overview of how Islamic finance intersects with global financial system architecture and ESG.",
                "level": "Supplementary",
            },
            {
                "title": "A Critique of Islamic Economics: The Case for Reform",
                "author": "Timur Kuran",
                "publisher": "Princeton University Press",
                "relevance": "Rigorous critical examination of the form vs substance debate and the political economy of Islamic finance. Essential for balanced perspective.",
                "level": "Critical Perspective",
            },
            {
                "title": "Dana Gas Sukuk Restructuring: Legal Analysis and Lessons",
                "author": "Various (law firm client alerts: Allen & Overy, Clifford Chance, Linklaters)",
                "publisher": "Various law firm publications (2017-2018)",
                "relevance": "Best practitioner analysis of the Dana Gas dispute — purchase undertaking enforceability, form vs substance risks, jurisdictional complexity.",
                "level": "Case Study",
            },
        ],
    },
    {
        "category": "Indices and Market Data",
        "items": [
            {
                "title": "MSCI Islamic Index Methodology",
                "author": "MSCI",
                "publisher": "MSCI",
                "relevance": "Definitive methodology for Shariah equity screening — business activity and financial ratio screens, buffer rules.",
                "level": "Practitioner Reference",
            },
            {
                "title": "S&P Global Shariah Indices Methodology",
                "author": "S&P Dow Jones Indices",
                "publisher": "S&P",
                "relevance": "Alternative major screening methodology — useful for comparing index construction and screened universe characteristics.",
                "level": "Practitioner Reference",
            },
        ],
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# BUILDER
# ──────────────────────────────────────────────────────────────────────────────

LEVEL_BADGE = {
    "Core": "**Core**",
    "Practitioner Reference": "*Practitioner Reference*",
    "Annual Reference": "*Annual Reference*",
    "Case Study": "*Case Study*",
    "Forward-Looking": "*Forward-Looking*",
    "Critical Perspective": "*Critical Perspective*",
    "Supplementary": "*Supplementary*",
}


def build_reading_list_md() -> str:
    lines = [
        "---",
        'title: "Essential Reading List"',
        'description: "Curated reading list for Islamic Finance & Structuring — executive course references."',
        "---",
        "",
        "# Essential Reading List",
        "",
        "This curated list covers the primary texts, regulatory standards, market reports, and critical "
        "analyses referenced throughout the course. Items are organised by category and annotated with "
        "their relevance and recommended depth of engagement.",
        "",
        "!!! tip \"How to use this list\"",
        "    - **Core** items are essential for all participants.",
        "    - **Practitioner Reference** items should be on your desk — you will return to them repeatedly.",
        "    - **Annual Reference** items should be read each year to stay current.",
        "    - **Case Study** items support Module 8 directly.",
        "    - **Critical Perspective** items challenge mainstream narratives — essential for balanced judgement.",
        "",
    ]

    for category in READING_LIST:
        lines.append(f"## {category['category']}")
        lines.append("")
        lines.append("| Title | Author / Publisher | Relevance | Level |")
        lines.append("|---|---|---|---|")
        for item in category["items"]:
            badge = LEVEL_BADGE.get(item["level"], item["level"])
            title = item["title"].replace("|", "\\|")
            author = f"{item['author']} / {item['publisher']}".replace("|", "\\|")
            relevance = item["relevance"].replace("|", "\\|")
            lines.append(f"| {title} | {author} | {relevance} | {badge} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## How to Access These Resources",
        "",
        "| Resource Type | Access Route |",
        "|---|---|",
        "| AAOIFI Standards | Available via AAOIFI website (subscription) or through member institutions |",
        "| IFSB Publications | Freely downloadable from ifsb.org |",
        "| IIFM Reports | Freely available from iifm.net |",
        "| IMF Working Papers | Freely available from imf.org |",
        "| Law firm client alerts | Via firm websites or through Bloomberg Law/Practical Law |",
        "| SC Malaysia / BNM | Freely available from sc.com.my and bnm.gov.my |",
        "",
        "!!! note",
        "    AAOIFI Shariah Standards are the single most important practitioner reference in this field. "
        "    If you have access to only one resource, make it the complete AAOIFI Standards volume.",
    ]

    return "\n".join(lines)


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    content = build_reading_list_md()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Reading list written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
