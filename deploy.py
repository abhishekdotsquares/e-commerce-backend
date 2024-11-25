import modal
from core.server import app as main  # Import your FastAPI app directly
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Define the Modal app
app = modal.App("harmann-studios-phase-1")

# Define the Modal image with dependencies
image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

# # Create a secret group for your environment variables
# secrets = modal.Secret.from_dict({
#     "DEBUG": os.getenv("DEBUG"),
#     "DEFAULT_LOCALE": os.getenv("DEFAULT_LOCALE"),
#     "ENVIRONMENT": os.getenv("ENVIRONMENT"),
#     "RELEASE_VERSION": os.getenv("RELEASE_VERSION"),
#     "SECRET_KEY": os.getenv("SECRET_KEY"),
#     "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM"),
#     "JWT_EXPIRE_MINUTES": os.getenv("JWT_EXPIRE_MINUTES"),
#     "NEON_DB_USER": os.getenv("NEON_DB_USER"),
#     "NEON_DB_PASSWORD": os.getenv("NEON_DB_PASSWORD"),
#     "NEON_DB_HOST": os.getenv("NEON_DB_HOST"),
#     "NEON_DB_NAME": os.getenv("NEON_DB_NAME"),
# })

# Define the Modal function to handle ASGI app (FastAPI in this case)
@app.function(image=image, secrets=[modal.Secret.from_name("secret-manager")])
@modal.asgi_app()
def harmann_studios_phase1():
    return main

# # Run locally (for testing purposes only)
# if __name__ == "__main__":
#     with app.run():
#         pass
