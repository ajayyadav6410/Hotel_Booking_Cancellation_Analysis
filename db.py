import hashlib
import hmac
import os
import sqlite3

DB_PATH = "Hotel_demo.db"

def run_query(sql, params=(), fetch=False):
    conn =  sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        return rows
    finally:
        conn.close()


def init_db():
    run_query(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
        """
    )
    run_query(
        """
        CREATE TABLE IF NOT EXISTS rooms (
            room_type TEXT PRIMARY KEY,
            price_per_night INTEGER NOT NULL,
            total_rooms INTEGER NOT NULL
        )
        """
    )
    run_query(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            room_type TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            guests INTEGER NOT NULL,
            nights INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Confirmed',
            payment_status TEXT NOT NULL DEFAULT 'Unpaid',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    for room_type, price, total in [("Standard", 3000, 3), ("Deluxe", 4500, 2), ("Suite", 7000, 1)]:
        run_query(
            "INSERT OR IGNORE INTO rooms (room_type, price_per_night, total_rooms) VALUES (?, ?, ?)",
            (room_type, price, total),
        )



def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt.hex(), digest.hex()



def create_user(username, password):
    salt_hex, password_hash = hash_password(password)
    try:
        run_query(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt_hex),
        )
        return True
    except sqlite3.IntegrityError:
        return False


def check_login(username, password):
    rows = run_query(
        "SELECT password_hash, salt FROM users WHERE username = ?",
        (username,),
        fetch=True,

    )

    if not rows:
        return False
    stored_hash, salt_hex = rows[0]
    _, new_hash = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(stored_hash, new_hash)



def get_rooms():
    return run_query(
        "SELECT room_type, price_per_night, total_rooms FROM rooms ORDER BY price_per_night",
        fetch=True,
    )


def rooms_left(room_type, check_in, check_out):
    rooms = run_query(
        "SELECT total_rooms FROM rooms WHERE room_type = ?", (room_type,), fetch=True
    )
    if not rooms:
        return 0
    taken = run_query(
        """
        SELECT COUNT(*) FROM bookings
        WHERE room_type = ? AND status = 'Confirmed'
          AND check_in < ? AND check_out > ?
        """,
        (room_type, check_out.isoformat(), check_in.isoformat()),
        fetch=True,
    )[0][0]
    return rooms[0][0] - taken


def book_room(username, room_type, check_in, check_out, guests):
    nights = (check_out - check_in).days
    if nights < 1:
        return False, "Check-out must be after check-in."

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("BEGIN IMMEDIATE")
        room = conn.execute(
            "SELECT price_per_night, total_rooms FROM rooms WHERE room_type = ?",
            (room_type,),
        ).fetchone()
        if room is None:
            conn.rollback()
            return False, "Unknown room type."
        price, total_rooms = room

        taken = conn.execute(
            """
            SELECT COUNT(*) FROM bookings
            WHERE room_type = ? AND status = 'Confirmed'
              AND check_in < ? AND check_out > ?
            """,
            (room_type, check_out.isoformat(), check_in.isoformat()),
        ).fetchone()[0]
        if taken >= total_rooms:
            conn.rollback()
            return False, f"Sorry, no {room_type} rooms are available for these dates."

        total_price = nights * price
        conn.execute(
            """
            INSERT INTO bookings
                (username, room_type, check_in, check_out, guests, nights, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (username, room_type, check_in.isoformat(), check_out.isoformat(),
             guests, nights, total_price),
        )
        conn.commit()
        return True, f"Booking confirmed: {nights} night(s), total ₹{total_price:,}."
    finally:
        conn.close()


def get_user_bookings(username):
    return run_query(
        """
        SELECT id, room_type, check_in, check_out, guests, nights, total_price, status, payment_status
        FROM bookings WHERE username = ? ORDER BY id DESC
        """,
        (username,),
        fetch=True,
    )

def cancel_booking(booking_id, username):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            """
            UPDATE bookings
            SET status = 'Cancelled',
                payment_status = CASE
                    WHEN payment_status = 'Paid (demo)' THEN 'Refunded (demo)'
                    ELSE payment_status
                END
            WHERE id = ? AND username = ? AND status = 'Confirmed'
            """,
            (booking_id, username),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def pay_booking(booking_id, username):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            """
            UPDATE bookings SET payment_status = 'Paid (demo)'
            WHERE id = ? AND username = ?
              AND status = 'Confirmed' AND payment_status = 'Unpaid'
            """,
            (booking_id, username),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
        