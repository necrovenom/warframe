from flask import Flask, render_template, request
import requests
import sys
from typing import List, Dict, Any
from functools import lru_cache

# Type aliases
Mod = Dict[str, Any]
Order = Dict[str, Any]
Item = Dict[str, Any]

# URLs
MODS_URL = 'https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Mods.json'
MARKET_ITEMS_URL = 'https://api.warframe.market/v1/items'
MARKET_ORDER_URL = 'https://api.warframe.market/v1/items/{}/orders'

app = Flask(__name__)

# --- Utility Functions ---


def fetch_json(url: str) -> Any:
    """Fetch JSON data from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}", file=sys.stderr)
        return None


@lru_cache(maxsize=1)
def get_mods() -> List[Mod]:
    data = fetch_json(MODS_URL)
    return data if data else []


@lru_cache(maxsize=1)
def get_market_items() -> List[Item]:
    data = fetch_json(MARKET_ITEMS_URL)
    return data.get("payload", {}).get("items", []) if data else []


def find_market_url(mod_name: str) -> str:
    """Find market URL slug for a given mod name."""
    for item in get_market_items():
        if item.get("item_name", "").lower() == mod_name.lower():
            return item.get("url_name", "")
    return ""


def fetch_orders_for_mod(mod_name: str, mod_url: str) -> List[Order]:
    """Fetch orders for a given mod and annotate with metadata."""
    data = fetch_json(MARKET_ORDER_URL.format(mod_url))
    if not data:
        print(f"⚠️ Failed to fetch orders for {mod_name}", file=sys.stderr)
        return []
    orders = data.get("payload", {}).get("orders", [])
    for order in orders:
        order["mod_name"] = mod_name
        order["mod_url"] = mod_url
    return orders


# --- Main Logic ---


def modified_loc(user_locations: str) -> Dict[str, Any]:
    """Process locations and return matching mods and orders."""
    # Predefined Syndicates
    locations_map = {
        "1": "Arbiters of Hexis",
        "2": "Cephalon Suda",
        "3": "Steel Meridian",
        "4": "Entrati"
    }

    # Normalize input
    raw_inputs = user_locations.split(",")
    selected_locations = [
        locations_map.get(loc.strip(), loc.strip()).lower()
        for loc in raw_inputs
    ]

    mods = get_mods()
    matching_mods = {}

    for mod in mods:
        drops = mod.get("drops", [])
        mod_name = mod.get("name", "Unknown Mod")
        for drop in drops:
            location = drop.get("location", "").lower()
            if any(loc in location for loc in selected_locations):
                matching_mods.setdefault(mod_name,
                                         set()).add(drop.get("location"))
                break

    if not matching_mods:
        return {"error": "No mods found for the selected location(s)."}

    # Fetch orders
    all_orders: List[Order] = []
    for mod_name, locations in matching_mods.items():
        mod_url = find_market_url(mod_name)
        if not mod_url:
            continue
        orders = fetch_orders_for_mod(mod_name, mod_url)
        for order in orders:
            order["mod_locations"] = list(locations)
        all_orders.extend(orders)

    # Filter in-game buy orders
    filtered = [
        o for o in all_orders
        if o.get("visible") and o.get("order_type") == "buy"
        and o.get("user", {}).get("status") == "ingame"
    ]

    # Sort descending by price
    sorted_orders = sorted(filtered,
                           key=lambda x: x.get("platinum", 0),
                           reverse=True)

    return {
        "mods_found": {
            k: list(v)
            for k, v in matching_mods.items()
        },
        "orders": sorted_orders,
        "search_query": user_locations
    }


# --- Flask Routes ---


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    locations = request.form.get('locations', '')
    if not locations:
        return render_template('results.html',
                               error="Please enter at least one location.",
                               search_query="")

    results = modified_loc(locations)
    return render_template('results.html',
                           mods_found=results.get('mods_found', {}),
                           orders=results.get('orders', []),
                           error=results.get('error'),
                           search_query=results.get('search_query', locations))


# --- Run App ---

if __name__ == '__main__':
    print("⚙️ Initializing mod and market cache...")
    get_mods()
    get_market_items()
    print("✅ Cache loaded! Starting Flask app.")
    app.run(host='0.0.0.0', port=5000, debug=True)
