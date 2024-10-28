# E-commerce Backend

This e-commerce project follows a layered architecture that includes a model layer, a repository layer, a controller layer, and an API layer. It provides a robust and scalable backend solution for e-commerce applications.

## Project Setup

To set up the project, follow these steps:

1. **Clone the Repository**  
   Clone the project repository using the following command:
   ```bash
   git clone <github_url>
   ```

2. **Create a Virtual Environment**  
   Navigate to the project directory and create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**  
   Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Requirements**  
   Install the project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create Migrations**  
   Generate migration scripts for database changes:
   ```bash
   alembic revision --autogenerate -m "Modify database"
   ```

6. **Apply Migrations**  
   Apply the generated migrations to update the database schema:
   ```bash
   alembic upgrade head
   ```

7. **Run the Server**  
   Start the application server:
   ```bash
   python main.py
   ```

8. **Access Swagger Documentation**  
   Visit the following URL to access the API documentation:
   ```
   http://<host>/docs
   ```

9. **Run Test Cases**  
   Execute the test suite to ensure everything is functioning as expected:
   ```bash
   pytest -vv -s --cache-clear ./
   ```


## Explanation of your authentication design decisions.

I implemented a robust authentication mechanism featuring asynchronous database connections. This choice enhances performance under high concurrency, allowing multiple requests to be handled simultaneously without blocking. For user sessions, I utilized JWT authentication with refresh tokens, ensuring secure, stateless interactions. Passwords are hashed using bcrypt with unique salts, ensuring secure storage and protecting user credentials against potential breaches.

## Discussion on security measures implemented.

I implemented token blacklisting to invalidate refresh tokens when users log out or report suspicious activity. This prevents misuse of tokens. Additionally, each user is assigned a UUID instead of a sequential integer ID, mitigating risks associated with user enumeration and tracking. These measures enhance user privacy and security, ensuring the integrity of user sessions and data within the application.


## Ideas for further enhancing the authentication system (e.g., 2FA, OAuth integration).

To enhance the authentication system, consider implementing Two-Factor Authentication (2FA) using OTPs via SMS/email or authenticator apps for improved security and user trust. Introduce Role-Based Access Control (RBAC) with fine-grained permissions to ensure users access only authorized resources. Additionally, implement auditing and logging for compliance by tracking authentication events and securing logs to aid incident response and meet industry regulations.


## Notes
- Ensure that you have the required software installed (e.g., Python, pip, Alembic).
- Adjust the `<host>` in the Swagger URL to match your server's address.