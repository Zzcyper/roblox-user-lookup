# RoLookup — Roblox User Lookup Web App

A modern Flask web application for looking up any Roblox user's public profile.  
Built with Python, Flask, Bootstrap 5, and the public Roblox API.

> **Not affiliated with Roblox Corporation.**

---

## Features

| Feature | Details |
|---|---|
| **Profile Search** | Look up any Roblox user by username |
| **Avatar Display** | Headshot + full-body avatar with toggle |
| **User Details** | Username, display name, user ID, verified badge, ban status |
| **Social Stats** | Friends, followers, and following counts |
| **Account Age** | Join date, age in years/months/days, visual progress bar |
| **Group Memberships** | All groups with icons and your role in each |
| **Created Games** | Games made by the player with thumbnails & visit counts |
| **Roblox Badges** | Official Roblox account badges |
| **Recent Searches** | localStorage-based history with quick re-access |
| **JSON API** | Programmatic access via `/api/user/<username>` |
| **Share Profile** | Web Share API with clipboard fallback |
| **Responsive UI** | Mobile-first Bootstrap 5 dark theme |

---

## Screenshots

> Coming soon — run locally to see the UI.

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/roblox-user-lookup.git
cd roblox-user-lookup

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-…` | Flask session secret — **change in production** |
| `FLASK_DEBUG` | `true` | Set to `false` in production |

Create a `.env` file (never commit it):
```
SECRET_KEY=your-super-secret-key
FLASK_DEBUG=false
```

---

## API

### `GET /api/user/<username>`

Returns a JSON object with the user's public profile data.

**Example:**
```
GET /api/user/Roblox
```

**Response:**
```json
{
  "id": 1,
  "username": "Roblox",
  "displayName": "Roblox",
  "description": "...",
  "created": "2006-02-27T21:06:40.3Z",
  "isBanned": false,
  "hasVerifiedBadge": true,
  "avatar": "https://tr.rbxcdn.com/...",
  "friends": 73,
  "followers": 9200000,
  "following": 0,
  "groupCount": 3,
  "profileUrl": "https://www.roblox.com/users/1/profile"
}
```

---

## Deployment

### Render / Railway / Heroku

The `Procfile` is included for one-click deployment:
```
web: gunicorn app:app
```

Set `SECRET_KEY` and `FLASK_DEBUG=false` as environment variables on your platform.

---

## Tech Stack

- **Backend:** Python 3, Flask
- **HTTP Client:** Requests
- **Frontend:** Bootstrap 5, Font Awesome 6, Vanilla JS
- **Fonts:** Inter (Google Fonts)
- **Data Source:** [Roblox Public APIs](https://create.roblox.com/docs/cloud/open-cloud/overview)

---

## Project Structure

```
roblox-user-lookup/
├── app.py                  # Flask application & Roblox API helpers
├── requirements.txt
├── Procfile                # Gunicorn entry point (deploy)
├── .gitignore
├── templates/
│   ├── base.html           # Shared layout (navbar, footer)
│   ├── index.html          # Home / search page
│   └── profile.html        # User profile page
└── static/
    ├── css/
    │   └── style.css       # Custom dark theme
    └── js/
        └── main.js         # Recent searches, clipboard, toast, etc.
```

---

## License

MIT — feel free to use this project in your own portfolio.
