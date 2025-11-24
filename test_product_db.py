from db.product_queries import query_product_by_name
from agents.product_catalog_agent import get_product_info

def main():
    print("DB product:", query_product_by_name("iPhone 15 Pro"))
    print("Tool product:", get_product_info("iPhone 15 Pro"))

if __name__ == "__main__":
    main()
