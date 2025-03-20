# Import required libraries
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# Debug settings
DEBUG = os.getenv("DEBUG", "False") == "True"

# Database information
DATABASE_TYPE = os.getenv("DATABASE_TYPE")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_DIR = os.getenv("DATABASE_DIR")

# AWS credentials

REGION = os.getenv("REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


#file Directories
IMAGEDIR = os.getenv("IMAGEDIR")
AUDIODIR= os.getenv("AUDIODIR")
PDFDIR= os.getenv("PDFDIR")
TEMPAUDIODIR= os.getenv("TEMPAUDIODIR")


SECRET_KEY = os.getenv("SECRET_KEY")