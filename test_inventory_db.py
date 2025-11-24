from db.inventory_queries import query_inventory
from agents.inventory_agent import get_inventory_info

def main():
    print("DB inventory:", query_inventory("iPhone 15 Pro"))
    print("Tool inventory:", get_inventory_info("iPhone 15 Pro"))

if __name__ == "__main__":
    main()
