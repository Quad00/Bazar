import requests
import re
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
def agg(url):
	url_pocet = url + "9999999999999999999" + "/"
	strankovanie_req = requests.get(url_pocet).text
	strankovanie = BeautifulSoup(strankovanie_req, 'html.parser')
	strankovanie_linky = strankovanie.find_all("div", class_="strankovani")
	for lnks in strankovanie_linky:
		lnkss = lnks.find("a", href=True)['href']
	pocet_str = lnkss[1:-1]
	pocet_int = int(pocet_str)/20
	pocet = int(pocet_int)
	k = 20
	host = url.partition('://')[2]
	kategoria = host.partition('.')[0]
	for f in range(pocet):
		url = url + str(k) + "/"
		k = k+20	
		stranka = requests.get(url).text
		soup = BeautifulSoup(stranka, 'html.parser')
		a = soup.find_all("div", class_="inzeraty inzeratyflex")
		for inzerat in a:
			nadpis = inzerat.select('.nadpis')[0].text		
			popis = inzerat.select('.popis')[0].text
			cena = inzerat.select('.inzeratycena')[0].text
			data.append({"Nadpis": nadpis, "Popis": popis, "Cena": cena})
		db_zapis(data,kategoria)
def db_zapis(data, kategoria):
	kurzor = db.cursor()
	SQL = "INSERT INTO bazar_raw (nazov, popis, cena, nazov_md5, popis_md5, odtlacok, kategoria) VALUES (%s, %s, %s, %s, %s, %s, %s)"
	for a in range(len(data)):
		nazov_md5 = hashlib.md5(data[a]["Nadpis"].encode("utf-8")).hexdigest()
		popis_md5 = hashlib.md5(data[a]["Popis"].encode("utf-8")).hexdigest()
		odtlacok_c = nazov_md5 + popis_md5
		odtlacok = hashlib.md5(odtlacok_c.encode("utf-8")).hexdigest()
		val = (data[a]["Nadpis"], data[a]["Popis"], data[a]["Cena"], nazov_md5, popis_md5, odtlacok, kategoria)
		kurzor.execute(SQL,val)
	db.commit()
	data = []

if __name__ == "__main__":
	url_list = get_url()
	id = 1
	for l in url_list:
		id = threading.Thread(target=agg,args=(l,), daemon=True)
		id.start()
		id.join()
		id = id+1	
	#x = threading.Thread(target=agg, args=(1, "https://auto.bazos.sk/",), daemon=True)
	#x.start()
	#x.join()
