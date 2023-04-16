from flask import render_template, flash, url_for, redirect, session, send_file
from app import app
from app.forms import LocationForm, SearchForm, SelectForm, CheckboxForm, OptimizeForm
from app.controller.location_utils import geolocate
from app.controller.search_utils import grocery_search
from app.controller.map_utils import get_map


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
        result_map = get_map(session["geocoded_location"], session["formatted_address"])
    else:
        result_map = get_map()
    # map_html = result_map.get_root().render()
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
    return redirect("/index")

