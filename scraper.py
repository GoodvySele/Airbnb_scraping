from playwright.sync_api import sync_playwright, TimeoutError, expect
from random import uniform


def unexpected_notif(page):
    try:
        page.get_by_role("button", name="Got it").click(timeout=3000)
    except TimeoutError:
        pass

def search_city(page, city, arriving, depart, stepper_adults, stepper_kids, stepper_pets):
    page.goto("https://www.airbnb.com/", wait_until="domcontentloaded" )

    unexpected_notif(page)

    search_bar1 = page.get_by_test_id("structured-search-input-field-query")
    search_bar2 = page.get_by_test_id("little-search-location")
    expect(search_bar1.or_(search_bar2)).to_be_visible(timeout=5000)
    search_bar1.or_(search_bar2).click(timeout=5000)
    page.get_by_test_id("structured-search-input-field-query").click()
    page.get_by_test_id("structured-search-input-field-query").fill(city)
    page.get_by_test_id("option-0").click()
    page.wait_for_timeout(1000)

    page.evaluate("window.scrollTo(0, 500)")
    try:
        page.get_by_test_id("little-search-date").click(timeout=2000)
    except TimeoutError:
        pass

    
    dates = [arriving, depart]
    for date in dates:
        while True:
            try:
                page.locator(f'button[data-state--date-string="{date}"]').click(timeout=uniform(1000, 2000))   
                break
            except TimeoutError:
                a = page.locator("div[aria-label='Calendar'] > div:nth-of-type(2) > button").last
                b = page.get_by_label("Move forward to switch to the next month.")
                expect(a.or_(b)).to_be_visible(timeout=10000)

                a.or_(b).click()
                

    page.evaluate("window.scrollTo(0, 300)")
    travelers = page.locator("div.fbb0tkq")
    add_guests = page.get_by_test_id("little-search-guests")
    expect(travelers.or_(add_guests)).to_be_visible(timeout=10000)
    travelers.or_(add_guests).click()

    #.click()
    for i in range(stepper_adults.get()):
        page.get_by_test_id("stepper-adults-increase-button").click()
    for i in range(stepper_kids.get()):
        page.get_by_test_id("stepper-children-increase-button").click()
    for i in range(stepper_pets.get()):
        page.get_by_test_id("stepper-pets-increase-button").click()

    page.get_by_test_id("structured-search-input-search-button").click()

    unexpected_notif(page)

    page.wait_for_load_state("domcontentloaded")
    return page.content()
     


def get_next_page(page):
    nav_combined ="""
        nav[aria_label='Search results pagination'],
        [aria-label='Search results pagination'],
        div.cn6uggc
        """


    page.wait_for_selector(nav_combined, timeout=10000)
    next_page = page.get_by_label("Next").last
    try:
        expect(next_page).to_be_visible(timeout=5000)
        first_card_before = page.locator('div[data-testid="card-container"]').first.inner_text()

        next_page.click(timeout=3000)
        
        page.wait_for_function(
            f"document.querySelector('div[data-testid=\"card-container\"]') && document.querySelector('div[data-testid=\"card-container\"]').innerText !== {repr(first_card_before)}",
            timeout=5000
        )

        page.wait_for_load_state("domcontentloaded")

        page.wait_for_timeout(uniform(1000, 2000))
        
        return page.content()
        
    except (TimeoutError, Exception):
        return None




    

