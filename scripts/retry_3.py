"""Retry the 3 remaining timed-out sections."""
import asyncio, time, re
from notebooklm import NotebookLMClient

NOTEBOOK_ID = "089061de-5c74-411f-9315-af4717aef843"

SECTIONS = [
    {
        "module": 2, "slug": "islamic-finance-vs-conventional-finance",
        "section_id": "2.4", "section_title": "Where Islamic Finance Is Strong vs Contested",
        "query": (
            "Expand on strong areas of Islamic finance (resilience in crises, ethical appeal, "
            "ESG alignment, access to Muslim-majority investor pools) and contested areas "
            "(standardisation gaps, scholar concentration, interpretive divergence across "
            "jurisdictions). Cite all sources from the notebook."
        ),
    },
    {
        "module": 3, "slug": "core-islamic-contracts-and-structuring-toolkit",
        "section_id": "3.4", "section_title": "Ijara and Ijara Muntahia Bittamleek",
        "query": (
            "Expand on Ijara and Ijara Muntahia Bittamleek: definitions, AAOIFI Shariah Standard 9, "
            "full transaction flow, use cases (real estate, aircraft, equipment, UK Sovereign Sukuk "
            "2014), key risks (asset maintenance, insurance, notional ownership). "
            "Executive takeaway: 'return via renting use'. Cite all sources from the notebook."
        ),
    },
    {
        "module": 10, "slug": "new-developments-innovation-and-debate",
        "section_id": "10.4", "section_title": "ESG and Sustainable Sukuk Convergence",
        "query": (
            "Expand on ESG and sustainable sukuk convergence: ICMA/IsDB/LSEG guidance, green sukuk "
            "exceeding USD 15 billion in 2024, natural convergence with Islamic finance principles "
            "(real-economy linkage, ethical screening, transparency), Malaysia SRI sukuk leadership. "
            "Cite all sources from the notebook."
        ),
    },
]


def inject(filepath, section_id, section_title, body):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    header = re.escape(f"## {section_id} {section_title}")
    pattern = rf"({header}\n)(.*?)(?=\n## |\Z)"
    replacement = f"## {section_id} {section_title}\n\n{body.strip()}\n\n"
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count == 0:
        new_content = content.rstrip() + f"\n\n## {section_id} {section_title}\n\n{body.strip()}\n\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


async def main():
    ok = 0
    for item in SECTIONS:
        filepath = f"docs/module-{str(item['module']).zfill(2)}-{item['slug']}/index.md"
        print(f"  [{item['section_id']}] {item['section_title']} ...", end=" ", flush=True)
        try:
            async with await NotebookLMClient.from_storage() as client:
                result = await client.chat.ask(NOTEBOOK_ID, item["query"])
                body = result.answer if hasattr(result, "answer") else str(result)
            inject(filepath, item["section_id"], item["section_title"], body)
            print("OK")
            ok += 1
        except Exception as exc:
            print(f"FAILED ({exc})")
        time.sleep(5)
    print(f"\nDone — {ok}/{len(SECTIONS)} succeeded.")

if __name__ == "__main__":
    asyncio.run(main())
