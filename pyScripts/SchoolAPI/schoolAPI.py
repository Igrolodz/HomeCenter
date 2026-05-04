from flask import json
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


def extract_subject_from_tooltip_text(tooltip_text):
    lines = [line.strip() for line in tooltip_text.splitlines() if line.strip()]
    if not lines:
        return ""

    time_range_pattern = r'^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}$'
    for index, line in enumerate(lines[:-1]):
        if re.match(time_range_pattern, line):
            return lines[index + 1]

    return lines[0]


class SchoolAPI():
    def __init__(self):
        self.attendance_data = None
        self.subject_hours = {}
        self.normal_schedule_positions = {}
        self.weeks = 0
        
    async def Initialize(self):
        print("Initializing SchoolAPI...")
        # reads the numbers of hours per week from the website and stores them in the subject_hours dictionary
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to login page
                await page.goto("https://zspolesnica.mobidziennik.pl/dziennik")
                await page.wait_for_load_state()

                # Fill in login form
                await page.fill("input[name=login]", os.getenv("MB_LOGIN"))
                await page.fill("input[name=haslo]", os.getenv("MB_PASSWORD"))
                await page.click("input[type=submit]")
                
                await page.goto("https://zspolesnica.mobidziennik.pl/dziennik/planlekcji")
                await page.wait_for_load_state()
                
                await page.click("#content > div.fright.nieDoDruku > a")
                await page.wait_for_load_state()

                subject_position = 0
                
                # color check if the schedule is original or if there are already some substitutions
                forward_movement = True
                found_original_schedule = False
                
                while not found_original_schedule:
                    days = await page.query_selector_all("div.autoTooltip")
                    
                    for day in days:
                        spans = await day.query_selector_all("span")
                        if spans:
                            curDate = datetime.now().month
                            if curDate == 6 or curDate == 12:
                                forward_movement = False

                            if forward_movement:
                                await page.click("#content > div.fright.nieDoDruku > div:nth-child(3) > a:nth-child(1)")
                                await page.wait_for_load_state()
                                break
                            
                            if not forward_movement:
                                await page.click("#content > div.fright.nieDoDruku > div:nth-child(3) > a:nth-child(3)")
                                await page.wait_for_load_state()
                                break
                    else:
                        found_original_schedule = True
                        
                            
                    
                subject_names = await page.query_selector_all("div.tooltip")
                
                for subject in subject_names:
                    # subject_text = (await subject.query_selector("span > b").inner_text()).strip()
                    element = await subject.query_selector("span.sr-only")
                    if not element:
                        continue

                    subject_text_raw = (await element.inner_text()).strip()
                    subject_text = extract_subject_from_tooltip_text(subject_text_raw)
                    if not subject_text:
                        continue
                    
                    subject_key = format_subject_name(subject_text)
                    
                    style = await subject.get_attribute("style")
                    left_match = re.search(r'left:\s*(\d+)', style) if style else None
                    subject_left_value = left_match.group(1) if left_match else None
                    subject_left_value = int(subject_left_value) if subject_left_value else None
                    subject_days = {}
                    
                    if subject_key == "" or subject_key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        continue
                    
                    if subject_left_value is None:
                        print(f"Could not find left value for subject: {subject_text}")
                        continue
                    
                    # Get parent's style to extract top coordinate
                    parent = await subject.evaluate_handle("node => node.parentElement")
                    parent_style = await parent.get_attribute("style")
                    top_match = re.search(r'top:\s*([\d.]+%?)', parent_style) if parent_style else None
                    subject_top_value = top_match.group(1) if top_match else None
                    
                    if subject_left_value == 0:
                        subject_days["Monday"] = subject_days.get("Monday", 0) + 1
                    elif subject_left_value == 20:
                        subject_days["Tuesday"] = subject_days.get("Tuesday", 0) + 1
                    elif subject_left_value == 40:
                        subject_days["Wednesday"] = subject_days.get("Wednesday", 0) + 1
                    elif subject_left_value == 60:
                        subject_days["Thursday"] = subject_days.get("Thursday", 0) + 1
                    elif subject_left_value == 80:
                        subject_days["Friday"] = subject_days.get("Friday", 0) + 1
                    
                    if subject_key not in self.subject_hours:
                        self.subject_hours[subject_key] = {
                            'name': subject_text,
                            'days': subject_days,
                            'hours': 1,
                            'times_replaced': 0
                        }
                    else:
                        self.subject_hours[subject_key]['hours'] += 1
                        for day, count in subject_days.items():
                            self.subject_hours[subject_key]['days'][day] = self.subject_hours[subject_key]['days'].get(day, 0) + count
                    
                    # Map this coordinate pair to the subject for later substitution tracking
                    if subject_top_value:
                        coord_key = (subject_left_value, subject_top_value)
                        self.normal_schedule_positions[str(coord_key)] = subject_key
                    subject_position += 1
                
                with open("pyScripts/SchoolAPI/debug/subject_hours.json", "w") as f:
                    json.dump(self.subject_hours, f)
                    
                with open("pyScripts/SchoolAPI/debug/normal_schedule_positions.json", "w") as f:
                    json.dump(self.normal_schedule_positions, f)
                    
                # TODO:
                # - handle substitute teachers
                # - handle changes in schedule (e.g., canceled classes, rescheduled classes)
                # - scrap the info from the schedule changes to the date(eg. if a class was canceled, then the hours for that subject should be reduced by 1 for that week so times_replaced should be increased by 1) and then use that info in the attendance calculation to get more accurate attendance rates
                
                await page.click("#content > div.fright.nieDoDruku > a")
                await page.wait_for_load_state()
                
                # scanning for all replaced classes and updating the self.subject_hours dictionary accordingly
                currentDate = datetime.now().month
                date_selector = "#content > div.fright.nieDoDruku > div:nth-child(3) > div > select"
                await page.wait_for_selector(date_selector)
                
                option_values = await page.eval_on_selector_all(date_selector + " option", "options => options.map(option => ({value: option.value, month: option.parentElement.getAttribute('label')}))")
                for option_value in option_values:
                    if currentDate >= 9 and currentDate <= 12:
                        if option_value["month"] in ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec"]:
                            continue
                    else:
                        if option_value["month"] in ["Wrzesień", "Październik", "Listopad", "Grudzień"]:
                            continue
                    
                    await page.select_option(date_selector, value=option_value["value"])
                    # Selecting a new month can reload parts of the page and invalidate old JS handles.
                    await page.wait_for_load_state("domcontentloaded")
                    # Some weeks can be empty, so don't require lesson tooltips to exist.
                    await page.wait_for_selector("#content", state="attached")
                    await page.wait_for_selector("#content div.table, #content div.fright.nieDoDruku", state="attached")
                    
                    # cancelled classes logic
                    cancelled_class_names = await page.locator("div.tooltip[alt='Lekcja odwołana'] span.sr-only").all_inner_texts()
                    for class_text in cancelled_class_names:
                        class_parts = [part.strip() for part in class_text.splitlines() if part.strip()]
                        class_text = class_parts[2] if len(class_parts) >= 3 else class_text.strip()
                        class_key = format_subject_name(class_text)
                        
                        if class_key in self.subject_hours:
                            self.subject_hours[class_key]['times_replaced'] += 1
                        
                    # handling free days logic
                    day_names = await page.query_selector_all("div.autoTooltip")
                    for day in day_names:
                        # print("DAY IS: ", day)
                        day_text = (await day.inner_text()).strip()
                        # print(f"Day text: {day_text}")
                        day_name = None
                        if "Poniedziałek" in day_text:
                            day_name = "Monday"
                        elif "Wtorek" in day_text:
                            day_name = "Tuesday"
                        elif "Środa" in day_text:
                            day_name = "Wednesday"
                        elif "Czwartek" in day_text:
                            day_name = "Thursday"
                        elif "Piątek" in day_text:
                            day_name = "Friday"
                        else:
                            continue
                        
                        if await day.query_selector("span"):
                            for class_hour in self.subject_hours:
                                if day_name in self.subject_hours.get(class_hour, {}).get('days', {}):
                                    for count in range(self.subject_hours[class_hour]['days'][day_name]):
                                        self.subject_hours[class_hour]['times_replaced'] += 1

                        
                        
                    # Handling substituted classes logic
                    # Use coordinate pairs (left, top) to identify slots
                    all_classes = await page.query_selector_all("div.tooltip")
                    for element in all_classes:
                        if await element.get_attribute("alt") == "Zastępstwo":
                            class_element = await element.query_selector("span.sr-only")
                            if not class_element:
                                continue
                            
                            class_text_raw = (await class_element.inner_text()).strip()
                            class_text = extract_subject_from_tooltip_text(class_text_raw)
                            if not class_text:
                                continue
                            class_key = format_subject_name(class_text)
                            
                            # Skip empty/invalid entries
                            if class_key == "" or class_key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                                continue
                            
                            # Extract coordinates from element's style
                            parent = await element.evaluate_handle("node => node.parentElement")
                            parent_style = await parent.get_attribute("style")
                            element_style = await element.get_attribute("style")
                            left_match = re.search(r'left:\s*(\d+)', element_style) if element_style else None
                            top_match = re.search(r'top:\s*([\d.]+%?)', parent_style) if parent_style else None
                            element_left = left_match.group(1) if left_match else None
                            element_top = top_match.group(1) if top_match else None
                            
                            if element_left is None or element_top is None:
                                continue
                            
                            element_left = int(element_left)
                            coord_key = str((element_left, element_top))
                            
                            # This is a substitution - find what was originally at this coordinate
                            original_subject_key = self.normal_schedule_positions.get(coord_key)
                            
                            if original_subject_key and original_subject_key in self.subject_hours:
                                self.subject_hours[original_subject_key]['times_replaced'] += 1
                            
                            # The substituting class had one less cancellation
                            if class_key in self.subject_hours:
                                self.subject_hours[class_key]['times_replaced'] -= 1
                    self.weeks += 1
                with open("pyScripts/SchoolAPI/debug/subject_hours.json", "w") as f:
                    json.dump(self.subject_hours, f)
    
                print("Initialization complete.")
                return
                        
                    
            except Exception as e:
                print(f"Error occurred: {str(e)}")
            finally:
                await browser.close()
        
    async def get_attendance_data(self):
        if self.attendance_data is None:
            self.attendance_data = {}
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
                        if subject and subject != "Podsumowanie" and subject != "zajęcia z wychowawcą":
                            subject_key = format_subject_name(subject)
                            self.attendance_data[subject_key] = {
                                'name': subject,  # Keep original name as a field
                                'present': int((await cells[1].inner_text()).strip() or "0"),
                                'late': int((await cells[2].inner_text()).strip() or "0"),
                                'excused': int((await cells[3].inner_text()).strip() or "0"),
                                'absent_excused': int((await cells[4].inner_text()).strip() or "0"),
                                'absent_unexcused': int((await cells[5].inner_text()).strip() or "0"),
                                'total': int((await cells[6].inner_text()).strip() or "0"),
                                'attendance_rate': float((await cells[7].inner_text()).strip().replace(",", ".") or "0"),
                                'subject_hours': self.subject_hours.get(subject_key, 0),
                                'weeks': self.weeks
                            }
                    else:
                        if subject and subject != "Podsumowanie" and subject != "zajęcia z wychowawcą":
                            subject_key = format_subject_name(subject)
                            self.attendance_data[subject_key] = {
                                'name': subject,  # Keep original name as a field
                                'present': int((await cells[8].inner_text()).strip() or "0"),
                                'late': int((await cells[9].inner_text()).strip() or "0"),
                                'excused': int((await cells[10].inner_text()).strip() or "0"),
                                'absent_excused': int((await cells[11].inner_text()).strip() or "0"),
                                'absent_unexcused': int((await cells[12].inner_text()).strip() or "0"),
                                'total': int((await cells[13].inner_text()).strip() or "0"),
                                'attendance_rate': float((await cells[14].inner_text()).strip().replace(",", ".") or "0"),
                                'subject_hours': self.subject_hours.get(subject_key, 0),
                                'weeks': self.weeks
                            }

            except Exception as e:
                print(f"Error occurred: {str(e)}")
            finally:
                await browser.close()
            return self.attendance_data