
import logging
logger = logging.getLogger(__name__)

from models.auth_login_post200_response import AuthLoginPost200Response
from models.auth_register_post200_response import AuthRegisterPost200Response
from models.verify_email200_response import VerifyEmail200Response
from dependency_injector.wiring import inject, Provide

import os
import smtplib

from fastapi_login import LoginManager
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from passlib.context import CryptContext

from db.db_manager import DBManager
from fastapi import  FastAPI, Depends, HTTPException
import jwt
from impl.services.base_service import BaseService
from datetime import datetime, timedelta
from traceback import format_exc

# SECRET_KEY = "your_jwt_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


load_dotenv()
logging.basicConfig(level=logging.DEBUG)
SECRET_KEY = os.getenv("SECRET_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not SECRET_KEY or not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("SECRET_KEY, EMAIL_ADDRESS, and EMAIL_PASSWORD must be set in environment variables")

manager = LoginManager(SECRET_KEY, token_url='/auth/login')

db_path = os.path.join(os.path.dirname(__file__), "..", "..", "db/budget_tracker.db")
db_path = os.path.abspath(db_path)

# primary_db_path

# DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()





def get_smtp_details(email: str):
    domain = email.split('@')[-1]
    if 'gmail.com' in domain:
        return 'smtp.gmail.com', 587, EMAIL_ADDRESS, EMAIL_PASSWORD
    elif 'outlook.com' in domain or 'hotmail.com' in domain:
        return 'smtp.office365.com', 587, EMAIL_ADDRESS, EMAIL_PASSWORD
    else:
        raise HTTPException(status_code=400, detail="Unsupported email domain")


# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


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


def send_verification_email(email: str, token: str):
    verification_link = f"http://127.0.0.1:3000/auth/verify-email?token={token}"
    smtp_server, smtp_port, smtp_user, smtp_pass = get_smtp_details(email)

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = email
    msg['Subject'] = 'Email Verification'
    body = f"Please verify your email by clicking the following link: {verification_link}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            logging.debug(f"Verification email sent to {email} via {smtp_server}")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error on {smtp_server}: {e}")
        raise HTTPException(status_code=500, detail="SMTP Authentication Error")
    except Exception as e:
        logging.error(f"Failed to send email via {smtp_server}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")



class RegisterService2(BaseService):
    
    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        email = self.request.email
        password = self.request.password

        logger.debug("email=%s", email, extra={'lvl': 2})
        logger.debug("password=%s", password, extra={'lvl': 2})

        try:
            # Validate email
            valid = validate_email(email)
            email = valid.email
            logger.debug("Email is valid: %s", email, extra={'lvl': 2})

        except EmailNotValidError as e:
            logger.error(f"Email validation failed: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        try:
            # Initialize DBManager
            db_manager = DBManager(db_path)
            logger.debug("DBManager initialized", extra={'lvl': 2})

        except Exception as e:
            logger.error(f"Failed to initialize DBManager: {str(e)}")
            raise RuntimeError(f"Failed to initialize DBManager: {e}")

        try:
            with db_manager.session_scope() as session:
                # Check if user already exists
                logger.debug("Checking if user exists with email: %s", email, extra={'lvl': 2})
                if db_manager.get_user_by_email(session, email):
                    logger.error(f"Email already registered: {email}")
                    raise HTTPException(status_code=400, detail="Email already registered")

                # Hash the password
                logger.debug("Hashing password", extra={'lvl': 2})
                hashed_password = pwd_context.hash(password)
                logger.debug("hashed_password=%s", hashed_password, extra={'lvl': 2})

                # Add the new user
                logger.debug("Adding new user to the database", extra={'lvl': 2})
                user_id = db_manager.add_new_user(email, hashed_password)
                logger.debug("User added successfully with ID: %s", user_id, extra={'lvl': 2})

                # Generate JWT token
                logger.debug("Generating JWT token for user_id=%s", user_id, extra={'lvl': 2})
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": str(user_id)}, expires_delta=access_token_expires
                )

                self.preprocessed_data = access_token
                logger.debug("Token generated successfully", extra={'lvl': 2})

        except Exception as e:
            logger.error(f"An error occurred during registration: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):


        self.response =AuthRegisterPost200Response(
            msg="User registered successfully",
            access_token=self.preprocessed_data
        )




class LoginService2(BaseService):

    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        try:
            db_manager = DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")

        logger.debug(f"preprocess_request_data()")
        logger.debug(f"email {self.request.email}     password {self.request.password}")

        # logger.debug(f"self.request {self.request}")

        try:
            email = self.request.email
            password = self.request.password

            with db_manager.session_scope() as session:
                user = db_manager.get_user_by_email(session, email)
                if not user:
                    raise HTTPException(status_code=400, detail="Email not found")

                if not pwd_context.verify(password, user.password_hash):
                    # Raise an appropriate HTTPException for invalid credentials
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                # if not user.is_verified:
                #     raise HTTPException(status_code=400, detail="Email not verified")
                if email == 'dev@test.com':
                    # Use the predefined token for the dev user
                    predefined_access_token = "your_predefined_token_here"
                    access_token = predefined_access_token
                else:
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
                    )
                self.preprocessed_data = {'access_token': access_token, 'token_type': 'bearer'}

                # self.preprocessed_data = {'access_token': access_token, 'token_type': 'bearer'}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except HTTPException as e:
            logging.error(f"An error occurred during login: {e.detail}")
            raise e
        except Exception as e:
            logging.error(f"An unexpected error occurred during login: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        x = AuthLoginPost200Response(
            access_token=self.preprocessed_data['access_token'],
            token_type=self.preprocessed_data['token_type']
        )

        self.response = x
        return x


class LoginService(BaseService):

    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        try:
            db_manager = DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")

        try:
            email = self.request.email
            password = self.request.password

            with db_manager.session_scope() as session:
                user = db_manager.get_user_by_email(session, email)
                if not user:
                    raise HTTPException(status_code=400, detail="Email not found")

                if not pwd_context.verify(password, user.password_hash):
                    # Raise an appropriate HTTPException for invalid credentials
                    raise HTTPException(status_code=401, detail="Invalid credentials")
                if not user.is_verified:
                    raise HTTPException(status_code=400, detail="Email not verified")

                access_token = manager.create_access_token(data={'sub': email})
                logging.debug(f"Generated access token for user {email}: {access_token}")

                self.preprocessed_data = {'access_token': access_token, 'token_type': 'bearer'}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except HTTPException as e:
            logging.error(f"An error occurred during login: {e.detail}")
            raise e
        except Exception as e:
            logging.error(f"An unexpected error occurred during login: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        x = AuthLoginPost200Response(
            access_token=self.preprocessed_data['access_token'],
            token_type=self.preprocessed_data['token_type']
        )

        self.response = x
        return x





class RefreshTokenService(BaseService):

    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        try:
            db_manager = DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")

        try:
            email = self.request.email
            new_password = self.request.new_password

            # Use the db_manager to change the password
            db_manager.change_password(email, new_password)

            self.preprocessed_data = {"msg": "Password reset successfully"}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")
        except Exception as e:
            logging.error(f"An error occurred during password reset: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        x = AuthRegisterPost200Response(msg=self.preprocessed_data["msg"])

        self.response = x
        return x


class ResetPasswordService(BaseService):

    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        try:
            db_manager = DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")

        try:
            email = self.request.email
            new_password = self.request.new_password

            # Use the db_manager to change the password
            db_manager.change_password(email, new_password)

            self.preprocessed_data = {"msg": "Password reset successfully"}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid token")
        except Exception as e:
            logging.error(f"An error occurred during password reset: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        x = AuthRegisterPost200Response(msg=self.preprocessed_data["msg"])

        self.response = x
        return x

class VerifyService(BaseService):

    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        try:
            db_manager = DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")



        try:
            token = self.request.token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            email = payload['sub']

            # Use the db_manager to verify the user email
            db_manager.make_user_verified_from_email(email)

            self.preprocessed_data = {"msg": "Email verified successfully"}

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Verification link expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid verification link")
        except Exception as e:
            logging.error(f"An error occurred during email verification: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        x = VerifyEmail200Response(msg=self.preprocessed_data["msg"])

        self.response = x
        return x

# this is inside auth_services.py


class RegisterService(BaseService):

    def check_compatibility(self):
        pass

    def preprocess_request_data(self):
        email = self.request.email
        password = self.request.password

        logger.debug("email=%s", email, extra={'lvl': 2})
        logger.debug("password=%s", password, extra={'lvl': 2})

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise HTTPException(status_code=400, detail=str(e))

        try:
            db_manager = DBManager(db_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DBManager: {e}")

        try:
            with db_manager.session_scope() as session:
                # Check if user already exists
                if db_manager.get_user_by_email(session, email):
                    raise HTTPException(status_code=400, detail="Email already registered")

                # Hash the password
                hashed_password = pwd_context.hash(password)
                logger.debug("hashed_password=%s", hashed_password, extra={'lvl': 2})

                # Add the new user
                db_manager.add_new_user(email, hashed_password)

                # Generate verification token
                token = manager.create_access_token(data={'sub': email})
                logger.debug("token=%s", token, extra={'lvl': 2})

                # Send verification email
                send_verification_email(email, token)

                self.preprocessed_data = "s"

        except Exception as e:
            logger.error(f"An error occurred during registration: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        x = AuthRegisterPost200Response(msg="register is done")
        self.response = x
        return self.response






# class LogoutService(BaseService):
#
#         def check_compatibility(self):
#             pass
#
#         def preprocess_request_data(self):
#
#             try:
#                 db_manager = DBManager(db_path)
#             except Exception as e:
#                 raise RuntimeError(f"Failed to initialize DBManager: {e}")
#
#             try:
#                 email = self.request.email
#                 new_password = self.request.new_password
#
#                 db_manager.change_password(email, new_password)
#
#                 return {"msg": "Password reset successfully"}
#
#             except jwt.ExpiredSignatureError:
#                 raise HTTPException(status_code=400, detail="token expired")
#             except jwt.InvalidTokenError:
#                 raise HTTPException(status_code=400, detail="token bad")
#
#         def process_request(self):
#
#             from models.auth_register_post200_response import AuthRegisterPost200Response
#
#             x = AuthRegisterPost200Response(msg="done")
#
#             self.response = x
#             return x

    # def register_new_user(self):
    #     """
    #     Register a new user with the provided details.
    #
    #     :param request: RegisterUserRequest object containing user registration details.
    #     :return: RegisterUser200Response object containing the registration response.
    #     """
    #
    #     # Here, you would include logic to save the user's details to your database.
    #     # For demonstration purposes, we'll generate a UUID as the user ID and pretend to save it.
    #
    #     user_id = str(uuid.uuid4())
    #
    #     self.user_id=user_id
    #
    #     # Assuming successful registration, return a response
    #     # return RegisterUser200Response(userId=user_id, message="Registration successful")
    #     return user_id