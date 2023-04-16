# grocery-route-planner
A flask and JS web app for grocery route planning

# Running the code
First create a conda environment and then install the required packages using the `requirements.txt` provided in this repository. You can use the command `pip install -r requirements.txt` after activating the environment to do this.

To run the flask server, use the following command:
```
python -m flask run
```

You can open the website on the localhost link shown in the terminal.

**Note**: You might have to add the google maps api key to the terminal via `zshrc` or `bashrc` so that you can access it in the flask config file in `config.py` file. Or you can also hardcode it inside that file.

# Salient features:
1. UI as close as possible to prototype
2. User can choose items from our top 9 relevant results
3. CSRF protection for security
4. Ranking is done using the **OKAPI BM25** algorithm for better precision and recall. Can always test the TF-IDF agorithm as well. Library used is Whoosh. Alternative library/tool => Elastic Search.
5. The search index needs to be regenerated once more with updated units.
6. Units for Kroger data were extracted using the `quantulum3` library.
7. Geocoding is done using the Google Maps API and the maps are currently generated using `folium`.
8. Code uses sessions extensively and does not use any databases. Minor in-efficiency but it's a quick fix nonetheless.

# Brief explanation of optimization code:

Refer to the below code for implementing the routing algorithm.

```
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
```
1. All the optimization code needs to be written in the `optimize` route in the template directory.
2. Inside this function you can access a dictionary called `selected_items_final` as shown in the function above. The dictionary has elements in the form as shown below:

```
{
    "Milk": [
        ["Prairie Farms 2% Milk - 0.5gal", "target", 3.79, 1.0, "piece"],
        [
            "Organic 2% Milk - 0.5gal - Good & Gather&#8482;",
            "target",
            3.99,
            1.0,
            "piece",
        ],
        ["Hiland Chocolate Milk, 1 Pint", "walmart", 1.38, 1.0, "piece"],
        ["a2 Milk 2% Reduced Fat Milk", "kroger", 4.99, 1.0, "piece"],
        ["CADBURY DAIRY MILK Milk Chocolate Candy Bar", "kroger", 2.0, 1.0, "piece"],
        ["Kroger® 1% Lowfat Milk", "kroger", 2.49, 1.0, "piece"],
    ],
    "Mushroom": [
        ["McCormick Mushroom Gravy Mix .75oz", "target", 1.59, 75.0, "oz"],
        [
            "Campbell&#39;s Condensed Golden Mushroom Soup - 10.5oz",
            "target",
            1.79,
            10.5,
            "oz",
        ],
        [
            "Great Value Mushroom Pieces and Stems Mushroom, 8 oz Can",
            "walmart",
            2.54,
            8.0,
            "oz",
        ],
        ["Mushroom Soy Sauce 20.85oz", "walmart", 36.62, 20.85, "oz"],
        ["Heinz Homestyle Mushroom Gravy", "kroger", 2.0, 1.0, "piece"],
        ["Kroger® Mushroom Gravy Mix", "kroger", 0.5, 1.0, "piece"],
    ],
}
```

Here the keys are the items that the user wants and the values are the relevant items from our dataset. The column names are `[name, store, price, quantity, unit]`.

The start location is given via the session values of `geocoded_location` and `formatted_address` respectively. You can access them as `start_location = session["geocoded_location"]` in the function. 

Use Google Maps API to find the nearest **Kroger**, **Walmart**, and **Target** from the `start_location`. You can add this code to the `location_utils.py` file inside the `controller` directory.

Based on this data, you can find the best route and then modify the `map_utils.py` function accordingly to display the final routes and the map. For an example on how to draw a map with route in Folium, given the order of stores, refer to this code [here](https://drive.google.com/file/d/1Ga5m5tVCNdm-7OyvwW2xP6OupSI54z2N/view?usp=sharing).