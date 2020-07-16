from selenium import webdriver
import requests
import time
import re
from parallel_sync import wget
import pandas as pd

data_xlsx_file = 'HIST_PAINEL_COVIDBR.xlsx'
data_csv_file = 'municipality_data.csv'
url = 'https://covid.saude.gov.br/'
download_url = None

opts = webdriver.ChromeOptions()
opts.set_capability('goog:loggingPrefs', {"performance": "ALL"})
opts.add_argument("--headless")

driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub',
                          desired_capabilities=opts.to_capabilities())

try:
    driver.get(url)
    time.sleep(10)

    btns = driver.find_elements_by_tag_name('ion-button')
    url_found = False
    for btn in btns:
        if btn.text.strip() == 'Arquivo CSV':
            print('Found download button!')
            btn.click()

            browser_log = driver.get_log("performance")
            for entry in browser_log:
                if 'HIST_PAINEL_COVIDBR' in entry["message"]:
                    download_url = re.search(
                        'https://mobileapps.saude.gov.br/.*xlsx',
                        entry["message"])[0]
                    url_found = True
                    break

            break

    if not url_found:
        print('Cannot find download URL!')
        exit(1)
except Exception as e:
    print('Error ocurred when downloading Brazil data!')
    print(e)
    exit(1)

driver.quit()

print('Downloading ' + download_url)
wget.download('.', download_url, filenames=data_xlsx_file)

data = pd.read_excel(data_xlsx_file)
data = data[[
    'regiao', 'estado', 'municipio', 'codmun', 'data', 'casosAcumulado',
    'obitosAcumulado'
]]
data = data[data['municipio'].notnull()]
data['codmun'] = data['codmun'].astype('int64')

data.to_csv(data_csv_file, encoding='utf-8', index=False)