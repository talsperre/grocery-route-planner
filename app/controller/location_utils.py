import googlemaps

def geolocate(location, secret_key):
    gmaps_client = googlemaps.Client(key=secret_key)
    geocode_result = gmaps_client.geocode(location)
    if len(geocode_result) == 0:
        # geocode_result = gmaps_client.geocode("The Standard Atlanta")
        return None, None
    formatted_address = geocode_result[0]["formatted_address"]
    geocode_location = geocode_result[0]["geometry"]["location"]
    return formatted_address, geocode_location