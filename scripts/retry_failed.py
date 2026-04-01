"""
retry_failed.py
---------------
Retries only the sections that failed in expand_sections.py.
Opens a fresh NotebookLM connection for every section to avoid
session-expiry errors on long runs.

Run:
    python scripts/retry_failed.py
"""

import asyncio
import os
import re
import time

from notebooklm import NotebookLMClient

NOTEBOOK_ID = "089061de-5c74-411f-9315-af4717aef843"
DELAY_SECONDS = 4

# ── Only the sections that failed ─────────────────────────────────────────────
FAILED_SECTIONS = [
    # ── Only 3 remaining timeouts ──────────────────────────────────────────────
    {
        "module": 2,
        "slug": "islamic-finance-vs-conventional-finance",
        "title": "Islamic Finance vs Conventional Finance",
        "section_id": "2.4",
        "section_title": "Where Islamic Finance Is Strong vs Contested",
        "query": (
            "Expand on strong areas of Islamic finance (resilience in crises, ethical appeal, "
            "ESG alignment, access to Muslim-majority investor pools, competitive differentiation) "
            "and contested areas (standardisation gaps, scholar concentration — few top scholars "
            "dominate multiple boards — interpretive divergence across jurisdictions). "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 3,
        "slug": "core-islamic-contracts-and-structuring-toolkit",
        "title": "Core Islamic Contracts and Structuring Toolkit",
        "section_id": "3.4",
        "section_title": "Ijara and Ijara Muntahia Bittamleek",
        "query": (
            "Expand comprehensively on Ijara and Ijara Muntahia Bittamleek: definitions (lessor "
            "owns asset, leases usufruct for rent; lease-to-own adds compliant title transfer path), "
            "AAOIFI Shariah Standard 9 codification, full transaction flow, use cases (real estate, "
            "aircraft/ship finance, equipment finance, sovereign/corporate sukuk — UK Sovereign "
            "Sukuk 2014 example), key risks (asset maintenance/insurance alignment with Shariah "
            "allocation, risk if asset not really owned or purely notional). Explain why Ijara is "
            "'return via renting use' — structurally closer to leasing than lending. "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 6,
        "slug": "sukuk-and-public-capital-markets",
        "title": "Sukuk and Public Capital Markets",
        "section_id": "6.3",
        "section_title": "Sukuk Structure Menu",
        "query": (
            "Expand on the full sukuk structure menu: Ijara Sukuk (lease/rental cash flows, most "
            "tradable, used in most sovereign sukuk — UK, Saudi, UAE), Wakala Sukuk (agent manages "
            "portfolio, flexible for diversified pools, robust agency agreements needed), "
            "Murabaha/Salam Sukuk (tradability constraints from debt receivable dominance, AAOIFI "
            "SS 59 on sale of debt), Musharaka/Mudaraba Sukuk (equity-based, AAOIFI 2008 substance "
            "requirements, genuine profit/loss sharing), and Hybrid Sukuk (combined contracts, "
            "minimum tangible asset ratio 33-51% for tradability). "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 9,
        "slug": "market-landscape-and-ecosystem",
        "title": "Market Landscape and Ecosystem",
        "section_id": "9.3",
        "section_title": "Key Ecosystem Players",
        "query": (
            "Expand on the full Islamic finance ecosystem player map: Shariah Standards (AAOIFI, "
            "62+ standards), Prudential Standards (IFSB), Market Documentation (IIFM), Liquidity "
            "Instruments (IILM), Global Multilaterals (IsDB, IMF, World Bank), Key Regulators "
            "(BNM, SC Malaysia, CBUAE, SAMA), Islamic Banks (Al Rajhi, Dubai Islamic Bank, KFH), "
            "Fintechs (300+ globally, 74 in Saudi), and Indices (Dow Jones Islamic, FTSE Shariah, "
            "MSCI Islamic covering approximately USD 4.3 trillion). "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.1",
        "section_title": "Form vs Substance (Still Central)",
        "query": (
            "Expand on the form vs substance debate in Islamic finance: academic criticism of "
            "excessive 'Islamisation of conventional products' risking hollowed substance, calls "
            "for refocus on community banking/social investment/meaningful risk-sharing, how this "
            "shapes product acceptability, investor confidence, and regulatory direction. "
            "Cite specific academic works and regulatory discussions from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.2",
        "section_title": "AAOIFI Standard 62 and Standardisation Pressure",
        "query": (
            "Expand on AAOIFI Standard 62: the sukuk standard initiative triggering high-level "
            "debate, concern about cost/liquidity impacts of true legal asset transfer, possibility "
            "of delayed/softened implementation, impact on existing asset-based sukuk structures, "
            "market participant and rating agency warnings about fragmentation. "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.3",
        "section_title": "Digitisation and Tokenisation",
        "query": (
            "Expand on digitisation and tokenisation in Islamic finance: Malaysia SC collaboration "
            "with Khazanah on tokenised bond/sukuk, platforms like Wethaq and ADIB Smart Sukuk "
            "using blockchain for fractional 'micro-sukuk' from USD 10,000, traditional sukuk "
            "issuance costs (USD 500K-1.5M) vs digital platform reductions. Cover the 5-10 year "
            "outlook: tokenisation, retail access, cross-border platforms, smart-contract "
            "automation of profit distribution. Cite all sources from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.4",
        "section_title": "ESG and Sustainable Sukuk Convergence",
        "query": (
            "Expand on ESG/sustainable sukuk convergence: ICMA/IsDB/LSEG guidance mapping "
            "green/social/sustainability sukuk, green sukuk exceeding USD 15 billion in 2024, "
            "climate/sustainability as highest natural convergence point with Islamic finance "
            "(both mandate real-economy linkage, ethical screening, transparency), Malaysia's "
            "SRI sukuk regulatory leadership. Cite all sources from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.5",
        "section_title": "AI-Driven Shariah Compliance",
        "query": (
            "Expand on AI-driven Shariah compliance in Islamic finance: scholars using AI for "
            "real-time transaction monitoring replacing annual Shariah audits, applications "
            "(automated screening, real-time revenue purification, document review), significant "
            "potential for reducing operational risk. Cite all sources from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.6",
        "section_title": "The Authenticity Movement",
        "query": (
            "Expand on the authenticity movement in Islamic finance: growing scholarly and consumer "
            "backlash against 'synthetic' products like Tawarruq, future belonging to 'authentic' "
            "risk-sharing models (Musharaka) and 'utility-based' fintech products solving real "
            "problems for SMEs and the unbanked, strongest in academic circles and next-generation "
            "scholars but influencing product design and marketing. "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 10,
        "slug": "new-developments-innovation-and-debate",
        "title": "New Developments, Innovation, and Debate",
        "section_id": "10.7",
        "section_title": "Private Market Innovation",
        "query": (
            "Expand on private market innovation in Islamic finance: new product formats (Shariah-"
            "compliant private credit strategies, DIFC-based private credit funds with commodity "
            "Murabaha structuring per PwC/DIFC report, digital onboarding and evergreen platforms), "
            "tokenised real assets, Shariah-compliant VC, cross-border co-investment platforms as "
            "the frontier. Cite all sources from the notebook."
        ),
    },
    {
        "module": 11,
        "slug": "product-development-and-opportunity-mapping",
        "title": "Product Development and Opportunity Mapping",
        "section_id": "11.1",
        "section_title": "White Space Map",
        "query": (
            "Expand on the complete white space opportunity map in Islamic finance: (1) Shariah-"
            "compliant private credit (liquidity/ethical demand, GCC family offices, "
            "Wakala/Murabaha hybrids); (2) Family office co-investment platform (direct deal "
            "access, Diminishing Musharaka); (3) SME fintech distribution (unbanked/underbanked, "
            "Murabaha/Musharaka micro); (4) Tokenised infrastructure sukuk (fractional access, "
            "digital Ijara/Wakala); (5) Musharaka REIT (Islamic real estate fund); (6) "
            "Green/sustainable sukuk platform (ESG-Islamic convergence). For each: market gap, "
            "target investors, structure, barriers, attractiveness. "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 11,
        "slug": "product-development-and-opportunity-mapping",
        "title": "Product Development and Opportunity Mapping",
        "section_id": "11.2",
        "section_title": "Decision Matrix for Platform Launch",
        "query": (
            "Expand on the decision matrix for evaluating Islamic finance platform launch "
            "opportunities: (i) market gap size, (ii) target investor base (GCC family offices, "
            "ESG investors, retail), (iii) proposed structure, (iv) execution barriers "
            "(regulatory/Shariah approval, technology), (v) attractiveness (economics + branding), "
            "(vi) jurisdictional complexity. Cite all sources from the notebook."
        ),
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "section_id": "12.1",
        "section_title": "The Five-Question Robustness Test",
        "query": (
            "Expand on the Five-Question Robustness Test for any Islamic finance structure: "
            "(1) Asset Linkage — genuine identifiable asset, prove ownership? "
            "(2) Risk-Sharing — meaningful risk allocation or synthetic guarantee? "
            "(3) Substance Over Form — real economic purpose beyond Shariah form? "
            "(4) Governing Law Enforceability — title, security, trust, insolvency under governing "
            "law, Wa'ad tested in jurisdiction? "
            "(5) Shariah Board Consensus — broad scholarly support or single scholar/niche board? "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "section_id": "12.2",
        "section_title": "Checklist for Structure Robustness",
        "query": (
            "Expand on the complete robustness checklist for Islamic finance structures: ownership "
            "proof, cash-flow mapping (returns tied to permitted activity), red flags for pure debt "
            "mimicry (guaranteed returns, no asset risk, circular trades), scholar shopping "
            "indicators, jurisdictional enforcement assessment, tax neutrality confirmation. "
            "Cite all sources from the notebook."
        ),
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "section_id": "12.3",
        "section_title": "Red Flags",
        "query": (
            "Expand on all red flags for Islamic finance structures: Wa'ad dependency without "
            "genuine asset backing, high scholar concentration reliance, guaranteed returns "
            "language in equity-based structures, circular commodity trades without genuine "
            "third-party market, purely notional asset link, purchase undertakings at nominal "
            "value in Musharaka/Mudaraba sukuk (post-AAOIFI 2008), documentation that cannot "
            "survive judicial scrutiny under governing law. Cite all sources from the notebook."
        ),
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "section_id": "12.4",
        "section_title": "Questions to Ask Key Parties",
        "query": (
            "Expand on questions to ask key parties in an Islamic finance transaction: Shariah "
            "advisors (juristic basis, contested points, would opinion survive different board?), "
            "Lawyers (title/security/trust/insolvency, jurisdiction, Wa'ad enforceability "
            "precedents?), Arrangers (real value creation vs replication, secondary market plan, "
            "competitive pricing?), Sponsors/issuers (why Islamic, target investor base, "
            "reputational risk tolerance?). Cite all sources from the notebook."
        ),
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "section_id": "12.5",
        "section_title": "Evaluating an Islamic PE Opportunity",
        "query": (
            "Expand on evaluating an Islamic private equity opportunity: Mudaraba or Wakala-based "
            "fund? Fee justification? Carry under partnership/agency principles? Hurdle as "
            "'priority in profit distribution' or guaranteed rate? Leverage source and level? "
            "Portfolio company screening criteria? Exit structuring (Musharaka buy-out, IPO, trade "
            "sale)? Cite all sources from the notebook."
        ),
    },
    {
        "module": 12,
        "slug": "executive-toolkit",
        "title": "Executive Toolkit",
        "section_id": "12.6",
        "section_title": "Platform Decision Framework",
        "query": (
            "Expand on the platform decision framework for Islamic finance: evaluate market gap "
            "size vs execution barriers vs ROI (economics + branding), key dimensions "
            "(jurisdictional complexity, Shariah board capacity, investor education requirements, "
            "documentation standardisation availability, regulatory pathway clarity, competitive "
            "landscape). Cite all sources from the notebook."
        ),
    },
]


def build_fallback(section_id: str, section_title: str, query: str) -> str:
    return (
        f"!!! warning \"Content Pending — Retry Failed\"\n"
        f"    Section **{section_id} {section_title}** could not be retrieved from NotebookLM.\n"
        f"    Re-run `python scripts/retry_failed.py` to attempt again.\n"
    )


def inject_section(filepath: str, section_id: str, section_title: str, new_body: str) -> bool:
    """Replace the fallback block for this section in the existing index.md."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Match the section header and everything up to the next ## header or end of file
    header_pattern = re.escape(f"## {section_id} {section_title}")
    next_header = r"(?=\n## |\Z)"
    full_pattern = rf"({header_pattern}\n)(.*?)({next_header})"

    replacement = f"## {section_id} {section_title}\n\n{new_body.strip()}\n\n"
    new_content, count = re.subn(full_pattern, replacement, content, flags=re.DOTALL)

    if count == 0:
        # Section heading not found — append
        new_content = content.rstrip() + f"\n\n## {section_id} {section_title}\n\n{new_body.strip()}\n\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return count > 0


async def retry_section(item: dict) -> bool:
    """Open a fresh connection and retry a single section. Returns True on success."""
    module_num = str(item["module"]).zfill(2)
    filepath = f"docs/module-{module_num}-{item['slug']}/index.md"

    print(f"  [{item['section_id']}] {item['section_title']} ...", end=" ", flush=True)
    try:
        async with await NotebookLMClient.from_storage() as client:
            result = await client.chat.ask(NOTEBOOK_ID, item["query"])
            body = result.answer if hasattr(result, "answer") else str(result)
        inject_section(filepath, item["section_id"], item["section_title"], body)
        print("OK")
        return True
    except Exception as exc:
        print(f"FAILED ({exc})")
        fallback = build_fallback(item["section_id"], item["section_title"], item["query"])
        inject_section(filepath, item["section_id"], item["section_title"], fallback)
        return False


async def main():
    print(f"Retrying {len(FAILED_SECTIONS)} failed sections...\n")
    ok = 0
    failed = 0
    for item in FAILED_SECTIONS:
        success = await retry_section(item)
        if success:
            ok += 1
        else:
            failed += 1
        time.sleep(DELAY_SECONDS)

    print(f"\nDone — {ok} succeeded, {failed} failed.")
    if failed:
        print("Re-run this script to retry remaining failures.")


if __name__ == "__main__":
    asyncio.run(main())
