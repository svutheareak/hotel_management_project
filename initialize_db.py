import sqlite3

# Connect to SQLite3 database
conn = sqlite3.connect("hotel_management.db")
conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key constraints

cursor = conn.cursor()

#   Create Rooms Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL UNIQUE,
        room_type TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        base_price REAL NOT NULL,
        discount_price REAL DEFAULT 0, 
        low_season_price REAL DEFAULT NULL,  
        high_season_price REAL DEFAULT NULL, 
        three_hour_price REAL DEFAULT NULL,  
        status TEXT DEFAULT 'Available' CHECK (status IN ('Available', 'Booked', 'Occupied')),
        image_path TEXT DEFAULT NULL  
    )
""")

#   Create Guests Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        email TEXT,
        address TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS GuestImages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        FOREIGN KEY (guest_id) REFERENCES Guests(id) ON DELETE CASCADE
    )
""")

#   Create Bookings Table (with Payment Status)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,  
        check_out_date TEXT NOT NULL, 
        check_in_time TEXT DEFAULT '12:00',  
        check_out_time TEXT DEFAULT '10:00',  
        price_type TEXT NOT NULL CHECK (price_type IN ('Normal', 'Low Season', 'High Season', '3 Hour')),
        custom_price REAL DEFAULT NULL,  --   Added custom_price for 3 Hour bookings
        payment_status TEXT CHECK (payment_status IN ('PENDING', 'HALF PAID', 'PAID')) DEFAULT 'PENDING',
        calculated_price REAL NOT NULL DEFAULT 0.0,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY(guest_id) REFERENCES Guests(id) ON DELETE CASCADE,
        FOREIGN KEY(room_id) REFERENCES Rooms(id) ON DELETE CASCADE
    );
""")

#   Prevent Booking the Same Room for Different Guests on the Same Date (Except for "3 Hour")
cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_room_booking
    ON Bookings (room_id, check_in_date)
    WHERE price_type != '3 Hour';
""")

#   Ensure Time Constraints for "3 Hour" Bookings
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_room_booking_time
    ON Bookings (room_id, check_in_date, check_in_time, check_out_time)
    WHERE price_type = '3 Hour';
""")

#   Create Guest History Table with Total Amount
cursor.execute("""
    CREATE TABLE IF NOT EXISTS GuestHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        check_out_date TEXT NOT NULL,
        total_amount REAL DEFAULT 0.0,  --   Added total_amount column
        payment_status TEXT CHECK (payment_status IN ('PENDING', 'PAID')) DEFAULT 'PENDING',
        FOREIGN KEY(guest_id) REFERENCES Guests(id) ON DELETE CASCADE,
        FOREIGN KEY(room_id) REFERENCES Rooms(id) ON DELETE CASCADE
    )
""")


#   Create Payments Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        amount_paid REAL NOT NULL,
        remaining_balance REAL DEFAULT 0,
        payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
        payment_method TEXT CHECK(payment_method IN ('Cash', 'KHQR')),
        FOREIGN KEY(booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
    )
""")

#   Create `BookingDetails` as a Table (instead of a View)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS BookingDetails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL UNIQUE,
        guest_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,  
        check_in_time TEXT DEFAULT '12:00',  
        check_out_date TEXT NOT NULL, 
        check_out_time TEXT DEFAULT '10:00',  
        calculated_price REAL NOT NULL DEFAULT 0.0,  --   Ensured calculated_price is never NULL
        payment_status TEXT CHECK (payment_status IN ('PENDING', 'HALF PAID', 'PAID')) DEFAULT 'PENDING',
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
    )
""")

#   Trigger to Auto-Insert Data into `BookingDetails` When a New Booking is Created
cursor.execute("""    
    CREATE TRIGGER insert_booking_details
    AFTER INSERT ON Bookings
    BEGIN
        INSERT INTO BookingDetails (booking_id, guest_id, room_id, check_in_date, check_in_time, check_out_date, check_out_time, calculated_price, payment_status, status)
        SELECT 
            NEW.id, NEW.guest_id, NEW.room_id, NEW.check_in_date, 
            IFNULL(NEW.check_in_time, '12:00'), 
            NEW.check_out_date, IFNULL(NEW.check_out_time, '10:00'),
            CASE 
                WHEN NEW.price_type = '3 Hour' THEN 
                    (SELECT COALESCE(NEW.calculated_price, (SELECT three_hour_price FROM Rooms WHERE id = NEW.room_id), 0))
                WHEN NEW.price_type = 'Low Season' THEN 
                    (SELECT COALESCE(base_price * 0.9, 0) FROM Rooms WHERE id = NEW.room_id)  --   Apply 10% discount
                WHEN NEW.price_type = 'High Season' THEN 
                    (SELECT COALESCE(base_price * 1.1, 0) FROM Rooms WHERE id = NEW.room_id)  --   Apply 10% increase
                ELSE 
                    (SELECT COALESCE(base_price, 0) FROM Rooms WHERE id = NEW.room_id)
            END,
            NEW.payment_status,
            NEW.status;
    END;

""")

#   Trigger to Auto-Update `BookingDetails` When a Booking is Updated
cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_booking_details
    AFTER UPDATE ON Bookings
    BEGIN
        UPDATE BookingDetails
        SET check_in_date = NEW.check_in_date,
            check_in_time = IFNULL(NEW.check_in_time, '12:00'),
            check_out_date = NEW.check_out_date,
            check_out_time = IFNULL(NEW.check_out_time, '10:00'),

            -- 🛠️ Fix Calculation of `calculated_price`
            calculated_price = CASE 
                WHEN NEW.price_type = 'Normal' THEN (SELECT base_price FROM Rooms WHERE id = NEW.room_id)
                WHEN NEW.price_type = 'Low Season' THEN (SELECT base_price * 0.9 FROM Rooms WHERE id = NEW.room_id)
                WHEN NEW.price_type = 'High Season' THEN (SELECT base_price * 1.1 FROM Rooms WHERE id = NEW.room_id)
                WHEN NEW.price_type = '3 Hour' THEN 
                    COALESCE((SELECT three_hour_price FROM Rooms WHERE id = NEW.room_id), NEW.calculated_price, 0)
                ELSE 0
            END,

            payment_status = NEW.payment_status,
            status = NEW.status
        WHERE booking_id = NEW.id;
    END;

""")

#   Trigger to Auto-Delete `BookingDetails` When a Booking is Deleted
cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS delete_booking_details
    AFTER DELETE ON Bookings
    BEGIN
        DELETE FROM BookingDetails WHERE booking_id = OLD.id;
    END;
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS RoomImages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES Rooms(id) ON DELETE CASCADE
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'user')) NOT NULL
    );
""")


#   Insert default admin user only if no employees exist
cursor.execute("""
    INSERT INTO Employees (username, password, role)
    SELECT 'admin', 'admin123', 'admin'
    WHERE NOT EXISTS (SELECT 1 FROM Employees WHERE username = 'admin');
""")





conn.commit()
conn.close()
