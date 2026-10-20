import re
import csv
import json
import sqlite3
import datetime
import threading
from pathlib import Path
from scraper import search_city, get_next_page
from random import uniform


from bs4 import BeautifulSoup as bts
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright
from dateutil.relativedelta import relativedelta
from loguru import logger

file_logger = Path(__file__).parent / "logger.log"

logger.remove()
logger.add(file_logger, level='WARNING', rotation='1 MB')

remaining_seconds = 0
overtime_seconds = 0
timer_generation = 0
timer_active = False


def save_location(city, format, arriving, depart):
    """Generates and returns the standardized file path in the user's Downloads directory 
    for saving the scraped Airbnb listings based on the city and format.
    """
    town = city.upper()
    downloads_folder = Path.home() / "Downloads"
    downloads_folder.mkdir(parents=True, exist_ok=True)
    file = downloads_folder / fr"Airbnb_{town}_({arriving}__{depart}).{format}"
    return file


def get_listings_data(html: str) -> list:   
    """Parses the HTML content of the search results page using BeautifulSoup 
    to extract listing titles, prices, ratings, and structural details.
    """
    soup = bts(html, "html.parser")
    all_locations = soup.select('div[data-testid="card-container"]')
    listings = []
    
    for location in all_locations:
        title_article = location.select_one("div[data-testid='listing-card-title']")
        title = title_article.text.strip() if title_article else "Airbnb Location"

        rating_elem = location.select_one('[data-testid="listing-card-title"] + div >span span:last-of-type')
        rating = 0.0
        if rating_elem:
            match_rating = re.search(r"(\d+[\.,]\d+)", rating_elem.text)
            if match_rating:
                rating = float(match_rating.group(1).replace(",", "."))

        price_html = location.select("button")[-1].select("span")[-1]
        price_val = 0
        price_final = ""
        if price_html:
            dirty_price = re.sub(r"[\xa0\u202f]", "", price_html.get_text(strip=True))
            match = re.search(r"([€$])?\s*(\d+[\d,\.]*)\s*([€$])?", dirty_price)
            if match:
                symbole = match.group(1) if match.group(1) else match.group(3)
                if not symbole:
                    symbole = ""
                price_str = match.group(2)
                price_clean = price_str.replace(",", "").replace(".", "") 
                price_val = int(price_clean)
                
                if match.group(3):
                    price_final = f"{price_val} {symbole}".strip()
                else:
                    price_final = f"{symbole}{price_val}".strip()

        subtitles = location.select('div[data-testid="listing-card-subtitle"]')

        try:

            details_article = subtitles[0]
            details = details_article.text

            layout_el = subtitles[1].text

            layout_no_space= layout_el.replace("\xa0", " ").replace("·", "")
            layout_no_duplicates = [l.strip() for l in layout_no_space.split(",")]

            unique_result = []
            for el in layout_no_duplicates:
                m = re.match(r"(.+?)\1+$", el)
                if m:
                    unique_result.append(m.group(1).strip())
                else:
                    unique_result.append(el)

            layout = ", ".join(unique_result)
                            
        except IndexError:
            layout='SWW' 
            logger.error('Index out of range')
        except AttributeError:
            layout='SWW'
            logger.error('Attribute error')
        except TypeError:
            layout='SWW'
            logger.error('Type error')
        except Exception as e:
            layout='SWW'
            logger.error(f'Unexpected error: {str(e)}')

    
        if price_val > 0:
            listings.append({
                "TITLE": title,
                "DETAILS": details,
                "LAYOUT": layout,
                "PRICE": price_final,
                "RATING": rating,
            })
            
    return listings

def update_countdown(app_instance, label_timer, generation):
    """Handles the graphical countdown timer displayed on the UI while the scraping 
    process is running in the background thread.
    """
    global remaining_seconds, overtime_seconds
    if not timer_active or generation != timer_generation:
        return

    if remaining_seconds > 0:
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        label_timer.configure(text=f"⏱ Estimated time: {minutes:02d}:{seconds:02d}")
        remaining_seconds -= 1
    else:
        overtime_seconds += 1
        minutes = overtime_seconds // 60
        seconds = overtime_seconds % 60
        label_timer.configure(
            text=f"⏱ Scraping finishing up... (+{minutes:02d}:{seconds:02d})"
        )

    app_instance.after(
        1000, lambda: update_countdown(app_instance, label_timer, generation)
    )



def main(city,
        arriving,
        depart,
        is_headless, 
        menu_format, 
        stepper_adults, 
        stepper_kids, 
        stepper_pets, 
        textbox, 
        label_timer, 
        start_button, 
        app_instance
):
    """Main scraping orchestrator using Playwright. Manages browser context, 
    pagination loops, data extraction, sorting, console display, and file export 
    (CSV, JSON, or SQLite).
    """
    all_listings = []
    ua = UserAgent()


    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=is_headless)
        try:
            context = browser.new_context(
                user_agent=ua.random,
                locale="en-US",
                timezone_id="America/New_York",
                extra_http_headers={"Accept-Language": "en-US, en;q=0.9"}
            )

    
            page = context.new_page()
            
            html = search_city(page, city, arriving, depart, stepper_adults, stepper_kids, stepper_pets)
             

            while True:
                all_listings.extend(get_listings_data(html))
                page.wait_for_timeout(uniform(1000, 2000))           

                new_page = get_next_page(page)
                if not new_page:
                    break
                html = new_page
        finally:
            browser.close()

    global remaining_seconds, timer_active
    remaining_seconds = 0 

    seen_titles = set()
    unique_listings = []
    for item in all_listings:
        identifier = (item["TITLE"], item["PRICE"])
        if identifier not in seen_titles:
            seen_titles.add(identifier)
            unique_listings.append(item)
    all_listings = unique_listings


    if all_listings:
        cheapest_3 = sorted(all_listings, key=lambda x: int(re.sub(r"\D", "", x["PRICE"])))[:3]
        best_rated_3 = sorted(all_listings, key=lambda x: x["RATING"], reverse=True)[:3]

        textbox.insert("end", "\n=== 💰 TOP 3 Cheapest locations ===\n")
        for item in cheapest_3:
            textbox.insert("end", f"• {item['TITLE'][:30]}... : {item['PRICE']}\n")

        textbox.insert("end", "\n=== ⭐ TOP 3 Best rated locations ===\n")
        for item in best_rated_3:
            textbox.insert("end", f"• {item['TITLE'][:30]}... : {item['RATING']}/5★ ({item['PRICE']})\n")

        textbox.insert("end", f"\nAVERAGE PRICE = {round(sum(int(re.sub(r'\D', '', item['PRICE'])) for item in all_listings) / len(all_listings))}\n")
    else:
        textbox.insert("end", "\n❌ Aucun logement trouvé.\n")

    format_choice = menu_format.get()
    file = save_location(city, format_choice.lower(), arriving, depart)

    if format_choice == "CSV":
        fieldnames = ["TITLE", "DETAILS", "LAYOUT", "PRICE", "RATING"]
        try:
            with open(file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                writer.writerows(all_listings)
        except PermissionError:
            textbox.insert("end", "\n❌ Error: Please close the CSV file if it's currently open in Microsoft Excel!\n")

        textbox.insert("end", f"\nA file named 'Airbnb_{city.upper()}_({arriving}__{depart}).csv' has been saved in your Downloads folder.\n")


    elif format_choice == "JSON":
        try:
            with open(file, "w", encoding='utf-8-sig') as f:
                json.dump(all_listings, f, ensure_ascii=False, indent=4)
        except PermissionError:
            textbox.insert("end", "\n❌ ERROR: Please close the JSON file if open.\n")
        textbox.insert("end", f"\nA file named 'Airbnb_{city.upper()}_({arriving}__{depart}).json' has been saved in your Downloads folder.\n")

            
    else: # SQLite
        file = save_location(city, "db")
        with sqlite3.connect(file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS Airbnb_{city}")
            cursor.execute(
                f"""
                CREATE TABLE Airbnb_{city}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    TITLE TEXT,
                    DETAILS TEXT,
                    LAYOUT TEXT,
                    PRICE INTEGER,
                    RATING TEXT
                )
                """
            )
            
            data = [(item["TITLE"], item["DETAILS"], item["LAYOUT"], item["PRICE"], item["RATING"]) for item in all_listings]
            cursor.executemany(
                f"INSERT INTO Airbnb_{city} (TITLE, DETAILS, LAYOUT, PRICE, RATING) VALUES (?, ?, ?, ?, ?)",
                data,
            )
        textbox.insert("end", f"\nA file named 'Airbnb_{city.upper()}_({arriving}__{depart}).db' has been saved in your Downloads folder.\n")


    timer_active = False
    app_instance.after(
        0,
        lambda: (
            label_timer.configure(text="✅ Scraping ended successfully!"),
            start_button.configure(state="normal", text="Start Scraping"),
        ),
    )


def run_main(city, arriving, depart, is_headless, menu_format, stepper_adults,
             stepper_kids, stepper_pets, textbox, label_timer, start_button,
             app_instance):
    """Runs the scraper and reports failures without leaving the timer active."""
    global timer_active
    try:
        main(
            city, arriving, depart, is_headless, menu_format, stepper_adults,
            stepper_kids, stepper_pets, textbox, label_timer, start_button,
            app_instance,
        )
    except Exception as e:
        logger.exception("Scraping failed")
        print(e)
        timer_active = False
        app_instance.after(
            0,
            lambda: (
                label_timer.configure(text="❌ Scraping failed. Check logger.log."),
                start_button.configure(state="normal", text="Start Scraping"),
            ),
        )



def start_primary_thread(app_instance, entry_city, arrival_date, depart_date, 
                        switch_headless, menu_format, stepper_adults, stepper_kids, 
                        stepper_pets, label_result1, label_result2, label_timer, textbox, start_button):
    
    """Validates user inputs (city and dates), updates the UI state, triggers 
    the countdown timer, and spawns a background thread to run the main scraper.
    """
    city = entry_city.get()
    if not city.replace(" ", "").replace("-", "").isalpha():
        label_result1.configure(text="Invalid City", text_color="red")
        return
    label_result1.configure(text=f"Search for city: {city}", text_color="green")

    today_date = datetime.date.today()
    date1 = arrival_date.get_date()
    date2 = depart_date.get_date()
    condition = today_date + relativedelta(years=1, months=11, days=25)
    
    if date1 < today_date or date2 > condition or date2 <= date1:
        label_result2.configure(text="Invalid dates...", text_color="red")
        return    
    label_result2.configure(text="Valid dates...", text_color="green")


    textbox.insert("end", "▶ Starting Scraping...\n")
    start_button.configure(state="disabled", text="Scraping in progress...")

    global remaining_seconds, overtime_seconds, timer_generation, timer_active
    remaining_seconds = 120
    overtime_seconds = 0
    timer_generation += 1
    timer_active = True
    update_countdown(app_instance, label_timer, timer_generation)

    arriving = arrival_date.get()
    depart = depart_date.get()
    is_headless = bool(switch_headless.get())

    thread = threading.Thread(
        target=run_main, 
        args=(city, arriving, depart, is_headless,
            menu_format, stepper_adults, stepper_kids,
            stepper_pets, textbox, label_timer, start_button, app_instance), 
        daemon=True
    )
    thread.start()