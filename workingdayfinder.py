import holidays
import calendar
from datetime import date
from pyscript import document, window

countries = {
    "UK": "GB",
    "Netherlands": "NL",
    "Germany": "DE",
    "Italy": "IT",
    "Spain": "ES",
    "France": "FR",
    "Poland": "PL",
    "South Africa": "ZA",
    "Turkey": "TR",
    "Dubai (UAE)": "AE",
    "Abu Dhabi (UAE)": "AE",
    "Saudi Arabia": "SA",
    "Qatar": "QA"
}

def calculate(event):
    country_name = document.getElementById("country").value
    country_code = countries[country_name]
    month_selection = document.getElementById("month").value
    
    try:
        year_str = document.getElementById("year").value
        year = int(year_str)
    except ValueError:
        window.alert("Please enter a valid numeric year.")
        return

    try:
        country_holidays = holidays.country_holidays(country_code, years=year)
    except NotImplementedError:
        if country_name == "Qatar":
            window.alert("Bank holidays for Qatar might not be natively supported in your version of the library. Only weekends will be deducted.")
            country_holidays = {}
        else:
            window.alert(f"Bank holidays for {country_name} are not supported in your 'holidays' version.")
            return

    if country_name in ["Saudi Arabia", "Qatar"]:
        weekend_days = [4, 5]
    elif country_name in ["Dubai (UAE)", "Abu Dhabi (UAE)"] and year < 2022:
        weekend_days = [4, 5]
    else:
        weekend_days = [5, 6]

    if month_selection == "All Year":
        months_to_check = range(1, 13)
    else:
        month_idx = list(calendar.month_name).index(month_selection)
        months_to_check = [month_idx]
        
    total_days = 0
    results_html = f"""
        <div>
            <h2>{country_name} ({year})</h2>
            <p>Working Days Calculation</p>
        </div>
        <ul>
    """
    
    specific_month_breakdown = ""

    for month in months_to_check:
        working_days = 0
        weekend_count = 0
        holidays_in_month = []
        num_days = calendar.monthrange(year, month)[1]
        
        for day in range(1, num_days + 1):
            curr_date = date(year, month, day)
            is_weekend = curr_date.weekday() in weekend_days
            is_holiday = curr_date in country_holidays
            
            if is_holiday:
                h_name = country_holidays.get(curr_date)
                if is_weekend:
                    h_name += " (Falls on weekend)"
                holidays_in_month.append((curr_date, h_name))
            if is_weekend:
                weekend_count += 1
            
            if not is_weekend and not is_holiday:
                working_days += 1
                
        month_name = calendar.month_name[month]
        bh_count = len(holidays_in_month)
        results_html += f"""
            <li style="margin-bottom: 15px;">
                <strong>{month_name}</strong>
                <ul style="list-style-type: disc; margin-left: 20px; margin-top: 5px;">
                    <li>Days in month: {num_days}</li>
                    <li>Weekends: {weekend_count}</li>
                    <li>Bank holidays: {bh_count}</li>
                    <li>Working days: {working_days}</li>
                </ul>
            </li>
        """
        total_days += working_days
        
        if month_selection != "All Year":
            specific_month_breakdown += f"""
                <div>
                    <h3>Breakdown for {month_name}</h3>
                    <div>
                        <span>Bank Holidays:</span>
                    </div>
            """
            if holidays_in_month:
                specific_month_breakdown += "<ul>"
                for d, name in holidays_in_month:
                    date_fmt = f"{d.day:02d} {calendar.month_abbr[d.month]}"
                    specific_month_breakdown += f"""
                        <li>
                            <span>{date_fmt}</span> - 
                            <span>{name}</span>
                        </li>
                    """
                specific_month_breakdown += "</ul>"
            else:
                specific_month_breakdown += "<p>None</p>"
            specific_month_breakdown += "</div>"
        
    results_html += "</ul>"
    
    if month_selection != "All Year":
        results_html += specific_month_breakdown
        
    results_html += f"""
        <div>
            <h3>Total Working Days: {total_days}</h3>
        </div>
    """
    
    document.getElementById("results-section").innerHTML = results_html
