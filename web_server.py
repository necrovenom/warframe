from flask import Flask, render_template, request, redirect, url_for
import sys
import io

from typing import List, Dict, Any

from contextlib import redirect_stdout
from typing import List, Dict, Any

# Import the functions from app.py
from app import getMods, getMarket, loc, mods_data, market_data, find_market_url, fetch_orders_for_mod

app = Flask(__name__)

# Global variables to store search results
search_results = {}


def modified_loc(user_locations: str) -> Dict[str, Any]:
    """Modified version of loc() that returns results instead of printing them"""
    # Ensure data is loaded
    if not mods_data:
        getMods()
    if not market_data:
        getMarket()

    locations_map = {
        "1": "Arbiters of Hexis",
        "2": "Cephalon Suda",
        "3": "Steel Meridian",
        "4": "Entrati"
    }

    # Process user input
    user_input = user_locations.strip().split(",")

    # Process input: convert numbers via map, keep others as custom locations
    selected_locations = []
    for val in user_input:
        val = val.strip()
        if val in locations_map:
            selected_locations.append(locations_map[val].strip().lower())
        else:
            selected_locations.append(val.strip().lower())

    if not selected_locations:
        return {
            "error": "Invalid input. Please enter at least one valid location."
        }

    matching_mods = set()
    mod_locations = {}

    for mod in mods_data:
        for drop in mod.get("drops", []):
            location = drop.get("location", "").lower()
            if any(search in location for search in selected_locations):
                mod_name = mod.get("name", "Unknown Mod")
                matching_mods.add(mod_name)
                mod_locations.setdefault(mod_name, set()).add(
                    drop.get("location", "Unknown Location"))
                break

    if not matching_mods:
        return {"error": "No mods found for the selected location(s)."}

    # Convert sets to lists for JSON serialization
    for mod_name in mod_locations:
        mod_locations[mod_name] = list(mod_locations[mod_name])

    # Fetch market orders
    all_orders: List[Dict[str, Any]] = []
    for mod_name in matching_mods:
        mod_url = find_market_url(mod_name)
        if not mod_url:
            continue
        orders = fetch_orders_for_mod(mod_name, mod_url)
        for order in orders:
            order["mod_locations"] = mod_locations.get(mod_name, [])
        all_orders.extend(orders)

    # Filter and sort orders (only visible, in-game, buy orders)
    sell_orders = [
        order for order in all_orders
        if (order.get("visible") and order.get("order_type") == "buy"
            and order.get("user", {}).get("status") == "ingame")
    ]

    # Sort descending by platinum
    sorted_orders = sorted(sell_orders,
                           key=lambda x: x.get("platinum", 0),
                           reverse=True)

    return {
        "mods_found": mod_locations,
        "orders": sorted_orders,
        "search_query": user_locations
    }


@app.route('/')
def index():
    """Show the main search form"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle form submission and show results"""
    locations = request.form.get('locations', '')

    if not locations:
        return render_template('results.html',
                               error="Please enter at least one location",
                               search_query="")

    # Call the modified loc function
    results = modified_loc(locations)

    return render_template('results.html',
                           mods_found=results.get('mods_found', {}),
                           orders=results.get('orders', []),
                           error=results.get('error'),
                           search_query=results.get('search_query', locations))


if __name__ == '__main__':
    # Initialize data on startup
    print("Loading Warframe mod data...")
    getMods()
    getMarket()
    print("Data loaded successfully!")

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
