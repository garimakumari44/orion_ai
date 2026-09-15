import asyncio
import json

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models.research_result import ResearchResult


async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ResearchResult)
            .where(ResearchResult.research_id == 63)
        )

        row = result.scalar_one_or_none()

        if row is None:
            print("ResearchResult not found")
            return

        print("=" * 100)
        print("RESULT ID:", row.id)
        print("RESEARCH ID:", row.research_id)
        print("=" * 100)

        print("\nEVIDENCE:")
        print(json.dumps(row.evidence, indent=2, default=str))

        print("\nDOCUMENTS:")
        print(json.dumps(row.documents, indent=2, default=str))

        print("\nINSIGHTS:")
        print(json.dumps(row.insights, indent=2, default=str))

        print("\nCITATIONS:")
        print(json.dumps(row.citations, indent=2, default=str))

        print("\nAGENT RESULTS:")
        print(json.dumps(row.agent_results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
