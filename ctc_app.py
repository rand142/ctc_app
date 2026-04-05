import streamlit as st
import pandas as pd
import holidays

class CTCCalculator:
    def __init__(self, annual_ctc, start_date, end_date, country="ZA"):
        self.annual_ctc = annual_ctc
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.country = country
        self.daily_rate = annual_ctc / 365.0

    def get_working_days(self):
        all_days = pd.date_range(self.start_date, self.end_date, freq="D")
        weekdays = all_days[~all_days.weekday.isin([5, 6])]
        holiday_list = holidays.country_holidays(self.country, years=range(self.start_date.year, self.end_date.year+1))
        working_days = [day for day in weekdays if day not in holiday_list]
        return pd.DatetimeIndex(working_days)

    def breakdown(self):
        working_days = self.get_working_days()
        total_working_days = len(working_days)
        total_ctc = total_working_days * self.daily_rate

        monthly_breakdown = (
            pd.Series(working_days)
            .groupby(working_days.to_period("M"))
            .count()
            .apply(lambda d: d * self.daily_rate)
        )

        return {
            "total_working_days": total_working_days,
            "total_ctc": round(total_ctc, 2),
            "monthly_breakdown": monthly_breakdown.round(2).to_dict()
        }

# Streamlit UI
st.title("💰 Cost-to-Company (CTC) Calculator")

annual_ctc = st.number_input("Enter Annual CTC (ZAR)", min_value=0, value=600000, step=1000)
start_date = st.date_input("Start Date", pd.to_datetime("2026-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2026-12-31"))
country = st.text_input("Country Code (default ZA)", "ZA")

if st.button("Calculate"):
    calc = CTCCalculator(annual_ctc, start_date, end_date, country)
    result = calc.breakdown()

    st.subheader("📊 Results")
    st.write(f"**Total Working Days:** {result['total_working_days']}")
    st.write(f"**Total CTC (Working Days Only):** ZAR {result['total_ctc']}")

    st.subheader("📅 Monthly Breakdown")
    monthly_df = pd.DataFrame(list(result["monthly_breakdown"].items()), columns=["Month", "CTC"])
    st.table(monthly_df)
    st.bar_chart(monthly_df.set_index("Month"))
