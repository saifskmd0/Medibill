import sqlite3
import os

def create_or_connect_database(db_filename):
    """
    Checks if a SQLite database file exists. If it does, connects to it.
    If it doesn't, creates the database and connects to it.

    Args:
        db_filename (str): The filename of the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the database, or None if an error occurs.
    """
    try:
        conn = sqlite3.connect(db_filename)
        print(f"Connected to or created database: {db_filename}")
        return conn

    except sqlite3.Error as e:
        print(f"Error connecting to or creating database: {e}")
        return None

def create_tables(conn):
    """
    Creates the necessary tables in the database.

    Args:
        conn (sqlite3.Connection): A connection object to the database.
    """
    try:
        cursor = conn.cursor()

        # CompanyDetails Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CompanyDetails (
                company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(255),
                dl_number VARCHAR(255),
                gst_number VARCHAR(255),
                pan_number VARCHAR(255),
                registered_name VARCHAR(255),
                bank_name VARCHAR(255),
                account_number VARCHAR(255),
                ifsc_code VARCHAR(255),
                branch VARCHAR(255),
                address_line1 VARCHAR(255),
                address_line2 VARCHAR(255),
                city VARCHAR(255),
                state VARCHAR(255),
                pin_code VARCHAR(20),
                phone VARCHAR(20),
                email VARCHAR(255),
                password VARCHAR(255)
            );
        ''')

        # Products Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name VARCHAR(255),
                quantity INTEGER,
                pack VARCHAR(50),
                hsn VARCHAR(50),
                mfg_by VARCHAR(255),
                batch VARCHAR(50),
                expiry DATE,
                mrp DECIMAL(10, 2),
                rate DECIMAL(10, 2),
                sch VARCHAR(50),
                gst DECIMAL(5, 2),
                company_id INT,
                supplier_id INT,
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
            );
        ''')

        # Suppliers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name VARCHAR(255),
                address VARCHAR(255),
                phone_number VARCHAR(20),
                email VARCHAR(255)
            );
        ''')

        # Invoices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INT,
                invoice_date DATETIME,
                invoice_no INTEGER,
                sgst DECIMAL(10, 2),
                cgst DECIMAL(10, 2),
                gross DECIMAL(10, 2),
                discount DECIMAL(10, 2),
                total_amount DECIMAL(10, 2),
                payment_method VARCHAR(50),
                notes TEXT
            );
        ''')

        # Invoice_Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoice_Items (
                invoice_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no INTEGER,
                product_id INTEGER,
                company_id INT,
                product_name VARCHAR(255),
                quantity INTEGER,
                pack VARCHAR(50),
                hsn VARCHAR(50),
                mfg_by VARCHAR(255),
                batch VARCHAR(50),
                expiry DATE,
                mrp DECIMAL(10, 2),
                rate DECIMAL(10, 2),
                sch VARCHAR(50),
                gst DECIMAL(5, 2),
                amount DECIMAL(5, 2),
                FOREIGN KEY (product_id) REFERENCES Products(product_id)
            );
        ''')

        # Inventory Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Inventory (
                inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity_in_stock INTEGER,
                last_updated DATETIME,
                expiry_date DATE,
                FOREIGN KEY (product_id) REFERENCES Products(product_id)
            );
        ''')

        conn.commit()
        print("Tables created successfully.")

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

def main():
    db_filename = "pharmacy.sqlite"
    conn = create_or_connect_database(db_filename)

    if conn:
        create_tables(conn)
        conn.close()

if __name__ == "__main__":
    main()