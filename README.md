# 💙 Serene — Mental Health Anonymous Support Platform

A full-stack web application where anyone can seek mental health support **anonymously** — no email, no name, no judgment.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                        NGINX (Port 80)                   │
│              Reverse Proxy — Routes all traffic          │
└────────┬──────────────────────────┬────────────────────┘
         │ /api/* + /ws/*           │ /*
         ▼                          ▼
┌─────────────────┐      ┌─────────────────────┐
│  Django + Daphne│      │    React Frontend    │
│    (Port 8000)  │      │     (Port 3000)      │
│                 │      └─────────────────────┘
│  ┌───────────┐  │
│  │  REST API │  │      ┌─────────────────────┐
│  │ (DRF)     │  │◄────►│     MySQL (3306)     │
│  └───────────┘  │      │  Tables:             │
│  ┌───────────┐  │      │  - anonymous_users   │
│  │ WebSocket │  │      │  - chat_rooms        │
│  │ (Channels)│  │      │  - messages          │
│  └───────────┘  │      │  - mood_entries      │
└────────┬────────┘      │  - emergency_logs    │
         │               └─────────────────────┘
         ▼
┌─────────────────┐      ┌─────────────────────┐
│   Redis (6379)  │      │    OpenAI API        │
│ WebSocket Layer │      │  GPT-4o-mini         │
└─────────────────┘      └─────────────────────┘
```

---

## 📁 Project Structure

```
mental-health-platform/
├── docker-compose.yml              # Orchestrates all services
├── nginx/
│   └── nginx.conf                  # Reverse proxy config
├── mysql/
│   └── init.sql                    # DB initialization
│
├── backend/                        # Django project
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── .env.example                # ← Copy to .env and fill in
│   ├── mental_health_project/
│   │   ├── settings.py             # All Django config
│   │   ├── urls.py                 # Root URL routing
│   │   └── asgi.py                 # ASGI for WebSocket support
│   └── apps/
│       ├── users/                  # Anonymous auth (UUID + JWT)
│       │   ├── models.py           # AnonymousUser model
│       │   ├── views.py            # register, login, me
│       │   ├── serializers.py
│       │   └── urls.py
│       ├── chat/                   # Real-time chat
│       │   ├── models.py           # ChatRoom, Message
│       │   ├── consumers.py        # WebSocket handler
│       │   ├── routing.py          # WebSocket URL patterns
│       │   ├── views.py            # REST API for rooms
│       │   └── urls.py
│       ├── mood/                   # Mood tracking
│       │   ├── models.py           # MoodEntry
│       │   ├── views.py            # log, history, stats
│       │   └── urls.py
│       ├── emergency/              # Crisis detection
│       │   ├── models.py           # EmergencyLog
│       │   ├── utils.py            # Keyword detection logic
│       │   ├── views.py            # check, resources, logs
│       │   └── urls.py
│       └── chatbot/                # AI integration
│           ├── views.py            # OpenAI API call
│           └── urls.py
│
└── frontend/                       # React application
    ├── Dockerfile
    ├── package.json
    ├── .env
    └── src/
        ├── App.js                  # Router + protected routes
        ├── index.js
        ├── index.css               # Global styles + CSS variables
        ├── context/
        │   └── AuthContext.js      # Global auth state
        ├── hooks/
        │   └── useWebSocket.js     # WebSocket management hook
        ├── services/
        │   └── api.js              # All API calls (axios)
        ├── pages/
        │   ├── LandingPage.js      # Login/register
        │   ├── Dashboard.js        # Home after login
        │   ├── ChatPage.js         # AI chat interface
        │   ├── MoodPage.js         # Mood tracker + chart
        │   └── EmergencyPage.js    # Crisis resources
        └── components/
            ├── layout/AppLayout.js # Sidebar navigation
            └── emergency/EmergencyBanner.js
```

---

## 🚀 Quick Start — Docker (Recommended)

### Step 1: Clone and Configure

```bash
git clone <your-repo-url>
cd mental-health-platform

# Configure backend environment
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
DB_NAME=mental_health_db
DB_USER=mental_health_user
DB_PASSWORD=your-strong-password
DB_HOST=db
REDIS_HOST=redis
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Step 2: Start All Services

```bash
docker-compose up --build
```

This will:
1. Start MySQL and wait for it to be healthy
2. Start Redis
3. Run Django migrations automatically
4. Start the Django backend (Daphne ASGI)
5. Start the React frontend
6. Start Nginx reverse proxy

### Step 3: Access the App

| Service        | URL                          |
|----------------|------------------------------|
| App (via Nginx) | http://localhost              |
| React Dev      | http://localhost:3000         |
| Django API     | http://localhost:8000/api/    |
| Django Admin   | http://localhost:8000/admin/  |

### Step 4: Create Admin User (Optional)

```bash
docker-compose exec backend python manage.py createsuperuser \
  --username admin --noinput
# Then set password manually:
docker-compose exec backend python manage.py shell -c \
  "from apps.users.models import AnonymousUser; u=AnonymousUser.objects.get(username='admin'); u.set_password('admin123'); u.save()"
```

---

## 🛠️ Local Development (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your local MySQL credentials
# Set DB_HOST=localhost, REDIS_HOST=localhost

# Run migrations
python manage.py makemigrations users chat mood emergency chatbot
python manage.py migrate

# Start development server (HTTP only, no WebSocket)
python manage.py runserver

# For WebSocket support, use Daphne:
daphne -b 0.0.0.0 -p 8000 mental_health_project.asgi:application
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
# React runs on http://localhost:3000
```

### Local Services Needed

```bash
# MySQL
mysql -u root -p
CREATE DATABASE mental_health_db CHARACTER SET utf8mb4;
CREATE USER 'mental_health_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL ON mental_health_db.* TO 'mental_health_user'@'localhost';

# Redis (Mac)
brew install redis && brew services start redis

# Redis (Ubuntu)
sudo apt install redis-server && sudo systemctl start redis
```

---

## 🔌 API Reference

### Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

#### POST `/api/auth/register/`
Create anonymous session. No body required.

**Response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "eyJ0eXAiOiJKV1Q...",
  "message": "Anonymous session created. Save your user_id to return!"
}
```

#### POST `/api/auth/login/`
Return to existing session with UUID.

**Body:**
```json
{ "user_id": "550e8400-e29b-41d4-a716-446655440000" }
```

#### POST `/api/auth/token/refresh/`
Get new access token.

**Body:**
```json
{ "refresh": "eyJ0eXAiOiJKV1Q..." }
```

---

### Chatbot AI

#### POST `/api/chatbot/message/`
Send message to AI assistant.

**Body:**
```json
{
  "message": "I've been feeling really anxious lately",
  "room_id": "uuid",
  "conversation_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How are you?"}
  ]
}
```

**Response:**
```json
{
  "response": "I hear you, and I want you to know...",
  "is_emergency": false,
  "room_id": "uuid",
  "user_message_id": "uuid",
  "ai_message_id": "uuid"
}
```

---

### Mood Tracking

#### POST `/api/mood/log/`
Log or update today's mood.

**Body:**
```json
{
  "mood": "anxious",
  "note": "Big presentation tomorrow"
}
```

**Valid moods:** `happy`, `calm`, `hopeful`, `numb`, `anxious`, `sad`, `angry`, `overwhelmed`

#### GET `/api/mood/stats/weekly/`
```json
{
  "period": "weekly",
  "entries": [...],
  "average_score": 3.5,
  "most_common_mood": "calm",
  "mood_distribution": {"happy": 3, "calm": 2, "anxious": 2},
  "total_entries": 7
}
```

---

### Emergency

#### POST `/api/emergency/check/`
Check text for crisis keywords.

**Body:**
```json
{ "text": "I feel hopeless", "source": "mood_note" }
```

**Response (emergency):**
```json
{
  "is_emergency": true,
  "severity": "high",
  "keywords_found": ["hopeless"],
  "resources": [
    {
      "name": "iCall (India)",
      "number": "9152987821",
      "available": "Mon-Sat, 8am-10pm IST"
    }
  ]
}
```

---

### WebSocket

Connect: `ws://localhost:8000/ws/chat/<room_id>/?token=<jwt_access_token>`

**Send message:**
```json
{ "message": "Hello, I need to talk" }
```

**Receive (normal message):**
```json
{
  "type": "message",
  "message": "Hello, I need to talk",
  "sender_id": "uuid",
  "sender_type": "user",
  "message_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_emergency": false
}
```

**Receive (emergency alert):**
```json
{
  "type": "emergency",
  "message": "We noticed some concerning words...",
  "resources": [...],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🧪 Postman Testing Guide

### 1. Register (get tokens)
```
POST http://localhost:8000/api/auth/register/
Content-Type: application/json
(No body)
```
→ Save `access_token`, `refresh_token`, and `user_id` from response.

### 2. Set Auth Header
In Postman: Authorization tab → Bearer Token → paste `access_token`

### 3. Send AI Message
```
POST http://localhost:8000/api/chatbot/message/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "I've been feeling really anxious about work"
}
```

### 4. Log Mood
```
POST http://localhost:8000/api/mood/log/
Authorization: Bearer <token>

{ "mood": "anxious", "note": "Stressful day at work" }
```

### 5. Get Weekly Stats
```
GET http://localhost:8000/api/mood/stats/weekly/
Authorization: Bearer <token>
```

### 6. Check Emergency Keywords
```
POST http://localhost:8000/api/emergency/check/
Authorization: Bearer <token>

{ "text": "I feel so hopeless and can't go on" }
```

### 7. Test WebSocket (use Postman WebSocket or wscat)
```bash
# Install wscat
npm install -g wscat

# Connect (replace room_id and token)
wscat -c "ws://localhost:8000/ws/chat/ROOM-UUID/?token=YOUR-JWT-TOKEN"

# Send message
> {"message": "Hello, I need support"}
```

---

## 🔒 Security Notes

1. **Never commit `.env`** — add to `.gitignore`
2. **Change `SECRET_KEY`** in production — use `python -c "import secrets; print(secrets.token_hex(50))"`
3. **Set `DEBUG=False`** in production
4. **Use HTTPS** — configure SSL in Nginx for production
5. **Change MySQL passwords** — don't use defaults
6. **Rate limiting** — already configured in DRF settings (1000 req/day per user)
7. **CORS** — update `CORS_ALLOWED_ORIGINS` with your production domain

---

## ⚡ Performance for 10,000 Users

The platform is architected for scale:

| Concern | Solution |
|---------|----------|
| Database | MySQL with indexes on FKs and date fields |
| API | Pagination (20 items/page) on all list endpoints |
| WebSocket | Redis channel layer distributes across multiple servers |
| Static files | Nginx serves directly (bypasses Django) |
| Caching | Add Redis caching to stats endpoints with `@cache_page` |
| Scale-out | Add more Django workers behind Nginx load balancer |

**To scale further:**
```bash
# Run multiple Django workers
docker-compose up --scale backend=3
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `mysqlclient` install fails | Install `libmysqlclient-dev` (Ubuntu) or `mysql-connector-c` (Mac) |
| WebSocket `4001` error | JWT token missing in WS URL query string |
| `django.db.OperationalError` | MySQL not ready yet — wait 10s and retry |
| CORS error in browser | Add frontend origin to `CORS_ALLOWED_ORIGINS` in settings.py |
| OpenAI error | Check `OPENAI_API_KEY` in `.env` |
| Redis connection refused | Ensure Redis is running: `redis-cli ping` → `PONG` |

---

## 📝 Database Schema (MySQL)

```sql
-- Run: python manage.py migrate
-- This creates all tables automatically from models.

anonymous_users (
  id           CHAR(32) PRIMARY KEY,  -- UUID
  username     VARCHAR(50) NULL,
  created_at   DATETIME,
  last_active  DATETIME,
  is_active    TINYINT,
  is_staff     TINYINT
)

chat_rooms (
  id           CHAR(32) PRIMARY KEY,
  created_by   CHAR(32) FK→anonymous_users,
  name         VARCHAR(100),
  created_at   DATETIME,
  updated_at   DATETIME
)

messages (
  id           CHAR(32) PRIMARY KEY,
  room_id      CHAR(32) FK→chat_rooms,
  sender_id    CHAR(32) FK→anonymous_users NULL,
  sender_type  VARCHAR(10),  -- 'user'|'ai'|'system'
  message_text LONGTEXT,
  timestamp    DATETIME,
  is_flagged   TINYINT
)

mood_entries (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      CHAR(32) FK→anonymous_users,
  mood         VARCHAR(20),
  note         LONGTEXT NULL,
  date         DATE,
  UNIQUE KEY (user_id, date)  -- one entry per user per day
)

emergency_logs (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id       CHAR(32) FK→anonymous_users NULL,
  detected_text LONGTEXT,
  keywords_found JSON,
  severity      VARCHAR(10),
  source        VARCHAR(20),
  alert_triggered TINYINT,
  timestamp     DATETIME
)
```

---

## 🎯 What Each File Does (For Beginners)

| File | Role | Analogy |
|------|------|---------|
| `settings.py` | Django config | App's control panel |
| `models.py` | Database tables | Spreadsheet column definitions |
| `serializers.py` | JSON ↔ Python | Translator |
| `views.py` | API logic | Request handler |
| `urls.py` | URL routing | Receptionist |
| `consumers.py` | WebSocket handler | Live phone call handler |
| `routing.py` | WS URL routing | WebSocket receptionist |
| `AuthContext.js` | Global auth state | App's memory |
| `api.js` | API calls | Phone book |
| `useWebSocket.js` | WS connection | Live intercom |

---

*Built with ❤️ for mental health awareness. Remember: seeking help is strength.*
