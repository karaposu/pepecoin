# impl/services/file/file_records_categorization_service.py

import logging
from fastapi import HTTPException
from datetime import datetime
from traceback import format_exc
from categorizer.record_manager import RecordManager

logger = logging.getLogger(__name__)

def get_current_time():
    return datetime.utcnow()

class FileRecordsCategorizerService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside RecordCategorizerService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        user_id = self.request.user_id
        file_id = self.request.file_id

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"user_id: {user_id}")
        logger.debug(f"file_id: {file_id}")

        try:
            # Access session_factory and repositories from dependencies
            logger.debug("Accessing session_factory and repositories from dependencies")
            session_factory = self.dependencies.session_factory()
            record_repository_provider = self.dependencies.record_repository
            file_repository_provider = self.dependencies.file_repository

            # Create a new database session
            session = session_factory()
            try:
                logger.debug("Now inside the database session")

                # Instantiate repositories with the session
                record_repository = record_repository_provider(session=session)
                file_repository = file_repository_provider(session=session)

                # Get records for the user and file
                logger.debug(f"Retrieving records for user_id: {user_id}, file_id: {file_id}")
                records_df = record_repository.get_records_by_user_and_file(user_id, file_id)
                logger.debug(f"Number of records retrieved: {len(records_df)}")

                if records_df.empty:
                    logger.error("No records found for categorization")
                    raise HTTPException(status_code=404, detail="No records found for categorization")

                # Initialize the RecordManager
                logger.debug("Initializing RecordManager")
                record_manager = self.initialize_llm_categorizer()

                # Load records into RecordManager
                record_manager.load_records(
                    record_inputs=records_df,
                    categories_yaml_path='assets/config/categories.yaml'
                )
                logger.debug("Records loaded into RecordManager")

                # Update processing status to 'in progress'
                logger.debug("Updating processing status to 'in progress'")

                # process_status
                file_repository.update_processing_status(
                    user_id=user_id,
                    file_id=file_id,
                    process_status="in progress",
                    started_at=get_current_time()
                )

                # Run categorization
                try:
                    logger.debug("Running categorization")
                    self.run_categorization(
                        record_manager,
                        record_repository,
                        file_repository,
                        user_id,
                        file_id
                    )
                    # Update processing status to 'completed'
                    logger.debug("Updating processing status to 'completed'")
                    file_repository.update_processing_status(
                        user_id=user_id,
                        file_id=file_id,
                        process_status="completed",
                        completed_at=get_current_time()
                    )
                    session.commit()
                except Exception as e:
                    logger.error(f"Error during categorization: {e}\n{format_exc()}")
                    # Update processing status to 'failed'
                    file_repository.update_processing_status(
                        user_id=user_id,
                        file_id=file_id,
                        process_status="failed"
                    )
                    session.commit()
                    raise HTTPException(status_code=500, detail=f"Error during categorization: {e}")

                self.preprocessed_data = "Categorization completed successfully"

            except HTTPException as http_exc:
                session.rollback()
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")

            finally:
                session.close()

        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # Prepare the response
        self.response = {"msg": self.preprocessed_data}

    def initialize_llm_categorizer(self):
        # Initialize your RecordManager or similar
        return RecordManager()

    def run_categorization(self, record_manager, record_repository, file_repository, user_id, file_id):
        logger.debug("run_categorization()")
        # Perform categorization
        df = record_manager.categorize_records(user_id=user_id, file_id=file_id, file_repository=file_repository)
        logger.debug("Categorization completed")

        # Update processing status to 'in progress(AI)'
        file_repository.update_processing_status(
            user_id=user_id,
            file_id=file_id,
            process_status="in progress(AI)"
        )

        # Update processed data in the database
        record_repository.update_processed_data(df)
        logger.debug("Processed data updated in the database")
