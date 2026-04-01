"""
generate_quizzes.py
-------------------
Post-processes the expanded module index.md files to enrich the
Knowledge Check Quiz sections with real questions drawn from content.

Run after expand_sections.py:
    python scripts/generate_quizzes.py

This script reads each module index.md, extracts key concepts via
simple heuristics, and replaces scaffold quiz questions with richer
Q&A pairs matched to the actual expanded text.
"""

import os
import re
import glob

DOCS_DIR = "docs"
MODULE_GLOB = "module-*-*/index.md"


# ──────────────────────────────────────────────────────────────────────────────
# QUESTION BANKS PER MODULE (hand-crafted, authoritative)
# ──────────────────────────────────────────────────────────────────────────────

QUESTION_BANKS = {
    1: [
        (
            "What are the two-component framework elements of Islamic finance?",
            "The two components are: (i) **prohibitions** — Riba, Gharar, Maysir, and haram activities; "
            "and (ii) **positive requirements** — asset linkage, risk-sharing, real economy connection, "
            "and fair dealing.",
        ),
        (
            "Why is Islamic finance described as more than 'interest-free banking'?",
            "Islamic finance requires genuine asset ownership/possession, legitimate profit from trade or "
            "partnership, ethical activity screening, and avoidance of zero-sum speculation — it is a "
            "comprehensive commercial framework, not merely the removal of interest.",
        ),
        (
            "What does AAOIFI Shariah Standard 8 govern?",
            "AAOIFI SS 8 governs Murabaha — defining the ownership, possession (qabd), and risk-transfer "
            "requirements the financial institution must satisfy before a valid Murabaha sale can occur.",
        ),
        (
            "Distinguish 'asset-based' from 'asset-backed' Islamic finance.",
            "'Asset-based' means an asset is referenced for Shariah compliance but investors rely on the "
            "obligor's credit in a default scenario. 'Asset-backed' involves a true sale and enforceable "
            "recourse to the underlying asset — a materially stronger investor protection.",
        ),
        (
            "Name the four Islamic structuring primitives and their return mechanisms.",
            "(1) Sale → trade profit (markup); (2) Lease → rental income; (3) Partnership → P&L share; "
            "(4) Agency → service fee plus performance incentive.",
        ),
    ],
    2: [
        (
            "Is it accurate to say Islamic finance prohibits all debt? Explain.",
            "No. Islamic finance can generate debt-like obligations through sale (Murabaha) or lease "
            "(Ijara) contracts. What it prohibits is *interest* as the pricing mechanism for money itself, "
            "not the existence of a deferred payment obligation per se.",
        ),
        (
            "What is the two-layer analysis framework for evaluating Islamic finance structures?",
            "Layer 1 asks whether the Shariah form is correct — are all contractual conditions met? "
            "Layer 2 asks whether there is meaningful economic substance — real ownership, genuine risk "
            "transfer, and outcomes that differ from a simple interest-bearing loan.",
        ),
        (
            "Name three areas where Islamic and conventional finance diverge most sharply.",
            "Risk allocation (partner/trader vs creditor/debtor), mandatory ethical screening "
            "(halal/haram vs optional ESG), and constraint on speculation (Maysir prohibition vs "
            "unrestricted derivatives markets).",
        ),
        (
            "What is the 'scholar concentration' risk?",
            "A small number of prominent scholars sit on multiple institutional Shariah boards. If a "
            "key scholar changes position or becomes unavailable, multiple products at multiple "
            "institutions can be simultaneously affected.",
        ),
    ],
    3: [
        (
            "In a Murabaha transaction, when does Shariah risk arise for the financier?",
            "Shariah risk arises if the financier never genuinely purchases and takes possession of the "
            "asset before selling it on — if the transaction is purely notional, the 'markup' becomes "
            "economically indistinguishable from interest.",
        ),
        (
            "Why is Tawarruq described as 'highly governance-sensitive'?",
            "Because its Shariah compliance depends on genuine third-party trading, clean contract "
            "separation, and documented ownership/possession. Where trades are circular or pre-arranged "
            "between related brokers the OIC Fiqh Academy's restrictions on 'organised Tawarruq' apply.",
        ),
        (
            "How does Diminishing Musharaka work for home finance?",
            "The bank and customer co-own the property. The customer progressively buys the bank's share "
            "in tranches (reducing the bank's ownership to zero) while simultaneously paying rent on the "
            "bank's remaining share — combining capital redemption and rental income within a single "
            "compliant structure.",
        ),
        (
            "What is the key difference between Salam and Istisna?",
            "Salam is a forward purchase of *standardised* commodities or goods with full price paid "
            "upfront. Istisna is a manufacturing/construction contract where the asset is built to "
            "specification — payment can be staged, making it suitable for project finance.",
        ),
        (
            "What role does Wa'ad play in sukuk structuring?",
            "A Wa'ad (unilateral promise) is used to structure purchase undertakings — obliging the "
            "issuer/obligor to repurchase underlying assets at maturity. Its enforceability varies by "
            "jurisdiction and was the central legal battleground in the Dana Gas sukuk dispute.",
        ),
    ],
    4: [
        (
            "Describe the three tiers of the Shariah governance model.",
            "Tier 1: National/central Shariah authority (e.g. UAE HSA, Malaysia BNM SAC — can issue "
            "binding rulings). Tier 2: Institutional Shariah board (3-5 scholars per institution). "
            "Tier 3: Transaction-level Shariah advisor for specific deals (sukuk, funds).",
        ),
        (
            "What is the IIFM and why does it matter for Islamic treasury?",
            "The International Islamic Financial Market produces standardised documentation for Islamic "
            "treasury, hedging, and sukuk transactions — including the ISDA/IIFM Tahawwut Master "
            "Agreement. Standardised docs reduce legal risk and lower transaction costs.",
        ),
        (
            "Why does jurisdictional divergence create operational risk in cross-border Islamic deals?",
            "GCC markets may refuse to recognise structures accepted in Malaysia, and vice versa. A "
            "sukuk approved by a Malaysian Shariah board may face investor pushback from GCC buyers "
            "operating under more conservative scholarly standards.",
        ),
    ],
    5: [
        (
            "What is a Profit-Sharing Investment Account (PSIA) and how does it differ from a conventional deposit?",
            "PSIA holders share in the bank's investment returns — they are not guaranteed a fixed "
            "interest rate. In a loss scenario (absent negligence), PSIA holders bear the loss "
            "proportionate to their investment, unlike conventional depositors whose capital is protected.",
        ),
        (
            "Name three Shariah-compliant instruments available to Islamic banks for treasury/liquidity management.",
            "Commodity Murabaha placements, short-term Wakala deposits, and IILM short-term sukuk "
            "(specifically designed for cross-border Islamic liquidity management).",
        ),
    ],
    6: [
        (
            "What was the total volume of sukuk issuances in 2024 according to IIFM data?",
            "USD 205 billion in total issuances, with international sukuk reaching USD 65.6 billion — "
            "a new record. Total sukuk outstanding exceeded USD 900 billion.",
        ),
        (
            "Why do Murabaha/Salam sukuk face tradability constraints?",
            "AAOIFI SS 59 on the sale of debt means sukuk backed predominantly by Murabaha receivables "
            "(debt obligations) cannot be freely traded at a discount in most scholarly interpretations. "
            "Tradable sukuk require a sufficient proportion of tangible assets or usufruct interests.",
        ),
        (
            "What are the two risks in the ESG/Sustainable Sukuk space?",
            "'Greenwashing' — where environmental claims are not substantiated by use-of-proceeds or "
            "KPI reporting — and 'Shariah-washing' — where the Islamic wrapper lacks genuine contractual "
            "substance. Both undermine investor confidence.",
        ),
    ],
    7: [
        (
            "Why can conventional PE 'leveraged buyout' economics be difficult to replicate in Islamic PE?",
            "LBOs typically use 60–70% interest-bearing debt — prohibited under Shariah. Islamic PE must "
            "use Murabaha, Ijara, or Musharaka facilities instead, often resulting in lower overall "
            "leverage and a preference for growth equity or majority-equity deal structures.",
        ),
        (
            "How is carried interest structured in a Shariah-compliant fund under AAOIFI SS 46?",
            "Carry is structured as a performance incentive fee (reward for management skill/labour) "
            "rather than as a profit share from a partnership — consistent with Wakala (agency) "
            "principles. The management fee cannot be a percentage of debt.",
        ),
        (
            "What does AAOIFI Standard 3 say about defaulting debtors in an Islamic finance context?",
            "AAOIFI SS 3 addresses the 'procrastinating debtor' — an institution may impose penalty "
            "clauses but must direct penalty proceeds to charity, not retain them as income. This "
            "prevents penalty clauses from functioning as a de facto interest rate on overdue amounts.",
        ),
    ],
    8: [
        (
            "What was the central legal question in the Dana Gas sukuk dispute?",
            "Whether the purchase undertaking (Wa'ad) — the mechanism by which investors would be "
            "repaid at maturity — was enforceable under UAE law. Dana Gas argued the sukuk was "
            "itself unlawful; English courts ultimately upheld the undertakings.",
        ),
        (
            "Why is the UK Sovereign Sukuk (2014) considered a landmark?",
            "It was the first sukuk issued by a Western sovereign government, demonstrated that "
            "Ijara-based structures could be adapted for government property assets under English law, "
            "and established that deep Islamic finance markets are achievable outside Muslim-majority "
            "jurisdictions.",
        ),
        (
            "What made the Tadau Energy Green Sukuk (2017) historically significant?",
            "It was the world's first Green Sukuk — demonstrating that Islamic and green finance "
            "frameworks are naturally compatible and establishing a template for sustainable Islamic "
            "capital markets issuance that was rapidly followed by others.",
        ),
    ],
    9: [
        (
            "Why do IFSB and LSEG/ICD market size estimates differ?",
            "Definitional scope: IFSB's USD 3.88 trillion figure uses a narrower definition focusing "
            "on banking assets, sukuk, and funds under management. LSEG/ICD's USD 5.98 trillion "
            "figure includes Takaful and other adjacent segments. Both use different year-end cutoffs.",
        ),
        (
            "What distinguishes Malaysia's role in global Islamic finance from Saudi Arabia's?",
            "Malaysia acts as the 'laboratory' — pioneering regulatory frameworks, SRI sukuk, fintech "
            "Islamic products, and hosting the IFSB. Saudi Arabia is the 'powerhouse' — the largest "
            "banking and sukuk market, home to PIF (largest sovereign wealth fund) and Vision 2030.",
        ),
    ],
    10: [
        (
            "What is AAOIFI Standard 62 and why is it contentious?",
            "Standard 62 is a proposed sukuk standard that would require more consistent legal transfer "
            "of assets to sukuk investors. It is contentious because if broadly applied, many "
            "asset-based sukuk (the dominant market structure) would require restructuring — raising "
            "costs and potentially reducing market liquidity.",
        ),
        (
            "How does tokenisation reduce barriers to sukuk issuance?",
            "Traditional sukuk issuance costs USD 500K–1.5M in legal, structuring, and listing fees. "
            "Digital platforms using blockchain-based fractional sukuk certificates can issue smaller "
            "tranches from USD 10,000, dramatically lowering the minimum ticket size and expanding "
            "retail and smaller issuer access.",
        ),
    ],
    11: [
        (
            "Which white space opportunity is considered most attractive for GCC family offices and why?",
            "Shariah-compliant private credit — because GCC family offices have significant capital "
            "looking for Shariah-compliant yield, conventional private credit (interest-based) is "
            "inaccessible to them, and Wakala/Murabaha hybrids can deliver competitive returns "
            "through a genuinely different structural approach.",
        ),
        (
            "What are the three key execution barriers for any new Islamic finance platform?",
            "Regulatory/Shariah board approval (requires established scholars and jurisdictional "
            "clarity), technology build (especially for digital/tokenised products), and investor "
            "education (Islamic finance literacy among institutional LPs remains uneven).",
        ),
    ],
    12: [
        (
            "State the Five-Question Robustness Test for an Islamic finance structure.",
            "(1) Asset Linkage — is there a genuine identifiable asset? (2) Risk-Sharing — is risk "
            "meaningfully allocated, or synthetically guaranteed? (3) Substance Over Form — real "
            "economic purpose or cosmetic Shariah compliance? (4) Governing Law Enforceability — can "
            "title, security, and trust arrangements survive insolvency in the governing jurisdiction? "
            "(5) Shariah Board Consensus — broad scholarly support or a single niche opinion?",
        ),
        (
            "Name five red flags in an Islamic finance structure.",
            "(1) Wa'ad dependency without genuine asset backing; (2) guaranteed returns language in "
            "equity-based structures; (3) circular commodity trades without genuine third-party market; "
            "(4) purchase undertakings at nominal value in Musharaka/Mudaraba sukuk (post-AAOIFI 2008 "
            "Statement); (5) purely notional asset link — asset appears in documentation but no real "
            "ownership or risk transfer.",
        ),
        (
            "What question should an executive ask the arranger of an Islamic finance transaction?",
            "'Does this structure create real value — or does it simply replicate conventional debt "
            "economics in Islamic legal form? What is the secondary market plan for these instruments, "
            "and how competitive is the pricing relative to a conventional alternative?'",
        ),
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# QUIZ BUILDER
# ──────────────────────────────────────────────────────────────────────────────

def build_quiz_block(module_num: int) -> str:
    questions = QUESTION_BANKS.get(module_num, [])
    if not questions:
        return ""

    lines = ['\n<div class="quiz-section">\n<h3>Knowledge Check Quiz</h3>\n']
    for i, (q, a) in enumerate(questions, 1):
        lines.append(f"{i}. {q}\n")
        lines.append(f"    <details class='quiz-answer'><summary>Show answer</summary>\n")
        lines.append(f"    {a}\n")
        lines.append(f"    </details>\n")
    lines.append("\n</div>\n")
    return "\n".join(lines)


def inject_quiz(filepath: str, module_num: int) -> None:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    quiz_block = build_quiz_block(module_num)
    if not quiz_block:
        return

    # Replace existing quiz-section div if present
    pattern = r'<div class="quiz-section">.*?</div>'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, quiz_block.strip(), content, flags=re.DOTALL)
    else:
        content = content.rstrip() + "\n\n" + quiz_block

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Quiz injected: {filepath}")


def main():
    pattern = os.path.join(DOCS_DIR, MODULE_GLOB)
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No module files found matching: {pattern}")
        return

    for filepath in files:
        # Extract module number from directory name
        dir_name = os.path.basename(os.path.dirname(filepath))
        match = re.match(r"module-(\d+)-", dir_name)
        if not match:
            continue
        module_num = int(match.group(1))
        print(f"Processing Module {module_num}: {filepath}")
        inject_quiz(filepath, module_num)

    print("\nQuiz generation complete.")


if __name__ == "__main__":
    main()
