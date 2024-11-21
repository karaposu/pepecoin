# impl/services/auth/register_services.py

import logging
from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException
import jwt
from traceback import format_exc

from models.auth_register_post200_response import AuthRegisterPost200Response

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()
import os
# logging.basicConfig(level=logging.DEBUG)
SECRET_KEY = os.getenv("SECRET_KEY")


# Constants for JWT token creation
ALGORITHM = "HS256"
# SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 3000  # Set as per your requirement

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None, unlimited: bool = False):
    to_encode = data.copy()

    if unlimited:
        # Set a very far expiration date for unlimited tokens
        expire = datetime.utcnow() + timedelta(days=365 * 100)  # 100 years
    elif expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

class RegisterService:

    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside RegisterService2")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        email = self.request.email
        password = self.request.password

        logger.debug("Inside preprocess_request_data")
        logger.debug(f"Email: {email}")
        logger.debug(f"Password: {password}")

        try:
            # Validate the email address
            valid = validate_email(email)
            email = valid.email
            logger.debug(f"Email is valid: {email}")

        except EmailNotValidError as e:
            logger.error(f"Email validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        try:
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

                # Check if the user already exists
                logger.debug(f"Checking if user exists with email: {email}")
                if user_repository.check_user_by_email(email):
                    logger.error(f"Email already registered: {email}")
                    raise HTTPException(status_code=400, detail="Email already registered")

                # Hash the user's password
                logger.debug("Hashing password")
                hashed_password = pwd_context.hash(password)
                logger.debug("Password hashed successfully")

                # Add the new user to the database
                logger.debug("Adding new user to the database")
                user_id = user_repository.add_new_user(email, hashed_password)
                logger.debug(f"User added successfully with ID: {user_id}")

                # Generate a JWT token for the new user
                logger.debug(f"Generating JWT token for user_id: {user_id}")
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": str(user_id)},
                    expires_delta=access_token_expires
                )

                # Store the generated token
                self.preprocessed_data = access_token
                logger.debug("Token generated successfully")

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred during registration: {e}\n{format_exc()}")
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
        # Prepare the response with the access token
        self.response = AuthRegisterPost200Response(
            msg="User registered successfully",
            access_token=self.preprocessed_data
        )
