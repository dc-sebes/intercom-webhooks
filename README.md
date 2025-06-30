# 🔗 Intercom-Webhooks Integration

```
    ╔═══════════════════════════════════════════════╗
    ║           🚀 Asana Task Automation            ║
    ╚═══════════════════════════════════════════════╝
```

A Flask webhook service that automatically links Intercom conversations with Asana tasks, creating seamless integration between customer support and project management.

## 🌟 Features

- 🔄 **Automatic Task Linking**: Links Intercom conversations to existing Asana tasks
- 📧 **Smart Email Filtering**: Excludes internal team emails from automation
- 🎯 **Task Movement**: Automatically moves tasks to designated sections
- 🔍 **Search & Discovery**: Finds tasks by conversation ID in attachments
- 🛡️ **Health Monitoring**: Built-in health checks and test endpoints
- 📊 **Debug Support**: Comprehensive logging and debug endpoints

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- Asana API token
- Intercom API token

### Installation
```bash
pip install -r requirements.txt
```

### Environment Setup
```bash
export ASANA_ACCESS_TOKEN="your_asana_token"
export ASANA_PROJECT_GID="your_project_id"
export ASANA_TARGET_SECTION_GID="your_section_id"
export INTERCOM_ACCESS_TOKEN="your_intercom_token"
```

### Run Development Server
```bash
python main.py
```

### Production Deployment
```bash
gunicorn main:app
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/intercom-webhook` | POST | Main webhook processor |
| `/health` | GET | Health check |
| `/test-asana` | GET | Test Asana connectivity |
| `/test-intercom` | GET | Test Intercom connectivity |
| `/test-search/<id>` | GET | Test task search |
| `/debug` | GET | Environment debug info |

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Intercom   │───▶│   Webhook    │───▶│   Asana     │
│Conversation │    │   Handler    │    │   Tasks     │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   Task       │
                   │   Linking    │
                   └──────────────┘
```

## 🔄 Workflow

1. **📨 Webhook Received**: Intercom sends conversation event
2. **🔍 Email Check**: Filters out internal team emails
3. **🎯 Task Search**: Searches Asana for related tasks
4. **🔗 Link Creation**: Links task URL to Intercom conversation
5. **📋 Task Movement**: Moves task to target section

## 🛠️ Configuration

### Required Environment Variables
- `ASANA_ACCESS_TOKEN`: Your Asana API token
- `ASANA_PROJECT_GID`: Target Asana project ID
- `ASANA_TARGET_SECTION_GID`: Section to move tasks to
- `INTERCOM_ACCESS_TOKEN`: Your Intercom API token

### Optional Variables
- `PORT`: Server port (default: 8080)
- `DEBUG`: Enable debug mode

## 🧪 Testing

Test the integration with built-in endpoints:

```bash
# Test Asana connection
curl http://localhost:8080/test-asana

# Test Intercom connection
curl http://localhost:8080/test-intercom

# Test task search
curl http://localhost:8080/test-search/CONVERSATION_ID
```

## 📁 Project Structure

```
intercom-webhooks/
├── 📄 main.py              # Flask application
├── 🔧 asana_client.py      # Asana API client
├── 💬 intercom_client.py   # Intercom API client
├── 📋 requirements.txt     # Dependencies
├── 📚 README.md           # This file
└── 🤖 CLAUDE.md           # AI assistant guidance
```
