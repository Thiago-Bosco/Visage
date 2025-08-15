from app import app, init_database

# Initialize database when running on Vercel
try:
    init_database()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

# For Vercel
application = app

if __name__ == '__main__':
    # Initialize database for local development
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
