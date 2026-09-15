import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.research_result import ResearchResult


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ResearchResult)
            .order_by(ResearchResult.id.desc())
        )

        rows = result.scalars().all()

        for row in rows:
            print("=" * 80)
            print("RESULT ID:", row.id)
            print("RESEARCH ID:", row.research_id)
            print("EVIDENCE:")
            print(row.evidence)
            print("DOCUMENTS:")
            print(row.documents)
            print("INSIGHTS:")
            print(row.insights)
            print("AGENT RESULTS COUNT:", len(row.agent_results or []))
            print("CITATIONS COUNT:", len(row.citations or []))


if __name__ == "__main__":
    asyncio.run(main())
