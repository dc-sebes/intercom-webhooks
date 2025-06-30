# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask webhook service that integrates Intercom conversations with Asana task management. When Intercom sends conversation events, the service searches for related Asana tasks and creates bidirectional links between them.

## Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Local Development
```bash
python main.py
```
The server runs on port 8080 by default (configurable via `PORT` environment variable).

### Production Deployment
```bash
gunicorn main:app
```

## Required Environment Variables

- `ASANA_ACCESS_TOKEN`: Asana API authentication token
- `ASANA_PROJECT_GID`: Target Asana project identifier
- `ASANA_TARGET_SECTION_GID`: Target section for moving tasks
- `INTERCOM_ACCESS_TOKEN`: Intercom API authentication token

Optional:
- `PORT`: Server port (default: 8080)
- `DEBUG`: Enable debug mode

## Architecture

### Core Components

1. **main.py**: Flask application with webhook endpoints
   - `/intercom-webhook` (POST): Main webhook processor
   - `/health`, `/test-asana`, `/test-intercom`: Health/testing endpoints

2. **asana_client.py**: Asana API wrapper
   - Searches tasks by conversation ID in attachments
   - Moves tasks between sections
   - Uses direct HTTP API calls (not Asana SDK)

3. **intercom_client.py**: Intercom API wrapper
   - Manages conversation custom attributes
   - Retrieves conversation and user data

### Business Logic Flow

1. Receive Intercom webhook for conversation events
2. Filter out emails from sebestech.com domain (see `EXCLUDED_EMAILS` in main.py)
3. Search Asana project for tasks containing conversation ID in attachments
4. Link Asana task URL to Intercom conversation as custom attribute
5. Move found task to target section (if not from excluded emails)

### Key Patterns

- **Client Initialization**: Both API clients validate connectivity during startup
- **Error Handling**: Comprehensive logging and error recovery throughout
- **URL Pattern Matching**: Regex-based extraction of conversation IDs from Intercom URLs in Asana attachments
- **Email Filtering**: Hardcoded exclusion list for internal team emails

## API Integration Details

### Asana Integration
- Uses Asana REST API v1.0 with Bearer token authentication
- Searches tasks by scanning attachment URLs for Intercom conversation patterns
- Task movement between project sections via API calls

### Intercom Integration
- Uses Intercom REST API with Bearer token authentication
- Manages custom attributes on conversations (asana_task_url)
- Processes webhook payloads for conversation events

## Testing

The service includes several test endpoints:
- `/test-asana`: Validates Asana API connectivity
- `/test-intercom`: Validates Intercom API connectivity  
- `/test-search/<conversation_id>`: Tests task search functionality
- `/debug`: Displays environment variable status

## Important Notes

- No automated testing framework is currently implemented
- The service is stateless with no database persistence
- Email exclusion list is hardcoded in main.py and may need updates
- All sensitive configuration is managed via environment variables