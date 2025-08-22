# CS50W Project 4: Network

A social networking website, similar to Twitter, built with Django. This was created as a project for Harvard's CS50W course.

## Core Features

*   **User Authentication:** Register, log in, and log out.
*   **Create & View Posts:** Create new posts and view a paginated feed of all posts.
*   **User Profiles:** View user profiles with their posts and follower/following counts.
*   **Social Interactions:** Follow/unfollow users, and like/unlike posts.
*   **Edit Posts:** Users can edit their own posts.

## Tech Stack

*   **Backend:** Python, Django
*   **Frontend:** JavaScript, HTML, CSS
*   **Database:** SQLite

## Getting Started

1.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```
2.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
3.  Open your browser to `http://127.0.0.1:8000/`.
