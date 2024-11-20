import modal
from core.server import app as main
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Initialize Modal app
app = modal.App("harmann-studios")

# Collect environment variables from .env
env_vars = {key: os.getenv(key) for key in [
    "DEBUG", "DEFAULT_LOCALE", "ENVIRONMENT", "RELEASE_VERSION",
    "SECRET_KEY", "JWT_ALGORITHM", "JWT_EXPIRE_MINUTES",
    "NEON_DB_USER", "NEON_DB_PASSWORD", "NEON_DB_HOST", "NEON_DB_NAME"
]}

# List of secret keys to be passed as secrets
secret_keys = [
    "DEBUG",
    "DEFAULT_LOCALE",
    "ENVIRONMENT",
    "RELEASE_VERSION",
    "JWT_EXPIRE_MINUTES",  # Added missing comma here
    "NEON_DB_PASSWORD", 
    "SECRET_KEY", 
    "JWT_ALGORITHM", 
    "NEON_DB_USER", 
    "NEON_DB_HOST",
    "NEON_DB_NAME"
]

# Use modal.Secret to securely pass environment variables to functions
secrets = [modal.Secret.from_name(key) for key in secret_keys]

# Define the Modal image (Debian-based with Python requirements)
image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

# Define the Modal function with the image and secrets
@app.function(image=image, secrets=secrets)
@modal.asgi_app()
def harmann_studios():
    return main

if __name__ == "__main__":
    # Start the Modal app
    app.serve()
