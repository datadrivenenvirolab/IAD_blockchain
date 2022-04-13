import geocoder
import requests
import json

# start internal utility functions
def arcgis(address, session):
	out = geocoder.arcgis(address, session=session)
	return out

def baidu(address, session): # Use actual Chinese characters for best results
	out = geocoder.baidu(address, key="aipmYGOb06ANkOrPWMDGjTIDOQLLjclV", session=session)
	return out

def bing(address, session):
	out = geocoder.bing(address, key="AqtMNzYRCTin5Xr4QNCasklJ4iNP_CxtJlZeVoXEXNDB6XbJjcmlWZb3v_FGBB4K", session=session)
	return out

def canadapost(address, session):
	out = geocoder.canadapost(address, key="e0558c0b7ba9344a : 85e4ec9a435c8e82755ffc", session=session)
	return out

def google(address, session):
	out = geocoder.google(address, session=session)
	return out

def geocode(address):
	# The other google function seems to only work on addresses, while this one does a more general company search.


	## This is Ross's API key; please be careful with usage.
    #url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyAdmtarz0RXOQ3apqbOrb9UF1zfn7B3s_w'.format(address)
	## Andrew's API key, current as of July 2018
	gmaps_api = 'AIzaSyDHrlXXJPxb8jskGz8CKnC2C84h8Xq_7RE'
	url = 'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, gmaps_api)
	resp = json.loads(requests.get(url).content)
	resp = resp['results'][0]
	add = resp['formatted_address']
	lat = resp['geometry']['location']['lat']
	lng = resp['geometry']['location']['lng']
	return lat, lng, add

def mapbox(address, session): # We only get 50k a month
	out = geocoder.mapbox(address, key="pk.eyJ1IjoiemV2bmljc2NhIiwiYSI6ImNqNGdmbzA0dzAyaGoycXA3YnVuZmhlOWcifQ.WZHhW8L_b4t05kXuTMnSgw", session=session)
	return out

def mapquest(address, session): # We only have 15k a month
	out = geocoder.mapquest(address, key="1xtrrwXUXtYMlEBR7AfIpydl5esFuEcz", session=session)
	return out

def opencage(address, session): # We only have 2.5k per day
	out = geocoder.opencage(address, key="4ea29826770f488b820058482ffabb44", session=session)
	return out

def osm(address, session):
	out = geocoder.osm(address, session=session)
	return out

def geocodefarm(address, session):
	out = geocoder.geocodefarm(address, session=session)
	return out

def geolytica(address, session):
	out = geocoder.geolytica(address, session=session)
	return out

def ottawa(address, session):
	out = geocoder.ottawa(address, session=session)
	return out

def here(address, session): #We only have 15k a month
	out = geocoder.here(address, app_id="5ESrnD8Y12ELbdtTfRe8", app_code="YxcWlq3NclMj_p6hZd44FA", session=session)
	return out

def tomtom(address, session):
	out = geocoder.tomtom(address, key="HTHMOS4tg1foHEOyihc8ssYDhgB12pLl", session=session)
	return out

def yahoo(address, session):
	out = geocoder.yahoo(address, session=session)
	return out

def yandex(address, session):
	out = geocoder.yandex(address, session=session)
	return out

def tgos(address, session):
	out = geocoder.yahoo(address, session=session)
	return out

geocoders = {
	"ArcGIS":arcgis,
	"Baidu":baidu,
	"Bing":bing,
	"CanadaPost":canadapost,
	"Google":google,
	"Mapbox":mapbox,
	"MapQuest":mapquest,
	"Opencage":opencage,
	"OpenStreetMap":osm,
	"GeocodeFarm":geocodefarm,
	"Geocoder.ca":geolytica,
	"GeoOttawa":ottawa,
	"HERE":here,
	"TomTom":tomtom,
	"Yahoo":yahoo,
	"Yandex":yandex,
	"TGOS":tgos
}

#End utility functions

def get_lat_long(addresses, services, verbose=False):
	"""
	A function to geocode an array of addresses (will work with some institution names as well)
	and return an array of [latitude,longitude] pairs.
	Also excepts an array of the geocoding services to use with allowed arguments of any combination of
	["ArcGIS","Baidu","Bing","CanadaPost","Google","Mapbox","MapQuest","Opencage","OpenStreetMap",
	"GeocodeFarm","Geocoder.ca","GeoOttawa","HERE","TomTom","Yahoo","Yandex","TGOS"]
	It will then try the listed services in the order listed until successful and warn if not

	Ex usage:
	get_lat_long(["New York, New York", "Moscow, Russia"], ["Google","Yandex"])
	"""
	with requests.Session() as session:
		lat_long = [None] * len(addresses)
		for i in range(len(addresses)):
			for service in services:
				g = geocoders[service](addresses[i], session)
				if g.ok:
					lat_long[i] = g.latlng
					break
		if None in lat_long:
			print("GEOCODE MODULE: One or more addresses could not be geocoded")
			if verbose:
				print("GEOCODE MODULE: Could not geocode")
				for i in range(len(lat_long)):
					if lat_long[i] == None:
						print(addresses[i])
				print("####")
		return lat_long
