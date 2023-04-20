import sys
import itertools
import googlemaps
from datetime import datetime


min_time_spent = sys.maxsize
min_time_route = []
STORE_LIST = ["kroger", "target", "walmart"]

def gen_combo(opt_type, userinput):
    """
    Args:
        opt_type(str)
        userinput(pandas dataframe): Which items users want to buy

    Returns:
        combinations(list): All possible combinations of store - category -
        product,so that user could find one item in each category they selected.
        Each combination in the list is a tuple.
    """
    if opt_type == "Lowest Price":
        # only keep items with the lowest prices
        min_prices = userinput.groupby("category")["price"].min()
        userinput["lowest_price"] = userinput["category"] \
            .apply(lambda x: min_prices[x])
        userinput = userinput[userinput["price"] == userinput["lowest_price"]]

    grouped = userinput.groupby("category")
    combinations = list(itertools.product(*[group[1].iterrows()
                                            for group in grouped]))
    return combinations


def get_store_combo(combinations):
    """
    Args:
        combinations(list): All possible combinations of store - category -
        product,so that user could find one item in each category they selected.
        Each combination in the list is a tuple.

    Returns:
        store_combos(list): All possible stores combinations. Each store
        combination in the list is a set. This step will make our route
        planning process easier.
    """
    store_combos = []
    for combination in combinations:
        store_combo = set([item[1]["store"] for item in combination])
        if store_combo not in store_combos:
            store_combos.append(store_combo)

    return store_combos


def nearby_stores(gmaps, home, my_nearby_place_id, store_metadata):
    current_index = 1
    for store in STORE_LIST:
        near_bys = gmaps.places_nearby(
            location=home,
            keyword=store_metadata[store]["keyword"],
            name=store_metadata[store]["keyword"],
            rank_by="distance",
            open_now=False,
            type=store_metadata[store]["type"])
        store_metadata[store]["my_nearby"] = ["place_id:" + p["place_id"] for p
                                              in near_bys["results"][:6]]
        my_nearby_place_id += store_metadata[store]["my_nearby"]
        store_metadata[store]["indexes"] = list(range(current_index,
                                                      current_index + len(
                                                          store_metadata[store][
                                                              "my_nearby"])))
        current_index += len(store_metadata[store]["my_nearby"])
    return my_nearby_place_id, store_metadata

def shortest_time(gmaps, my_nearby_place_id, store_set, home_matrix, store_metadata):
    # Prepare Matrix for each store
    for store in STORE_LIST:
        if len(store_metadata[store]["my_nearby"]) < 1:
            continue
        matrix = gmaps.distance_matrix(store_metadata[store]["my_nearby"],
                                       [item for item in my_nearby_place_id if
                                        item not in store_metadata[store][
                                            "my_nearby"]],
                                       mode='driving',
                                       departure_time=datetime.now())
        store_metadata[store]["matrix"] = [[e["duration_in_traffic"]["value"] for e in row["elements"]] for row in matrix["rows"]]
        store_metadata[store]["index_mapping"] = \
            [index for index in range(0, len(my_nearby_place_id)) if index not in store_metadata[store]["indexes"]]

    def next_step(selected_step, current_time, all_places, excluded, prev_index):
        excluded = set()
        for step in selected_step:
            excluded.update(store_metadata[step["store"]]["indexes"])
        avail = list(
            filter(lambda place: (place["index"] not in excluded), all_places))
        global min_time_spent
        global min_time_route
        if avail == []:
            current_time += home_matrix[0][prev_index]
            if current_time < min_time_spent:
                min_time_spent = current_time
                min_time_route = selected_step
            return
        for next_place in avail:
            store_picked = next_place["store"]
            excluded.update()
            current_index = next_place["index"]
            matrix_index = store_metadata[store_picked]["my_nearby"].index(
                next_place["place_id"])
            prev_matrx_index = store_metadata[store_picked]["index_mapping"].index(
                prev_index)
            current_time += store_metadata[store_picked]["matrix"][matrix_index][
                prev_matrx_index]
            if current_time > min_time_spent:
                return
            next_step(selected_step + [next_place], current_time, all_places,
                      excluded, current_index)

    for combo in store_set:
        # create a list of all place ids
        all_places = []
        for store in combo:
            place = [{"store": store, "place_id": place_id,
                      "index": store_metadata[store]["indexes"][
                          store_metadata[store]["my_nearby"].index(place_id)]}
                     for place_id in store_metadata[store]["my_nearby"]]
            all_places += place
        for first in all_places:
            store_picked = first["store"]
            current_index = first["index"]
            next_step([first], home_matrix[0][current_index], all_places,
                      set(store_metadata[store_picked]["indexes"]),
                      current_index)

def find_shortest_path(gmaps, home, store_combos):
    """
    Args:
        gmaps(Object): Google Map Client with API Key attached for getting nearby
        chain stores
        home(Object): Home Location in latitude and longitude
        store_combos(list): All possible stores combinations. Each store
        combination in the list is a set. This step will make our route
        planning process easier.

    Returns:
        min_time_route(list): Route with shortest time in Google Map placeId(s)
        min_time_spent(integer): Total time spent of the route in second
    """
    store_metadata = {
        "kroger": {
            "keyword": "Kroger",
            "type": "food",
            "my_nearby": [],
            "indexes": []
        },
        "target": {
            "keyword": "Target",
            "type": "department_store",
            "my_nearby": [],
            "indexes": [],
        },
        "walmart": {
            "keyword": "Walmart Supercenter",
            "type": "department_store",
            "my_nearby": [],
            "indexes": [],
        }
    }
    home_matrix = []
    my_nearby_place_id = [ home ]
    my_nearby_place_id, store_metadata = nearby_stores(gmaps, home, my_nearby_place_id, store_metadata)

    home_matrix = gmaps.distance_matrix(home, my_nearby_place_id,mode='driving',departure_time=datetime.now())

    home_matrix_value = [ [ e["duration_in_traffic"]["value"] for e in row["elements"] ] for row in home_matrix["rows"] ]

    shortest_time(gmaps, my_nearby_place_id, store_combos, home_matrix_value, store_metadata)

    global min_time_spent
    global min_time_route
    return min_time_route, min_time_spent

def get_final_combo_from_store(final_store_combo, combinations):
    """
    Args:
        final_store_combo(frozenset): a combination of stores that we choose to
        be final combo after checking route time
        combinations(list): all possible combinations we come up with based on
        user's intial input

    Returns:
        message(str): All information about the store-category-product mapping
        and final price
    """
    # transform the combinations to a dictionary and only keep the lowest
    # price option for each possible store combo
    store_price_mapping = {}
    for i in range(len(combinations)):
        combination = combinations[i]
        store_combo = set([item[1]["store"] for item in combination])
        store_combo = frozenset(store_combo)

        if store_combo not in store_price_mapping:
            store_price_mapping[store_combo] = {"idx": i, "price": sum(
                [item[1]["price"] for item in combination])}
        else:
            curr_price = sum([item[1]["price"] for item in combination])
            if curr_price < store_price_mapping[store_combo]["price"]:
                store_price_mapping[store_combo] = {"idx": i,
                                                    "price": curr_price}

    # choose final combo based on the final_store_combo from route planning
    final_combo = combinations[store_price_mapping[final_store_combo]["idx"]]

    # generate message
    final_price = str(round(store_price_mapping[final_store_combo]["price"], 2))
    final_combo_dict = {k: [] for k in final_store_combo}
    for item in final_combo:
        key = item[1]["store"]
        final_combo_dict[key].append([item[1]["category"],
                                      item[1]["product"],
                                      item[1]["price"],
                                      item[1]["quantity"],
                                      item[1]["unit"]])
    final_combo = final_combo_dict
    return final_price, final_combo

# get the route information
def geolocate(location, secret_key):
    gmaps_client = googlemaps.Client(key=secret_key)
    geocode_result = gmaps_client.geocode(location)
    if len(geocode_result) == 0:
        # geocode_result = gmaps_client.geocode("The Standard Atlanta")
        return None, None
    formatted_address = geocode_result[0]["formatted_address"]
    geocode_location = geocode_result[0]["geometry"]["location"]
    return formatted_address, geocode_location
