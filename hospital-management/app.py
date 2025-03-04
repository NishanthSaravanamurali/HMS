from flask import Flask, render_template, request, redirect, url_for,session
from db import init_db

app = Flask(__name__)
app.secret_key = b'\x86\xe2}\x9a\x12\x86\xaa\xa4\r^\xc31o\x06\xb4\x0e\x0e\x7f\xdd\x06\x12b\xect'

# Initialize the database connection
init_db()

# Import routes for different roles
from patient_routes import patient_blueprint
from admin_routes import admin_blueprint
from doctor_routes import doctor_blueprint

# Register the blueprints
app.register_blueprint(patient_blueprint, url_prefix='/patient')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(doctor_blueprint, url_prefix='/doctor')

# Route for home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = init_db()
        cur = conn.cursor()

        # Check the password based on the user type
        if user_type == 'admin':
            cur.execute("SELECT Password FROM Admin WHERE AdminID = %s", (user_id,))
        elif user_type == 'patient':
            cur.execute("SELECT Password FROM Patient WHERE PatientID = %s", (user_id,))
        elif user_type == 'doctor':
            cur.execute("SELECT Password FROM Doctor WHERE DoctorID = %s", (user_id,))
        elif user_type == 'nurse':
            cur.execute("SELECT Password FROM Nurse WHERE NurseID = %s", (user_id,))
        elif user_type == 'staff':
            cur.execute("SELECT Password FROM Staff WHERE StaffID = %s", (user_id,))
        else:
            return redirect(url_for('home'))

        user = cur.fetchone()
        cur.close()
        conn.close()

        # Verify password and redirect to the appropriate dashboard
        if user and user[0] == password:
            print(user_id)
            session['user_id'] = user_id
            session['user_type'] = user_type

            if user_type == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user_type == 'patient':
                return redirect(url_for('patient.patient_dashboard'))
            elif user_type == 'doctor':
                return redirect(url_for('doctor.doctor_dashboard'))
            elif user_type == 'nurse':
                return redirect(url_for('nurse.nurse_dashboard'))
            elif user_type == 'staff':
                return redirect(url_for('staff.staff_dashboard'))
        else:
            return 'Login failed. Please try again.'

    return render_template('home.html')

# Route for patient registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']  # Capture Age
        gender = request.form['gender']  # Capture Gender
        address = request.form['address']  # Capture Address
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Generate PatientID automatically
        conn = init_db()
        cur = conn.cursor()

        # Get the last patient ID and generate the new one
        cur.execute("SELECT PatientID FROM Patient ORDER BY PatientID DESC LIMIT 1;")
        last_id = cur.fetchone()

        if last_id:
            last_num = int(last_id[0].split('_')[1])  # Extract numeric part from last PatientID
            new_patient_id = f"PAT_{last_num + 1:03}"  # Increment and format new PatientID
        else:
            new_patient_id = "PAT_001"  # First PatientID if no records exist

        # Insert new patient data into the database with auto-generated PatientID
        cur.execute("""
            INSERT INTO Patient (PatientID, Name, Age, Gender, Address, Email, PhoneNo, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (new_patient_id, name, age, gender, address, email, phone, password))

        conn.commit()
        cur.close()
        conn.close()

        # Redirect to the success page and display the generated PatientID
        return render_template('registration_success.html', patient_id=new_patient_id)

    return render_template('register.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

