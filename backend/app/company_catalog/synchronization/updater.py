from typing import List

from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyCreate


class CompanyUpdater:
    """
    Handles database updates during synchronization.
    """

    def __init__(
        self,
        repository: CompanyRepository
    ):
        self.repository = repository


    async def update_companies(
        self,
        companies: List[CompanyCreate]
    ):
        """
        Insert new companies
        Update existing companies
        """

        created = 0
        updated = 0


        for company in companies:

            existing = await self.repository.get_by_ticker(
                company.ticker
            )


            if existing:

                await self.repository.update(
                    existing.id,
                    company
                )

                updated += 1


            else:

                await self.repository.create(
                    company
                )

                created += 1


        return {
            "created": created,
            "updated": updated
        }