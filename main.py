import re
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# go to cmd and cd to msedge.exe and enter this line "msedge.exe --remote-debugging-port=9222 --user-data-dir="C:\selprofile"
# open manually ---> https://dpa-hr.otepc.go.th/hr/people/management/1045450101

OUTPUT_FILE = 'result.txt'

def write_to_file(people_data, file_path):
    """Write formatted people data (dict version) to a text file."""
    with open(file_path, "a", encoding="utf-8") as file:
        for person in people_data:
            bachelors_str = ", ".join(f"'{b}'" for b in person["bachelors"])
            line = f"{person['name']} {person['last_name']} - {bachelors_str}\n"
            file.write(line)
            print(line.strip())  # Show in console


# 1. Attach to existing Edge
options = Options()
options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Edge(options=options)
wait = WebDriverWait(driver, 10)

# 2. Get all ID numbers from second column
id_numbers = []
rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) >= 2:
        text = cols[1].text.strip()
        if text.isdigit():
            id_numbers.append(text)

print(f"Found {len(id_numbers)} IDs: {id_numbers}")

# 3. Loop through each ID and extract info
people_data = []
for id_num in id_numbers:
    driver.get(f"https://dpa-hr.otepc.go.th/hr/people/management/edit/{id_num}")

    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))

    # Extract name + last name from inputs (adjust selectors as needed)
    first_name = driver.find_element(By.NAME, "FirstName").get_attribute("value")
    last_name = driver.find_element(By.NAME, "LastName").get_attribute("value")

    # 🔹 Adapted bachelor's extraction using your snippet
    input_elements = driver.find_elements(By.TAG_NAME, "input")
    bachelors = []
    for input_elem in input_elements:
        value = input_elem.get_attribute("value") or ""
        if "-" in value:
            # Remove number + dash before the text
            member = re.sub(r'^[\d\s]*-\s*', '', value)
            bachelors.append(member)

    # Unique list while preserving order
    unique_bachelors = list(dict.fromkeys(bachelors))

    people_data.append({
        "id": id_num,
        "name": first_name,
        "last_name": last_name,
        "bachelors": unique_bachelors
    })

write_to_file(people_data, OUTPUT_FILE)

# # 4. Print results
# for p in people_data:
#     print(f"{p['id']}: {p['name']} {p['last_name']} - {p['bachelors']}")
