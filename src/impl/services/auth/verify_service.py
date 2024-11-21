# impl/services/user_services.py

import logging
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt
from traceback import format_exc

from models.verify_email200_response import VerifyEmail200Response

logger = logging.getLogger(__name__)

# Constants for JWT token decoding
ALGORITHM = "HS256"
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key

class VerifyService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside VerifyService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        token = self.request.token

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"Token: {token}")

        try:
            # Decode the JWT token
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                logger.debug(f"Token decoded successfully: {payload}")
            except jwt.ExpiredSignatureError:
                logger.error("Verification link expired")
                raise HTTPException(status_code=400, detail="Verification link expired")
            except jwt.InvalidTokenError:
                logger.error("Invalid verification link")
                raise HTTPException(status_code=400, detail="Invalid verification link")

            # Extract email or user_id from the token payload
            # Assuming the token contains 'sub' which is the user's email
            email = payload.get('sub')
            if not email:
                logger.error("Token does not contain 'sub'")
                raise HTTPException(status_code=400, detail="Invalid token payload")

            logger.debug(f"Email extracted from token: {email}")

            # Access session_factory and user_repository providers from dependencies
            logger.debug("Accessing session_factory and user_repository providers")
            session_factory = self.dependencies.session_factory()
            user_repository_provider = self.dependencies.user_repository

            # Create a new database session
            session = session_factory()
            try:
                logger.debug("Now inside the database session")
                # Instantiate the UserRepository with the session
                user_repository = user_repository_provider(session=session)

                # Retrieve the user by email
                logger.debug(f"Retrieving user with email: {email}")
                db_user = user_repository.get_user_by_email(email)
                if not db_user:
                    logger.error(f"User not found with email: {email}")
                    raise HTTPException(status_code=400, detail="User not found")

                # Update the user's verified status in the database
                logger.debug("Updating user's verified status in the database")
                db_user.is_verified = True
                session.commit()
                logger.debug("User's verified status updated successfully")

                # Prepare the success message
                self.preprocessed_data = {"msg": "Email verified successfully"}

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during email verification: {e}\n{format_exc()}")
                raise e
            finally:
                session.close()

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise http_exc

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # Prepare the response
        self.response = VerifyEmail200Response(
            msg=self.preprocessed_data["msg"]
        )
