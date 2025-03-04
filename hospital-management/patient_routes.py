from flask import Blueprint, render_template, request,session,redirect,url_for,jsonify
from db import init_db

patient_blueprint = Blueprint('patient', __name__)
@patient_blueprint.route('/patient_dashboard')
def patient_dashboard():
    # Assume that 'patient_id' is stored in the session after login
    patient_id = session.get('user_id')
    
    if not patient_id:
        return redirect(url_for('home'))  # Redirect to home if not logged in

    conn = init_db()
    cur = conn.cursor()

    # Fetch patient details from the database
    cur.execute("""
        SELECT PatientID, Name, Age, Gender, Address 
        FROM Patient 
        WHERE PatientID = %s;
    """, (patient_id,))
    patient = cur.fetchone()

    if not patient:
        cur.close()
        conn.close()
        return "Patient not found", 404

    # Fetch patient appointments
    cur.execute("""
        SELECT AppointmentID, Date, Time, Status, DoctorID, FacilityID 
        FROM Appointment 
        WHERE PatientID = %s;
    """, (patient_id,))
    appointments = cur.fetchall()

    print(appointments)  # Debug print to check if appointments data is fetched

    cur.close()
    conn.close()

    # Convert the appointments data to a list of dictionaries for easier rendering in the template
    appointments_data = [
        {
            'appointment_id': appt[0],
            'date': appt[1],
            'time': appt[2],
            'status': appt[3],
            'doctor_id': appt[4],
            'facility_id': appt[5]
        }
        for appt in appointments
    ]

    # Render the dashboard with patient details and scheduled appointments
    return render_template('patient_dashboard.html', patient={
        'patient_id': patient[0],
        'name': patient[1],
        'age': patient[2],
        'gender': patient[3],
        'address': patient[4]
    }, appointments=appointments_data)
    
@patient_blueprint.route('/cancel_appointment/<appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    conn = init_db()
    cur = conn.cursor()

    # Update the appointment status to 'Cancelled'
    cur.execute("""
        UPDATE Appointment 
        SET Status = 'Cancelled' 
        WHERE AppointmentID = %s;
    """, (appointment_id,))
    
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('patient.patient_dashboard'))


@patient_blueprint.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    patient_id = session.get('user_id')  # Assuming patient ID is stored in the session

    if request.method == 'POST':
        # Get form data from POST request
        date = request.form.get('appointment_date')
        time = request.form.get('appointment_time')
        doctor_id = request.form.get('doctor_id')
        facility_id = request.form.get('facility_id')

        # Check if the patient already has an appointment at the same time
        conn = init_db()
        cur = conn.cursor()

        # Check if the selected doctor is already booked for the given date and time
        cur.execute("""
            SELECT * FROM Appointment 
            WHERE Date = %s AND Time = %s AND DoctorID = %s
        """, (date, time, doctor_id))
        
        existing_appointment = cur.fetchone()

        if existing_appointment:
            # Handle case where the doctor is already booked
            cur.close()
            conn.close()
            return "The selected doctor is already booked at this time.", 400

        # Generate new AppointmentID based on the last entry
        cur.execute("SELECT AppointmentID FROM Appointment ORDER BY AppointmentID DESC LIMIT 1;")
        last_id = cur.fetchone()
        if last_id:
            last_id_num = int(last_id[0].split('_')[1]) + 1
            new_id = f"APPT_{last_id_num:03d}"
        else:
            new_id = "APPT_001"

        # Insert the new appointment into the database
        cur.execute("""
            INSERT INTO Appointment (AppointmentID, Date, Time, Status, PatientID, DoctorID, FacilityID)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (new_id, date, time, 'Booked', patient_id, doctor_id, facility_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('patient.patient_dashboard'))

    else:
        # GET request: Fetch available facilities
        conn = init_db()
        cur = conn.cursor()

        # Fetch facilities (General and Specialist)
        cur.execute("SELECT FacilityID, FacilityName, Cost FROM Facility WHERE FacilityID IN ('FAC_001', 'FAC_002')")
        facilities = cur.fetchall()

        cur.close()
        conn.close()

        return render_template('book_appointment.html', facilities=facilities)


@patient_blueprint.route('/get_doctors', methods=['GET'])
def get_doctors():
    appointment_type = request.args.get('type')

    conn = init_db()
    cur = conn.cursor()

    if appointment_type == 'general':
        # Fetch general doctors
        cur.execute("""
            SELECT Doctor.DoctorID, Doctor.Name, Department.DepartmentName 
            FROM Doctor
            INNER JOIN Department ON Doctor.DepartmentID = Department.DepartmentID
            WHERE Doctor.Role = 'Specialist' AND Department.DepartmentName = 'General';
        """)
    elif appointment_type == 'specialist':
        # Fetch specialist doctors with their department
        cur.execute("""
            SELECT Doctor.DoctorID, Doctor.Name, Department.DepartmentName 
            FROM Doctor
            INNER JOIN Department ON Doctor.DepartmentID = Department.DepartmentID
            WHERE Doctor.Role = 'Specialist'  AND Department.DepartmentName != 'General';
        """)

    doctors = cur.fetchall()
    cur.close()
    conn.close()

    # Return the doctor list as JSON
    return jsonify(doctors)

@patient_blueprint.route('/view_lab_results')
def view_lab_results():
    patient_id = session['user_id']  # Fetch the patient ID from the session
    conn = init_db()
    cur = conn.cursor()

    # Fetch lab results for the current patient
    cur.execute("""
        SELECT LabTestID, TestName, Result, AppointmentID, FacilityID, Status
        FROM Lab
        WHERE PatientID = %s
        ORDER BY LabTestID DESC;
    """, (patient_id,))
    lab_results = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('view_lab_results.html', lab_results=lab_results)


@patient_blueprint.route('/view_surgery_records')
def view_surgery_records():
    patient_id = session['user_id']  # Fetch the patient ID from the session
    conn = init_db()
    cur = conn.cursor()

    # Fetch surgery records for the current patient
    cur.execute("""
        SELECT SurgeryID, SurgeryName, Date, DoctorID, FacilityID, Status, AppointmentID
        FROM Surgery
        WHERE PatientID = %s
        ORDER BY Date DESC;
    """, (patient_id,))
    surgery_records = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('view_surgery_records.html', surgery_records=surgery_records)


@patient_blueprint.route('/medical_records')
def medical_records():
    patient_id = session.get('user_id')  # Get the patient ID from the session
    print(patient_id)
    if not patient_id:
        return redirect(url_for('home'))  # Redirect if no patient ID is found

    conn = init_db()
    cur = conn.cursor()

    # Fetch medical records for the patient, ordered by appointment date (newest to oldest)
    cur.execute("""
        SELECT mr.RecordID, mr.Diagnosis, mr.Treatment, a.Date, a.AppointmentID
        FROM MedicalRecords mr
        JOIN Appointment a ON a.AppointmentID = mr.AppointmentID
        WHERE mr.PatientID = %s
        ORDER BY a.Date DESC;
    """, (patient_id,))

    medical_records = cur.fetchall()
    print(medical_records)

    # Fetch medications for each medical record
    medications = {}
    for record in medical_records:
        record_id = record[0]  # Get RecordID
        cur.execute("""
            SELECT m.MedicineName
            FROM Medication m
            WHERE m.RecordID = %s;
        """, (record_id,))
        medications[record_id] = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('medical_records.html', medical_records=medical_records, medications=medications)


@patient_blueprint.route('/billing', methods=['GET', 'POST'])
def view_billing():
    def generate_bill_id():
        conn = init_db()
        cur = conn.cursor()

        cur.execute("SELECT BillID FROM Billing ORDER BY BillID DESC LIMIT 1")
        last_bill_id = cur.fetchone()

        if last_bill_id:
            last_id_num = int(last_bill_id[0].split('_')[1])
            new_id_num = last_id_num + 1
            new_bill_id = f'BILL_{new_id_num:03}'
        else:
            new_bill_id = 'BILL_001'

        cur.close()
        conn.close()
        return new_bill_id

    conn = init_db()
    cur = conn.cursor()

    patient_id = session.get('user_id')  # Assuming patient is logged in

    # Fetch all appointments for the patient and their billing status
    cur.execute("""
        SELECT A.AppointmentID, A.Date, A.Time, COALESCE(B.Status, 'Not Generated') AS BillStatus, COALESCE(B.Amount, 0) AS Amount, B.BillID
        FROM Appointment A
        LEFT JOIN Billing B ON A.AppointmentID = B.AppointmentID
        WHERE A.PatientID = %s
    """, (patient_id,))
    appointments = cur.fetchall()

    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')

        # Check if the bill already exists and is paid
        cur.execute("SELECT Status FROM Billing WHERE AppointmentID = %s", (appointment_id,))
        bill_status = cur.fetchone()

        if bill_status and bill_status[0] == 'Paid':
            # If the bill is already paid, do not process payment again
            return "Bill already paid."

        # Fetch facility costs for the selected appointment
        cur.execute("""
            SELECT F.FacilityID, F.Cost 
            FROM Facility F
            INNER JOIN Appointment A ON A.FacilityID = F.FacilityID
            WHERE A.AppointmentID = %s
            UNION
            SELECT F.FacilityID, F.Cost
            FROM Facility F
            INNER JOIN Lab L ON L.FacilityID = F.FacilityID
            WHERE L.AppointmentID = %s
            UNION
            SELECT F.FacilityID, F.Cost
            FROM Facility F
            INNER JOIN Surgery S ON S.FacilityID = F.FacilityID
            WHERE S.AppointmentID = %s
        """, (appointment_id, appointment_id, appointment_id))
        facilities = cur.fetchall()

        total_amount = sum(f[1] for f in facilities)

        # Insert into Billing table
        bill_id = generate_bill_id()
        cur.execute("""
            INSERT INTO Billing (BillID, Amount, DateIssued, Status, PatientID, StaffID, AppointmentID)
            VALUES (%s, %s, CURRENT_DATE, 'Paid', %s, 'STAFF_001', %s)
        """, (bill_id, total_amount, patient_id, appointment_id))

        # Insert into Billing_Facilities table
        for facility in facilities:
            cur.execute("""
                INSERT INTO Billing_Facilities (BillID, FacilityID, IDS)
                VALUES (%s, %s, %s)
            """, (bill_id, facility[0], appointment_id))

        conn.commit()

    cur.close()
    conn.close()

    return render_template('patient/view_billing.html', appointments=appointments)


@patient_blueprint.route('/view_bill_details/<bill_id>', methods=['GET'])
def view_bill_details(bill_id):
    conn = init_db()
    cur = conn.cursor()

    # Fetch bill details
    cur.execute("SELECT Amount, DateIssued, Status FROM Billing WHERE BillID = %s", (bill_id,))
    bill_details = cur.fetchone()
    print(bill_details)

    if bill_details:
        total_amount, date_issued, bill_status = bill_details
        print(total_amount)

        # Fetch facilities covered by the bill
        cur.execute("""
            SELECT BF.FacilityID, F.FacilityName, F.Cost
            FROM Billing_Facilities BF
            INNER JOIN Facility F ON BF.FacilityID = F.FacilityID
            WHERE BF.BillID = %s
        """, (bill_id,))
        facilities = cur.fetchall()
        for facility in facilities:
            print(facility[1])
    else:
        total_amount, date_issued, bill_status, facilities = None, None, None, []

    cur.close()
    conn.close()

    return render_template('patient/view_bill_details.html', 
                           bill_id=bill_id, 
                           total_amount=total_amount, 
                           date_issued=date_issued, 
                           bill_status=bill_status, 
                           facilities=facilities)
