import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get("https://scoreboard.clippd.com/players/18810?season=2026", headers=HEADERS, timeout=10)

soup = BeautifulSoup(response.text, "html.parser")

tr_tags = soup.find_all("tr")

def parse_date_str(date_str):
    if not date_str or not "," in date_str:
        return None, None
    
    def parse_mm_dd(mm_dd_str):
        mm_str = mm_dd_str.split(" ")[0]
        dd_str = mm_dd_str.split(" ")[1]
        
        mm = None
        match mm_str:
            case "jan": mm = 1
            case "feb": mm = 2
            case "mar": mm = 3
            case "apr": mm = 4
            case "may": mm = 5
            case "jun": mm = 6
            case "jul": mm = 7
            case "aug": mm = 8
            case "sep": mm = 9
            case "oct": mm = 10
            case "nov": mm = 11
            case "dec": mm = 12
                
        dd = None
        if dd_str:
            try:
                dd = int(dd_str)
            except ValueError:
                pass
            
        return mm, dd
    
    comma_split = date_str.split(",")
    
    day_month_str = comma_split[0].lower().strip()

    # ensure a hyphen exists in the day month string before splitting
    # events without a hyphen are one day
    if "-" in day_month_str:
        start_date_str = day_month_str.split("-")[0].lower().strip()
        end_date_str = day_month_str.split("-")[1].lower().strip()
    else:
        start_date_str = day_month_str
        end_date_str = day_month_str
    
    start_date_mm, start_date_dd = parse_mm_dd(start_date_str)
    end_date_mm, end_date_dd = parse_mm_dd(end_date_str)
    
    year_str = comma_split[1].strip()
    year = None
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            pass

    try:
        start_date = date(year, start_date_mm, start_date_dd)
        end_date = date(year, end_date_mm, end_date_dd)
        
        return start_date, end_date
    except Exception:
        print(f"Error parsing start and end date for event")
        return None, None

def parse_li_data(soup):
    li_data = {}
    data_sentry_lis = soup.find_all("li", {"data-sentry-component": "DefinitionListItem"})
    
    for li in data_sentry_lis:
        li_spans = li.find_all("span")
        if len(li_spans) >= 2:
            # clean up colons in labels
            label = li_spans[0].get_text(strip=True).replace(":", "")
            value = li_spans[1].get_text(strip=True)
            li_data[label] = value

    return li_data

def parse_events(soup, uuid):
    events = []
    
    rows = soup.find_all("tr")
    
    for row in rows:
        cells = row.find_all("td")
        
        if len(cells) < 6:
            continue
        
        try:
            info_cell = cells[0]
            span_tags = info_cell.find_all("span")
            
            name_span = span_tags[0]
            name = name_span.text.strip() if name_span else None
            if not name:
                img_tag = info_cell.find("img")
                name = img_tag.get("alt", "").strip() if img_tag else "Unknown Tournament"
                
            date_span = span_tags[1]
            date_str = date_span.text.strip() if date_span else None
            
            start_date, end_date = parse_date_str(date_str)
            
            position_cell = cells[1]
            position = position_cell.text
            field_size = None
            
            # some event rows contain the field size and position within a p tag
            position_cell_p_tag = position_cell.find("p")
            if position_cell_p_tag:
                position_cell_strings = list(position_cell_p_tag.stripped_strings)
                
                position = position_cell_strings[0]
                field_size = position_cell_strings[2]
                
            score_cell = cells[2]
            score = score_cell.text
            
            event_sg_cell = cells[3]
            event_sg_text = event_sg_cell.text.strip()
            event_sg_cleaned = re.sub(r"[^\d\.-]", "", event_sg_text)
            event_sg = float(event_sg_cleaned) if event_sg_cleaned else 0.0
            
            total_points_cell = cells[4]
            total_points_cell_p_tag = total_points_cell.find("p")
            if total_points_cell_p_tag:
                total_points_cell_strings = list(total_points_cell_p_tag.stripped_strings)

                total_points_cleaned = re.sub(r"[^\d\.-]", "", total_points_cell_strings[0])
                total_points = round(float(total_points_cleaned), 3) if total_points_cleaned else 0.0

                # ensure that the rounds string exists
                if len(total_points_cell_strings) > 1:
                    total_rounds_cleaned = re.sub(r"[^\d]", "", total_points_cell_strings[1])
                    total_rounds = int(total_rounds_cleaned) if total_rounds_cleaned else 0

            weighted_points_cell = cells[5]
            weighted_points_text = weighted_points_cell.text.strip()
            weighted_points_cleaned = re.sub(r"[^\d\.-]", "", weighted_points_text)
            weighted_points = float(weighted_points_cleaned) if weighted_points_cleaned else 0.0

            event_tuple = (
                uuid,
                name,
                position,
                field_size,
                score,
                event_sg,
                total_points,
                weighted_points,
                total_rounds,
                start_date,
                end_date
            )

            events.append(event_tuple)
        
        except Exception as e:
            print(f"Error parsing event row: {e}")

    return events


events_tuples = parse_events(soup, "3537")

li_data = parse_li_data(soup)
coach = li_data.get("Head Coach", None)
graduation_year = li_data.get("School Year", None)
print(events_tuples)
print(coach)
print(graduation_year)