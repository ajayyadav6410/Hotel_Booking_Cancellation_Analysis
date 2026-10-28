
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
os.makedirs("charts", exist_ok=True)

df = pd.read_csv('dataset.csv')

print(df.head())
print(df.shape)
print(df.columns)
print(df.info())
print(df.describe())
print(df.isnull().sum())
print(df.duplicated().sum())

#checking for negative values in LeadTime column

print(df["LeadTime"].min())
print((df["LeadTime"] < 0).sum())

#filtering out negative values of LeadTime 

df = df[df["LeadTime"] >= 0]
print(df.shape)

df["IsCanceled"] = df["IsCanceled"].map({"Yes":1, "No":0})
print(df["IsCanceled"].head())

#cancellation rate

print(df["IsCanceled"].unique())
cancel_rate = df["IsCanceled"].mean() * 100
print(f"Cancellation rate: {cancel_rate:.2f}%")

#deposit type and customer type cancellation rates

print(df.groupby("DepositType")["IsCanceled"].mean() * 100)
print(df.groupby("CustomerType")["IsCanceled"].mean() * 100)

deposit_cancellation_rate = df.groupby("DepositType")["IsCanceled"].mean() * 100

deposit_cancellation_rate.plot(kind="bar", color="steelblue")
plt.title("Cancellation Rate by Deposit Type")
plt.xlabel("Deposit Type")
plt.ylabel("Cancellation Rate (%)")
plt.xticks(rotation=0)
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig("charts/cancellation_by_deposit_type.png", dpi=150)
plt.show()

#Convert number to Months and how much cancallation of every month 
 
month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
               7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

df ["MonthName"] = df["ArrivalDateMonth"].map(month_names)
month_order = list(month_names.values())

monthly_rate = df.groupby("MonthName")["IsCanceled"].mean()*100
monthly_rate = monthly_rate.reindex(month_order)
print(monthly_rate)

#checking the monthly cancallation rate 

monthly_rate.plot(kind="bar", color="steelblue")
plt.title("Cancellation Rate by Month")
plt.xlabel("Month")
plt.ylabel("Cancellation Rate (%)")
plt.xticks(rotation=45)
plt.ylim(0,100)
plt.tight_layout()
plt.savefig("charts/cancellation_by_month.png", dpi=150)
plt.show()


#max and min month cancellation rate
 
print("Sabse zyada:", monthly_rate.idxmax(), round(monthly_rate.max(), 2))
print("Sabse kam:", monthly_rate.idxmin(), round(monthly_rate.min(), 2))



#booking Value of every months 

bookings_per_month = df["MonthName"].value_counts().reindex(month_order)
print(bookings_per_month)

bookings_per_month.plot(kind="bar", color="seagreen")
plt.title("Number of Bookings by Month")
plt.xlabel("Month")
plt.ylabel("Bookings")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/bookings_by_month.png", dpi=150)
plt.show()

print("Busiest:", bookings_per_month.idxmax(), bookings_per_month.max())
print("Slowest:", bookings_per_month.idxmin(), bookings_per_month.min())
print("Average:", round(bookings_per_month.mean(), 1))

# ADR(Average daily Rate) and cancellation rate by month

df["TotalNights"] = df["StaysInWeekendNights"] + df["StaysInWeekNights"]
df["Revenue"] = df["ADR"] * df["TotalNights"]

total_revenue = df["Revenue"].sum()
lost_revenue = df.loc[df["IsCanceled"] == 1, "Revenue"].sum()

print(f"Total Potential Revenue: {total_revenue:,.0f}")
print(f"Revenue lost: {lost_revenue:,.0f}")
print(f"Loss %: {lost_revenue / total_revenue * 100:.2f}%")

#lead time analysis

df["LeadTimeGroup"] = pd.cut(
    df["LeadTime"],
    bins=[0, 30, 90, 150, 365],
    labels=["0-30 days", "31-90 days","91-150 days","150+ days"],
    include_lowest=True,
    )

lead_rate = df.groupby("LeadTimeGroup", observed=True)["IsCanceled"].mean() *100
print(lead_rate)

lead_rate.plot(kind="bar", color="steelblue")
plt.title("Cancellation Rate by Lead Time")
plt.xlabel("Lead Time")
plt.ylabel("Cancellation Rate (%)")
plt.xticks(rotation=0)
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig("charts/cancellation_by_lead_time.png", dpi=150)
plt.show()

# country-wise analysis 

country_bookings = df["Country"].value_counts()
print(country_bookings)

country_rate = df.groupby("Country")["IsCanceled"].mean() * 100
print(country_rate.round(2))

country_bookings.plot(kind="bar", color="coral")
plt.title("Bookings by Country")
plt.xlabel("Country")
plt.ylabel("Bookings")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("charts/cancellation_by_country.png", dpi=150)
plt.show() 

#correlation analysis

nums_cols =["IsCanceled", "LeadTime", "ADR", "TotalNights", "Revenue", "BookingChanges", "PreviousCancellations", "TotalOfSpecialRequests"]

corr = df[nums_cols].corr()
print(corr["IsCanceled"].round(3))

sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig("charts/correlation_heatmap.png", dpi=150)
plt.show()

# print("=" * 50)
# print("KEY FINDINGS:")
# print("=" * 50)
# print(f"1. Total Bookings Analyzed: {len(df)}")
# print(f"2. Overall Cancellation Rate: {cancel_rate:.2f}%")
# print(f"3. Busiest Month: {bookings_per_month.idxmax()} with {bookings_per_month.max()} bookings")
# print(f"4. Revenue Lost Due to Cancellations: {lost_revenue:,.0f} ({lost_revenue / total_revenue * 100:.2f}% of potential revenue)")
# print(f"5. Strongest Correlation with Cancellations: {corr['IsCanceled'].drop('IsCanceled').abs().idxmax()}")

#Market segments Booking Analyze 

segment_counts = df["MarketSegment"].value_counts()
print(segment_counts)

segment_counts.plot(kind="pie", autopct="%1.1f%%")
plt.title("Bookings by Market Segment")
plt.ylabel("")
plt.tight_layout()
plt.savefig("charts/bookings_by_market_segment.png", dpi=150)
plt.show()

segment_rate = df.groupby("MarketSegment")["IsCanceled"].mean() * 100
print(segment_rate.round(2))

#ADR (Average daily Rate)  per month Analysis

adr_month = df.groupby("MonthName")["ADR"].mean().reindex(month_order)
print(adr_month.round(1))

adr_month.plot(kind="line", color="orange")
plt.title("Average ADR by Month")
plt.xlabel("Month")
plt.ylabel("ADR")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/adr_by_month.png", dpi=150)
plt.show()

#ADR StatusCheck 
adr_status = df.groupby("IsCanceled")["ADR"].mean()
print(adr_status.round(2))

#Cancellation Bookings by Top countries 

cancelled_data = df[df["IsCanceled"] == 1]
cancelled_countries = cancelled_data["Country"].value_counts().head(10)
print(cancelled_countries)

cancelled_countries.plot(kind="pie", autopct="%1.1f%%")
plt.title("Cancelled bookings by Country")
plt.ylabel("")
plt.tight_layout()
plt.savefig("charts/cancelled_bookings_by_country.png", dpi=150)
plt.show()

#hypothesis Analysis ( if Price rate high then cancellation rate is more than high )

df["ADRGroup"] = pd.qcut(df["ADR"], 4, labels=["Low", "Medium", "High", "Very High"])
adr_group_rate = df.groupby("ADRGroup", observed=True)["IsCanceled"].mean() * 100

print(adr_group_rate.round(2))

#if waiting list is long then cancellation rate is more than high

df["WaitGroup"] = pd.cut(df["DaysInWaitingList"], bins=[-1, 0, 3, 7],
                         labels=["0 days", "1-3 days", "4-7 days"])
wait_rate = df.groupby("WaitGroup", observed=True)["IsCanceled"].mean() * 100

print(wait_rate.round(2))
print(df["WaitGroup"].value_counts())

#final key findings and summary of the analysis
print("=" * 55)
print("KEY FINDINGS")
print("=" * 55)
print(f"1. Total bookings analysed: {len(df)}")
print(f"2. Overall cancellation rate: {cancel_rate:.2f}%")
print(f"3. Busiest month: {bookings_per_month.idxmax()} ({bookings_per_month.max()} bookings)")
print(f"4. Slowest month: {bookings_per_month.idxmin()} ({bookings_per_month.min()} bookings)")
print(f"5. Revenue lost to cancellations: {lost_revenue:,.0f} ({lost_revenue / total_revenue * 100:.2f}%)")
print(f"6. Strongest correlation with cancellation: {corr['IsCanceled'].drop('IsCanceled').abs().idxmax()}")
print("7. Hypothesis 1 (higher price -> more cancellation): not supported")
print("8. Hypothesis 2 (longer waiting list -> more cancellation): not supported")

