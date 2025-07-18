# FastAPI Backend with MySQL

A modern FastAPI backend application with MySQL database integration, featuring environment-based configuration, database migrations, and a complete user management system.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🗄️ **MySQL** - Robust relational database with SQLAlchemy ORM
- 🔐 **Environment Variables** - Secure configuration management
- 📝 **Database Migrations** - Alembic for schema versioning
- 👥 **User Management** - Complete CRUD operations for users
- 🔒 **Password Hashing** - Secure password storage with bcrypt
- 📚 **Auto-generated Documentation** - Interactive API docs with Swagger UI
- 🛡️ **CORS Support** - Cross-origin resource sharing enabled
- ⚡ **Async Support** - High-performance async operations

## Project Structure

```
practice-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection and session
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py           # Main API router
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       └── users.py     # User endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User database model
│   └── schemas/
│       ├── __init__.py
│       └── user.py          # Pydantic schemas
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── run.py                  # Application runner
└── README.md
```

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd practice-fastapi
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your MySQL database credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=fastapi_db
   ```

5. **Create MySQL database**
   ```sql
   CREATE DATABASE fastapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Initialize database migrations**
   ```bash
   alembic init alembic  # Only if not already initialized
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

## Running the Application

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Users
- `GET /api/v1/users/` - Get all users (with pagination)
- `GET /api/v1/users/{user_id}` - Get specific user
- `POST /api/v1/users/` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### System
- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_USER` | MySQL username | root |
| `DB_PASSWORD` | MySQL password | (empty) |
| `DB_NAME` | MySQL database name | fastapi_db |
| `DATABASE_URL` | Complete database URL (alternative) | (auto-generated) |
| `APP_NAME` | Application name | FastAPI Backend |
| `DEBUG` | Debug mode | True |
| `SECRET_KEY` | Secret key for security | (change in production) |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

## Development

### Adding New Models

1. Create a new model file in `app/models/`
2. Import the model in `alembic/env.py`
3. Generate and apply migrations

### Adding New Endpoints

1. Create endpoint functions in `app/api/endpoints/`
2. Add router to `app/api/api.py`
3. Create corresponding schemas in `app/schemas/`

## Security Considerations

- Change the default `SECRET_KEY` in production
- Use strong passwords for database access
- Configure CORS origins properly for production
- Enable HTTPS in production
- Regularly update dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
