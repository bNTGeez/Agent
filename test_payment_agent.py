# test_payment_agent.py
import re
from agents.payment_agent import create_payment_intent, get_payment_status

# Create a payment intent
result = create_payment_intent(9.99, "usd", "test@example.com")
print(result)

# Extract the PaymentIntent ID from the output
# Format: "ID: pi_xxxxx"
match = re.search(r'ID: (pi_[a-zA-Z0-9]+)', result)
if match:
    payment_intent_id = match.group(1)
    print(f"\nTesting get_payment_status with ID: {payment_intent_id}")
    print(get_payment_status(payment_intent_id))
else:
    print("\nERROR: Could not extract payment intent ID from output")
    print("Please manually copy the ID and test with:")
    print('  print(get_payment_status("pi_xxxxx"))')
