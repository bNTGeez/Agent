from db.shipping_queries import query_shipping_estimate, query_tracking
from agents.shipping_agent import get_shipping_estimate, get_tracking_info

print("DB shipping:", query_shipping_estimate("iphone 15 pro"))
print("DB tracking:", query_tracking("1Z999"))

print("Tool shipping:", get_shipping_estimate("iphone 15 pro", "San Francisco"))
print("Tool tracking:", get_tracking_info("1Z999"))
