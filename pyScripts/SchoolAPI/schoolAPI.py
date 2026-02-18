from playwright.async_api import async_playwright
from datetime import datetime
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
    'doradztwo_zawodowe': 1
}


async def get_attendance_data():
    attendance_data = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        currentMonth = datetime.now().month
                
        try:
            # Navigate to login page
            await page.goto("https://zspolesnica.mobidziennik.pl/dziennik")
            await page.wait_for_load_state()

            # Fill in login form
            await page.fill("input[name=login]", os.getenv("MB_LOGIN"))
            await page.fill("input[name=haslo]", os.getenv("MB_PASSWORD"))
            await page.click("input[type=submit]")
            
            await page.goto("https://zspolesnica.mobidziennik.pl/dziennik/statystykafrekwencji")
            await page.wait_for_load_state()

            # Now get the attendance data
            rows = await page.query_selector_all("table.spis.frekwencja tr")
            for row in rows[2:]:  # Start from the third row
                cells = await row.query_selector_all("td")
                
                subject = (await cells[0].inner_text()).strip()
                
                if currentMonth >= 9 and currentMonth <= 12:
                    if subject and subject != "Podsumowanie":
                        subject_key = format_subject_name(subject)
                        attendance_data[subject_key] = {
                            'name': subject,  # Keep original name as a field
                            'present': int((await cells[1].inner_text()).strip() or "0"),
                            'late': int((await cells[2].inner_text()).strip() or "0"),
                            'excused': int((await cells[3].inner_text()).strip() or "0"),
                            'absent_excused': int((await cells[4].inner_text()).strip() or "0"),
                            'absent_unexcused': int((await cells[5].inner_text()).strip() or "0"),
                            'total': int((await cells[6].inner_text()).strip() or "0"),
                            'attendance_rate': float((await cells[7].inner_text()).strip().replace(",", ".") or "0"),
                            'hours_per_week': subject_hours.get(subject_key, 0)
                        }
                else:
                    if subject and subject != "Podsumowanie":
                        subject_key = format_subject_name(subject)
                        attendance_data[subject_key] = {
                            'name': subject,  # Keep original name as a field
                            'present': int((await cells[8].inner_text()).strip() or "0"),
                            'late': int((await cells[9].inner_text()).strip() or "0"),
                            'excused': int((await cells[10].inner_text()).strip() or "0"),
                            'absent_excused': int((await cells[11].inner_text()).strip() or "0"),
                            'absent_unexcused': int((await cells[12].inner_text()).strip() or "0"),
                            'total': int((await cells[13].inner_text()).strip() or "0"),
                            'attendance_rate': float((await cells[14].inner_text()).strip().replace(",", ".") or "0"),
                            'hours_per_week': subject_hours.get(subject_key, 0)
                        }

        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            await browser.close()

        return attendance_data