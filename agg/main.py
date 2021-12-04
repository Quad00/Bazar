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
def agg(cislo,url):
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
	kategoriaa = host.partition('.')[0]
	for f in range(pocet):
		url2 = url + str(k) + "/"
		k = k+20	
		stranka = requests.get(url2).text
		soup = BeautifulSoup(stranka, 'html.parser')
		a = soup.find_all("div", class_="inzeraty inzeratyflex")
		for inzerat in a:
			nadpis = inzerat.select('.nadpis')[0].text		
			popis = inzerat.select('.popis')[0].text
			cena = inzerat.select('.inzeratycena')[0].text
			data.append({"Nadpis": nadpis, "Popis": popis, "Cena": cena})
		db_zapis(data,kategoriaa)
		#data.clear()
		kategoria = ""
		print("Thread " + str(cislo) + " slo spat" + "URL: " + url2)
def db_zapis(data, kategoria):	
	db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password="HvDkORF2",
        database = "bazar"
	)
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
	kategoria = ""
if __name__ == "__main__":
	url_list = get_url()
	id = 1
#	agg(1, "https://auto.bazos.sk/")
	thread_list = []
	for l in url_list:
		link = str(l["URL"])
		print(link)
		thread = threading.Thread(target=agg,args=(id,link,),)
		#thread_list.append(thread)
		id = id+1	

	for thread in thread_list:
		thread.start()
	for thread in thread_list:
		thread.join()
	#x = threading.Thread(target=agg, args=(1, "https://auto.bazos.sk/",), daemon=True)
	#x.start()
	#x.join()
