# Quick Reference Guide - Flask Backend

This is a cheat sheet for daily Flask development tasks.

## 🚀 Daily Commands

### Start Development Server
```bash
python run.py
# OR
flask run
```

### Database Migrations
```bash
# Create migration after changing models.py
flask db migrate -m "Description of changes"

# Apply migrations to database
flask db upgrade

# Rollback last migration
flask db downgrade

# Check migration status
flask db current
```

### Check Database Connection
```bash
python check_db.py
```

---

## 📝 Common Code Patterns

### Adding a New Route

In `flaskr/routes.py`:
```python
@bp.route('/your-endpoint', methods=['GET', 'POST'])
def your_function():
    if request.method == 'GET':
        # Handle GET request
        return jsonify({"data": "something"})
    
    if request.method == 'POST':
        # Handle POST request
        data = request.get_json()
        return jsonify({"message": "created"}), 201
```

### Adding a New Model

In `flaskr/models.py`:
```python
class YourModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<YourModel {self.name}>"
```

Then:
```bash
flask db migrate -m "Add YourModel"
flask db upgrade
```

### Database CRUD Operations

```python
from flaskr.models import YourModel
from flaskr import db

# CREATE
item = YourModel(name="Example")
db.session.add(item)
db.session.commit()

# READ
item = YourModel.query.get(1)
all_items = YourModel.query.all()
filtered = YourModel.query.filter_by(name="Example").first()

# UPDATE
item.name = "New Name"
db.session.commit()

# DELETE
db.session.delete(item)
db.session.commit()
```

### Request/Response Patterns

```python
from flask import request, jsonify

# Get JSON data from POST request
data = request.get_json()
username = data.get('username')

# Get query parameters from GET request
page = request.args.get('page', 1, type=int)

# Return JSON response
return jsonify({"message": "Success", "data": result}), 200

# Return error
return jsonify({"error": "Not found"}), 404
```

### Relationships Between Models

```python
# One-to-Many: User has many Posts
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Usage:
user = User.query.get(1)
user_posts = user.posts  # Get all posts by this user

post = Post.query.get(1)
post_author = post.author  # Get author of this post
```

---

## 📁 File Structure Quick Guide

| File | Purpose | Edit When? |
|------|---------|------------|
| `flaskr/__init__.py` | App factory, configuration | Adding new blueprints, config changes |
| `flaskr/models.py` | Database models/tables | Creating new tables or columns |
| `flaskr/routes.py` | API endpoints | Adding new routes/endpoints |
| `run.py` | Entry point | Rarely (only for server config) |
| `.env` | Environment variables | Adding secrets, database URLs |
| `requirements.txt` | Dependencies | Installing new packages |

---

## 🔄 Workflow for Adding Features

### 1. Add a New Model
```python
# flaskr/models.py
class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
```
```bash
flask db migrate -m "Add NewModel"
flask db upgrade
```

### 2. Add Routes for the Model
```python
# flaskr/routes.py
@bp.route('/newmodel', methods=['GET'])
def get_newmodel():
    items = NewModel.query.all()
    return jsonify([{"id": i.id, "name": i.name} for i in items])
```

### 3. Test It
```bash
python run.py
# Visit http://localhost:5000/newmodel
```

---

## 🐛 Quick Fixes

### Database Connection Error
1. Check `.env` file exists
2. Verify `DATABASE_URL` is correct
3. Ensure PostgreSQL is running
4. Run `python check_db.py`

### Migration Error
```bash
# If migration fails, check what's different
flask db current
flask db history

# Reset (WARNING: deletes data!)
flask db downgrade -1  # Go back one migration
flask db upgrade       # Apply again
```

### Import Errors
```bash
# Make sure you're in project root
cd /home/jatin/Desktop/Jatin/Backend

# Make sure virtual environment is activated
source venv/bin/activate
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📦 Installing New Packages

```bash
# Install package
pip install package-name

# Add to requirements.txt
pip freeze > requirements.txt

# Or manually add to requirements.txt:
# package-name==1.0.0
```

---

## 🧪 Testing Your API

### Using curl
```bash
# GET request
curl http://localhost:5000/

# POST request
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com"}'
```

### Using Python requests
```python
import requests

# GET
response = requests.get('http://localhost:5000/')
print(response.json())

# POST
response = requests.post('http://localhost:5000/users', 
    json={'username': 'test', 'email': 'test@example.com'})
print(response.json())
```

---

## 💡 Pro Tips

1. **Always commit before migrations** - Migrations are code changes
2. **Use descriptive migration messages** - `flask db migrate -m "Add user profile picture"`
3. **Test locally before deploying** - `python check_db.py` is your friend
4. **Keep `.env` out of git** - Add to `.gitignore`
5. **Use app context** - When running scripts, wrap in `with app.app_context():`

---

Save this file and keep it handy! 📌

