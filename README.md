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

## Notes
- Ensure that you have the required software installed (e.g., Python, pip, Alembic).
- Adjust the `<host>` in the Swagger URL to match your server's address.

Feel free to contribute or raise issues if you encounter any problems!