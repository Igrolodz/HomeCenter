from playwright.sync_api import sync_playwright
import time
import json

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
            page.fill("input[name=login]", "ikolodziejczyk")
            page.fill("input[name=haslo]", "j362jTYp")
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
                            attendance_data[subject] = {
                                'present': int(cells[1].inner_text().strip() or "0"),
                                'late': int(cells[2].inner_text().strip() or "0"),
                                'excused': int(cells[3].inner_text().strip() or "0"),
                                'absent_excused': int(cells[4].inner_text().strip() or "0"),
                                'absent_unexcused': int(cells[5].inner_text().strip() or "0"),
                                'total': int(cells[6].inner_text().strip() or "0"),
                                'attendance_rate': float(cells[7].inner_text().strip().replace(",", ".") or "0")
                            }

        except Exception as e:
            print(f"Error occurred: {str(e)}")
        finally:
            browser.close()

        return attendance_data

# if __name__ == "__main__":
#     attendance = get_attendance_data()
#     print(json.dumps(attendance, indent=2, ensure_ascii=False))