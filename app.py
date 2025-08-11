import requests
from typing import List, Dict, Any

# Type aliases for readability
Mod = Dict[str, Any]
Order = Dict[str, Any]
Item = Dict[str, Any]

# Global data stores
mods_data: List[Mod] = []
market_data: List[Item] = []

MODS_URL = 'https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Mods.json'
MARKET_ITEMS_URL = 'https://api.warframe.market/v1/items'
MARKET_ORDER_URL = 'https://api.warframe.market/v1/items/{}/orders'


def fetch_json(url: str) -> Any:
    """Helper to fetch and return JSON from a URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    print(
        f"❌ Failed to fetch data from {url} — Status code: {response.status_code}"
    )
    return None


def getMods():
    global mods_data
    data = fetch_json(MODS_URL)
    if data:
        mods_data = data
        print(f"✅ Fetched {len(mods_data)} mods.")


def getMarket():
    global market_data
    data = fetch_json(MARKET_ITEMS_URL)
    if data:
        market_data = data.get("payload", {}).get("items", [])
        print(f"✅ Fetched {len(market_data)} market items.")


def find_market_url(mod_name: str) -> str:
    """Finds the market URL slug for a given mod name."""
    for item in market_data:
        if item.get("item_name", "").lower() == mod_name.lower():
            return item.get("url_name", "")
    return ""


def fetch_orders_for_mod(mod_name: str, mod_url: str) -> List[Order]:
    """Fetch orders for a given mod and tag each order with its mod name and URL."""
    orders_data = fetch_json(MARKET_ORDER_URL.format(mod_url))
    if orders_data:
        orders = orders_data.get("payload", {}).get("orders", [])
        for order in orders:
            order["mod_name"] = mod_name
            order["mod_url"] = mod_url
        return orders
    print(f"⚠️  Failed to fetch orders for '{mod_name}'.")
    return []


def displayOrders(all_orders: List[Dict[str, Any]]):
    print("\nAll Orders (sorted by price: high → low, in-game users only):")

    # Filter only visible, in-game, sell orders
    sell_orders = [
        order for order in all_orders
        if (order.get("visible") and order.get("order_type") == "buy"
            and order.get("user", {}).get("status") == "ingame")
    ]

    # Sort descending by platinum
    sorted_orders = sorted(sell_orders,
                           key=lambda x: x.get("platinum", 0),
                           reverse=True)

    if not sorted_orders:
        print("  No in-game sellers found.")
        return

    for order in sorted_orders:
        user = order.get("user", {})
        ingame_name = user.get("ingame_name", "Unknown")
        mod_name = order.get("mod_name", "Unknown Mod")
        mod_url = order.get("mod_url", "")
        mod_rank = order.get("mod_rank", "N/A")
        platinum = order.get("platinum", "N/A")
        locations = order.get("mod_locations", [])
        locations_str = ", ".join(
            locations) if locations else "Unknown Location"

        print(
            f"  • {ingame_name} [Rank {mod_rank}] → {platinum} platinum → {mod_name} | Locations: {locations_str} | https://warframe.market/items/{mod_url}"
        )


def loc():
    """Allow searching by location via menu numbers or custom strings (or both). Then fetch and display sorted orders."""
    locations_map = {
        "1": "Arbiters of Hexis",
        "2": "Cephalon Suda",
        "3": "Steel Meridian"
    }

    print("Select one or more locations (number or name):")
    for key, name in locations_map.items():
        print(f"{key}. {name.strip(',')}")

    user_input = input(
        "Enter location name(s) or number(s) (e.g., '1 3 Hydron'): ").strip(
        ).split()

    # Process input: convert numbers via map, keep others as custom locations
    selected_locations = []
    for val in user_input:
        if val in locations_map:
            selected_locations.append(locations_map[val].strip().lower())
        else:
            selected_locations.append(val.strip().lower())

    if not selected_locations:
        print("❌ Invalid input. Please enter at least one valid location.")
        return

    print(
        f"\n🔍 Searching for mods dropped at: {', '.join(selected_locations)}")

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
        print("❌ No mods found for the selected location(s).")
        return

    print(f"\n✅ {len(matching_mods)} mods found:")
    for mod in sorted(matching_mods):
        print(f" - {mod}")

    all_orders: List[Dict[str, Any]] = []
    for mod_name in matching_mods:
        mod_url = find_market_url(mod_name)
        if not mod_url:
            print(f"  ↳ Market data not found for '{mod_name}'")
            continue
        orders = fetch_orders_for_mod(mod_name, mod_url)
        for order in orders:
            order["mod_locations"] = mod_locations.get(mod_name, [])
        all_orders.extend(orders)

    displayOrders(all_orders)


def main():
    getMods()
    getMarket()
    loc()


if __name__ == "__main__":
    main()
