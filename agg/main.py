import requests
import logging
import threading
import time
import hashlib
from bs4 import BeautifulSoup 
import mysql.connector
from pprint import pprint

data = []

db = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password="HvDkORF2",
	database = "bazar"
)

def get_url():
	url = "https://www.bazos.sk"
	odkazy = []
	stranka = requests.get(url).text
	soup = BeautifulSoup(stranka, 'html.parser')
	a = soup.find_all("span", class_="nadpisnahlavni")
	for linky in a:
		f = linky.find("a", href=True)['href']
		odkazy.append({"URL": f})
	return odkazy
def agg(nazov):
	url = "https://auto.bazos.sk/10"
	stranka = requests.get(url).text
	soup = BeautifulSoup(stranka, 'html.parser')
	a = soup.find_all("div", class_="inzeraty inzeratyflex")
	for inzerat in a:
		nadpis = inzerat.select('.nadpis')[0].text		
		popis = inzerat.select('.popis')[0].text
		cena = inzerat.select('.inzeratycena')[0].text
		data.append({"Nadpis": nadpis, "Popis": popis, "Cena": cena})
	db_zapis(data)
def db_zapis(data):
	kurzor = db.cursor()
	SQL = "INSERT INTO bazar_raw (nazov, popis, cena, nazov_md5, popis_md5, odtlacok) VALUES (%s, %s, %s, %s, %s, %s)"
	for a in range(len(data)):
		nazov_md5 = hashlib.md5(data[a]["Nadpis"].encode("utf-8")).hexdigest()
		popis_md5 = hashlib.md5(data[a]["Popis"].encode("utf-8")).hexdigest()
		odtlacok_c = nazov_md5 + popis_md5
		odtlacok = hashlib.md5(odtlacok_c.encode("utf-8")).hexdigest()
		val = (data[a]["Nadpis"], data[a]["Popis"], data[a]["Cena"], nazov_md5, popis_md5, odtlacok)
		kurzor.execute(SQL,val)
	db.commit()

if __name__ == "__main__":
	x = threading.Thread(target=get_url, daemon=True)
	x.start()
	x.join()
