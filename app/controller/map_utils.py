import os
import polyline
import folium

def get_map(start_location=None, formatted_address=None, route_polyline=None, destination_list=None):
    folium_colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
    if start_location is None:
        m = folium.Map(location=[40.7128, -74.0060], zoom_start=13, width='97%', height='97%')
    else:
        print(start_location, formatted_address)
        lat = start_location["lat"]
        lng = start_location["lng"]
        m = folium.Map(location=(lat, lng), zoom_start=13, width='97%', height='97%')
        folium.Marker(
            location=(lat, lng), 
            icon=folium.Icon(prefix='fa', icon='circle', color='red'),
            popup=folium.Popup(formatted_address),
            tooltip='Home', 
            color='red'
        ).add_to(m)
        
    
    if route_polyline is not None:
        decoded_polyline = polyline.decode(route_polyline)
        folium.PolyLine(locations=decoded_polyline).add_to(m)
    
    if destination_list is not None:
        for i, destination in enumerate(destination_list):
            marker_color = folium_colors[i]
            destination_name = destination["name"]
            lat = destination["lat"]
            lng = destination["lng"]
            folium.Marker(
                location=(lat, lng), 
                icon=folium.Icon(prefix='fa', icon='circle', color=marker_color),
                popup=folium.Popup(destination_name),
                tooltip=destination_name, 
                color=marker_color
            ).add_to(m)

    return m