# Notebook to Codebase Mapping

This document explains how the notebook cells map to the new codebase structure.

## Configuration

- **Cell 11** → `config.py`
  - Retry configuration for LLM API calls

## Agent Definitions

### Product Catalog Agent

- **Cell 13** → `agents/product_catalog_agent.py`
  - `get_product_info()` tool function
  - `create_product_catalog_agent()` factory function

### Inventory Agent

- **Cell 30** → `agents/inventory_agent.py`
  - `get_inventory_info()` tool function
  - `create_inventory_agent()` factory function

### Shipping Agent

- **Cell 31** → `agents/shipping_agent.py`
  - `get_shipping_estimate()` tool function
  - `get_tracking_info()` tool function
  - `create_shipping_agent()` factory function

### Customer Support Agent

- **Cell 36** → `agents/customer_support_agent.py`
  - `create_customer_support_agent()` factory function
  - Takes RemoteA2aAgent proxies as parameters

## A2A Services

### Product Catalog Service

- **Cells 13, 15, 17** → `services/product_catalog_service.py`
  - Creates agent using factory function
  - Wraps with `to_a2a()` on port 8001
  - Can be run directly or with uvicorn

### Inventory Service

- **Cell 34 (Inventory section)** → `services/inventory_service.py`
  - Creates agent using factory function
  - Wraps with `to_a2a()` on port 8002
  - Can be run directly or with uvicorn

### Shipping Service

- **Cell 34 (Shipping section)** → `services/shipping_service.py`
  - Creates agent using factory function
  - Wraps with `to_a2a()` on port 8003
  - Can be run directly or with uvicorn

## Client Code

### Remote Agent Proxies

- **Cell 21** → `client/customer_support_client.py` (create_remote_agents function)
  - RemoteA2aAgent for Product Catalog (port 8001)
- **Cell 32** → `client/customer_support_client.py` (create_remote_agents function)
  - RemoteA2aAgent for Inventory (port 8002)
- **Cell 33** → `client/customer_support_client.py` (create_remote_agents function)
  - RemoteA2aAgent for Shipping (port 8003)

### Test Harness

- **Cell 37** → `client/customer_support_client.py` (test_a2a_communication function)
  - SessionService setup
  - Runner creation
  - Async execution loop
  - Response printing

### Main Function

- **Cells 36, 37, 38, 39, 40** → `client/customer_support_client.py` (main function)
  - Creates remote agents
  - Creates customer support agent
  - Runs test queries

## Key Differences from Notebook

1. **No subprocess.Popen**: Services are run directly with uvicorn instead of being spawned from within the notebook
2. **Factory Functions**: Agents are created via factory functions for better testability and reusability
3. **Separated Concerns**: Agent definitions, services, and client code are in separate modules
4. **Environment Variables**: GOOGLE_API_KEY is checked at service startup instead of using Kaggle secrets
5. **No Background Processes**: Services run in foreground (can be backgrounded with shell `&` or systemd)

## Port Assignments

- **8001**: Product Catalog Agent
- **8002**: Inventory Agent
- **8003**: Shipping Agent

These match the notebook's implementation (Cells 17, 34).
