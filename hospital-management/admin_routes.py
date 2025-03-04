from flask import Blueprint, render_template, request, redirect,session,url_for,flash
from db import init_db

admin_blueprint = Blueprint('admin', __name__)

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Replace with your own authentication logic
        if username == "admin" and password == "password":  # Example static credentials
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid credentials! Please try again.')
            return redirect(url_for('admin.login'))

    return render_template('admin_login.html')

# Admin dashboard
@admin_blueprint.route('/dashboard', methods=['GET'])
def admin_dashboard():
    # Fetch the logged-in admin's details
    admin_id = session.get('user_id')
    
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Admin WHERE AdminID = %s;", (admin_id,))
    admin_details = cur.fetchone()
    cur.close()
    conn.close()
    print(admin_details)

    return render_template('admin_dashboard.html', admin=admin_details)

@admin_blueprint.route('/edit_admin/<string:admin_id>', methods=['GET', 'POST'])
def edit_admin(admin_id):
    if request.method == 'POST':
        admin_name = request.form['name']
        password = request.form['password']

        conn = init_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Admin
            SET name = %s, password = %s
            WHERE adminid = %s;
        """, (admin_name, password, admin_id))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('admin.admin_dashboard'))

    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Admin WHERE adminid = %s;", (admin_id,))
    admin = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('admin/edit_admin.html', admin=admin)

# Manage facilities route
@admin_blueprint.route('/manage_facilities', methods=['GET', 'POST'])
def manage_facilities():
    if request.method == 'POST':
        facility_name = request.form['facility_name']
        cost = request.form['cost']
        
        conn = init_db()
        cur = conn.cursor()

        # Generate new FacilityID
        cur.execute("SELECT FacilityID FROM Facility ORDER BY FacilityID DESC LIMIT 1;")
        last_id = cur.fetchone()
        if last_id:
            last_id_num = int(last_id[0].split('_')[1]) + 1
            new_id = f"FAC_{last_id_num:03d}"
        else:
            new_id = "FAC_001"
        
        cur.execute("""
            INSERT INTO Facility (FacilityID, FacilityName, Cost)
            VALUES (%s, %s, %s);
        """, (new_id, facility_name, cost))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin.manage_facilities'))

    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Facility;")
    facilities = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/manage_facilities.html', facilities=facilities)

# Update facility route
@admin_blueprint.route('/update_facility/<string:facility_id>', methods=['GET', 'POST'])
def update_facility(facility_id):
    if request.method == 'POST':
        facility_name = request.form['facility_name']
        cost = request.form['cost']

        conn = init_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Facility
            SET FacilityName = %s, Cost = %s
            WHERE FacilityID = %s;
        """, (facility_name, cost, facility_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin.manage_facilities'))

    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Facility WHERE FacilityID = %s;", (facility_id,))
    facility = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('admin/update_facility.html', facility=facility)

# Remove facility route
@admin_blueprint.route('/remove_facility/<string:facility_id>', methods=['POST'])
def remove_facility(facility_id):
    conn = init_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Facility WHERE FacilityID = %s;", (facility_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin.manage_facilities'))


# Manage doctors
@admin_blueprint.route('/manage_doctors', methods=['GET', 'POST'])
def manage_doctors():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        role = request.form['role']
        department_id = request.form['department_id']
        password = request.form['password']
        
        conn = init_db()
        cur = conn.cursor()

        # Generate new DoctorID
        cur.execute("SELECT DoctorID FROM Doctor ORDER BY DoctorID DESC LIMIT 1;")
        last_id = cur.fetchone()
        if last_id:
            last_id_num = int(last_id[0].split('_')[1]) + 1
            new_id = f"DOC_{last_id_num:03d}"
        else:
            new_id = "DOC_001"
        
        cur.execute("""
            INSERT INTO Doctor (DoctorID, Name, Specialization, Phone, Role, DepartmentID, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (new_id, name, specialization, phone, role, department_id, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin.manage_doctors'))

    conn = init_db()
    cur = conn.cursor()

    # Fetch doctors
    cur.execute("SELECT * FROM Doctor;")
    doctors = cur.fetchall()

    # Fetch departments for dropdown
    cur.execute("SELECT DepartmentID, DepartmentName FROM Department;")
    departments = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('admin/manage_doctors.html', doctors=doctors, departments=departments)

@admin_blueprint.route('/update_doctor/<string:doctor_id>', methods=['GET', 'POST'])
def update_doctor(doctor_id):
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        role = request.form['role']
        department_id = request.form['department_id']
        password = request.form['password']

        conn = init_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Doctor
            SET Name = %s, Specialization = %s, Phone = %s, Role = %s, DepartmentID = %s, Password = %s
            WHERE DoctorID = %s;
        """, (name, specialization, phone, role, department_id, password, doctor_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin.manage_doctors'))

    conn = init_db()
    cur = conn.cursor()

    # Fetch the doctor data
    cur.execute("SELECT * FROM Doctor WHERE DoctorID = %s;", (doctor_id,))
    doctor = cur.fetchone()

    # Fetch departments for dropdown
    cur.execute("SELECT DepartmentID, DepartmentName FROM Department;")
    departments = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('admin/update_doctor.html', doctor=doctor, departments=departments)

@admin_blueprint.route('/remove_doctor/<string:doctor_id>', methods=['POST'])
def remove_doctor(doctor_id):
    conn = init_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM Doctor WHERE DoctorID = %s;", (doctor_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin.manage_doctors'))


# Manage Nurses (View all, Add)
@admin_blueprint.route('/manage_nurses', methods=['GET', 'POST'])
def manage_nurses():
    conn = init_db()
    cur = conn.cursor()
    error = None

    # Fetch Department IDs for dropdown
    cur.execute("SELECT DepartmentID, DepartmentName FROM Department;")
    departments = cur.fetchall()

    if request.method == 'POST':
        nurse_name = request.form['name']
        role = request.form['role']
        shift = request.form['shift']
        department_id = request.form['department_id']
        password = request.form['password']

        # Validation
        if not nurse_name or not role or not shift or not department_id or not password:
            error = "All fields are required."
        else:
            try:
                # Generate new NurseID (similar format)
                cur.execute("SELECT NurseID FROM Nurse ORDER BY NurseID DESC LIMIT 1;")
                last_id = cur.fetchone()
                if last_id:
                    last_id_num = int(last_id[0].split('_')[1]) + 1
                    new_id = f"NUR_{last_id_num:03d}"
                else:
                    new_id = "NUR_001"

                # Insert new nurse into the database
                cur.execute("""
                    INSERT INTO Nurse (NurseID, Name, Role, Shift, DepartmentID, Password)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (new_id, nurse_name, role, shift, department_id, password))
                conn.commit()

            except Exception as e:
                conn.rollback()
                error = f"Failed to add nurse: {str(e)}"

    # Fetch existing nurses to display
    cur.execute("SELECT * FROM Nurse;")
    nurses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/manage_nurses.html', nurses=nurses, departments=departments, error=error)

# Edit Nurse (Dropdown for department)
@admin_blueprint.route('/edit_nurse/<id>', methods=['GET', 'POST'])
def edit_nurse(id):
    conn = init_db()
    cur = conn.cursor()
    error = None

    # Fetch Department IDs for dropdown
    cur.execute("SELECT DepartmentID, DepartmentName FROM Department;")
    departments = cur.fetchall()

    if request.method == 'POST':
        nurse_name = request.form['name']
        role = request.form['role']
        shift = request.form['shift']
        department_id = request.form['department_id']
        password = request.form['password']

        if not nurse_name or not role or not shift or not department_id or not password:
            error = "All fields are required."
        else:
            try:
                # Update nurse details in the database
                cur.execute("""
                    UPDATE Nurse 
                    SET Name = %s, Role = %s, Shift = %s, DepartmentID = %s, Password = %s
                    WHERE NurseID = %s;
                """, (nurse_name, role, shift, department_id, password, id))
                conn.commit()

            except Exception as e:
                conn.rollback()
                error = f"Failed to update nurse: {str(e)}"

    # Fetch nurse data to pre-fill the form
    cur.execute("SELECT * FROM Nurse WHERE NurseID = %s;", (id,))
    nurse = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('admin/edit_nurse.html', nurse=nurse, departments=departments, error=error)

# Delete Nurse
@admin_blueprint.route('/delete_nurse/<id>', methods=['POST'])
def delete_nurse(id):
    conn = init_db()
    cur = conn.cursor()

    try:
        # Delete nurse from database
        cur.execute("DELETE FROM Nurse WHERE NurseID = %s;", (id,))
        conn.commit()

    except Exception as e:
        conn.rollback()
        error = f"Failed to delete nurse: {str(e)}"

    cur.close()
    conn.close()

    return redirect(url_for('admin.manage_nurses'))

# Manage Staff (View all, Add)
@admin_blueprint.route('/manage_staff', methods=['GET', 'POST'])
def manage_staff():
    conn = init_db()
    cur = conn.cursor()
    error = None

    # Fetch Department IDs for dropdown
    cur.execute("SELECT DepartmentID, DepartmentName FROM Department;")
    departments = cur.fetchall()

    if request.method == 'POST':
        staff_name = request.form['name']
        role = request.form['role']
        department_id = request.form['department_id']
        password = request.form['password']

        if not staff_name or not role or not department_id or not password:
            error = "All fields are required."
        else:
            try:
                # Generate new StaffID
                cur.execute("SELECT StaffID FROM Staff ORDER BY StaffID DESC LIMIT 1;")
                last_id = cur.fetchone()
                if last_id:
                    last_id_num = int(last_id[0].split('_')[1]) + 1
                    new_id = f"STA_{last_id_num:03d}"
                else:
                    new_id = "STA_001"

                cur.execute("""
                    INSERT INTO Staff (StaffID, Name, Role, DepartmentID, Password)
                    VALUES (%s, %s, %s, %s, %s);
                """, (new_id, staff_name, role, department_id, password))
                conn.commit()

            except Exception as e:
                conn.rollback()
                error = f"Failed to add staff: {str(e)}"

    # Fetch existing staff to display
    cur.execute("SELECT * FROM Staff;")
    staff = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/manage_staff.html', staff=staff, departments=departments, error=error)

# Edit Staff (Dropdown for department)
@admin_blueprint.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit_staff(id):
    conn = init_db()
    cur = conn.cursor()
    error = None

    # Fetch Department IDs for dropdown
    cur.execute("SELECT DepartmentID, DepartmentName FROM Department;")
    departments = cur.fetchall()

    if request.method == 'POST':
        staff_name = request.form['name']
        role = request.form['role']
        department_id = request.form['department_id']
        password = request.form['password']

        if not staff_name or not role or not department_id or not password:
            error = "All fields are required."
        else:
            try:
                cur.execute("""
                    UPDATE Staff 
                    SET Name = %s, Role = %s, DepartmentID = %s, Password = %s
                    WHERE StaffID = %s;
                """, (staff_name, role, department_id, password, id))
                conn.commit()

            except Exception as e:
                conn.rollback()
                error = f"Failed to update staff: {str(e)}"

    cur.execute("SELECT * FROM Staff WHERE StaffID = %s;", (id,))
    staff = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('admin/edit_staff.html', staff=staff, departments=departments, error=error)

# Delete Staff
@admin_blueprint.route('/delete_staff/<id>', methods=['POST'])
def delete_staff(id):
    conn = init_db()
    cur = conn.cursor()

    try:
        # Delete staff from database
        cur.execute("DELETE FROM Staff WHERE StaffID = %s;", (id,))
        conn.commit()

    except Exception as e:
        conn.rollback()
        error = f"Failed to delete staff: {str(e)}"

    cur.close()
    conn.close()

    return redirect(url_for('admin.manage_staff'))


# Manage departments
@admin_blueprint.route('/manage_departments', methods=['GET', 'POST'])
def manage_departments():
    conn = init_db()
    cur = conn.cursor()

    if request.method == 'POST':
        department_name = request.form['department_name']

        # Automatically generate DepartmentID (like DEP_001, DEP_002, ...)
        cur.execute("SELECT COUNT(*) FROM Department;")
        count = cur.fetchone()[0]
        department_id = f"DEP_{count + 1:03d}"

        cur.execute("""
            INSERT INTO Department (DepartmentID, DepartmentName)
            VALUES (%s, %s);
        """, (department_id, department_name))
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('admin.manage_departments'))

    # Fetch all departments
    cur.execute("SELECT * FROM Department;")
    departments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin/manage_departments.html', departments=departments)

# Update department
@admin_blueprint.route('/update_department/<department_id>', methods=['GET', 'POST'])
def update_department(department_id):
    conn = init_db()
    cur = conn.cursor()

    if request.method == 'POST':
        department_name = request.form['department_name']

        # Update department details
        cur.execute("""
            UPDATE Department
            SET DepartmentName = %s
            WHERE DepartmentID = %s;
        """, (department_name, department_id))
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('admin.manage_departments'))

    # Fetch department details for editing
    cur.execute("SELECT * FROM Department WHERE DepartmentID = %s;", (department_id,))
    department = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('admin/update_department.html', department=department)

# Remove department
@admin_blueprint.route('/remove_department/<department_id>', methods=['POST'])
def remove_department(department_id):
    conn = init_db()
    cur = conn.cursor()

    # Delete the department
    cur.execute("DELETE FROM Department WHERE DepartmentID = %s;", (department_id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('admin.manage_departments'))

# View all data (patients)
@admin_blueprint.route('/view_patients')
def view_patients():
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Patient;")
    patients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/view_data.html', patients=patients)

    
@admin_blueprint.route('/view_appointments', methods=['GET', 'POST'])
def view_appointments():
    conn = init_db()
    cur = conn.cursor()

    # Fetch all appointments
    cur.execute("""
        SELECT a.AppointmentID, a.Date, a.Time, a.Status, p.PatientID, p.Name as PatientName, d.DoctorID, d.Name as DoctorName, f.FacilityName
        FROM Appointment a
        JOIN Patient p ON a.PatientID = p.PatientID
        JOIN Doctor d ON a.DoctorID = d.DoctorID
        JOIN Facility f ON a.FacilityID = f.FacilityID
    """)
    appointments = cur.fetchall()

    if request.method == 'POST':
        # Update the status of an appointment
        appointment_id = request.form.get('appointment_id')
        new_status = request.form.get(f'status_{appointment_id}')
        cur.execute("""
            UPDATE Appointment
            SET Status = %s
            WHERE AppointmentID = %s
        """, (new_status, appointment_id))
        conn.commit()

    cur.close()
    conn.close()

    return render_template('admin/view_appointments.html', appointments=appointments)


@admin_blueprint.route('/view_lab_reports', methods=['GET', 'POST'])
def view_lab_reports():
    conn = init_db()
    cur = conn.cursor()

    # Fetch all lab reports
    cur.execute("""
        SELECT l.LabTestID, l.TestName, l.Result, l.Status, a.AppointmentID, p.PatientID, p.Name as PatientName
        FROM Lab l
        JOIN Appointment a ON l.AppointmentID = a.AppointmentID
        JOIN Patient p ON l.PatientID = p.PatientID
    """)
    lab_reports = cur.fetchall()

    if request.method == 'POST':
        # Update the result and status of a lab test
        lab_test_id = request.form.get('lab_test_id')
        new_result = request.form.get(f'result_{lab_test_id}')
        new_status = request.form.get(f'status_{lab_test_id}')
        cur.execute("""
            UPDATE Lab
            SET Result = %s, Status = %s
            WHERE LabTestID = %s
        """, (new_result, new_status, lab_test_id))
        conn.commit()

    cur.close()
    conn.close()

    return render_template('admin/view_lab_reports.html', lab_reports=lab_reports)


@admin_blueprint.route('/view_surgeries', methods=['GET', 'POST'])
def view_surgeries():
    conn = init_db()
    cur = conn.cursor()

    # Fetch all surgeries
    cur.execute("""
        SELECT s.SurgeryID, s.SurgeryName, s.Date, s.Status, p.PatientID, p.Name as PatientName, d.DoctorID, d.Name as DoctorName
        FROM Surgery s
        JOIN Patient p ON s.PatientID = p.PatientID
        JOIN Doctor d ON s.DoctorID = d.DoctorID
    """)
    surgeries = cur.fetchall()

    if request.method == 'POST':
        # Update surgery status
        surgery_id = request.form.get('surgery_id')
        new_status = request.form.get(f'status_{surgery_id}')
        cur.execute("""
            UPDATE Surgery
            SET Status = %s
            WHERE SurgeryID = %s
        """, (new_status, surgery_id))
        conn.commit()

    cur.close()
    conn.close()

    return render_template('admin/view_surgeries.html', surgeries=surgeries)


@admin_blueprint.route('/view_pharmacy', methods=['GET', 'POST'])
def view_pharmacy():
    conn = init_db()
    cur = conn.cursor()

    # Fetch all medicines in the pharmacy
    cur.execute("""
        SELECT MedicineID, MedicineName, Cost, Stock
        FROM Pharmacy
    """)
    medicines = cur.fetchall()

    if request.method == 'POST':
        # Update medicine stock or cost
        medicine_id = request.form.get('medicine_id')
        new_cost = request.form.get(f'cost_{medicine_id}')
        new_stock = request.form.get(f'stock_{medicine_id}')
        cur.execute("""
            UPDATE Pharmacy
            SET Cost = %s, Stock = %s
            WHERE MedicineID = %s
        """, (new_cost, new_stock, medicine_id))
        conn.commit()

    cur.close()
    conn.close()

    return render_template('admin/view_pharmacy.html', medicines=medicines)

@admin_blueprint.route('/view_all_bills', methods=['GET'])
def view_all_bills():
    conn = init_db()
    cur = conn.cursor()

    # Fetch all bills generated
    cur.execute("""
        SELECT B.BillID, B.Amount, B.DateIssued, B.Status, B.PatientID
        FROM Billing B
        
        ORDER BY B.DateIssued DESC
    """)
    bills = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/view_all_bills.html', bills=bills)

@admin_blueprint.route('/view_rooms', methods=['GET'])
def view_rooms():
    conn = init_db()
    cur = conn.cursor()

    # Fetch room data
    cur.execute("""
        SELECT R.RoomID, R.Type, R.Availability, R.Duration, R.PatientID, R.NurseID, F.FacilityName
        FROM Room R
        LEFT JOIN Facility F ON R.FacilityID = F.FacilityID
    """)
    rooms = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/view_rooms.html', rooms=rooms)
