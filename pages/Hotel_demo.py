import time
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import db

st.set_page_config(page_title="Hotel Demo", layout="centered")

db.init_db()

if "user" not in st.session_state:
    st.session_state.user = None


st.title("Hotel Demo")
st.caption(

    "Demo only. Please do not use a real password or any personal details. "
    "No real payment is taken on this site."
)


# ----- Login / Sign up (shown only when nobody is logged in) ----------

if st.session_state.user is None:
    login_tab, signup_tab = st.tabs(["Login", "Sign up"])

    with login_tab:

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Login")


        if login_clicked:

            clean_name = username.strip().lower()
            if db.check_login(clean_name, password):
                st.session_state.user = clean_name
                st.rerun()
            else:
                st.error("Wrong username or password.")

    with signup_tab:

        with st.form("signup_form"):

            new_username = st.text_input("Choose a username")
            new_password = st.text_input("Choose a password (do not reuse a real one)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            signup_clicked = st.form_submit_button("Create account")

        if signup_clicked:

            clean_name = new_username.strip().lower()
            if len(clean_name) < 3:
                st.error("Username must be at least 3 characters.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif db.create_user(clean_name, new_password):
                st.success("Account created. Now go to the Login tab.")
            else:
                st.error("This username is already taken.")

    st.stop()

# ---------- Logged-in area ----------
user = st.session_state.user
st.success(f"Logged in as {user}")

if st.button("Log out"):
    st.session_state.user = None
    st.rerun()

# One-time message (shown once after booking or cancelling)
if st.session_state.get("flash"):
    kind, text = st.session_state.pop("flash")
    if kind == "success":
        st.success(text)
    else:
        st.error(text)

# ---------- Book a room ----------
st.divider()
st.subheader("Book a room")

room_info = {r[0]: {"price": r[1], "total": r[2]} for r in db.get_rooms()}

room_type = st.selectbox("Room type", list(room_info.keys()))
guests = st.number_input("Guests", min_value=1, max_value=4, value=2)
check_in = st.date_input("Check-in", value=date.today() + timedelta(days=7), min_value=date.today())
check_out = st.date_input("Check-out", value=date.today() + timedelta(days=9), min_value=date.today())

nights = (check_out - check_in).days
rooms_available = 0

if nights < 1:
    st.warning("Check-out must be after check-in.")
else:
    price = room_info[room_type]["price"]
    rooms_available = db.rooms_left(room_type, check_in, check_out)
    st.write(f"{nights} night(s) x ₹{price:,} = **₹{nights * price:,}**")
    if rooms_available > 0:
        st.info(f"{rooms_available} of {room_info[room_type]['total']} {room_type} room(s) available for these dates.")
    else:
        st.error(f"No {room_type} rooms available for these dates. Try other dates or another room type.")

if st.button("Book now", disabled=(rooms_available < 1)):
    ok, message = db.book_room(user, room_type, check_in, check_out, int(guests))
    st.session_state.flash = ("success" if ok else "error", message)
    st.rerun()


# ---------- My bookings ----------
st.divider()
st.subheader("My bookings")

rows = db.get_user_bookings(user)
if rows:
    my_df = pd.DataFrame(
        rows,
        columns=["ID", "Room", "Check-in", "Check-out", "Guests", "Nights", "Total (₹)", "Status", "Payment"],
    )
    st.dataframe(my_df, hide_index=True)

    # ----- Pay (demo) -----
    unpaid = [r for r in rows if r[7] == "Confirmed" and r[8] == "Unpaid"]
    if unpaid:
        st.subheader("Pay for a booking (demo)")
        pay_id = st.selectbox("Booking to pay for (ID)", [r[0] for r in unpaid])
        amount = next(r[6] for r in unpaid if r[0] == pay_id)
        method = st.radio("Payment method", ["💳 Card", "📱 UPI", "🏦 Net banking"], horizontal=True)
        st.caption("Demo only: no card, UPI or bank details are asked for, and no money moves.")
        if st.button(f"Pay ₹{amount:,} (demo)"):
            with st.spinner("Processing demo payment..."):
                time.sleep(1)
            if db.pay_booking(pay_id, user):
                st.session_state.flash = (
                    "success",
                    f"Demo payment of ₹{amount:,} received via {method} (no real money moved).",
                )
            else:
                st.session_state.flash = ("error", "Could not complete this demo payment.")
            st.rerun()

    # ----- Cancel -----
    confirmed_ids = [r[0] for r in rows if r[7] == "Confirmed"]
    if confirmed_ids:
        cancel_id = st.selectbox("Cancel a booking (ID)", confirmed_ids)
        if st.button("Cancel selected booking"):
            if db.cancel_booking(cancel_id, user):
                st.session_state.flash = ("success", f"Booking {cancel_id} cancelled.")
            else:
                st.session_state.flash = ("error", "Could not cancel this booking.")
            st.rerun()
else:
    st.write("You have no bookings yet.")