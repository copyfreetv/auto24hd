```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import requests
import json
import time
import os
import re

from datetime import datetime



# =========================================
# CONFIG
# =========================================

URL =
"https://full24th.com/"

SAVE_DIR =
"output"

JSON_FILE =
os.path.join(
    SAVE_DIR,
    "full24th.json"
)

M3U_FILE =
os.path.join(
    SAVE_DIR,
    "live.m3u"
)



# =========================================
# EXTRACT M3U8
# =========================================

def extract_m3u8(url):

    try:

        r =
        requests.get(

            url,

            headers={

                "User-Agent":
                "Mozilla/5.0",

                "Referer":
                "https://full24th.com/"

            },

            timeout=10

        )

        html = r.text


        # =================================
        # direct m3u8
        # =================================

        match =
        re.search(

            r'https?:\/\/[^"\']+\.m3u8[^"\']*',

            html

        )

        if match:

            return match.group(0)


        # =================================
        # escaped
        # =================================

        match =
        re.search(

            r'https?:\\\/\\\/[^"]+\.m3u8[^"]*',

            html

        )

        if match:

            return (
                match.group(0)
                .replace("\\/","/")
            )


        return url

    except:

        return url



# =========================================
# SELENIUM
# =========================================

options = Options()

options.add_argument("--headless")

options.add_argument("--no-sandbox")

options.add_argument(
    "--disable-dev-shm-usage"
)

options.add_argument(
    "--window-size=1920,1080"
)

options.add_argument(
    "--disable-blink-features=AutomationControlled"
)

options.add_experimental_option(

    "excludeSwitches",

    ["enable-automation"]

)

options.add_experimental_option(

    "useAutomationExtension",

    False

)

options.add_argument(

"user-agent=Mozilla/5.0 "
"(Windows NT 10.0; Win64; x64) "
"AppleWebKit/537.36 "
"(KHTML, like Gecko) "
"Chrome/120.0.0.0 Safari/537.36"

)



# =========================================
# CHROME DRIVER
# =========================================

service =
Service("/usr/bin/chromedriver")

driver =
webdriver.Chrome(

    service=service,

    options=options

)



# =========================================
# LOAD PAGE
# =========================================

try:

    driver.get(URL)

    driver.execute_script("""

Object.defineProperty(
navigator,
'webdriver',
{
get: () => undefined
})

""")

    WebDriverWait(
        driver,
        30
    ).until(

        EC.presence_of_element_located(
            (
                By.TAG_NAME,
                "body"
            )
        )

    )

    time.sleep(5)


    # =====================================
    # AUTO SCROLL
    # =====================================

    last_height =
    driver.execute_script(
        "return document.body.scrollHeight"
    )

    while True:

        driver.execute_script(

            "window.scrollTo("
            "0,"
            "document.body.scrollHeight"
            ");"

        )

        time.sleep(2)

        new_height =
        driver.execute_script(
            "return document.body.scrollHeight"
        )

        if new_height == last_height:
            break

        last_height = new_height


    soup =
    BeautifulSoup(
        driver.page_source,
        "html.parser"
    )

finally:

    driver.quit()



# =========================================
# PARSE
# =========================================

results = []


# =========================================
# MATCH CARDS
# =========================================

cards =
soup.select("a")

for card in cards:

    href =
    card.get("href","")

    text =
    card.get_text(
        " ",
        strip=True
    )


    # =====================================
    # FILTER
    # =====================================

    if not href:
        continue

    if "บอลสด" not in text \
    and "vs" not in text.lower():
        continue


    # =====================================
    # TIME
    # =====================================

    time_match =
    re.search(

        r'(\d{1,2}:\d{2})',

        text

    )

    match_time = \
    time_match.group(1) \
    if time_match \
    else "00:00"


    # =====================================
    # TEAM
    # =====================================

    lines =
    text.split("\n")

    match_name =
    text


    # =====================================
    # IMAGE
    # =====================================

    img =
    card.find("img")

    image =
    img.get("src","") \
    if img \
    else ""


    # =====================================
    # M3U8
    # =====================================

    real_url =
    extract_m3u8(href)


    # =====================================
    # TIME SORT
    # =====================================

    try:

        hh,mm =
        match_time.split(":")

        time_sort =
        int(hh)*60 + int(mm)

    except:

        time_sort = 0


    results.append({

        "time":
        match_time,

        "time_sort":
        time_sort,

        "match":
        match_name,

        "image":
        image,

        "url":
        real_url,

        "referer":
        "https://full24th.com/",

        "userAgent":
        "Mozilla/5.0"

    })



# =========================================
# SORT
# =========================================

results = sorted(

    results,

    key=lambda x: (
        x["time_sort"]
    )

)



# =========================================
# CREATE OUTPUT
# =========================================

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)



# =========================================
# SAVE JSON
# =========================================

with open(

    JSON_FILE,

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        results,

        f,

        ensure_ascii=False,

        indent=2

    )



# =========================================
# BUILD M3U
# =========================================

m3u =
"#EXTM3U\n"


for item in results:

    m3u += (

f'#EXTINF:-1 '
f'tvg-logo="{item["image"]}" '
f'group-title="ฟุตบอล",'
f'{item["match"]}\n'

f'{item["url"]}\n\n'

    )



# =========================================
# SAVE M3U
# =========================================

with open(

    M3U_FILE,

    "w",

    encoding="utf-8"

) as f:

    f.write(m3u)



# =========================================
# DONE
# =========================================

print(
    f"JSON SAVED → {JSON_FILE}"
)

print(
    f"M3U SAVED → {M3U_FILE}"
)

print(
    f"TOTAL MATCHES → {len(results)}"
)
```
