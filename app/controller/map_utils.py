import os
import folium

def get_map(start_location=None, formatted_address=None):
    if start_location is None:
        m = folium.Map(location=[40.7128, -74.0060], tiles="Stamen Terrain", zoom_start=13, width='100%', height='100%')
    else:
        print(start_location, formatted_address)
        lat = start_location["lat"]
        lng = start_location["lng"]
        m = folium.Map(location=(lat, lng), tiles="Stamen Terrain", zoom_start=15, width='100%', height='100%')
        folium.Marker(location=(lat, lng), popup=formatted_address, tooltip='Home').add_to(m)
    
    return m