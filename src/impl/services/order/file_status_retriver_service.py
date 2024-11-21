# impl/services/file/file_status_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc

from models.get_categorization_status200_response import GetCategorizationStatus200Response

logger = logging.getLogger(__name__)

class FileStatusRetrieverService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside FileStatusRetrieverService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        user_id = self.request.user_id
        file_id = self.request.file_id

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"user_id: {user_id}")
        logger.debug(f"file_id: {file_id}")

        try:
            # Access session_factory and file_repository providers from dependencies
            logger.debug("Accessing session_factory and file_repository providers")
            session_factory = self.dependencies.session_factory()
            file_repository_provider = self.dependencies.file_repository

            # Create a new database session
            session = session_factory()
            try:
                logger.debug("Now inside the database session")
                # Instantiate the FileRepository with the session
                file_repository = file_repository_provider(session=session)

                # Get the categorization status
                logger.debug(f"Retrieving categorization status for user_id: {user_id}, file_id: {file_id}")
                status_data = file_repository.get_categorization_status(user_id, file_id)
                logger.debug(f"Categorization status retrieved: {status_data}")

                self.preprocessed_data = status_data

            except HTTPException as http_exc:
                session.rollback()
                logger.error(f"HTTPException during status retrieval: {http_exc.detail}")
                raise http_exc

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during status retrieval: {e}\n{format_exc()}")
                raise HTTPException(status_code=500, detail="Internal server error")

            finally:
                session.close()

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # Prepare the response using the GetCategorizationStatus200Response model
        self.response = GetCategorizationStatus200Response(**self.preprocessed_data)
