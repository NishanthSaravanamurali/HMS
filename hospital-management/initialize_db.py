import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(host="db", user="postgres", password="Database", port=5432)
conn.autocommit = True  
cur = conn.cursor()

new_db_name = "cloud_test1"

try:
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db_name)))
    print(f"Database '{new_db_name}' created successfully.")
except Exception as e:
    print(f"Database '{new_db_name}' already exists. Error: {e}")

cur.close()
conn.close()

conn = psycopg2.connect(host="db", user="postgres", password="Database", port=5432, dbname=new_db_name)
cur = conn.cursor()

conn.autocommit = True

tables = [
    """
    CREATE TABLE Patient (
        PatientID VARCHAR(20) PRIMARY KEY,
        Name VARCHAR(100),
        Age INT,
        Gender VARCHAR(10),
        Address VARCHAR(255),
        PhoneNo VARCHAR(15),
        Email VARCHAR(100),
        Password VARCHAR(100)
    );
    """,
    """
    CREATE TABLE Facility (
        FacilityID VARCHAR(20) PRIMARY KEY,
        FacilityName VARCHAR(100),
        Cost INT
    );
    """,
    """
    CREATE TABLE Department (
        DepartmentID VARCHAR(20) PRIMARY KEY,
        DepartmentName VARCHAR(100)
    );
    """,
    """
    CREATE TABLE Doctor (
        DoctorID VARCHAR(20) PRIMARY KEY,
        Name VARCHAR(100),
        Specialization VARCHAR(100),
        Phone VARCHAR(15),
        Role VARCHAR(50),
        DepartmentID VARCHAR(20),
        Password VARCHAR(100),
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    );
    """,
    """
    CREATE TABLE Appointment (
        AppointmentID VARCHAR(20) PRIMARY KEY,
        Date DATE,
        Time TIME,
        Status VARCHAR(50),
        PatientID VARCHAR(20),
        DoctorID VARCHAR(20),
        FacilityID VARCHAR(20),
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID),
        FOREIGN KEY (FacilityID) REFERENCES Facility(FacilityID)
    );
    """, 
    """
    CREATE TABLE Nurse (
        NurseID VARCHAR(20) PRIMARY KEY,
        Name VARCHAR(100),
        Role VARCHAR(50),
        Shift VARCHAR(50),
        DepartmentID VARCHAR(20),
        Password VARCHAR(100),
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    );
    """,
    """
    CREATE TABLE Staff (
        StaffID VARCHAR(20) PRIMARY KEY,
        Name VARCHAR(100),
        Role VARCHAR(50),
        DepartmentID VARCHAR(20),
        Password VARCHAR(100),
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    );
    """,
    """
    CREATE TABLE Lab (
        LabTestID VARCHAR(20) PRIMARY KEY,
        TestName VARCHAR(100),
        Result TEXT,
        AppointmentID VARCHAR(20),
        FacilityID VARCHAR(20),
        FOREIGN KEY (FacilityID) REFERENCES Facility(FacilityID),
        FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
    );
    """,
    """
    CREATE TABLE Surgery (
        SurgeryID VARCHAR(20) PRIMARY KEY,
        SurgeryName VARCHAR(100),
        Date DATE,
        DoctorID VARCHAR(20),
        PatientID VARCHAR(20),
        FacilityID VARCHAR(20),
        AppointmentID VARCHAR(20),
        FOREIGN KEY (FacilityID) REFERENCES Facility(FacilityID),
        FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID),
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
    );
    """,
    """
    CREATE TABLE MedicalRecords (
        RecordID VARCHAR(20) PRIMARY KEY,
        Diagnosis VARCHAR(255),
        Treatment TEXT,
        PatientID VARCHAR(20),
        DoctorID VARCHAR(20),
        AppointmentID VARCHAR(20),
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID),
        FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
    );
    """,
    """
    CREATE TABLE Pharmacy (
        MedicineID VARCHAR(20) PRIMARY KEY,
        MedicineName VARCHAR(100),
        Cost DECIMAL(10, 2),
        Stock INT
    );
    """,
    """
    CREATE TABLE Medication (
        MedicineID VARCHAR(20),
        MedicineName VARCHAR(100),
        RecordID VARCHAR(20),
        FOREIGN KEY (MedicineID) REFERENCES Pharmacy(MedicineID),
        FOREIGN KEY (RecordID) REFERENCES MedicalRecords(RecordID)
    );
    """,
    """
    CREATE TABLE Billing (
        BillID VARCHAR(20) PRIMARY KEY,
        Amount DECIMAL(10, 2),
        DateIssued DATE,
        Status VARCHAR(50),
        PatientID VARCHAR(20),
        StaffID VARCHAR(20),
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
    );
    """,
    """
    CREATE TABLE Billing_Facilities (
        BillID VARCHAR(20),
        FacilityID VARCHAR(20),
        IDS VARCHAR(20),
        PRIMARY KEY (BillID, FacilityID),
        FOREIGN KEY (BillID) REFERENCES Billing(BillID),
        FOREIGN KEY (FacilityID) REFERENCES Facility(FacilityID)
    );
    """,
    """
    CREATE TABLE Room (
        RoomID VARCHAR(20) PRIMARY KEY,
        Type VARCHAR(50),
        Availability BOOLEAN,
        Duration INTERVAL,
        PatientID VARCHAR(20),
        StaffID VARCHAR(20),
        FacilityID VARCHAR(20),
        FOREIGN KEY (FacilityID) REFERENCES Facility(FacilityID),
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
    );
    """,
    """
    CREATE TABLE Admin (
        AdminID VARCHAR(20) PRIMARY KEY,
        Name VARCHAR(100),
        Password VARCHAR(100)
    );"""
]


for table_sql in tables:
    cur.execute(sql.SQL(table_sql))

cur.execute(sql.SQL("INSERT INTO admin (adminid, name, password) VALUES ('ADM_001', 'X', '0000');"))


departments = [
    ('DEP_001', 'Administration'),
    ('DEP_002', 'Management'),
    ('DEP_003', 'Finance'),
    ('DEP_004', 'Human Resources'),
    ('DEP_005', 'Cardiology'),
    ('DEP_006', 'Neurology'),
    ('DEP_007', 'Orthopedics'),
    ('DEP_008', 'Pulmonology'),
    ('DEP_009', 'Nephrology'),
    ('DEP_010', 'General'),
    ('DEP_011', 'Nursing')
]
for dept_id, dept_name in departments:
    cur.execute("""
            INSERT INTO Department (DepartmentID, DepartmentName)
            VALUES (%s, %s)
        """, (dept_id, dept_name))
    
    # Commit the transaction
    conn.commit()

cur.close()
conn.close()
def insert_doctors():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # Doctor data for departments DEP_005 to DEP_010
    doctor_data = [
        # DEP_005
        ('DOC_001', 'Dr. John Smith', 'Cardiology', '555-1234', 'Head of Department', 'DEP_005', 'password1'),
        ('DOC_002', 'Dr. Alice Jones', 'Cardiology', '555-5678', 'Department Specialist', 'DEP_005', 'password2'),
        ('DOC_003', 'Dr. Michael White', 'Cardiology', '555-9876', 'Specialist', 'DEP_005', 'password3'),
        ('DOC_004', 'Dr. Laura Green', 'Cardiology', '555-6543', 'Trainee', 'DEP_005', 'password4'),
        
        # DEP_006
        ('DOC_005', 'Dr. Robert Brown', 'Neurology', '555-4321', 'Head of Department', 'DEP_006', 'password5'),
        ('DOC_006', 'Dr. Emily Davis', 'Neurology', '555-8765', 'Department Specialist', 'DEP_006', 'password6'),
        ('DOC_007', 'Dr. William Johnson', 'Neurology', '555-3456', 'Specialist', 'DEP_006', 'password7'),
        ('DOC_008', 'Dr. Olivia Wilson', 'Neurology', '555-9870', 'Trainee', 'DEP_006', 'password8'),
        
        # DEP_007
        ('DOC_009', 'Dr. James Miller', 'Orthopedics', '555-2345', 'Head of Department', 'DEP_007', 'password9'),
        ('DOC_010', 'Dr. Sophia Moore', 'Orthopedics', '555-7654', 'Department Specialist', 'DEP_007', 'password10'),
        ('DOC_011', 'Dr. Henry Thomas', 'Orthopedics', '555-8764', 'Specialist', 'DEP_007', 'password11'),
        ('DOC_012', 'Dr. Grace Taylor', 'Orthopedics', '555-1239', 'Trainee', 'DEP_007', 'password12'),
        
        # DEP_008
        ('DOC_013', 'Dr. Benjamin Anderson', 'Pediatrics', '555-2349', 'Head of Department', 'DEP_008', 'password13'),
        ('DOC_014', 'Dr. Chloe Martin', 'Pediatrics', '555-6743', 'Department Specialist', 'DEP_008', 'password14'),
        ('DOC_015', 'Dr. Daniel King', 'Pediatrics', '555-8967', 'Specialist', 'DEP_008', 'password15'),
        ('DOC_016', 'Dr. Mia Walker', 'Pediatrics', '555-1274', 'Trainee', 'DEP_008', 'password16'),
        
        # DEP_009
        ('DOC_017', 'Dr. Alexander Scott', 'Oncology', '555-2348', 'Head of Department', 'DEP_009', 'password17'),
        ('DOC_018', 'Dr. Ella Harris', 'Oncology', '555-4983', 'Department Specialist', 'DEP_009', 'password18'),
        ('DOC_019', 'Dr. Jacob Turner', 'Oncology', '555-6745', 'Specialist', 'DEP_009', 'password19'),
        ('DOC_020', 'Dr. Lily Clark', 'Oncology', '555-2341', 'Trainee', 'DEP_009', 'password20'),
        
        # DEP_010
        ('DOC_021', 'Dr. Samuel Wright', 'Dermatology', '555-2493', 'Head of Department', 'DEP_010', 'password21'),
        ('DOC_022', 'Dr. Ava Hall', 'Dermatology', '555-5483', 'Department Specialist', 'DEP_010', 'password22'),
        ('DOC_023', 'Dr. Ethan Lee', 'Dermatology', '555-3745', 'Specialist', 'DEP_010', 'password23'),
        ('DOC_024', 'Dr. Isabella Young', 'Dermatology', '555-2346', 'Trainee', 'DEP_010', 'password24')
    ]

    # SQL query to insert doctor data
    sql = """
        INSERT INTO Doctor (DoctorID, Name, Specialization, Phone, Role, DepartmentID, Password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # Execute the query for each doctor in the list
    for doctor in doctor_data:
        cur.execute(sql, doctor)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

    print("Doctors inserted successfully.")

insert_doctors()

def insert_nurses():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # Set DepartmentID to DEP_011 for all nurses
    department_id = 'DEP_011'

    # Nurse data with fixed department DEP_011
    nurse_data = [
        # CNA
        ('NUR_001', 'Nurse Alice Brown', 'CNA', 'Day Shift', department_id, 'password1'),
        ('NUR_002', 'Nurse John White', 'CNA', 'Night Shift', department_id, 'password2'),
        ('NUR_003', 'Nurse Lucy Black', 'CNA', 'Evening Shift', department_id, 'password3'),
        
        # LPN
        ('NUR_004', 'Nurse Laura Green', 'LPN', 'Day Shift', department_id, 'password4'),
        ('NUR_005', 'Nurse Kevin Blue', 'LPN', 'Night Shift', department_id, 'password5'),
        ('NUR_006', 'Nurse Emma Gray', 'LPN', 'Evening Shift', department_id, 'password6'),
        
        # RN
        ('NUR_007', 'Nurse Rachel Adams', 'RN', 'Day Shift', department_id, 'password7'),
        ('NUR_008', 'Nurse Jake Brown', 'RN', 'Night Shift', department_id, 'password8'),
        ('NUR_009', 'Nurse Lily Evans', 'RN', 'Evening Shift', department_id, 'password9'),
        
        # OR Nurse (Scrub Nurse)
        ('NUR_010', 'Nurse Claire Hall', 'OR Nurse (Scrub Nurse)', 'Day Shift', department_id, 'password10'),
        ('NUR_011', 'Nurse Henry Clark', 'OR Nurse (Scrub Nurse)', 'Night Shift', department_id, 'password11'),
        ('NUR_012', 'Nurse Ava Johnson', 'OR Nurse (Scrub Nurse)', 'Evening Shift', department_id, 'password12'),
        
        # Nurse Practitioner (NP)
        ('NUR_013', 'Nurse Mia Scott', 'Nurse Practitioner (NP)', 'Day Shift', department_id, 'password13'),
        ('NUR_014', 'Nurse Oliver White', 'Nurse Practitioner (NP)', 'Night Shift', department_id, 'password14'),
        ('NUR_015', 'Nurse Ella King', 'Nurse Practitioner (NP)', 'Evening Shift', department_id, 'password15'),
        
        # Nurse Manager
        ('NUR_016', 'Nurse Ethan Walker', 'Nurse Manager', 'Day Shift', department_id, 'password16'),
        ('NUR_017', 'Nurse Sophia Martinez', 'Nurse Manager', 'Night Shift', department_id, 'password17'),
        ('NUR_018', 'Nurse Mason Harris', 'Nurse Manager', 'Evening Shift', department_id, 'password18')
    ]

    # SQL query to insert nurse data
    sql = """
        INSERT INTO Nurse (NurseID, Name, Role, Shift, DepartmentID, Password)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    # Execute the query for each nurse in the list
    for nurse in nurse_data:
        cur.execute(sql, nurse)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()


insert_nurses()

def insert_staff():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # Staff data with expanded roles for each department (DEP_001 to DEP_004)
    staff_data = [
        # DEP_001 - Administration
        ('STAFF_001', 'Staff Alice Brown', 'Manager', 'DEP_001', 'password1'),
        ('STAFF_002', 'Staff John White', 'Assistant Manager', 'DEP_001', 'password2'),
        ('STAFF_003', 'Staff Lucy Black', 'Team Lead', 'DEP_001', 'password3'),
        ('STAFF_004', 'Staff Daniel Grey', 'Senior Staff', 'DEP_001', 'password4'),
        ('STAFF_005', 'Staff Emily Cooper', 'Junior Staff', 'DEP_001', 'password5'),

        # DEP_002 - Management
        ('STAFF_006', 'Staff Laura Green', 'Manager', 'DEP_002', 'password6'),
        ('STAFF_007', 'Staff Kevin Blue', 'Assistant Manager', 'DEP_002', 'password7'),
        ('STAFF_008', 'Staff Emma Gray', 'Team Lead', 'DEP_002', 'password8'),
        ('STAFF_009', 'Staff Peter Woods', 'Senior Staff', 'DEP_002', 'password9'),
        ('STAFF_010', 'Staff Susan Wilson', 'Junior Staff', 'DEP_002', 'password10'),

        # DEP_003 - Finance
        ('STAFF_011', 'Staff Rachel Adams', 'Manager', 'DEP_003', 'password11'),
        ('STAFF_012', 'Staff Jake Brown', 'Assistant Manager', 'DEP_003', 'password12'),
        ('STAFF_013', 'Staff Lily Evans', 'Team Lead', 'DEP_003', 'password13'),
        ('STAFF_014', 'Staff Max Turner', 'Senior Staff', 'DEP_003', 'password14'),
        ('STAFF_015', 'Staff Sara Jones', 'Junior Staff', 'DEP_003', 'password15'),

        # DEP_004 - HR
        ('STAFF_016', 'Staff Claire Hall', 'Manager', 'DEP_004', 'password16'),
        ('STAFF_017', 'Staff Henry Clark', 'Assistant Manager', 'DEP_004', 'password17'),
        ('STAFF_018', 'Staff Ava Johnson', 'Team Lead', 'DEP_004', 'password18'),
        ('STAFF_019', 'Staff William Baker', 'Senior Staff', 'DEP_004', 'password19'),
        ('STAFF_020', 'Staff Olivia Harris', 'Junior Staff', 'DEP_004', 'password20')
    ]

    # SQL query to insert staff data
    sql = """
        INSERT INTO Staff (StaffID, Name, Role, DepartmentID, Password)
        VALUES (%s, %s, %s, %s, %s)
    """

    # Execute the query for each staff member in the list
    for staff in staff_data:
        cur.execute(sql, staff)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

insert_staff()


# Database connection setup
def connect_db():
    return psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )

# Inserting various facilities into the database
def insert_facilities():
    conn = connect_db()
    cur = conn.cursor()

    # Facility data including services relevant to the doctors in various departments
    facility_data = [
        # Appointments
        ('FAC_001', 'General Appointment', 500),
        ('FAC_002', 'Specialist Appointment', 1000),

        # Lab Tests
        ('FAC_003', 'Blood Test', 200),
        ('FAC_004', 'X-Ray', 400),
        ('FAC_005', 'MRI Scan', 2000),
        ('FAC_006', 'Ultrasound', 800),

        # Surgeries
        ('FAC_007', 'Appendectomy', 30000),
        ('FAC_008', 'Heart Bypass Surgery', 500000),
        ('FAC_009', 'Knee Replacement Surgery', 200000),

        # Rooms
        ('FAC_010', 'General Ward Room', 1000),
        ('FAC_011', 'Private Room', 5000),
        ('FAC_012', 'ICU Room', 10000),

        # Services
        ('FAC_013', 'Ambulance Service', 1500),
        ('FAC_014', 'Physiotherapy Session', 1200),
        ('FAC_015', 'Dietary Consultation', 600),

        # Cardiology Services
        ('FAC_016', 'ECG (Electrocardiogram)', 500),
        ('FAC_017', 'Echocardiogram', 1500),
        ('FAC_018', 'Stress Test', 1000),
        ('FAC_019', 'Heart Surgery', 300000),
        
        # Neurology Services
        ('FAC_020', 'EEG (Electroencephalogram)', 2000),
        ('FAC_021', 'CT Scan (Brain)', 4000),
        ('FAC_022', 'MRI Brain Scan', 6000),
        ('FAC_023', 'Neurosurgery', 500000),
        
        # Orthopedics Services
        ('FAC_024', 'X-Ray', 400),
        ('FAC_025', 'Bone Density Test', 1200),
        ('FAC_026', 'Joint Replacement Surgery', 250000),
        ('FAC_027', 'Fracture Treatment', 5000),

        # Pulmonology Services
        ('FAC_028', 'Pulmonary Function Test', 1500),
        ('FAC_029', 'Chest X-Ray', 400),
        ('FAC_030', 'Bronchoscopy', 5000),
        ('FAC_031', 'Lung Biopsy', 7000),

        # Nephrology Services
        ('FAC_032', 'Dialysis', 3000),
        ('FAC_033', 'Kidney Function Test', 1000),
        ('FAC_034', 'Renal Biopsy', 7000),
        ('FAC_035', 'Kidney Transplant Surgery', 400000),

        # General Services
        ('FAC_036', 'General Checkup', 300),
        ('FAC_037', 'Vaccination', 500),
        ('FAC_038', 'Wound Treatment', 200),
        ('FAC_039', 'Basic Blood Tests', 200),

        # General Services
        ('FAC_040', 'Private room', 23000),
        ('FAC_041', 'Emergency room', 25000),
        ('FAC_042', 'General room', 10000),
        ('FAC_043', 'ICU', 30000)
    ]

    # SQL query to insert facility data
    sql = """
        INSERT INTO Facility (FacilityID, FacilityName, Cost)
        VALUES (%s, %s, %s)
    """

    # Execute the query for each facility in the list
    for facility in facility_data:
        cur.execute(sql, facility)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()


insert_facilities()

def insert_rooms():
    conn = connect_db()
    cur = conn.cursor()

    # Room data
    rooms = [
        # General Rooms
        ('ROOM_GEN_001', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_002', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_003', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_004', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_005', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_006', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_007', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_008', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_009', 'General', True, None, 'FAC_042'),
        ('ROOM_GEN_010', 'General', True, None, 'FAC_042'),

        # Private Rooms
        ('ROOM_PRI_001', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_002', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_003', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_004', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_005', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_006', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_007', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_008', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_009', 'Private', True, None, 'FAC_040'),
        ('ROOM_PRI_010', 'Private', True, None, 'FAC_040'),

        # ICU Rooms
        ('ROOM_ICU_001', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_002', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_003', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_004', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_005', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_006', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_007', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_008', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_009', 'ICU', True, None, 'FAC_043'),
        ('ROOM_ICU_010', 'ICU', True, None, 'FAC_043'),

        # Emergency Rooms
        ('ROOM_EMG_001', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_002', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_003', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_004', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_005', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_006', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_007', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_008', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_009', 'Emergency', True, None, 'FAC_041'),
        ('ROOM_EMG_010', 'Emergency', True, None, 'FAC_041')
    ]

    # Insert query
    insert_query = """
    INSERT INTO Room (RoomID, Type, Availability, Duration, FacilityID)
    VALUES (%s, %s, %s, %s, %s)
    """

    # Execute the query for each room
    try:
        for room in rooms:
            cur.execute(insert_query, room)

        # Commit the transaction
        conn.commit()
        print("Rooms inserted successfully!")

    except Exception as e:
        print(f"Error inserting rooms: {e}")
        conn.rollback()

    # Close cursor and connection
    cur.close()
    conn.close()

# Run the function to insert rooms
insert_rooms()

def alter_lab_table():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # SQL command to add PatientID and Status columns
    alter_table_sql = """
    ALTER TABLE Lab
    ADD COLUMN PatientID VARCHAR(20),
    ADD COLUMN Status VARCHAR(20);
    """

    # Execute the command
    cur.execute(alter_table_sql)

    # Commit the transaction
    conn.commit()

    # Set foreign key constraint for PatientID
    add_foreign_key_sql = """
    ALTER TABLE Lab
    ADD CONSTRAINT fk_patient
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID);
    """

    # Execute the command
    cur.execute(add_foreign_key_sql)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()


# Call the function to alter the Lab table
alter_lab_table()

def alter_Surgery_table():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # SQL command to add PatientID and Status columns
    alter_table_sql = """
    ALTER TABLE Surgery
    ADD COLUMN Status VARCHAR(20);
    """

    # Execute the command
    cur.execute(alter_table_sql)

    # Commit the transaction
    conn.commit()

    cur.close()
    conn.close()


# Call the function to alter the Lab table
alter_Surgery_table()


def alter_Surgery_table2():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # SQL command to add PatientID and Status columns
    alter_table_sql = """
    ALTER TABLE Billing
    ADD COLUMN AppointmentID VARCHAR(20);
    """

    # Execute the command
    cur.execute(alter_table_sql)

    # Commit the transaction
    conn.commit()

    add_foreign_key_sql = """
    ALTER TABLE Billing
    ADD CONSTRAINT fk_appointment
    FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID);
    """

    # Execute the command
    cur.execute(add_foreign_key_sql)

    # Commit the transaction and close the connection
    conn.commit()
    

    cur.close()
    conn.close()

    print("Lab table modified successfully with PatientID and Status.")

# Call the function to alter the Lab table
alter_Surgery_table2()

def insert_pharmacy_records():
    # Connect to the database
    conn = psycopg2.connect(
        host="db",  # Update with your host details
        database="cloud_test1",  # Update with your database name
        user="postgres",  # Update with your PostgreSQL username
        password="Database"  # Update with your PostgreSQL password
    )
    cur = conn.cursor()

    # Expanded pharmacy data (medicine records)
    pharmacy_data = [
        ('MED_001', 'Paracetamol', 10.50, 200),  # Fever Relief
        ('MED_002', 'Amoxicillin', 25.00, 150),  # Antibiotic
        ('MED_003', 'Ibuprofen', 15.00, 180),  # Pain Relief
        ('MED_004', 'Naproxen', 20.00, 100),  # Chronic Pain Relief
        ('MED_005', 'Albuterol', 30.00, 120),  # Respiratory Issues
        ('MED_006', 'Metformin', 15.00, 80),  # Diabetes Medication
        ('MED_007', 'Atorvastatin', 40.00, 60),  # Cholesterol Management
        ('MED_008', 'Sertraline', 35.25, 50),  # Antidepressant
        ('MED_009', 'Omeprazole', 20.00, 90),  # Stomach Acid Reducer
        ('MED_010', 'Cetirizine', 18.50, 100),  # Allergy Relief
        ('MED_011', 'Dextromethorphan', 10.00, 110),  # Cold and Cough Relief
        ('MED_012', 'Loratadine', 12.00, 130),  # Antihistamine
        ('MED_013', 'Fluconazole', 50.00, 40),  # Fungal Infection Treatment
        ('MED_014', 'Oseltamivir', 200.00, 30),  # Antiviral Medication
        ('MED_015', 'Aspirin', 5.00, 300)  # Pain Reliever for Headaches
    ]

    # SQL query to insert pharmacy data
    sql = """
        INSERT INTO Pharmacy (MedicineID, MedicineName, Cost, Stock)
        VALUES (%s, %s, %s, %s)
    """

    # Execute the query for each medicine in the list
    for medicine in pharmacy_data:
        cur.execute(sql, medicine)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()


# Call the function to insert pharmacy records
insert_pharmacy_records()
