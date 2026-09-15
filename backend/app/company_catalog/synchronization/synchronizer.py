from app.company_catalog.providers.provider_manager import ( 
                                                            ProviderManager
)

from app.company_catalog.processing.pipeline import (
    CompanyProcessingPipeline
)

from app.company_catalog.synchronization.updater import (
    CompanyUpdater
)



class CompanySynchronizer:


    def __init__(
        self,
        provider_manager: ProviderManager,
        processing_pipeline: CompanyProcessingPipeline,
        updater: CompanyUpdater
    ):

        self.provider_manager = provider_manager

        self.processing_pipeline = processing_pipeline

        self.updater = updater



    async def synchronize(
        self,
        provider_name: str | None = None
    ):


        # 1. Fetch companies

        companies = await self.provider_manager.fetch_companies(
            provider_name
        )


        # 2. Normalize + Validate

        processed_companies = (
            await self.processing_pipeline.process(
                companies
            )
        )


        # 3. Update database

        result = await self.updater.update_companies(
            processed_companies
        )


        return {

            "status": "completed",

            "total_processed":
                len(processed_companies),

            "database":
                result
        }