# WINS Forum

WINS Forum is a modern, sleek forum website with a dark theme. It features user authentication, real-time notifications, pagination, email notifications, and more.

## Features

- User authentication with JWT
- Real-time notifications using WebSockets
- Pagination for threads and posts
- User profile management including avatar upload
- Email notifications for password reset and other events
- Rate limiting to prevent abuse
- Dark theme for a modern look

## Requirements

- Python 3.8+
- Node.js 12+

## Setup Instructions

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/wins-forum.git
   cd wins-forum

    Create a virtual environment and activate it

    bash

python -m venv env
source env/bin/activate   # On Windows use `env\Scripts\activate`

Install the dependencies

bash

pip install -r requirements.txt

Set up environment variables for email settings

Create a .env file in the project root with the following content:

plaintext

EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password

Run the migrations

bash

python manage.py migrate

Create a superuser

bash

python manage.py createsuperuser

Run the development server

bash

    python manage.py runserver

Frontend Setup

    Navigate to the frontend directory

    bash

cd frontend

Install the dependencies

bash

npm install

Start the development server

bash

    npm start

Running the Entire Project

Run the backend and frontend servers as described above. The frontend will be available at http://localhost:3000 and the backend at http://localhost:8000.
Running Tests

    Navigate to the project root

    bash

cd wins-forum

Run the tests

bash

    python manage.py test

Contributing

    Fork the repository.
    Create a new branch: git checkout -b feature-name.
    Make your changes and commit them: git commit -m 'Add some feature'.
    Push to the branch: git push origin feature-name.
    Submit a pull request.

License

This project is licensed under the MIT License - see the LICENSE file for details.
