# Lead Management Automation System

Automated, resilient lead management system built with Python, adhering strictly to Clean Architecture principles and Test-Driven Development (TDD). The application extracts lead data from emails (Google Ads, website contact forms), parses non-structured text into validated domain entities, and persists the records to a target Google Sheet while ensuring strict idempotency.

---

## 1. System Architecture

The project follows Clean Architecture, decoupling core business logic from external drivers and frameworks:

```
app/
├── domain/                  # Core Business Logic & Models (Pure Python / Pydantic)
│   └── models.py            # Lead entity, LeadSource, LeadStatus, Address
├── application/             # Use Cases & Parsing Services
│   ├── parse_lead.py        # Email text extraction engine
│   └── sync_lead_usecase.py # Sync orchestration & repository abstraction
├── infrastructure/          # External Interfaces & Adaptations
│   ├── gmail/               # Gmail API client wrapper & Label manager
│   └── sheets/              # Google Sheets API adapter (gspread)
├── config.py                # Environment management via pydantic-settings
└── main.py                  # Entrypoint runner (Polling Engine)
```

### Architectural Guarantees
* **Dependency Inversion:** Use cases interact with persistence layers via Protocols (`typing.Protocol`), preventing framework lock-in.
* **Idempotency:** Duplicates are prevented through unique external message identifier validation (`external_message_id`).
* **Testability:** Domain models, parsers, and orchestration workflows are covered by unit tests using test mocks.

---

## 2. Technology Stack

* **Language:** Python 3.12+
* **Package Manager:** `uv`
* **Validation & Settings:** `pydantic` (v2), `pydantic-settings`
* **External APIs:** `gspread`, `google-api-python-client`, `google-auth-oauthlib`
* **Testing:** `pytest`, `pytest-asyncio`, `unittest.mock`

---

## 3. Installation and Local Setup

### Prerequisites
* Python 3.12 or higher installed.
* `uv` package manager installed (`pip install uv` or via official installer).

### 1. Clone & Install Dependencies
```bash
git clone <repository-url>
cd <repository-folder>
uv sync
```

### 2. Configure Environment Variables
Copy the template file `.env.example` to `.env`:
```bash
cp .env.example .env
```

Set the required environment variables inside `.env`:
```env
SPREADSHEET_ID=your_google_sheet_id_here
GOOGLE_CREDENTIALS_PATH=credentials.json
APP_NAME=MaidPad Lead Automation
```

### 3. Run Test Suite
```bash
uv run pytest
```

---

## 4. Google Cloud Platform Setup Guide

To run the application against live Google Services, a Google Cloud Service Account must be configured.

### Step 1: Create GCP Project & Enable APIs
1. Access the Google Cloud Console.
2. Create a new project (e.g., `lead-automation-prod`).
3. Navigate to **APIs & Services > Library**.
4. Enable the following APIs:
   * **Google Sheets API**
   * **Google Drive API**
   * **Gmail API**

### Step 2: Create Service Account & Keys
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > Service Account**.
3. Name the account (e.g., `lead-sync-bot`) and complete creation.
4. Select the created Service Account, open the **Keys** tab, click **Add Key > Create new key**, and select **JSON**.
5. Save the downloaded file as `credentials.json` in the project root directory.

### Step 3: Grant Spreadsheet Access
1. Open the JSON credentials file and locate the `client_email` value (e.g., `lead-sync-bot@project.iam.gserviceaccount.com`).
2. Open the destination Google Sheet in your web browser.
3. Click **Share** in the upper right corner.
4. Paste the Service Account email address and assign the **Editor** role.

---

## 5. Current Execution Strategy: Polling + Labeling (Strategy 1)

### Execution Model
The application executes periodic polling queries via the Gmail API. To ensure read/unread status on dispatchers' user interfaces does not interfere with automation:

1. Query Gmail API for messages matching search filters that do **not** contain the `PROCESSED_BY_BOT` custom label (`-label:PROCESSED_BY_BOT`).
2. Parse extracted message text into structured `Lead` domain instances.
3. Append formatted lead fields to the destination Google Sheet.
4. Apply the `PROCESSED_BY_BOT` label to the email message in Gmail upon successful persistence.

### Manual Execution
```bash
uv run python -m app.main
```

---

## 6. Technical Roadmap: Migration to Strategy 2 (Real-Time Webhooks)

### Objective
Migrate from scheduled polling to event-driven real-time execution (< 1 second latency) using Google Cloud Pub/Sub and FastAPI.

### Architecture Comparison

| Aspect | Strategy 1 (Current) | Strategy 2 (Roadmap) |
| :--- | :--- | :--- |
| **Ingestion Type** | Scheduled Polling | Event-Driven Push Webhook |
| **Latency** | 1 to 5 minutes | Instant (< 1 second) |
| **Entrypoint** | CLI Script (`app/main.py`) | FastAPI Endpoint (`POST /webhook/gmail`) |
| **Infrastructure** | Local / Cron execution | Cloud Run / Web Server with HTTPS |
| **Cost** | $0.00 | $0.00 (Within GCP Free Tier quotas) |

### Migration Plan

1. **Infrastructure Component Addition:**
   * Create `app/entrypoints/api.py` exposing a FastAPI web server.
   * Add endpoint `POST /webhook/gmail` to consume Google Pub/Sub push messages.

2. **GCP Pub/Sub Setup:**
   * Create a Pub/Sub Topic: `projects/<project_id>/topics/gmail-lead-events`.
   * Grant publish permissions to Gmail service account (`gmail-api-push@system.gserviceaccount.com`).
   * Configure a Push Subscription targeting `https://<your-domain>/webhook/gmail`.
   * Call `users.watch()` in Gmail API to activate push notifications.

3. **Domain Layer Compatibility:**
   * Because the core orchestration (`SyncLeadUseCase`) relies on dependency inversion, no changes are required within `app/domain` or `app/application`.
   * The webhook handler will extract `message_id` from the Pub/Sub payload and pass it directly to `SyncLeadUseCase.execute()`.

### Free Tier Cost Breakdown (Strategy 2)
* **Google Cloud Pub/Sub:** 10 GB of monthly message traffic free.
* **Google Cloud Run:** 2 million free HTTP requests per month with scale-to-zero compute allocation.
* **SSL Certificate:** Managed HTTPS provided automatically by Cloud Run.