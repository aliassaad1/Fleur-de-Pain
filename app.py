"""
Fleur de Pain — Agent-Powered Business Assistant
Standalone app for deployment (e.g., Hugging Face Spaces)
"""

import os
import json
from datetime import datetime
from pathlib import Path
import gradio as gr
from openai import OpenAI
from PyPDF2 import PdfReader

# Load environment variables (fallback to direct file read if dotenv fails)
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
except:
    api_key = None

# Fallback: Read .env file directly if dotenv didn't work
if not api_key or not api_key.startswith('sk-'):
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY'):
                    api_key = line.split('=', 1)[1].strip()
                    break
    except:
        pass

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please create a .env file with your API key.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Ensure logs directory exists
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


def load_business_context():
    """Load business information from PDF and text files."""
    context = ""

    # Load PDF
    pdf_path = Path("me/about_business.pdf")
    if pdf_path.exists():
        reader = PdfReader(str(pdf_path))
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        context += "=== Business Profile (from about_business.pdf) ===\n" + pdf_text + "\n\n"

    # Load text summary
    txt_path = Path("me/business_summary.txt")
    if txt_path.exists():
        with open(txt_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()
        context += "=== Business Summary (from business_summary.txt) ===\n" + txt_content + "\n"

    return context


# Load the business context
BUSINESS_CONTEXT = load_business_context()


# System prompt
SYSTEM_PROMPT = f"""You are Fleur de Pain's chat assistant.

🚨 CRITICAL RULE - FEEDBACK LOGGING:
You MUST call record_feedback() IMMEDIATELY whenever a customer makes ANY statement about:
- Products they tried (e.g., "The croissants were amazing!", "The bread was too dry")
- Their experience (e.g., "Great service", "Long wait time")
- Suggestions (e.g., "You should add gluten-free options")
- Questions you cannot answer from the business documents

EXAMPLES that MUST trigger record_feedback():
✓ "The croissants were amazing! Best I've ever had" → CALL record_feedback(feedback="The croissants were amazing! Best I've ever had")
✓ "Your coffee is too weak" → CALL record_feedback(feedback="Your coffee is too weak")
✓ "Loved it!" → CALL record_feedback(feedback="Loved it!")
✓ "Do you deliver to Canada?" → CALL record_feedback(feedback="Do you deliver to Canada?")

GOALS:
1) Answer questions strictly using the business_summary.txt and about_business.pdf.
2) If the user asks for ordering or quotes, collect leads:
   - Ask for name, email (or WhatsApp), desired items, quantities, date/time.
3) Stay on brand: warm, concise, transparent about bake times.
4) Emphasize the bakery's policies:
   - Fresh batches every 3 hours; nothing day-old marketed as fresh.
   - Custom cakes require 24-hour notice.
   - Pre-order via WhatsApp; 2-hour delivery windows (when available).

BEHAVIOR:
- Never invent prices or availability if not stated; offer to collect details.
- For cake inquiries, summarize options (flavors/fillings/sizes) and note 24h lead time.
- For bread timing, consult "Bake Times" (if provided) or explain typical windows and that schedule.
- Always encourage sharing contact info (politely) so the team can confirm and schedule.

🚨 WORKFLOW FOR FEEDBACK/OPINIONS:
When a customer shares ANY feedback or opinion (positive, negative, suggestions):
STEP 1: IMMEDIATELY call record_feedback() with their exact statement
STEP 2: THEN respond warmly thanking them
Example:
User: "The croissants were amazing! Best I've ever had"
→ You MUST: Call record_feedback(feedback="The croissants were amazing! Best I've ever had")
→ Then respond: "Thank you so much! We're thrilled you loved our croissants!"

TOOLS:
- record_customer_interest(email, name, message) - General lead capture
- record_feedback(feedback) - MANDATORY for ALL customer opinions, experiences, or unanswered questions
- schedule_pickup(customer_name, items, pickup_date, pickup_time) - Schedule item pickups
- create_cake_order(name, email, cake_size, flavor, pickup_date, custom_message) - Custom cake orders

When collecting leads, use record_customer_interest. For scheduling pickups of bread/pastries,
use schedule_pickup. For custom CAKES specifically, use create_cake_order (remember 24h notice!).

=== BUSINESS CONTEXT ===
{BUSINESS_CONTEXT}
"""


def record_customer_interest(email: str, name: str, message: str) -> dict:
    """
    Record customer lead information to JSONL file.

    Args:
        email: Customer email or WhatsApp contact
        name: Customer name
        message: Order intent or inquiry details

    Returns:
        Confirmation dictionary
    """
    lead_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "email": email,
        "name": name,
        "message": message
    }

    # Append to JSONL file
    leads_file = Path("logs/leads.jsonl")
    with open(leads_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(lead_data) + "\n")

    return {
        "status": "success",
        "message": f"Lead recorded for {name}. Our team will reach out via {email} soon!"
    }


def record_feedback(feedback: str) -> dict:
    """
    Record customer feedback, suggestions, compliments, or unknown questions to JSONL file.

    Args:
        feedback: The customer's feedback, compliment, suggestion, or question

    Returns:
        Confirmation dictionary
    """
    feedback_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "feedback": feedback
    }

    # Append to JSONL file
    feedback_file = Path("logs/feedback.jsonl")
    with open(feedback_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(feedback_data) + "\n")

    return {
        "status": "success",
        "message": "Thank you for your feedback! We truly appreciate it and our team will review it."
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
        Confirmation dictionary
    """
    pickup_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "customer_name": customer_name,
        "items": items,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time
    }

    # Append to JSONL file
    pickup_file = Path("logs/scheduled_pickups.jsonl")
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
        Confirmation dictionary
    """
    cake_order_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "name": name,
        "email": email,
        "cake_size": cake_size,
        "flavor": flavor,
        "pickup_date": pickup_date,
        "custom_message": custom_message
    }

    # Append to JSONL file
    cake_orders_file = Path("logs/cake_orders.jsonl")
    with open(cake_orders_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(cake_order_data) + "\n")

    return {
        "status": "success",
        "message": f"Custom cake order received for {name}! {flavor.capitalize()} cake ({cake_size}) scheduled for {pickup_date}. Our team will reach out via {email} to confirm details and pricing."
    }


# Tool definitions for OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "record_customer_interest",
            "description": "Record customer lead information when they express interest in ordering or want a quote. Call this when you have collected their contact details and order intent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Customer's email address or WhatsApp number"
                    },
                    "name": {
                        "type": "string",
                        "description": "Customer's full name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Details about their order intent, items wanted, quantities, dates, etc."
                    }
                },
                "required": ["email", "name", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_feedback",
            "description": "MANDATORY: Call this function for EVERY customer statement about products, experiences, or opinions. This includes: (1) ANY positive comments like 'The croissants were amazing!', 'Best bread ever', 'Loved it', 'Delicious', 'Great service' (2) ANY negative comments like 'Too expensive', 'Stale bread', 'Bad experience' (3) ANY suggestions like 'Add more options', 'Open earlier' (4) ANY questions you cannot answer from docs. DO NOT just respond - you MUST call this function to log their feedback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feedback": {
                        "type": "string",
                        "description": "The exact customer feedback, compliment, criticism, suggestion, or question to log"
                    }
                },
                "required": ["feedback"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_pickup",
            "description": "Schedule a pickup appointment when customer wants to pick up specific items at a specific time. Use this for same-day or future pickups of bread, pastries, or ready orders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Customer's full name"
                    },
                    "items": {
                        "type": "string",
                        "description": "Description of items to pick up (e.g., '2 sourdough loaves, 1 baguette')"
                    },
                    "pickup_date": {
                        "type": "string",
                        "description": "Date for pickup (e.g., '2025-10-20', 'tomorrow', 'Saturday')"
                    },
                    "pickup_time": {
                        "type": "string",
                        "description": "Preferred pickup time (e.g., '3:00 PM', 'afternoon', 'morning')"
                    }
                },
                "required": ["customer_name", "items", "pickup_date", "pickup_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_cake_order",
            "description": "Create a custom cake order with all required details. Use this specifically for custom celebration cakes (not general lead capture). Remember: custom cakes require 24-hour notice.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Customer's full name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer's email or WhatsApp number"
                    },
                    "cake_size": {
                        "type": "string",
                        "description": "Size of cake (e.g., '8 inch', 'serves 15 people', 'small/medium/large')"
                    },
                    "flavor": {
                        "type": "string",
                        "description": "Cake flavor (e.g., 'chocolate', 'vanilla', 'red velvet', 'strawberry')"
                    },
                    "pickup_date": {
                        "type": "string",
                        "description": "Date for pickup (must be at least 24 hours in advance)"
                    },
                    "custom_message": {
                        "type": "string",
                        "description": "Optional message or text to be written on the cake"
                    }
                },
                "required": ["name", "email", "cake_size", "flavor", "pickup_date"]
            }
        }
    }
]


def detect_feedback(message):
    """
    Detect if message contains feedback/opinion keywords.
    Returns True if feedback detected, False otherwise.
    """
    message_lower = message.lower()

    # Positive feedback keywords
    positive_keywords = [
        'amazing', 'love', 'loved', 'best', 'great', 'excellent', 'delicious',
        'wonderful', 'fantastic', 'awesome', 'perfect', 'incredible', 'outstanding',
        'tasty', 'yummy', 'fresh', 'good', 'nice', 'enjoyed', 'favorite', 'favourite'
    ]

    # Negative feedback keywords
    negative_keywords = [
        'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'disappointed',
        'too expensive', 'too sweet', 'too salty', 'stale', 'cold', 'dry', 'burnt',
        'undercooked', 'overcooked', 'worst', 'disgusting', 'gross'
    ]

    # Suggestion keywords
    suggestion_keywords = [
        'should', 'could', 'suggest', 'recommend', 'add', 'wish', 'hope',
        'would be nice', 'would be better', 'improve', 'change'
    ]

    # Check for feedback patterns
    for keyword in positive_keywords + negative_keywords + suggestion_keywords:
        if keyword in message_lower:
            return True

    # Check for exclamation marks (often indicates strong opinion/feedback)
    if '!' in message and len(message.split()) < 20:  # Short excited statements
        return True

    return False


def chat_with_agent(message, history):
    """
    Process user message and return bot response.
    Handles function calling for lead capture and feedback.
    """
    # Build messages from history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for human, assistant in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": assistant})

    # Add current message
    messages.append({"role": "user", "content": message})

    # Call OpenAI API with function calling
    response = client.chat.completions.create(
        model="gpt-4o",  # Using GPT-4o for best performance
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    # Check if the model wants to call a function
    if response_message.tool_calls:
        # Process each tool call
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute the appropriate function
            if function_name == "record_customer_interest":
                function_response = record_customer_interest(
                    email=function_args.get("email"),
                    name=function_args.get("name"),
                    message=function_args.get("message")
                )
            elif function_name == "record_feedback":
                function_response = record_feedback(
                    feedback=function_args.get("feedback")
                )
            elif function_name == "schedule_pickup":
                function_response = schedule_pickup(
                    customer_name=function_args.get("customer_name"),
                    items=function_args.get("items"),
                    pickup_date=function_args.get("pickup_date"),
                    pickup_time=function_args.get("pickup_time")
                )
            elif function_name == "create_cake_order":
                function_response = create_cake_order(
                    name=function_args.get("name"),
                    email=function_args.get("email"),
                    cake_size=function_args.get("cake_size"),
                    flavor=function_args.get("flavor"),
                    pickup_date=function_args.get("pickup_date"),
                    custom_message=function_args.get("custom_message", "")
                )
            else:
                function_response = {"error": "Unknown function"}

            # Add function response to messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response)
            })

        # Get final response after function execution
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        final_response = second_response.choices[0].message.content

        # Fallback: If feedback was detected but not logged by any function call
        feedback_logged = any(
            tool_call.function.name == "record_feedback"
            for tool_call in response_message.tool_calls
        )
        if not feedback_logged and detect_feedback(message):
            record_feedback(feedback=message)

        return final_response

    # No function call needed, return direct response
    final_response = response_message.content

    # Fallback: Check if message contains feedback and log it
    if detect_feedback(message):
        record_feedback(feedback=message)

    return final_response


# Create Gradio chat interface
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="Fleur de Pain — Business Assistant",
    description="Ask me about our fresh-baked goods, menu, ordering, custom cakes, and more!",
    examples=[
        "What types of bread do you offer?",
        "When are fresh batches available?",
        "I need a custom cake for 20 people this Saturday",
        "How do I pre-order for delivery?",
        "Tell me about your viennoiserie",
        "Do you have gluten-free options?"
    ],
    theme=gr.themes.Soft()
)


if __name__ == "__main__":
    demo.launch()
