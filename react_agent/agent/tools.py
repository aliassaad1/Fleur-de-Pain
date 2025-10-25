"""
Tools for Fleur de Pain ReAct Agent
Implements two core functions: lead capture and feedback logging
"""

import json
from datetime import datetime
from pathlib import Path


def record_customer_interest(email: str, name: str, message: str) -> dict:
    """
    Record customer lead information to JSONL file.

    Args:
        email: Customer email or WhatsApp contact
        name: Customer name
        message: Order intent or inquiry details (items, quantities, dates, etc.)

    Returns:
        dict: Confirmation with status and message
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create lead data
    lead_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "email": email,
        "name": name,
        "message": message
    }

    # Append to JSONL file (one JSON object per line)
    leads_file = logs_dir / "leads.jsonl"
    with open(leads_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(lead_data) + "\n")

    return {
        "status": "success",
        "message": f"Lead recorded for {name}. Our team will reach out via {email} soon!"
    }


def record_feedback(question: str) -> dict:
    """
    Record unknown questions or feedback to JSONL file.

    Args:
        question: The customer's question or feedback that couldn't be answered

    Returns:
        dict: Confirmation with status and message
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create feedback data
    feedback_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "question": question
    }

    # Append to JSONL file (one JSON object per line)
    feedback_file = logs_dir / "feedback.jsonl"
    with open(feedback_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(feedback_data) + "\n")

    return {
        "status": "success",
        "message": "Thank you! We've logged your question for our team to review."
    }


def schedule_pickup(customer_name: str, items: str, pickup_date: str, pickup_time: str) -> dict:
    """
    Schedule a pickup appointment for customer orders.

    Args:
        customer_name: Customer's full name
        items: Description of items to pick up (e.g., "2 sourdough loaves, 1 baguette")
        pickup_date: Date for pickup (e.g., "2025-10-20" or "Saturday")
        pickup_time: Preferred time (e.g., "3:00 PM" or "afternoon")

    Returns:
        dict: Confirmation with status and message
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create pickup data
    pickup_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "customer_name": customer_name,
        "items": items,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time
    }

    # Append to JSONL file (one JSON object per line)
    pickup_file = logs_dir / "scheduled_pickups.jsonl"
    with open(pickup_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(pickup_data) + "\n")

    return {
        "status": "success",
        "message": f"Pickup scheduled for {customer_name} on {pickup_date} at {pickup_time}. We'll have {items} ready!"
    }


def create_cake_order(name: str, email: str, cake_size: str, flavor: str, pickup_date: str, custom_message: str = "") -> dict:
    """
    Create a structured custom cake order with all required details.

    Args:
        name: Customer's full name
        email: Customer's email or WhatsApp
        cake_size: Size of cake (e.g., "8 inch", "serves 15", "small/medium/large")
        flavor: Cake flavor (e.g., "chocolate", "vanilla", "red velvet")
        pickup_date: Date for pickup (must be at least 24 hours in advance)
        custom_message: Optional message/text for the cake

    Returns:
        dict: Confirmation with status and message
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create cake order data
    cake_order_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "name": name,
        "email": email,
        "cake_size": cake_size,
        "flavor": flavor,
        "pickup_date": pickup_date,
        "custom_message": custom_message
    }

    # Append to JSONL file (one JSON object per line)
    cake_orders_file = logs_dir / "cake_orders.jsonl"
    with open(cake_orders_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(cake_order_data) + "\n")

    return {
        "status": "success",
        "message": f"Custom cake order received for {name}! {flavor.capitalize()} cake ({cake_size}) scheduled for {pickup_date}. Our team will reach out via {email} to confirm details and pricing."
    }


# Tool registry for easy lookup
TOOLS = {
    "record_customer_interest": record_customer_interest,
    "record_feedback": record_feedback,
    "schedule_pickup": schedule_pickup,
    "create_cake_order": create_cake_order
}


def get_tool(tool_name: str):
    """Get a tool function by name."""
    return TOOLS.get(tool_name)


def get_tool_descriptions() -> str:
    """
    Get formatted tool descriptions for the LLM prompt.

    Returns:
        str: Formatted tool descriptions
    """
    return """
Available Tools:

1. record_customer_interest(email, name, message)
   - Purpose: Store potential customer leads (general orders/inquiries)
   - When to use: Customer wants to order, needs a quote, or expresses general interest
   - Parameters:
     * email (str): Customer's email or WhatsApp number
     * name (str): Customer's full name
     * message (str): Details about order intent, items, quantities, dates, etc.
   - Returns: Confirmation that lead was recorded

2. record_feedback(question)
   - Purpose: Log unknown questions or general feedback
   - When to use: You cannot answer confidently from the business documents
   - Parameters:
     * question (str): The customer's question or feedback
   - Returns: Confirmation that feedback was logged

3. schedule_pickup(customer_name, items, pickup_date, pickup_time)
   - Purpose: Schedule a pickup appointment for bread/pastries
   - When to use: Customer wants to pick up specific items at a specific time
   - Parameters:
     * customer_name (str): Customer's full name
     * items (str): Items to pick up (e.g., "2 sourdough loaves, 1 baguette")
     * pickup_date (str): Date for pickup (e.g., "2025-10-20", "Saturday")
     * pickup_time (str): Preferred time (e.g., "3:00 PM", "afternoon")
   - Returns: Confirmation with scheduled details

4. create_cake_order(name, email, cake_size, flavor, pickup_date, custom_message)
   - Purpose: Create a structured custom cake order (REQUIRES 24-hour notice!)
   - When to use: Customer specifically wants a CUSTOM CAKE (not general orders)
   - Parameters:
     * name (str): Customer's full name
     * email (str): Customer's email or WhatsApp
     * cake_size (str): Size (e.g., "8 inch", "serves 15", "medium")
     * flavor (str): Cake flavor (e.g., "chocolate", "vanilla", "red velvet")
     * pickup_date (str): Pickup date (must be 24+ hours from now)
     * custom_message (str, optional): Message/text for the cake
   - Returns: Confirmation with cake order details

Tool Call Format:
Action: tool_name({"param1": "value1", "param2": "value2"})

Examples:
Action: record_customer_interest({"email": "ana@example.com", "name": "Ana Darwish", "message": "Interested in weekly bread delivery"})
Action: record_feedback({"question": "Do you have gluten-free sourdough daily?"})
Action: schedule_pickup({"customer_name": "John Smith", "items": "2 sourdough loaves", "pickup_date": "Saturday", "pickup_time": "3 PM"})
Action: create_cake_order({"name": "Maria", "email": "maria@test.com", "cake_size": "serves 20", "flavor": "chocolate", "pickup_date": "2025-10-28", "custom_message": "Happy Birthday!"})
"""
