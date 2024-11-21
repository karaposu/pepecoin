# impl/services/user_services.py

import logging
from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException
import jwt
from traceback import format_exc

# from models.auth_reset_password_post200_response import AuthResetPasswordPost200Response
from models.auth_register_post200_response import AuthRegisterPost200Response

logger = logging.getLogger(__name__)

# Constants for JWT token creation
ALGORITHM = "HS256"
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ResetPasswordService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside ResetPasswordService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        email = self.request.email
        new_password = self.request.new_password

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"Email: {email}")
        logger.debug(f"New Password: {new_password}")

        try:
            # Validate the email address
            try:
                valid = validate_email(email)
                email = valid.email
                logger.debug(f"Email is valid: {email}")
            except EmailNotValidError as e:
                logger.error(f"Email validation failed: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

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

                # Hash the new password
                logger.debug("Hashing new password")
                hashed_password = pwd_context.hash(new_password)
                logger.debug("New password hashed successfully")

                # Update the user's password in the database
                logger.debug("Updating user's password in the database")
                db_user.hashed_password = hashed_password
                session.commit()
                logger.debug("User's password updated successfully")

                # Prepare the success message
                self.preprocessed_data = {"msg": "Password reset successfully"}

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during password reset: {e}\n{format_exc()}")
                raise e
            finally:
                session.close()

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise http_exc

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # Prepare the response
        self.response = AuthRegisterPost200Response(
            msg=self.preprocessed_data["msg"]
        )
