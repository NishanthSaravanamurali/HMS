from flask import Blueprint, render_template,session,redirect,url_for,request
from db import init_db
from datetime import date

doctor_blueprint = Blueprint('doctor', __name__)

@doctor_blueprint.route('dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    doctor_id = session['user_id']
    conn = init_db()
    cur = conn.cursor()

    # Check if a specific date is selected, otherwise default to today's date
    if request.method == 'POST':
        selected_date = request.form.get('appointment_date')
    else:
        selected_date = date.today()

    # Fetch doctor details
    cur.execute("SELECT * FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    doctor = cur.fetchone()

    # Fetch appointments for the selected date
    cur.execute("""
        SELECT a.AppointmentID, a.Date, a.Time, a.Status, p.Name, p.Age , p.patientid
        FROM Appointment a
        JOIN Patient p ON a.PatientID = p.PatientID
        WHERE a.DoctorID = %s AND a.Date = %s
        ORDER BY a.Time ASC;
    """, (doctor_id, selected_date))

    appointments = cur.fetchall()

    # Close the cursor
    cur.close()

    return render_template('doctor_dashboard.html', doctor=doctor, appointments=appointments, selected_date=selected_date)


@doctor_blueprint.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    doctor_id = session['user_id']  # Assuming doctor ID is stored in session
    conn = init_db()
    cur = conn.cursor()

    # Fetch current doctor's details
    cur.execute("SELECT * FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    doctor = cur.fetchone()

    if request.method == 'POST':
        # Get updated details from form
        specialization = request.form['specialization']
        email = request.form['email']
        phone = request.form['phone']

        # Update doctor's details in the database
        cur.execute("""
            UPDATE Doctor 
            SET Specialization = %s, Email = %s, Phone = %s 
            WHERE DoctorID = %s
        """, (specialization, email, phone, doctor_id))
        conn.commit()

        cur.close()
        conn.close()

        # Redirect to the dashboard after successful update
        return redirect(url_for('doctor.doctor_dashboard'))

    cur.close()
    conn.close()
    return render_template('edit_profile.html', doctor=doctor)


@doctor_blueprint.route('/view_patient_info/<appointment_id>/<patient_id>', methods=['GET', 'POST'])
def view_patient_info(appointment_id, patient_id):
    conn = init_db()
    cur = conn.cursor()

    # Fetch patient details
    cur.execute("SELECT * FROM Patient WHERE PatientID = %s", (patient_id,))
    patient = cur.fetchone()

    # Fetch patient's medical records
    cur.execute("""
        SELECT mr.RecordID, mr.Diagnosis, mr.Treatment, m.MedicineName
        FROM MedicalRecords mr 
        LEFT JOIN Medication m ON mr.RecordID = m.RecordID
        WHERE mr.PatientID = %s
        ORDER BY mr.RecordID DESC
    """, (patient_id,))
    medical_records = cur.fetchall()

    # Fetch medicine names for the dropdown
    cur.execute("SELECT MedicineID, MedicineName FROM Pharmacy")
    medicines = cur.fetchall()

    # Fetch available lab tests for scheduling
    cur.execute("""
        SELECT FacilityID, FacilityName 
        FROM Facility 
        WHERE FacilityID IN ('FAC_003', 'FAC_004', 'FAC_005', 'FAC_006')
    """)
    available_lab_tests = cur.fetchall()

    # Fetch the scheduled lab tests for the appointment
    cur.execute("""
        SELECT LabTestID, TestName, Result, Status 
        FROM Lab 
        WHERE AppointmentID = %s AND PatientID = %s
    """, (appointment_id, patient_id))
    lab_tests = cur.fetchall()

    # Fetch available surgeries for the dropdown
    cur.execute("""
        SELECT FacilityID, FacilityName 
        FROM Facility 
        WHERE FacilityID IN ('FAC_007', 'FAC_008', 'FAC_009', 'FAC_019', 'FAC_023', 'FAC_026', 'FAC_027', 'FAC_030', 'FAC_035')
    """)
    available_surgeries = cur.fetchall()

    # Fetch the scheduled surgeries for the appointment
    cur.execute("""
        SELECT SurgeryID, SurgeryName, Date, Status
        FROM Surgery
        WHERE AppointmentID = %s AND PatientID = %s
    """, (appointment_id, patient_id))
    surgeries = cur.fetchall()

    if request.method == 'POST':
        if 'update_status' in request.form:
            # Update the appointment status
            appointment_status = request.form.get('appointment_status')
            if appointment_status:
                cur.execute("""
                    UPDATE Appointment
                    SET Status = %s
                    WHERE AppointmentID = %s
                """, (appointment_status, appointment_id))
                conn.commit()
                return redirect(url_for('doctor.view_patient_info', appointment_id=appointment_id, patient_id=patient_id))

        elif 'add_record' in request.form:
            # Add a new medical record
            diagnosis = request.form.get('diagnosis')
            treatment = request.form.get('treatment')
            prescribed_medicine = request.form.get('prescribed_medicine')

            # Generate new RecordID
            cur.execute("SELECT MAX(RecordID) FROM MedicalRecords")
            max_record_id = cur.fetchone()[0]

            if max_record_id:
                current_number = int(max_record_id.split('_')[1]) + 1
                new_record_id = f"REC_{current_number:03d}"
            else:
                new_record_id = "REC_001"

            cur.execute("""
                INSERT INTO MedicalRecords (RecordID, Diagnosis, Treatment, PatientID, DoctorID, AppointmentID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_record_id, diagnosis, treatment, patient_id, session['user_id'], appointment_id))
            conn.commit()

            if prescribed_medicine:
                cur.execute("""
                    INSERT INTO Medication (MedicineID, MedicineName, RecordID)
                    VALUES (%s, %s, %s)
                """, (prescribed_medicine, prescribed_medicine, new_record_id))
                conn.commit()

            return redirect(url_for('doctor.view_patient_info', appointment_id=appointment_id, patient_id=patient_id))

        elif 'schedule_lab_test' in request.form:
            # Schedule a lab test
            test_name = request.form.get('test_name')
            result = request.form.get('result', None)

            # Generate new LabTestID
            cur.execute("SELECT MAX(LabTestID) FROM Lab")
            max_lab_id = cur.fetchone()[0]

            if max_lab_id:
                current_number = int(max_lab_id.split('_')[1]) + 1
                new_lab_id = f"LAB_{current_number:03d}"
            else:
                new_lab_id = "LAB_001"

            cur.execute("""
                INSERT INTO Lab (LabTestID, TestName, Result, AppointmentID, FacilityID, PatientID, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (new_lab_id, test_name, result, appointment_id, test_name, patient_id, 'Scheduled'))
            conn.commit()

            return redirect(url_for('doctor.view_patient_info', appointment_id=appointment_id, patient_id=patient_id))

        elif 'update_lab_test' in request.form:
            # Update lab test result
            lab_test_id = request.form.get('lab_test_id')
            updated_result = request.form.get(f'updated_result_{lab_test_id}')
            updated_status = request.form.get(f'updated_status_{lab_test_id}')

            cur.execute("""
                UPDATE Lab
                SET Result = %s, Status = %s
                WHERE LabTestID = %s
            """, (updated_result, updated_status, lab_test_id))
            conn.commit()

            return redirect(url_for('doctor.view_patient_info', appointment_id=appointment_id, patient_id=patient_id))

        elif 'schedule_surgery' in request.form:
            # Schedule a surgery
            surgery_name = request.form.get('surgery_name')
            surgery_date = request.form.get('surgery_date')

            # Generate new SurgeryID
            cur.execute("SELECT MAX(SurgeryID) FROM Surgery")
            max_surgery_id = cur.fetchone()[0]

            if max_surgery_id:
                current_number = int(max_surgery_id.split('_')[1]) + 1
                new_surgery_id = f"SUR_{current_number:03d}"
            else:
                new_surgery_id = "SUR_001"

            cur.execute("""
                INSERT INTO Surgery (SurgeryID, SurgeryName, Date, DoctorID, PatientID, FacilityID, AppointmentID, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (new_surgery_id, surgery_name, surgery_date, session['user_id'], patient_id, surgery_name, appointment_id, 'Scheduled'))
            conn.commit()

            return redirect(url_for('doctor.view_patient_info', appointment_id=appointment_id, patient_id=patient_id))

        elif 'update_surgery' in request.form:
            # Update surgery details
            surgery_id = request.form.get('surgery_id')
            updated_surgery_status = request.form.get(f'updated_surgery_status_{surgery_id}')

            cur.execute("""
                UPDATE Surgery
                SET Status = %s
                WHERE SurgeryID = %s
            """, (updated_surgery_status, surgery_id))
            conn.commit()

            return redirect(url_for('doctor.view_patient_info', appointment_id=appointment_id, patient_id=patient_id))

    cur.close()
    conn.close()

    return render_template('view_patient_info.html', patient=patient, medical_records=medical_records, medicines=medicines, available_lab_tests=available_lab_tests, lab_tests=lab_tests, available_surgeries=available_surgeries, surgeries=surgeries, appointment_id=appointment_id)


@doctor_blueprint.route('/prescribe_medicine', methods=['POST'])
def prescribe_medicine():
    patient_id = request.form.get('patient_id')
    medicine_name = request.form.get('medicine_name')
    record_id = request.form.get('record_id')

    conn = init_db()
    cur = conn.cursor()

    # Fetch medicine ID from Pharmacy table based on the name
    cur.execute("SELECT MedicineID FROM Pharmacy WHERE MedicineName = %s", (medicine_name,))
    medicine_id = cur.fetchone()

    if medicine_id:
        # Insert the prescribed medicine into the Medication table
        cur.execute("""
            INSERT INTO Medication (MedicineID, MedicineName, RecordID)
            VALUES (%s, %s, %s)
        """, (medicine_id[0], medicine_name, record_id))
        conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for('doctor.view_patient_info', appointment_id=request.args.get('appointment_id'), patient_id=patient_id))
