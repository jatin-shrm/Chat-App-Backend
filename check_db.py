from flaskr import create_app, db
from flaskr.models import User

app = create_app()

with app.app_context():
    # Check if user table exists by trying to query it
    try:
        # Try to get all users (should work even if table is empty)
        users = User.query.all()
        print(f"✓ Database connection successful!")
        print(f"✓ 'user' table exists!")
        print(f"✓ Current number of users: {len(users)}")
        
        # Also check table name directly
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Tables in database: {tables}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("The table might not exist or there's a connection issue.")

