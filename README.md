# QuizArenaDjango

QuizArenaDjango is a web-based platform for creating, taking, and managing quizzes, as well as accessing a learning hub with curated resources. Built with Django, it supports user registration, staff/admin dashboards, and a variety of quiz and learning features.

## Features
- User registration, login, and profile management (with avatars)
- Take quizzes and track your results and statistics
- Staff/admin dashboard for quiz and user management
- Create, edit, and delete quizzes (staff only)
- Learning Hub: Browse topics and resources (articles, videos, code, exercises)
- Submit and manage resources (staff only)
- Contact, feedback, and support forms
- Leaderboard, statistics, and FAQ sections

## Project Structure
```
quiz_project/
├── quiz_app/         # Main quiz logic, user profiles, results
├── learning_hub/     # Topics and resources for learning
├── quiz_project/     # Django project settings and URLs
├── manage.py         # Django management script
├── db.sqlite3        # SQLite database (default)
└── staticfiles/      # Static files (CSS, JS, images)
```

## Installation
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd QuizArenaDjango/quiz_project
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv my-env
   source my-env/bin/activate  # On Windows: my-env\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install django
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the app:**
   - Main site: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Usage
- Register as a user to take quizzes and view your profile/statistics.
- Staff/admin users can create and manage quizzes and resources.
- Browse the Learning Hub for curated topics and resources.
- Use the contact and feedback forms for support or suggestions.

## Key Models
- **UserProfile:** Extends Django User with avatar, stats
- **Quiz, Question, QuizResult:** Core quiz logic and results
- **Topic, Resource:** Learning hub content

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.
