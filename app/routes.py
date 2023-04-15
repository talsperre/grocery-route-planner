from flask import render_template, flash, url_for, redirect, session
from app import app
from app.forms import LocationForm, SearchForm
from app.controller.location_utils import geolocate
from app.controller.search_utils import grocery_search


@app.before_first_request
def startup():
    print("IN STARTUP FUNCTION")
    session.clear()

@app.route('/')
@app.route('/index')
def index():
    location_form = LocationForm()
    search_form = SearchForm()
    return render_template('index.html', location_form=location_form, search_form=search_form)

@app.route('/location', methods=['GET', 'POST'])
def location():
    location_form = LocationForm()
    search_form = SearchForm()

    if location_form.validate_on_submit():
        location = location_form.location.data
        gmaps_api_secret_key = app.config["GMAPS_API_SECRET_KEY"]
        print("Input location: {}".format(location))
        formatted_address, geocode_location = geolocate(location, gmaps_api_secret_key)
        if formatted_address is None:
            flash("The location {} does not exist.".format(location))
            return redirect("/index")
            # return redirect(url_for('index', location_form=location_form, search_form=search_form))
        print("Formatted Address: {}".format(formatted_address))
        print("Geocoded Location: {}".format(geocode_location))
        session["formatted_address"] = formatted_address
        session["geocoded_location"] = geocode_location
    return redirect("/index")
    # return redirect(url_for('index', location_form=location_form, search_form=search_form))

@app.route('/search', methods=['GET', 'POST'])
def search():
    location_form = LocationForm()
    search_form = SearchForm()

    if search_form.validate_on_submit():
        item_name = search_form.item.data
        results = grocery_search.get_search_results(item_name)
        if len(results) == 0:
            flash("The item {} does not exist in any of the stores".format(item_name))
            return redirect("/index")
            # return redirect(url_for('index', location_form=location_form, search_form=search_form))
        if "selected_items" not in session:
            session["selected_items"] = {}
        selected_items = session["selected_items"]
        if item_name not in selected_items:
            print("item_name: {}".format(item_name))
            selected_items[item_name] = results
        session["selected_items"] = selected_items
    return redirect("/index")
    # return redirect(url_for('index', location_form=location_form, search_form=search_form))
    # return 

@app.route('/items/<item_name>', methods=['GET', 'POST'])
def items(item_name):
    item_form = ItemForm()
    location_form = LocationForm()
    search_form = SearchForm()
    selected_items = session["selected_items"]

    if item_name not in selected_items:
        flash("The item {} has not yet been selected".format(item_name))
        return redirect(url_for('index', location_form=location_form, search_form=search_form))

    print("Inside items function / route")
    print(selected_items[item_name])
    return render_template('items.html', item_name=item_name)