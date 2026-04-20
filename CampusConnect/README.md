# CampusConnect

## Backend setup (Django)

1. Create and activate a virtual environment (PowerShell):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

- Copy `env.example` to `.env` at project root
- Edit `.env` values (secret key, email creds, allowed hosts)

4. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

6. Static and media:

- Media uploads are stored in `media/`
- For production, collect static files with:

```bash
python manage.py collectstatic
```

## API Endpoints (prefix: `/api/`)

- Auth & Profile
  - POST `auth/signup/` – create account
  - POST `auth/login/` – JWT obtain (username, password)
  - POST `auth/refresh/` – refresh token
  - POST `auth/logout/` – client-side token discard
  - GET/PUT/PATCH `me/profile/` – view/update profile

- Products
  - GET `categories/` – list categories
  - GET/POST `products/` – list/create products
  - GET/PUT/PATCH/DELETE `products/{id}/` – retrieve/update/delete
  - Filtering examples: `products/?category__slug=electronics&search=book&ordering=-price`

- Chat (HTTP)
  - GET/POST `conversations/`
  - GET/POST `conversations/{conversation_id}/messages/`

- Chat (WebSocket)
  - `ws://localhost:8000/ws/chat/{conversation_id}/`
