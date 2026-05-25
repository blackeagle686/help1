# Basma Qena Project Summary

This document provides a summary of the directory structure and file contents of the **Basma Qena** portal.

---

## 📂 Root Directory Files

*   **`manage.py`**: Django's administrative command-line utility. Used to run the development server, apply migrations, create custom users, and execute management commands.
*   **`requirements.txt`**: Lists Python dependency packages required to run the application.
*   **`db.sqlite3`**: Local SQLite database storing system data, user profiles, projects, services, chats, and nominations.
*   **`deploy_basma.sh`**: A shell deployment script used to automate pulling code updates, running migrations, collecting static files, and reloading the application services.
*   **`start_ngrok.py`**: A helper Python utility that automates starting and managing ngrok tunnels for external access to the local development environment.
*   **`index.html`**: A standalone static template/mockup document.
*   **`logo.png`**: The main logo graphic of the Basma Qena platform.
*   **`LICENSE`**: The open-source or proprietary license definition file.
*   **`.gitignore`**: Defines folders and files (like `venv/`, `media/`, `staticfiles/`, `db.sqlite3`, and IDE configs) that should not be tracked by Git.

---

## 📁 `config/`
The core Django project configuration folder.

*   **`settings.py`**: The global settings file for the Django project. Configures databases, templates, installed applications, middlewares, static asset paths, media uploads, and security settings.
*   **`urls.py`**: Root routing module that maps incoming HTTP requests to their respective applications (such as `/admin/` and the main `/` portal routes).
*   **`wsgi.py` / `asgi.py`**: Web server entry points. `wsgi.py` is for traditional synchronous servers (like Gunicorn), and `asgi.py` is for asynchronous configurations.
*   **`__init__.py`**: Marks this folder as a Python package.

---

## 📁 `portal/`
The primary Django application containing the portal database models, business logic, URL routes, and test suites.

*   **`models.py`**: Definess the application data layer schemas using Django's ORM:
    *   `UserProfile`: Stores user metadata and credentials for administrators, innovators, and investors.
    *   `Project` & `Initiative`: Information fields about submitted innovations and community initiatives.
    *   `StoryMaker`: Data on success stories and impact makers.
    *   `Podcast`: Podcast episodes with support for video embeds, audio URLs, and audio file uploads.
    *   `Service`: Support services provided by administration or partners.
    *   `Investor`: Registered investment partners looking to support projects.
    *   `Nomination`: Submissions for new projects/initiatives/innovators to be reviewed by admins.
    *   `ChatMessage`: Standard messaging database schema for internal portal communications.
*   **`views.py`**: Implements the controller/logic layer of the application. Handles dashboard rendering, chat rooms, expressions of interest, analytics page tracking, authentication flows, and public page routing.
*   **`urls.py`**: Maps specific web page endpoints (like public listings, detail views, and API calls) to their respective functions in `views.py`.
*   **`admin.py`**: Configures how the database models are displayed, searched, and managed in Django's built-in administration dashboard (`/admin`).
*   **`tests.py`**: Contains test scripts verifying views, message routing, search criteria, permissions, and model integrations.
*   **`templatetags/portal_extras.py`**: Defines custom Django template filters used in HTML rendering:
    *   `embed_video`: Converts YouTube/Google Drive URLs to clean embed URLs.
    *   `embed_audio`: Converts Google Drive audio URLs to direct streamable links.
    *   `card_image`: Fallback logic to retrieve main cover images, gallery items, video thumbnails, or category placeholders.
*   **`management/commands/seed_data.py`**: A custom management command (`python3 manage.py seed_data`) that populates the database with initial sample and mock records for development and testing.

---

## 📁 `static/`
Contains public-facing static assets.

*   **`css/style.css`**: The main stylesheet for the application. Defines the global design system, color themes (e.g., brand primary, accent colors), typography, spacing, responsive design media queries, layouts, and animations.
*   **`images/logo.png`**: The primary logo asset.
*   **`js/`**: Directory designated for front-end JavaScript scripts.

---

## 📁 `templates/portal/`
Django HTML templates rendered using context data from views.

### 🏠 Main Pages
*   **`base.html`**: The parent layout template. Includes meta tags, common navigation bar, footer, font imports (Amiri/Outfit), FontAwesome, and standard style inclusions.
*   **`home.html`**: The platform landing page, showcasing highlighted projects, success metrics, recent announcements, and navigation options.
*   **`about.html`**: Static content explaining the vision and objectives of the Basma Qena platform.
*   **`nominate.html`**: The nomination page for users to pitch new innovators, projects, or initiatives.

### 📋 Listing Catalog Pages
*   **`projects_list.html`**: Catalog displaying projects and community initiatives with categories and query filtering.
*   **`story_list.html`**: Grid view of success stories and impact makers.
*   **`podcast_list.html`**: Directory of podcast episodes.
*   **`service_list.html`**: Directory of support services.
*   **`investor_list.html`**: Catalog of active investment partners.

### 🔍 Detail Pages
*   **`project_detail.html`**: Individual page for a project (details, team roster, update logs, and administration communication buttons).
*   **`initiative_detail.html`**: Detail page for an initiative.
*   **`story_detail.html`**: Details, biography, achievements, and partner information for an impact maker.
*   **`podcast_detail.html`**: Renders podcast episode media players (audio player and embed video frame).
*   **`service_detail.html`**: Explains individual services and provides inquiry channels.
*   **`investor_detail.html`**: Showcases an investor's background, allowing registered innovators to express interest or initiate messages.

### 📊 Dashboards & Admin Pages
*   **`admin_dashboard.html`**: Central control panel for administrators to review nominations, manage users, and view statistics.
*   **`admin_nomination_detail.html`**: Interface for review and approval workflow of submitted nominations.
*   **`innovator_dashboard.html`**: Custom panel for innovators to manage their submissions and view chat threads.
*   **`investor_dashboard.html`**: custom panel for investors.
