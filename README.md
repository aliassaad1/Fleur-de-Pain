# 🥖 Fleur de Pain — AI-Powered Business Assistant

An intelligent chatbot agent for **Fleur de Pain**, a fictional artisan bakery, built with OpenAI GPT-4o and function calling. The agent answers customer questions, captures leads, schedules pickups, and processes custom cake orders through a Gradio web interface.

## 🎯 Features

- **Business Q&A**: Answers questions using business documents (PDF + TXT)
- **Lead Capture**: Records general customer inquiries with contact info
- **Pickup Scheduling**: Schedules appointments for bread/pastry pickups
- **Cake Orders**: Processes structured custom cake orders
- **Feedback Logging**: Captures unknown questions for team review
- **4 Function Calling Tools**: Intelligent routing based on customer intent

## 🏗️ Architecture

- **Model**: OpenAI GPT-4o with function calling
- **Interface**: Gradio ChatInterface
- **Context**: RAG from business documents (5,000+ characters)
- **Logging**: JSONL format for structured data storage

## 📁 Project Structure

```
Fleur_de_Pain/
├── me/
│   ├── about_business.pdf        # Business profile (3 pages)
│   └── business_summary.txt      # Short summary
├── logs/
│   ├── .gitkeep                  # Preserves directory
│   ├── leads.jsonl              # General inquiries (gitignored)
│   ├── feedback.jsonl           # Unknown questions (gitignored)
│   ├── scheduled_pickups.jsonl  # Pickup appointments (gitignored)
│   └── cake_orders.jsonl        # Custom cake orders (gitignored)
├── business_agent.ipynb         # Jupyter notebook demo
├── app.py                       # Standalone Python script
├── requirements.txt             # Dependencies
├── .env.example                 # API key template
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/Fleur_de_Pain.git
cd Fleur_de_Pain
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements**:
- `openai>=1.12.0`
- `gradio>=4.19.0`
- `python-dotenv>=1.0.0`
- `PyPDF2>=3.0.0`

### 3. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
```

**⚠️ IMPORTANT**: Never commit the `.env` file!

### 4. Run the Application

**Option A - Jupyter Notebook** (Recommended for demo):
```bash
jupyter notebook business_agent.ipynb
```

**Option B - Python Script** (For deployment):
```bash
python app.py
```

The Gradio interface will launch at `http://127.0.0.1:7860`

## 🛠️ Function Calling Tools

The agent uses 4 intelligent tools based on customer intent:

### 1. `record_customer_interest`
- **Purpose**: Capture general leads and inquiries
- **When**: Customer wants information about products/services
- **Log**: `logs/leads.jsonl`

### 2. `record_feedback`
- **Purpose**: Log questions outside business knowledge
- **When**: Agent cannot answer from documents
- **Log**: `logs/feedback.jsonl`

### 3. `schedule_pickup` ⭐
- **Purpose**: Schedule pickup appointments
- **When**: Customer wants to pick up items at specific time
- **Log**: `logs/scheduled_pickups.jsonl`
- **Parameters**: customer_name, items, pickup_date, pickup_time

### 4. `create_cake_order` ⭐
- **Purpose**: Process custom cake orders
- **When**: Customer orders celebration cake
- **Log**: `logs/cake_orders.jsonl`
- **Parameters**: name, email, cake_size, flavor, pickup_date, custom_message

## 💬 Example Interactions

### Business Q&A
```
User: What types of bread do you offer?
Bot: We offer artisan breads including baguette, country sourdough,
     multigrain, ciabatta, brioche, and rye, all baked fresh every morning.
```

### Schedule Pickup
```
User: I want to pick up 2 sourdough loaves tomorrow at 3pm
Bot: Could you please provide your full name?
User: I'm David
Bot: ✓ Pickup scheduled for David! 2 sourdough loaves ready tomorrow at 3:00 PM.
```

### Custom Cake Order
```
User: I need a chocolate birthday cake for Saturday
Bot: We'd be delighted to help! Note: custom cakes require 24-hour notice.
     Could you provide details?
User: For 20 people, I'm Maria, maria@test.com
User: Write 'Happy Birthday!' on it
Bot: ✓ Cake order confirmed! Chocolate cake (serves 20) for Saturday with
     "Happy Birthday!" Our team will reach out to maria@test.com.
```

## 🏢 Business Context

**Fleur de Pain** is a fictional artisan bakery offering:

- **Artisan Breads**: Baguette, sourdough, multigrain, ciabatta, brioche, rye
- **Viennoiserie**: Croissants, pain au chocolat, danishes, éclairs
- **Custom Cakes**: Celebration cakes with 24-hour notice
- **Coffee & Beverages**: Espresso drinks, filter coffee, hot chocolate
- **Catering**: Breakfast boxes, dessert tables, mini-pastry trays

**Key Policies**:
- Fresh batches every 3 hours
- No day-old bread marketed as fresh
- Custom cakes require 24-hour notice
- Pre-order via WhatsApp

## 📊 Log Files (JSONL Format)

All interactions are logged in JSON Lines format for easy analysis:

### Scheduled Pickup Example
```json
{
  "ts": "2025-10-19T12:00:00Z",
  "customer_name": "David",
  "items": "2 sourdough loaves",
  "pickup_date": "tomorrow",
  "pickup_time": "3:00 PM"
}
```

### Cake Order Example
```json
{
  "ts": "2025-10-19T12:05:00Z",
  "name": "Maria",
  "email": "maria@test.com",
  "cake_size": "serves 20 people",
  "flavor": "chocolate",
  "pickup_date": "Saturday",
  "custom_message": "Happy Birthday!"
}
```

## 🔒 Security

- ✅ API keys stored in `.env` (gitignored)
- ✅ Customer data in logs (gitignored)
- ✅ `.env.example` provided as template
- ✅ No credentials in source code

## 🧪 Testing

The system has been thoroughly tested with:
- Business Q&A scenarios
- Multi-turn conversations
- All 4 tool function calls
- JSONL log file generation
- Edge cases and error handling

## 📝 Assignment Details

- **Course**: EECE 503P - Fall 2026
- **Topic**: Agent-Powered Business Assistant
- **Requirements**:
  - ✅ Fictitious business with documents
  - ✅ Minimum 2 tool functions (delivered 4)
  - ✅ Chatbot with OpenAI function calling
  - ✅ Gradio interface
  - ✅ JSONL logging

## 🤝 Contributing

This is an academic project. For educational purposes only.

## 📄 License

Educational project for EECE 503P.

## 👤 Author

Ali Assaad - AUB Student

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- Gradio for chat interface framework
- Course instructors for project guidance

---

**⭐ If you find this helpful, please star the repository!**
