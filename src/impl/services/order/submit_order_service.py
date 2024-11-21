# impl/services/file/upload_file_service.py





import logging
from fastapi import HTTPException
from datetime import datetime
import os
import tempfile
from traceback import format_exc

# from models.upload_and_process_pdf200_response import UploadAndProcessPdf200Response
# from bsd_analyser.extractors import get_extractor

logger = logging.getLogger(__name__)

import yaml


class SubmitOrderService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside UploadFileService")

        self.preprocess_request_data()
        self.process_request()

        self.is_first_upload=None

    def preprocess_request_data(self):

        amount = self.request.amount
        currency = self.request.currency

        description = self.request.description
        customer_email = self.request.customer_email
        metadata = self.request.metadata

        logger.debug("Inside preprocess_request_data")

        try:
            # Access session_factory and repositories from dependencies
            logger.debug("Accessing session_factory and repositories from dependencies")
            # session_factory = self.dependencies.session_factory()

            # Access providers from dependencies
            main_session_factory = self.dependencies.session_factory
            order_repository_provider = self.dependencies.order_repository
            main_sessionmaker = main_session_factory()
            main_session = main_sessionmaker()

            order_repository = order_repository_provider(session=main_session)


            try:
                logger.debug("Now inside the database session")
                try:

                    order_processor = OrderProcesser()
                    processing_result = order_processor.process()
                    logger.debug("File processed successfully")
                except Exception as e:
                    logger.error(f"Error during file processing: {e}\n{format_exc()}")
                    raise HTTPException(status_code=500, detail=f"Error during file processing: {e}")

                try:

                    logger.debug("Saving order processing results to the database")

                    file_id = file_repository.save_raw_file_to_db(
                        file_path=extractor.file_path,
                        bank_name=string_bank_id,
                        bank_id=bank_id,
                        user_id=user_id,
                        currency=country_currency_code,
                        country_code= country_code
                    )

                except Exception as e:
                    logger.error(f"Failed to save raw file to the database: {e}\n{format_exc()}")
                    main_session.rollback()
                    raise HTTPException(status_code=500, detail=f"Failed to save raw file to the database: {e}")



                # Prepare the preprocessed data
                self.preprocessed_data = {
                    "file_id": file_id,
                    "upload_timestamp": datetime.now().isoformat()
                }

            except HTTPException as http_exc:
                main_session.rollback()
                exchange_rate_session.rollback()
                raise http_exc

            except Exception as e:
                main_session.rollback()
                exchange_rate_session.rollback()
                logger.error(f"An error occurred: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")

            finally:
                main_session.close()
                exchange_rate_session.close()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        self.response = UploadAndProcessPdf200Response(
            file_id=self.preprocessed_data["file_id"],
            upload_timestamp=self.preprocessed_data["upload_timestamp"]
        )
