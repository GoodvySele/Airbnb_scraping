# Airbnb Desktop Scraper & Analyzer

A powerful desktop application built with Python, **CustomTkinter**, **Playwright**, and native **SQLite** to automate the search and scraping of Airbnb listings. It allows users to query properties by city, dates, and guest specifications, extract listing details, analyze top-rated or cheapest options, and export data in multiple formats (**CSV**, **JSON**, or **SQLite**).

---

## 📂 Project Structure

The project is structured around three core modular scripts:

1. **`GUI.py` (The User Interface)**
   - Manages the graphical interface using `CustomTkinter`.
   - Includes custom components like the numeric steppers (`NumberStepper`) for guests (adults, children, pets).
   - Integrates `tkcalendar` for seamless date-picker inputs (Check-In / Check-Out).
   - Handles multi-threading (`threading`) to keep the UI fully responsive while scraping runs in the background.

2. **`scraper.py` (The Core Automation Engine)**
   - Powered by **Playwright** (Chromium headless/headed browser automation) for browser actions.
   - Handles dynamic pagination, lazy loading, and automatic dismissal of cookie popups or overlays.

3. **`all_logic.py` (The Business Logic & Analytics)**
   - Parses HTML content using **BeautifulSoup** and extracts structured listing data.
   - Computes data insights (Top 3 cheapest, Top 3 best-rated, and average prices).
   - Manages local countdown timers, logging (`loguru`), and exports structured data directly to your local **Downloads** folder (`.csv`, `.json`, or `.db`).

---

## ✨ Features

- **Modern GUI**: Sleek and responsive desktop interface built with `CustomTkinter` supporting system theme adaptation.
- **Interactive Calendar & Steppers**: Integrated date pickers (`tkcalendar`) and custom numeric steppers for adults, children, and pets.
- **Automated Scraping**: Uses `Playwright` (with headless or visible browser modes) to handle dynamic loading, pop-ups, and pagination smoothly.
- **Data Analytics & Ranking**: Instantly computes and displays the **Top 3 Cheapest** locations, **Top 3 Best Rated** locations, and the **Average Price** of the search results.
- **Multiple Export Formats**: Save your scraped data directly into your local `Downloads` folder as a **CSV file**, a **JSON file**, or an organized **SQLite Database** (using Python's native `sqlite3` module, no external extensions required).

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **GUI**: `customtkinter`, `tkcalendar`
- **Scraping & Parsing**: `playwright`, `beautifulsoup4`, `fake-useragent`, `python-dateutil`
- **Data & Storage**: `sqlite3` (built-in), native `csv` & `json` modules
- **Logging & Utilities**: `loguru`

---

## 📦 Installation & Setup

1. **Clone the repository:**
    ```bash
    git clone [https://github.com/GoodvySele/Airbnb_scraping.git](https://github.com/GoodvySele/Airbnb_scraping.git)
    cd Airbnb_scraping
    ```

2. **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Install Playwright browsers:**
    ```bash
    playwright install
    ```

---

## 🚀 Usage

1. 🏙️ **Enter your target city** (e.g., *Brazzaville*, *Paris*, *Tokyo*).
2. 🗓️ **Select your Check-In and Check-Out dates** via the interactive calendar interface.
3. 👥 **Adjust the traveler counters** (Adults, Children, Pets).
4. 📂 **Choose your preferred save format** (`CSV`, `JSON`, or `SQLite`).
5. ▶️ **Click "Start Scraping"** and watch the results appear live in the text box while saving automatically to your Downloads folder!

---

## ⚠️ Disclaimer

This script is shared strictly for educational, demonstration, and personal research purposes. Using automated web scraping tools on third-party platforms must always comply with the target website's Terms of Service, data privacy regulations (such as GDPR), and avoid overloading target servers. The author assumes no liability for any misuse or non-compliant use of this software.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.