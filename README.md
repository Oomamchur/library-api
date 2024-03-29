# Library Service API

API service for managing library with DRF. 
Implemented possibility of managing books.
Also you can borrow books and return them.

## Installation

Python 3 should be installed. Docker should be installed.

    git clone https://github.com/rakamakaphone/library-api
    cd library-api
    python -m venv venv
    source venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate    
    python manage.py runserver

This project uses environment variables to store sensitive information such as the Django secret key.
Create a `.env` file in the root directory of your project and add your environment variables to it.
This file should not be committed to the repository.
You can see the example in `.env.sample` file.

## Getting access
Use the following command to load prepared data from fixture to test and debug your code:

    python manage.py loaddata fixture_data.json

After loading data from fixture you can use user (or create another one by yourself):

    Login: admin@admin.com
    Password: pass1234

    create user via /api/user/register/
    get access token via /api/user/token/

## Features

1. Admin panel.
2. Creating user via email.
3. Managing own profile.
4. Managing books for admin users.
5. Filtering books by title and author.
6. Borrowing books with possibility to return them.
7. Non-admins can see only their borrowings.
8. Filtering active borrowings for all users.
9. Filtering by user_id for admin users.
10. Added different permissions for different actions.
11. Added validation for date and book inventory.
12. Added tests for different endpoints.
13. JWT authenticated.
14. Documentation located at /api/doc/swagger/

## Schema

![diag.jpg](diag.jpg)