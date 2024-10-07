import sqlite3 as sql

def initialize_database():
    conn = sql.connect("EntranceSystem.db")
    print("Database EntranceSystem.db created")

    create_enrolledemployees_table_command = """
    CREATE TABLE IF NOT EXISTS EnrolledEmployees (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Firstname VARCHAR(50),
        Lastname VARCHAR(50),
        LastFour CHAR(4),
        GeneralAccess BOOLEAN DEFAULT 0,
        Weekends BOOLEAN DEFAULT 0,
        AfterHours BOOLEAN DEFAULT 0
    )
    """

    create_settings_table_command = """
    CREATE TABLE IF NOT EXISTS Settings (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        LockdownTime TIME,
        DoorOpen INTEGER,
        IsActive INTEGER
    )
    """

    create_tracking_table_command = """
    CREATE TABLE IF NOT EXISTS Tracking (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Firstname VARCHAR(50),
        Lastname VARCHAR(50),
        AccessDate DATETIME
        
    )
    """


    try:

        conn.execute(create_enrolledemployees_table_command)
        conn.execute(create_settings_table_command)
        conn.execute(create_tracking_table_command)
        # conn.execute(insertdata_command)
        print("Database tables created")
    except sql.Error as e:
        print("Database table creation failed", e)
    finally:
        conn.commit()
        conn.close()

# initialize_database()
def add_employee_to_database(firstname, lastname, lastfour, general_access=None, weekends=None, after_hours=None):
    conn = sql.connect("EntranceSystem.db")
    query = """
    INSERT INTO EnrolledEmployees (Firstname, Lastname, LastFour, GeneralAccess, Weekends, AfterHours)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    # Asignar valores por defecto si los parámetros son None
    general_access = general_access if general_access is not None else 0
    weekends = weekends if weekends is not None else 0
    after_hours = after_hours if after_hours is not None else 0

    try:
        conn.execute(query, (firstname, lastname, lastfour, general_access, weekends, after_hours))
        conn.commit()
        print(f"Employee added successfully: {firstname} {lastname}, LastFour={lastfour}, GeneralAccess={general_access}, Weekends={weekends}, AfterHours={after_hours}")
    except sql.Error as e:
        print("Failed to add employee", e)
    finally:
        conn.close()

def get_all_employees():
    conn = sql.connect("EntranceSystem.db")
    query = "SELECT * FROM EnrolledEmployees"
    try:
        cursor = conn.execute(query)
        employees = cursor.fetchall()
        return employees
    except sql.Error as e:
        print("Failed to retrieve employees", e)
    finally:
        conn.close()
    return []

def get_employee_by_name(firstname, lastname):
    conn = sql.connect("EntranceSystem.db")
    query = "SELECT * FROM EnrolledEmployees WHERE LOWER(Firstname) = LOWER(?) AND LOWER(Lastname) = LOWER(?)"
    try:
        cursor = conn.execute(query, (firstname, lastname))
        employee = cursor.fetchone()
        return employee
    except sql.Error as e:
        print("Failed to retrieve employee", e)
    finally:
        conn.close()
    return None



def employee_exists(firstname, lastname):
    conn = sql.connect("EntranceSystem.db")
    query = "SELECT 1 FROM EnrolledEmployees WHERE LOWER(Firstname) = LOWER(?) AND LOWER(Lastname) = LOWER(?)"
    try:
        cursor = conn.execute(query, (firstname, lastname))
        employee = cursor.fetchone()
        return employee is not None
    except sql.Error as e:
        print("Failed to check if employee exists", e)
        return False
    finally:
        conn.close()



def update_employee_by_name(firstname, lastname, lastfour=None, general_access=None, weekends=None, after_hours=None):
    conn = sql.connect("EntranceSystem.db")
    query = """
    UPDATE EnrolledEmployees
    SET LastFour = COALESCE(?, LastFour),
        GeneralAccess = COALESCE(?, GeneralAccess),
        Weekends = COALESCE(?, Weekends),
        AfterHours = COALESCE(?, AfterHours)
    WHERE LOWER(Firstname) = LOWER(?) AND LOWER(Lastname) = LOWER(?)
    """
    try:
        conn.execute(query, (lastfour, general_access, weekends, after_hours, firstname, lastname))
        conn.commit()
        if conn.total_changes == 0:
            print(f"Employee {firstname} {lastname} not found.")
            return False
        else:
            print("Employee updated successfully")
            return True
    except sql.Error as e:
        print("Failed to update employee", e)
        return False
    finally:
        conn.close()



def delete_employee_by_name(firstname, lastname):
    conn = sql.connect("EntranceSystem.db")
    query = "DELETE FROM EnrolledEmployees WHERE LOWER(Firstname) = LOWER(?) AND LOWER(Lastname) = LOWER(?)"
    try:
        cursor = conn.execute(query, (firstname, lastname))
        conn.commit()
        if cursor.rowcount == 0:
            return f"Employee {firstname} {lastname} not found"
        else:
            return f"Employee {firstname} {lastname} deleted successfully"
    except sql.Error as e:
        return f"Failed to delete employee: {str(e)}"
    finally:
        conn.close()


def update_setting_database(setting_id, lockdown_time=None, door_open=None, is_active=None):
    conn = sql.connect("EntranceSystem.db")
    query = """
    UPDATE Settings
    SET LockdownTime = COALESCE(?, LockdownTime),
        DoorOpen = COALESCE(?, DoorOpen),
        IsActive = COALESCE(?, IsActive)
    WHERE ID = ?
    """
    try:
        conn.execute(query, (lockdown_time, door_open, is_active, setting_id))
        conn.commit()
        print("Setting updated successfully")
    except sql.Error as e:
        print("Failed to update setting", e)
    finally:
        conn.close()
        
def get_setting_by_id(setting_id):
    conn = sql.connect("EntranceSystem.db")
    query = "SELECT * FROM Settings WHERE ID = ?"
    try:
        cursor = conn.execute(query, (setting_id,))
        setting = cursor.fetchone()
        return setting
    except sql.Error as e:
        print("Failed to retrieve setting", e)
    finally:
        conn.close()
    return None

def get_all_records():

    conn = sql.connect("EntranceSystem.db")
    query = """
    SELECT * FROM Tracking
    WHERE DATE(AccessDate) = DATE('now')
    ORDER BY AccessDate DESC
    """
    
    try:
        cursor = conn.execute(query)
        records = cursor.fetchall()
        return records
    except sql.Error as e:
        print("Failed to retrieve records", e)
        return []
    finally:
        conn.close()


def get_all_records_database():

    conn = sql.connect("EntranceSystem.db")
    query = """
    SELECT * FROM Tracking
    ORDER BY AccessDate DESC
    """
    
    try:
        cursor = conn.execute(query)
        records = cursor.fetchall()
        return records
    except sql.Error as e:
        print("Failed to retrieve records", e)
        return []
    finally:
        conn.close()

def insert_tracking(firstname, lastname, access_date):
    conn = sql.connect("EntranceSystem.db")
    insert_command = """
    INSERT INTO Tracking (Firstname, Lastname, AccessDate)
    VALUES (?, ?, ?)
    """
    cursor= conn.execute(insert_command, (firstname, lastname, access_date))
    conn.commit()
