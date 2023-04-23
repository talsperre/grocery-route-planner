import sys
import googlemaps
import pandas as pd
from datetime import datetime

from flask import render_template, flash, url_for, redirect, session
from app import app
from app.forms import LocationForm, SearchForm, SelectForm, CheckboxForm, OptimizeForm
# from app.controller.location_utils import *
from app.controller.location_utils import get_final_combo_from_store, get_store_combo, gen_combo, find_shortest_path, geolocate
from app.controller.search_utils import grocery_search
from app.controller.map_utils import get_map

min_time_spent = sys.maxsize
min_time_route = []

@app.before_first_request
def startup():
    session.clear()

@app.route('/')
@app.route('/index')
def index():
    location_form = LocationForm()
    search_form = SearchForm()
    optimize_form = OptimizeForm()
    if "formatted_address" in session:
        if "final_results" in session:
            list_of_locations = session["final_results"]["list_of_locations"]
            store_names = session["final_results"]["chain_order"]
            destination_list = []
            for i, location in enumerate(list_of_locations[1:-1]):
                gmaps_api_secret_key = app.config["GMAPS_API_SECRET_KEY"]
                _, geocode_location = geolocate(location, gmaps_api_secret_key)
                destination_list.append({
                    "store_name": store_names[i],
                    "address": location,
                    "lat": geocode_location["lat"],
                    "lng": geocode_location["lng"]
                })
            polyline_str = session["final_results"]["overview_polyline"]["points"]
            result_map = get_map(session["geocoded_location"], session["formatted_address"], polyline_str, destination_list)
        else:
            result_map = get_map(session["geocoded_location"], session["formatted_address"])
    else:
        result_map = get_map()
    map_html = result_map.get_root()._repr_html_()
    return render_template('index.html', location_form=location_form, search_form=search_form, optimize_form=optimize_form, map_html=map_html)

@app.route('/location', methods=['GET', 'POST'])
def location():
    location_form = LocationForm()

    if location_form.validate_on_submit():
        location = location_form.location.data
        gmaps_api_secret_key = app.config["GMAPS_API_SECRET_KEY"]
        print("Input location: {}".format(location))
        formatted_address, geocode_location = geolocate(location, gmaps_api_secret_key)
        if formatted_address is None:
            flash("The location {} does not exist.".format(location))
            return redirect("/index")
        print("Formatted Address: {}".format(formatted_address))
        print("Geocoded Location: {}".format(geocode_location))
        session["formatted_address"] = formatted_address
        session["geocoded_location"] = geocode_location
    return redirect("/index")

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_form = SearchForm()

    if search_form.validate_on_submit():
        item_name = search_form.search.data
        results = grocery_search.get_search_results(item_name)
        if len(results) == 0:
            flash("The item {} does not exist in any of the stores".format(item_name))
            return redirect("/index")
        # if the current item is not yet been selected, add it to session
        if "selected_items" not in session:
            session["selected_items"] = {}
        selected_items = session["selected_items"]
        if item_name not in selected_items:
            print("item_name: {}".format(item_name))
            selected_items[item_name] = results
        session["selected_items"] = selected_items
    return redirect(url_for("items", item_name=item_name))

@app.route('/items/<item_name>', methods=['GET', 'POST'])
def items(item_name):
    selected_items = session["selected_items"]

    if item_name not in selected_items:
        flash("The item {} has not yet been selected".format(item_name))
        return redirect("/index")

    num_items = len(selected_items[item_name])
    checkbox_forms = [CheckboxForm() for _ in range(num_items)]
    select_form = SelectForm(checkboxes=checkbox_forms)

    if select_form.validate_on_submit():
        selected_indices = []
        for i, field in enumerate(select_form.checkboxes):
            num = int(field.checkbox.name.split("-")[1])
            selected_indices.append(num)
        if "selected_items_final" not in session:
            session["selected_items_final"] = {}
        selected_items_final = session["selected_items_final"]
        if item_name not in selected_items_final:
            results = selected_items[item_name]
            updated_results = [results[i] for i in selected_indices]
            selected_items_final[item_name] = updated_results
        session["selected_items_final"] = selected_items_final
        return redirect("/index")

    return render_template('items.html', item_name=item_name, select_form=select_form, zip=zip)

@app.route('/optimize', methods=['GET', 'POST'])
def optimize():
    optimize_form = OptimizeForm()

    if optimize_form.validate_on_submit():
        print("Inside optimize function")
        print(optimize_form.optimize_type.data)

        if "selected_items_final" not in session:
            flash("Please select items before asking for the best route")
            return redirect("/index")

        if "geocoded_location" not in session:
            flash("Please enter a start location before asking for the best route")
            return redirect("/index")

        selected_items_final = session["selected_items_final"]
        start_location = session["geocoded_location"]
        print(selected_items_final)
        print(start_location)

        # transform the dictionary to a dataframe
        data = []
        for category, products in selected_items_final.items():
            for product in products:
                data.append([category] + product)

        userinput = pd.DataFrame(data, columns=["category", "product", "store",
                                                "price", "quantity", "unit"])

        optimization_type = optimize_form.optimize_type.data

        # generate combinations
        combinations = gen_combo(optimization_type, userinput)
        # print(combinations)

        # extract the store combo for route planning
        store_combos = get_store_combo(combinations)
        # print(store_combos)

        # route planning
        gmaps = googlemaps.Client(key=app.config["GMAPS_API_SECRET_KEY"])
        min_time_route, min_time_spent = find_shortest_path(gmaps, start_location, store_combos)

        # print(min_time_route)
        # print(min_time_spent)
        
        # get final combo & routes information
        final_store_combo = frozenset([chain['store'] for chain in
                                       min_time_route])
        print(final_store_combo)
        final_price, final_combo = get_final_combo_from_store(final_store_combo,
                                                 combinations)

        # get route details
        now = datetime.now()
        directions_result = gmaps.directions(start_location, start_location,
                                             waypoints=[e["place_id"] for e in min_time_route],
                                             mode="driving",
                                             departure_time=now,
                                             optimize_waypoints=True)
        distance_by_stops = [ leg["distance"]["value"] for leg in directions_result[0]["legs"] ]

        num_hours = min_time_spent // 3600
        num_minutes = (min_time_spent % 3600) // 60

        if num_hours > 0:
            formatted_time = "{} hour, {} minutes".format(num_hours, num_minutes)
        else:
            formatted_time = "{} minutes".format(num_minutes)        

        formatted_distance = "{:.2f}".format(sum(distance_by_stops) / 1000.0)

        session["final_results"] = {
            "final_price": final_price,
            "final_combo": final_combo,
            "formatted_time": formatted_time,
            "formatted_distance": formatted_distance,
            "chain_order": [ route["store"] for route in min_time_route ],
            "list_of_locations": [directions_result[0]["legs"][0]["start_address"]] + [ leg["end_address"] for leg in directions_result[0]["legs"] ],
            "total_driving_time": min_time_spent,
            "total_driving_distance": sum(distance_by_stops),
            "overview_polyline": directions_result[0]["overview_polyline"]
        }
        print(session["final_results"])

    return redirect("/index")

