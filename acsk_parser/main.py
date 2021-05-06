import os
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
import sqlite3

# Need to add proxies  
PROXIES = {}


conn = sqlite3.connect('certificate.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

BASE_DIR = "Z:\\\\cert\\"
DOWNLOAD_LINK = "https://acskidd.gov.ua/download/crls/"

def get_cert_date(string, begin=None, end=None):
    """
    Returns certificate date in datetime format 
    """
    assert begin or end, "Need to provide begin or end"
    if begin:
        result = re.search('Дата випуску: (.*)Наступний випуск:', string)        
    elif end:
        result = re.search('Наступний випуск: (.*)АЦСК', string)    
    date = result.group(1)
    return datetime.strptime(date, '%d.%m.%Y %H:%M:%S')   


def download_certificate(cert_name):
    """
    Download certificate by certificate name from DOWNLOAD_LINK url
    """
    certificate = c.execute("SELECT begin, end FROM certificate WHERE file_name=:file_name", {
                    "file_name": cert_name
                }).fetchone()
    url = DOWNLOAD_LINK + cert_name
    cert_file = requests.get(url, proxies=proxies)
    with open(BASE_DIR  + cert_name, "wb") as file:
        file.write(cert_file.content)    	
    print(f'Certificate - {cert_name} -- updated up to {certificate[1]}')    


def update_cert_database(first=None):
    """
    Updates certificate database. If first=True creates new cerificates entries
    """
    if first:
        c.execute("CREATE TABLE certificate(id INTEGER PRIMARY KEY, file_name TEXT, begin TIMESTAMP, end TIMESTAMP, is_actual INTEGER DEFAULT 1) ")
    try:
        page = requests.get("https://acskidd.gov.ua/certs-crls", proxies=PROXIES)
    except Exception as e:
        print(e)
        sleep(300)        
        return 1

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('table', class_='list')[1]
    links = table.find_all('a')
    trs = table.find_all('tr')
    now = datetime.now()
    for number, row in enumerate(trs):
        date = row.find_all("td")[1].get_text()    
        begin = get_cert_date(date, begin=True)
        end = get_cert_date(date, end=True)
        cert_name = links[number]["href"].split('/')[-1]
        status = 'actual' if begin < now and end > now else False
        if status:
            if first:
                c.execute("INSERT INTO certificate(begin, end, file_name) VALUES(:begin, :end, :file_name)", {
                    "file_name" : cert_name,
                    "begin" : begin,
                    "end": end
                })
            else:
                certificate = c.execute("SELECT begin, end FROM certificate WHERE file_name=:file_name", {
                    "file_name": cert_name
                }).fetchone()
                if certificate[0] < begin:
                    c.execute("UPDATE certificate SET begin=:begin, end=:end WHERE file_name=:file_name", {                    
                        "begin" : begin,
                        "end": end,
                        "file_name": cert_name                
                    })
                    download_certificate(cert_name)
                else:
                    print(f"{cert_name} -- is actual to {end}")
                    
    print()                
    conn.commit()
    return 0


def main():
    table = c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='certificate'").fetchone()
    if table[0] == 0:
        update_cert_database(first=True)
    else:
        while True:
            if not os.path.exists(BASE_DIR):
                print("Disk Z: is unreachable")
                sleep(300)
            
            if update_cert_database():
                continue
            now = datetime.now()
            start_update = c.execute("SELECT end FROM certificate ORDER BY end").fetchone()
            time = int((start_update[0] - now).total_seconds())
            with open(BASE_DIR  + "last.txt", "w") as file:
                file.write(str(time + 30))			
            sleep(time + 10)
            
        

if __name__ == "__main__":
    main()

    




