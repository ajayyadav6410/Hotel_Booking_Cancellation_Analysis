import hmac
from pathlib import Path

import streamlit as st
from PIL import Image

import analytics
import db

HOTEL_NAME = "Grand Demo Hotel"
IMAGE_DIR = Path(__file__).parent / "images"

st.set_page_config(
    page_title=HOTEL_NAME,
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

db.init_db()

# ---------- Top bar ----------
name_col, hi_col, link_col = st.columns([6, 1, 1])
name_col.markdown(f"### 🏨 {HOTEL_NAME}")

current_user = st.session_state.get("user")
if current_user:
    hi_col.write(f"Hi, {current_user}")
    link_col.page_link("pages/Hotel_demo.py", label="My bookings")
else:
    hi_col.page_link("pages/Hotel_demo.py", label="Login")
    link_col.page_link("pages/Hotel_demo.py", label="Sign up")

# ---------- Hero banner ----------
st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #1f4e79, #2e86c1);
                padding: 70px 30px; border-radius: 16px; text-align: center;">
        <h1 style="margin: 0; font-size: 3rem; color: white;">{HOTEL_NAME}</h1>
        <p style="font-size: 1.3rem; margin: 10px 0 0 0; color: white;">
            Comfortable rooms, a sunny pool and friendly service
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")
st.page_link("pages/Hotel_demo.py", label="Check availability and book a room", icon="🛎️")

# ---------- Rooms ----------
st.header("Our rooms")

ROOM_TEXT = {
    "Standard": ("🛏️", "Cosy room with a queen bed, AC and free Wi-Fi."),
    "Deluxe": ("🌆", "Bigger room with a city view and a work desk."),
    "Suite": ("👑", "Spacious suite with a living area and a bathtub."),
}

rooms = db.get_rooms()
room_cols = st.columns(len(rooms))
for col, (room_type, price, total) in zip(room_cols, rooms):
    icon, text = ROOM_TEXT.get(room_type, ("🛏️", "Comfortable room."))
    with col:
        with st.container(border=True):
            st.markdown(f"### {icon} {room_type}")
            st.write(text)
            st.markdown(f"**₹{price:,}** per night")
            st.caption(f"{total} room(s) in this demo")

# ---------- Facilities ----------
st.header("Facilities")

AMENITIES = [
    ("🏊", "Swimming pool", "Open every day, 7 am to 9 pm"),
    ("🅿️", "Free parking", "Covered parking for all guests"),
    ("🍽️", "Restaurant", "Breakfast, lunch and dinner"),
    ("📶", "Free Wi-Fi", "Fast Wi-Fi in all rooms"),
    ("🏋️", "Gym", "Open 24 hours"),
    ("🛎️", "24/7 front desk", "Always here to help"),
]

for start in range(0, len(AMENITIES), 3):
    cols = st.columns(3)
    for col, (icon, title, text) in zip(cols, AMENITIES[start:start + 3]):
        with col:
            with st.container(border=True):
                st.markdown(f"### {icon} {title}")
                st.write(text)

# ---------- Gallery ----------
st.header("Gallery")

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]

GALLERY = [
    ("pool", "🏊", "Swimming pool"),
    ("lobby", "🛎️", "Lobby"),
    ("room", "🛏️", "Room"),
    ("restaurant", "🍽️", "Restaurant"),
]

def find_image(name):
    for ext in IMAGE_EXTENSIONS:
        path = IMAGE_DIR / f"{name}{ext}"
        if path.exists():
            return path
    return None


def load_gallery_image(path):
    img = Image.open(path).convert("RGB")
    target_ratio = 4 / 3
    width, height = img.size
    if width / height > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))
    return img.resize((800, 600))


gallery_cols = st.columns(len(GALLERY))
for col, (name, icon, caption) in zip(gallery_cols, GALLERY):
    with col:
        image_path = find_image(name)
        if image_path:
            st.image(load_gallery_image(image_path), caption=caption)
        else:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align: center; padding: 40px 0; font-size: 3rem;'>{icon}</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"{caption} (photo coming soon)")


# ---------- Contact and footer ----------
st.divider()
st.markdown("**Contact (demo):** Demo Street, Sample City · +00 000 000 0000 · hello@example.com")
st.caption(
    "This is a fictional hotel made for a learning project. There are no real bookings or payments, "
    "and the address, phone number and email are not real."
)

# ---------- Staff area (analytics) ----------
st.write("")
with st.expander("Staff area"):
    try:
        staff_password = st.secrets["staff_password"]
    except Exception:
        staff_password = ""

    if not staff_password:
        st.info("The staff area is not set up on this computer.")
    else:
        entered = st.text_input("Staff password", type="password")
        if entered:
            if hmac.compare_digest(entered.encode(), staff_password.encode()):
                analytics.show_dashboard()
            else:
                st.error("Wrong password.")