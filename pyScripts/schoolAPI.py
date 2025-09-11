from playwright.sync_api import sync_playwright
import time
import re
import os
from dotenv import load_dotenv
load_dotenv("config.env")


def format_subject_name(subject):
    # Replace dots with nothing (except the last one)
    subject = re.sub(r'\.(?=.*\.)', '', subject)
    # Replace remaining dot (if any) with nothing
    subject = subject.replace('.', '')
    # Replace spaces and other special chars with underscore
    subject = re.sub(r'[^a-zA-Z0-9]', '_', subject.lower())
    # Replace multiple underscores with single one
    subject = re.sub(r'_+', '_', subject)
    # Remove trailing underscores
    subject = subject.strip('_')
    return subject

subject_hours = {
    'matematyka': 4,
    'j_polski': 3,
    'j_angielski': 3,
    'fizyka': 2,
    'chemia': 2,
    'biologia': 1,
    'historia': 1,
    'wychowanie_fizyczne': 3,
    'j_zyk_niemiecki': 1,
    'zaj_cia_z_wychowawc': 1,
    'j_angielski_zawodowy': 1,
    'tworzenie_stron_i_aplikacji_internetowych': 4,
    'witryny_i_aplikacje_internetowe': 4,
    'tworzenie_i_administrowanie_bazami_danych': 4,
}


def get_attendance_data():
    attendance_data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to login page
            page.goto("https://zspolesnica.mobidziennik.pl/dziennik")
            time.sleep(1)  # Give it a moment to load

            # Fill in login form
            page.fill("input[name=login]", os.getenv("MB_LOGIN"))
            page.fill("input[name=haslo]", os.getenv("MB_PASSWORD"))
            page.click("input[type=submit]")

            # Wait for navigation after login
            page.wait_for_load_state("networkidle")
            time.sleep(1)  # Give it a moment after login

            # Navigate to attendance page
            page.click("a[href='https://zspolesnica.mobidziennik.pl/dziennik/obecnosci']")
            page.wait_for_load_state("networkidle")
            time.sleep(1)

            # Navigate to detailed attendance statistics
            page.click("a[href='https://zspolesnica.mobidziennik.pl/dziennik/statystykafrekwencji']")
            page.wait_for_load_state("networkidle")
            time.sleep(1)  # Give it a moment to load the statistics

            # Now get the attendance data
            rows = page.query_selector_all("table.spis.frekwencja tr")
            if len(rows) > 2:  # Skip header rows
                for row in rows[2:]:  # Start from the third row
                    cells = row.query_selector_all("td")
                    if cells and len(cells) > 0:
                        subject = cells[0].inner_text().strip()
                        if subject and subject != "Podsumowanie":
                            subject_key = format_subject_name(subject)
                            attendance_data[subject_key] = {
                                'name': subject,  # Keep original name as a field
                                'present': int(cells[1].inner_text().strip() or "0"),
                                'late': int(cells[2].inner_text().strip() or "0"),
                                'excused': int(cells[3].inner_text().strip() or "0"),
                                'absent_excused': int(cells[4].inner_text().strip() or "0"),
                                'absent_unexcused': int(cells[5].inner_text().strip() or "0"),
                                'total': int(cells[6].inner_text().strip() or "0"),
                                'attendance_rate': float(cells[7].inner_text().strip().replace(",", ".") or "0"),
                                'hours_per_week': subject_hours.get(subject_key, 0)
                            }

        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            browser.close()

        return attendance_data