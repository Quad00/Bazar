import requests
from bs4 import BeautifulSoup 
from pprint import pprint
url = "https://auto.bazos.sk/10"

stranka = requests.get(url).text
data = []
soup = BeautifulSoup(stranka, 'html.parser')

#inzeraty = soup.select('.inzeraty.inzeratyflex')
a = soup.find_all("div", class_="inzeraty inzeratyflex")
f = 0
for inzerat in a:
	nadpis = inzerat.select('.nadpis')[0].text
	popis = inzerat.select('.popis')[0].text
	cena = inzerat.select('.inzeratycena')[0].text
	#print (inzerat.select('.inzeratycena'))
	data.append({"Nadpis": nadpis, "Popis": popis, "Cena": cena})
pprint(data)
