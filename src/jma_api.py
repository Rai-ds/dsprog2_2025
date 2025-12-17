import requests
import datetime

# Endpoints
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
ICON_BASE_URL = "https://www.jma.go.jp/bosai/forecast/img/"

def get_area_data():
    """Fetches area definitions."""
    try:
        response = requests.get(AREA_URL)
        response.raise_for_status()
        data = response.json()
        
        centers = data.get("centers", {})
        offices = data.get("offices", {})
        structured = {}

        for c_code, c_info in centers.items():
            r_name = c_info.get("name")
            children = c_info.get("children", [])
            structured[r_name] = {}
            for o_code in children:
                if o_code in offices:
                    o_name = offices[o_code].get("name")
                    structured[r_name][o_name] = o_code
        return structured
    except Exception as e:
        print(f"Error area data: {e}")
        return {}

def _fmt_date(iso_str):
    """Convert '2025-12-17T17:00...' to '2025-12-17'"""
    try:
        return datetime.datetime.fromisoformat(iso_str).strftime("%Y-%m-%d")
    except:
        return iso_str

def get_weather_forecast(area_code):
    """
    Robust fetcher that handles JMA evening updates where 'Today's' Min/Max 
    disappears from the Weekly report.
    """
    url = FORECAST_URL_TEMPLATE.format(area_code=area_code)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data: return []

        # --- 1. Basic Setup from Report 0 (Weather/Icons) ---
        report0 = data[0]
        try:
            ts_weather = report0["timeSeries"][0]
            dates = ts_weather["timeDefines"]
            area_data = ts_weather["areas"][0]
            codes = area_data.get("weatherCodes", [])
            texts = area_data.get("weathers", [])
        except:
            return [] # Malformed data

        forecast_map = {}
        
        for i, d_iso in enumerate(dates):
            d_key = _fmt_date(d_iso)
            code = codes[i] if i < len(codes) else "100"
            text = texts[i] if i < len(texts) else ""
            
            forecast_map[d_key] = {
                "date": d_key,
                "weather": text,
                "icon": f"{ICON_BASE_URL}{code}.svg",
                "min": "-", 
                "max": "-" 
            }

        # --- 2. Try Getting Min/Max from Report 1 (Weekly) ---
        # This usually has the best data for Tomorrow/Day After
        if len(data) > 1:
            try:
                report1 = data[1]
                for ts in report1["timeSeries"]:
                    # Find the series with temps
                    if "tempsMin" in ts["areas"][0] or "tempsMax" in ts["areas"][0]:
                        t_dates = ts["timeDefines"]
                        t_mins = ts["areas"][0].get("tempsMin", [])
                        t_maxs = ts["areas"][0].get("tempsMax", [])
                        
                        for i, d_iso in enumerate(t_dates):
                            d_key = _fmt_date(d_iso)
                            if d_key in forecast_map:
                                # Only overwrite if value is valid (not empty string or None)
                                val_min = t_mins[i] if i < len(t_mins) else ""
                                val_max = t_maxs[i] if i < len(t_maxs) else ""
                                
                                if val_min and val_min != "": forecast_map[d_key]["min"] = val_min
                                if val_max and val_max != "": forecast_map[d_key]["max"] = val_max
            except: pass

        # --- 3. FIX: Fallback for "Today" using Report 0 (3-Hour Temps) ---
        # If we are in the evening, Report 1 often skips "Today". 
        # We check Report 0 for any remaining temperature data.
        try:
            # Usually index 2 in timeSeries has the 3-hour temps
            if len(report0["timeSeries"]) >= 3:
                ts_temps = report0["timeSeries"][2]
                if "temps" in ts_temps["areas"][0]:
                    t_dates = ts_temps["timeDefines"]
                    t_vals = ts_temps["areas"][0]["temps"]
                    
                    # Group temps by day
                    day_temps = {}
                    for i, d_iso in enumerate(t_dates):
                        d_key = _fmt_date(d_iso)
                        if d_key not in day_temps: day_temps[d_key] = []
                        # JMA temps are strings, convert to float for comparison, ignore non-digits
                        try:
                            day_temps[d_key].append(float(t_vals[i]))
                        except: pass
                    
                    # Fill in missing "-" in our main map
                    for d_key, temps in day_temps.items():
                        if d_key in forecast_map:
                            current_max = forecast_map[d_key]["max"]
                            
                            # If Max is missing, use the highest value from the 3-hour forecast
                            if current_max == "-" and temps:
                                forecast_map[d_key]["max"] = str(int(max(temps)))
                                
                            # Note: We rarely get a true "Min" for the passed morning from this, 
                            # so we leave Min as "-" if it's missing. This is correct for evening.
        except: pass

        return sorted(forecast_map.values(), key=lambda x: x["date"])

    except Exception as e:
        print(f"API Error: {e}")
        return []