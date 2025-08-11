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


def displayOrders(all_orders: List[Order]):
    """Displays all sell orders from in-game users, sorted by highest price."""
    print("\n📦 All Orders (in-game users, sorted by price high → low):")

    sell_orders = [
        order for order in all_orders
        if (order.get("visible") and order.get("order_type") == "buy"
            and order.get("user", {}).get("status") == "ingame")
    ]

    sorted_orders = sorted(sell_orders,
                           key=lambda x: x.get("platinum", 0),
                           reverse=True)

    if not sorted_orders:
        print("❌ No in-game sellers found.")
        return

    for order in sorted_orders:
        user = order.get("user", {})
        print(
            f"  • {user.get('ingame_name', 'Unknown')} "
            f"[Rank {order.get('mod_rank', 'N/A')}] → {order.get('platinum', 'N/A')} platinum → {order['mod_name']} | https://warframe.market/items/{order['mod_url']}"
        )


def loc():
    """Main logic: get location input, find matching mods, fetch orders, and display results."""
    print("1. Arbiters of Hexis", "2. Cephalon Suda", "3. Steel Meridian")

    search_string = input("Enter location: ")

    if search_string == "1":
        search_string = "Arbiters of Hexis,"
    elif search_string == "2":
        search_string = "Cephalon Suda,"
    elif search_string == "3":
        search_string = "Steel Meridian,"

    search_string = search_string.strip().lower()

    matching_mods = [
        mod.get("name", "Unknown Mod") for mod in mods_data
        if any(search_string in drop.get("location", "").lower()
               for drop in mod.get("drops", []))
    ]

    if not matching_mods:
        print(f"\n❌ No mods found at locations matching '{search_string}'.")
        return

    print(f"\n🔍 {len(matching_mods)} mods found at '{search_string}':")
    for mod in matching_mods:
        print(f" - {mod}")

    all_orders: List[Order] = []
    for mod_name in matching_mods:
        mod_url = find_market_url(mod_name)
        if not mod_url:
            print(f"  ↳ Market data not found for '{mod_name}'")
            continue
        all_orders.extend(fetch_orders_for_mod(mod_name, mod_url))

    displayOrders(all_orders)


def main():
    getMods()
    getMarket()
    loc()


if __name__ == "__main__":
    main()
