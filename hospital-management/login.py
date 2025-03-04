from flask import Blueprint, request, redirect, url_for, session
from db import init_db

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    password = request.form['password']
    user_type = request.form['user_type']

    conn = init_db()
    cur = conn.cursor()

    # Check credentials based on user type
    if user_type == 'admin':
        cur.execute("SELECT * FROM Admin WHERE AdminID = %s AND Password = %s;", (user_id, password))
    else:
        # Assuming other user types have similar structures
        table_name = user_type.capitalize()  # e.g., 'Patient', 'Doctor', etc.
        cur.execute(f"SELECT * FROM {table_name} WHERE UserID = %s AND Password = %s;", (user_id, password))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        session['user_id'] = user_id
        session['user_type'] = user_type
        # Redirect to the appropriate dashboard
        return redirect(url_for(f'{user_type}.dashboard'))  # This assumes you have defined routes for each user type

    return "Invalid credentials", 401  # Handle failed login attempt
