import os
import pandas as pd
import numpy as np
from whoosh import index
from whoosh.fields import Schema, TEXT, NUMERIC, ID
from whoosh.qparser import QueryParser
from whoosh.query import Term


class GrocerySearch(object):
    def __init__(self):
        # Define the path where the index will be stored
        self.index_dir = os.path.abspath("./app/controller/index")

        # Define the set of stores we have
        self.stores = ["target", "walmart", "kroger"]

        # Define the schema for the index
        self.schema = Schema(
            name=TEXT(stored=True),
            store=ID(stored=True),
            price=NUMERIC(stored=True),
            search_query=TEXT(stored=True),
            category=TEXT(stored=True),
            quantity=NUMERIC(stored=True),
            unit=ID(stored=True)
        )
        
        # Create the index
        self.index = index.open_dir(self.index_dir)

        # Open a searcher for the index and parse the query
        self.searcher = self.index.searcher()
        self.parser = QueryParser("name", schema=self.index.schema)
    
    def get_search_results(self, query):
        results_list = []
        parsed_query = self.parser.parse(query)
        for store in self.stores:
            filter_term = Term("store", store)
            results = self.searcher.search(parsed_query, filter=filter_term, limit=5)
            for hit in results:
                results_list.append([hit["name"], hit["store"], hit["price"], hit["quantity"], hit["unit"]])
                # print(results_list[-1])
        # print("-"*50)
        # return pd.DataFrame(results_list, columns=["name", "store", "price", "quantity", "unit"])
        return results_list

grocery_search = GrocerySearch()
# grocery_search.get_search_results("Mushroom")
# grocery_search.get_search_results("Potatoes")
# grocery_search.get_search_results("milk")
# grocery_search.get_search_results("Radish")
# grocery_search.get_search_results("Popcorn")