# Hotel Booking Cancellation Analysis 
**Live demo:** (link will be added after hosting)

## Problem Statement
Hotel Ki Sbse Jayda Bookings Cancel ho rahi hai, jisse revenue ka loss hota hai.
Is this project , maine Cancellation ke patterns aur revenue Loss Analyse kiye.

## dataset 
- 10,000 bookings .28 columns (LeadTime, ADR, DepositType, Country, MarketSegment, etc.)
- Cleaning ke baad 9,770 rows (230 invalid negative LeadTime rows hataye)

## Research Questions 
1. How many bookings were cancelled, and how much revenue was lost?
2. Do factors such as the month, deposit type, country, market segment, or lead time affect cancellations?
3. Are cancellation rates higher when prices are higher or when there is a long waiting list?

## Tools 
Python, pandas, matplotlib, seaborn, Streamlit, SQLite
Os for save image 

## Steps 
1. Data load aur exploration (missing values, duplicates, data types)
2. Cleaning: invalid LeadTime hataya, IsCanceled ko 1/0 banaya
3. Feature engineering: TotalNights, Revenue, LeadTimeGroup, ADRGroup
4. Analysis: month, deposit type, customer type, market segment, country, lead time
5. Hypothesis testing aur correlation analysis


## Key Findings
- Cancellation rate: 90.16%
- Busiest month: May (892 bookings), slowest: February (749)
- Revenue lost to cancellations: 4,424,323 (90.41% of potential revenue)
- Cancellation rate month, deposit type, customer type, market segment, country aur lead time, sab mein 88-92% ke beech rahi
- Cancel hui aur na hui bookings ka average ADR lagbhag same (99.86 vs 98.86)
- Dono hypotheses (zyada price, lambi waiting list) ko data ka strong support nahi mila
- Koi numeric column cancellation se strongly correlated nahi (sab -0.02 se +0.02)


## Charts 

### Cancellation by Deposit Type
![Cancellation by Deposit Type](charts/cancellation_by_deposit_type.png)

### Cancellation by Month
![Cancellation by Month](charts/cancellation_by_month.png)

### Bookings by Month
![Bookings by Month](charts/bookings_by_month.png)

### Cancellation by Lead Time
![Cancellation by Lead Time](charts/cancellation_by_lead_time.png)

### Bookings by Market Segment
![Bookings by Market Segment](charts/bookings_by_market_segment.png)

### Correlation Heatmap
![Correlation Heatmap](charts/correlation_heatmap.png)

### Average ADR by Month
![Average ADR by Month](charts/adr_by_month.png)

### Cancelled Bookings by Country
![Cancelled Bookings by Country](charts/cancelled_bookings_by_country.png)







## Inspiration
I followed the structure of a YouTube tutorial on end-to-end data analysis projects. I wrote the code and did the analysis myself on my own dataset.

## Limitations
- The cancellation rate in this dataset is about 90%, which is much higher than what real hotels usually see.
- No factor (month, deposit type, country, lead time, price) showed a clear link with cancellations. All groups stayed between 88% and 92%.
- The dataset has no hotel type (City/Resort) or booking date columns, so I could not compare hotels or look at trends over time.
- Some groups are small (for example, only 174 bookings had a waiting list of4 to 7 days), so those numbers are not reliable.


## Project structure
```
app.py                    Home page of the demo hotel and a password-protected staff area
analytics.py              Cancellation dashboard (filters, KPIs, charts, insights)
db.py                     SQLite helpers (users, rooms, bookings)
pages/Hotel_demo.py       Sign up, login, booking, demo payment, cancel
images/                   Hotel photos
hotel_booking_project.py  The original analysis script
dataset.csv               Booking data
requirements.txt          Python libraries
```

## Interactive app (Streamlit)
- **Home page:** a simple hotel website with rooms, facilities and a photo gallery.
- **Hotel demo page:** sign up and login, room availability check, booking, a demo payment step and cancelling a booking.
- **Staff area (bottom of the home page):** the cancellation dashboard. The password only hides it from casual visitors. It is not real security, because the code and data are public.

### Run it on your computer
1. `pip install -r requirements.txt`
2. Create `.streamlit/secrets.toml` with `staff_password = "your-demo-password"` (this file is not in the repository).
3. `python -m streamlit run app.py`

## Notes about the demo
- This is a fictional hotel made for learning. No real payment is taken, and the app never asks for card, UPI or bank details.
- Passwords are stored as salted hashes (PBKDF2) in a local SQLite file. There is no email check or password reset, so please do not use a real password.
- Availability is checked by looking for overlapping confirmed bookings of the same room type. The check and the booking happen in one database transaction.
- The login is lost when the page is refreshed.
- On free hosting the database file may be reset when the app restarts, so bookings can disappear.
- Room types, prices and the number of rooms are made up.

