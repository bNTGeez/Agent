# A2A Multi-Agent System

A clean, IDE-friendly implementation of a multi-agent system using the Agent2Agent (A2A) protocol with Google ADK.

This project demonstrates how multiple specialized agents can communicate and collaborate:

- **Product Catalog Agent**: Provides product information
- **Inventory Agent**: Reports stock levels and restocking schedules
- **Shipping Agent**: Provides delivery estimates and tracking information
- **Customer Support Agent**: Coordinates all three agents to help customers

## Project Structure

```
.
├── agents/                      # Agent definitions
│   ├── __init__.py
│   ├── product_catalog_agent.py
│   ├── inventory_agent.py
│   ├── shipping_agent.py
│   └── customer_support_agent.py
├── services/                    # A2A service entrypoints
│   ├── __init__.py
│   ├── product_catalog_service.py  # Port 8001
│   ├── inventory_service.py        # Port 8002
│   └── shipping_service.py         # Port 8003
├── client/                     # Client test harness
│   ├── __init__.py
│   └── customer_support_client.py
├── config.py                   # Shared configuration
├── requirements.txt
└── README.md
```

## Prerequisites

1. **Python 3.11+**
2. **Google API Key**: You need a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/api-keys)

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Google API key:**

   **Option 1: Using a .env file (Recommended)**

   Create a `.env` file in the project root:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and replace `your-api-key-here` with your actual API key:

   ```
   GOOGLE_API_KEY=your-actual-api-key-here
   ```

   The `.env` file is automatically loaded by all services and the client.

   **Option 2: Environment variable**

   ```bash
   export GOOGLE_API_KEY='your-api-key-here'
   ```

   On Windows:

   ```cmd
   set GOOGLE_API_KEY=your-api-key-here
   ```

   **Note:** The `.env` file method is recommended because it's easier to manage and keeps your API key out of your shell history.

## Running the System

### Step 1: Start the A2A Services

You need to run all three services in separate terminals. Each service exposes an agent via the A2A protocol.

**Terminal 1 - Product Catalog Service (port 8001):**

```bash
python -m services.product_catalog_service
```

**Terminal 2 - Inventory Service (port 8002):**

```bash
python -m services.inventory_service
```

**Terminal 3 - Shipping Service (port 8003):**

```bash
python -m services.shipping_service
```

Alternatively, you can use uvicorn directly:

```bash
uvicorn services.product_catalog_service:app --host localhost --port 8001
uvicorn services.inventory_service:app --host localhost --port 8002
uvicorn services.shipping_service:app --host localhost --port 8003
```

### Step 2: Run the Client Test Harness

Once all three services are running, open a fourth terminal and run:

```bash
python -m client.customer_support_client
```

This will:

1. Create RemoteA2aAgent proxies for each service
2. Create the Customer Support Agent with these remote agents as sub-agents
3. Run several test queries to demonstrate A2A communication

## How It Works

### Agent Definitions (`agents/`)

Each agent is defined with:

- **Tools**: Python functions that the agent can call (e.g., `get_product_info`, `get_inventory_info`)
- **Instructions**: Natural language instructions that guide the agent's behavior
- **Model**: Gemini LLM configured with retry options

All data is stored in simple Python dictionaries (no databases).

### A2A Services (`services/`)

Each service file:

1. Creates an agent using the factory function from `agents/`
2. Wraps it with `to_a2a()` to expose it via the A2A protocol
3. Serves the agent card at `/.well-known/agent-card.json`
4. Handles A2A protocol requests at `/tasks`

### Client (`client/`)

The client:

1. Creates `RemoteA2aAgent` proxies that point to each service's agent card URL
2. Creates the Customer Support Agent with these remote agents as sub-agents
3. Uses `Runner` and `InMemorySessionService` to execute conversations
4. The Customer Support Agent automatically routes queries to the appropriate remote agent

## Example Queries

The test harness runs these example queries:

1. "Can you tell me about the iPhone 15 Pro? Is it in stock?"

   - Routes to: product_catalog_agent + inventory_agent

2. "Is the MacBook Pro 14 in stock?"

   - Routes to: inventory_agent

3. "How long will it take to ship an iPhone 15 Pro to San Francisco?"

   - Routes to: shipping_agent

4. "Where is package with tracking number 1Z999?"
   - Routes to: shipping_agent

## Key Concepts

### A2A Protocol

The Agent2Agent (A2A) protocol is a standard for agent-to-agent communication:

- **Agent Cards**: JSON documents that describe an agent's capabilities (served at `/.well-known/agent-card.json`)
- **Standard Endpoints**: All A2A agents expose `/tasks` for task execution
- **Cross-Framework**: Works across different languages and frameworks

### RemoteA2aAgent

`RemoteA2aAgent` is a client-side proxy that:

- Reads the remote agent's card to understand its capabilities
- Translates sub-agent calls into A2A protocol HTTP requests
- Makes remote agents appear as local sub-agents

### Agent Tools

Tools are Python functions registered with agents. They become "skills" in the A2A agent card:

- `get_product_info(product_name: str) -> str`
- `get_inventory_info(product_name: str) -> str`
- `get_shipping_estimate(product_name: str, destination: str) -> str`
- `get_tracking_info(tracking_number: str) -> str`

## Troubleshooting

### Services won't start

- Make sure `GOOGLE_API_KEY` is set in your environment
- Check that ports 8001, 8002, and 8003 are not already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Client can't connect to services

- Ensure all three services are running before starting the client
- Check that services are accessible at `http://localhost:8001`, `8002`, and `8003`
- Verify agent cards are accessible: `curl http://localhost:8001/.well-known/agent-card.json`

### API rate limits (429 errors)

The retry configuration in `config.py` handles transient errors automatically. If you see persistent 429 errors:

- Wait a few minutes and try again
- Check your API key quota in Google AI Studio

## Notes

- All data is stored in-memory using Python dictionaries (no databases)
- This is a learning/demo project - not production-ready
- In production, you'd deploy services to separate infrastructure and use proper authentication

## Learn More

- [A2A Protocol](https://a2a-protocol.org/)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [Exposing Agents with ADK](https://google.github.io/adk-docs/a2a/quickstart-exposing/)
- [Consuming Agents with ADK](https://google.github.io/adk-docs/a2a/quickstart-consuming/)
# Agent
