import holidays
import calendar
from datetime import date, timedelta
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
        if country_code == "GB":
            country_holidays = holidays.country_holidays(country_code, subdiv="ENG", years=year)
        else:
            country_holidays = holidays.country_holidays(country_code, years=year)
            
        try:
            if country_code == "GB":
                country_holidays_en = holidays.country_holidays(country_code, subdiv="ENG", years=year, language="en_US")
            else:
                country_holidays_en = holidays.country_holidays(country_code, years=year, language="en_US")
        except Exception:
            country_holidays_en = {}
            
    except NotImplementedError:
        if country_name == "Qatar":
            window.alert("Bank holidays for Qatar might not be natively supported in your version of the library. Only weekends will be deducted.")
            country_holidays = {}
            country_holidays_en = {}
        else:
            window.alert(f"Bank holidays for {country_name} are not supported in your 'holidays' version.")
            return

    if country_code == "AE" and year == 2026:
            # Two-pass approach to prevent dictionary collapse
            ae_fitr_dates = [d for d, n in country_holidays.items() if "Fitr" in n]
            popped_holidays = []
            
            for d in ae_fitr_dates:
                name = country_holidays.pop(d)
                name_en = country_holidays_en.pop(d, None)
                popped_holidays.append((d, name, name_en))
                
            for d, name, name_en in popped_holidays:
                new_date = d - timedelta(days=1)
                country_holidays[new_date] = name.replace(" (estimated)", "")
                if name_en:
                    country_holidays_en[new_date] = name_en.replace(" (estimated)", "")

    half_days = set()
    if country_name == "Turkey":
        # Safely concatenate holiday names to avoid overwriting existing holidays
        ramazan_dates = [d for d, n in country_holidays.items() if any(k in n for k in ["Ramazan", "Ramadan", "Fitr"])]
        if ramazan_dates:
            r_eve = min(ramazan_dates) - timedelta(days=1)
            half_days.add(r_eve)
            existing = country_holidays.get(r_eve)
            country_holidays[r_eve] = f"{existing} / Ramazan Bayramı Arifesi" if existing else "Ramazan Bayramı Arifesi"
            
            existing_en = country_holidays_en.get(r_eve)
            country_holidays_en[r_eve] = f"{existing_en} / Eve of Eid al-Fitr" if existing_en else "Eve of Eid al-Fitr"
                
            kurban_dates = [d for d, n in country_holidays.items() if any(k in n for k in ["Kurban", "Sacrifice", "Adha"])]
            if kurban_dates:
                k_eve = min(kurban_dates) - timedelta(days=1)
                half_days.add(k_eve)
                existing = country_holidays.get(k_eve)
                country_holidays[k_eve] = f"{existing} / Kurban Bayramı Arifesi" if existing else "Kurban Bayramı Arifesi"
                
                existing_en = country_holidays_en.get(k_eve)
                country_holidays_en[k_eve] = f"{existing_en} / Eve of Eid al-Adha" if existing_en else "Eve of Eid al-Adha"
                
            oct_28 = date(year, 10, 28)
            half_days.add(oct_28)
            existing = country_holidays.get(oct_28)
            country_holidays[oct_28] = f"{existing} / Cumhuriyet Bayramı Arifesi" if existing else "Cumhuriyet Bayramı Arifesi"
            
            existing_en = country_holidays_en.get(oct_28)
            country_holidays_en[oct_28] = f"{existing_en} / Eve of Republic Day" if existing_en else "Eve of Republic Day"

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
    working_days_text = f"<p>Working Days Calculation for {year}</p>" if month_selection == "All Year" else ""
    
    title_suffix = f"({month_selection} {year})" if month_selection != "All Year" else f"({year})"
    
    results_html = f"""
        <div>
            <h2>{country_name} {title_suffix}</h2>
            {working_days_text}
        </div>
    """
    
    if month_selection == "All Year":
        results_html += "<ul>"
    
    specific_month_breakdown = ""

    for month in months_to_check:
        working_days = 0
        weekend_count = 0
        bh_weekend_count = 0
        holidays_in_month = []
        num_days = calendar.monthrange(year, month)[1]
        
        for day in range(1, num_days + 1):
            curr_date = date(year, month, day)
            is_weekend = curr_date.weekday() in weekend_days
            is_holiday = curr_date in country_holidays
            is_half_day = curr_date in half_days
            
            if is_holiday:
                h_name = country_holidays.get(curr_date)
                h_name_en = country_holidays_en.get(curr_date)
                
                if h_name_en and h_name_en != h_name:
                    h_name += f" ({h_name_en})"
                    
                if is_half_day:
                    h_name += " (Half Day)"
                    
                if is_weekend:
                    h_name += " (Falls on weekend)"
                    bh_weekend_count += 1
                holidays_in_month.append((curr_date, h_name))
            if is_weekend:
                weekend_count += 1
            
            if not is_weekend:
                if is_holiday and not is_half_day:
                    pass
                elif is_holiday and is_half_day:
                    working_days += 0.5
                else:
                    working_days += 1
                
        month_name = calendar.month_name[month]
        bh_count = len(holidays_in_month)
        
        wd_disp = int(working_days) if float(working_days).is_integer() else working_days
        
        if month_selection == "All Year":
            results_html += f"""
                <li style="margin-bottom: 10px;">
                    <strong>{month_name} ({bh_count} Bank Holidays)</strong> - {wd_disp} Working days
                </li>
            """
        else:
            results_html += f"""
                <table style="width: 100%; max-width: 350px; border-collapse: collapse; margin-bottom: 20px; font-family: sans-serif;">
                    <tr>
                        <th colspan="2" style="text-align: left; padding: 8px 0; border-bottom: 2px solid #333; font-size: 1.2em;">{month_name} Summary</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;">Total Days in Month</td>
                        <td style="text-align: right; padding: 8px 0; border-bottom: 1px solid #ddd;">{num_days}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;">Weekends</td>
                        <td style="text-align: right; padding: 8px 0; border-bottom: 1px solid #ddd;">{weekend_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;">Bank Holidays</td>
                        <td style="text-align: right; padding: 8px 0; border-bottom: 1px solid #ddd;">{bh_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;">BH on Weekends</td>
                        <td style="text-align: right; padding: 8px 0; border-bottom: 1px solid #ddd;">{bh_weekend_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Working Days</td>
                        <td style="text-align: right; padding: 8px 0; font-weight: bold;">{wd_disp}</td>
                    </tr>
                </table>
            """
        total_days += working_days
        
        if month_selection != "All Year":
            specific_month_breakdown += f"""
                <table style="width: 100%; max-width: 350px; border-collapse: collapse; font-family: sans-serif;">
                    <tr>
                        <th colspan="2" style="text-align: left; padding: 8px 0; border-bottom: 2px solid #333; font-size: 1.1em;">Bank Holidays in {month_name}</th>
                    </tr>
            """
            if holidays_in_month:
                for d, name in holidays_in_month:
                    date_fmt = f"{d.day:02d} {calendar.month_abbr[d.month]}"
                    specific_month_breakdown += f"""
                        <tr>
                            <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>{date_fmt}</strong></td>
                            <td style="text-align: right; padding: 8px 0; border-bottom: 1px solid #eee; color: #555;">{name}</td>
                        </tr>
                    """
            else:
                specific_month_breakdown += f"""
                        <tr>
                            <td colspan="2" style="padding: 8px 0; color: #666; font-style: italic;">None</td>
                        </tr>
                """
            specific_month_breakdown += "</table>"
        
    if month_selection == "All Year":
        results_html += "</ul>"
    
    if month_selection != "All Year":
        results_html += specific_month_breakdown
        
    tot_disp = int(total_days) if float(total_days).is_integer() else total_days
        
    results_html += f"""
        <div>
            <h3>Total Working Days: {tot_disp}</h3>
        </div>
    """
    
    document.getElementById("results-section").innerHTML = results_html
