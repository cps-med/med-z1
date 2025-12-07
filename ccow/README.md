# HL7 CCOW Context Management Service

## Overview

The **CCOW Context Vault** is a lightweight subsystem within med-z1 that implements a simplified version of the HL7 CCOW (Clinical Context Object Workgroup) standard for patient context synchronization. This utility enables med-z1 and other clinical applications to maintain a shared "active patient" context, supporting seamless clinical workflows across multiple applications.

### Purpose

- Provide a **single source of truth** for the currently active patient context across multiple applications
- Enable med-z1 to **notify** external systems when the user changes the active patient
- Allow external applications to **query** the current active patient and optionally **set** the context
- Support future integration scenarios where multiple clinical applications need to stay synchronized

### Scope

This is a **mock/development implementation** designed to:

- Demonstrate CCOW-like context synchronization patterns
- Support local development and testing scenarios
- Serve as a foundation for future production CCOW integration

**Explicitly Out of Scope (Phase 1):**
- Full CCOW standard compliance
- Authentication/authorization
- Persistent storage (vault resets on service restart)
- Multi-user or multi-session contexts
- Real-time push notifications to clients (WebSocket/SSE)

This subsystem simultates CCOW, and does not perform full context negotiation, subscriptions, or multi-subject contexts. Think of this as:  
> "A tiny context manager service that keeps track of the current patient and shares it via HTTP."  

### Ports

If you don’t specify a port, Uvicorn defaults to 8000. Since the main app/ service is already using 8000, the CCOW service must use a different port.  

Using 8001 for CCOW is totally reasonable and a common pattern:

```bash
# main med-z1 app
uvicorn app.main:app --reload --port 8000

# CCOW service
uvicorn ccow.main:app --reload --port 8001
```

Now you have:

- Main app at: http://localhost:8000  
- CCOW service at: http://localhost:8001  

And your med-z1/app code can talk to CCOW at something like:  

- CCOW_BASE_URL = "http://localhost:8001"


## How to Test the Live API

Since the vault logic works, the next exciting step is to start the FastAPI service and test the HTTP API!

Here's what to do:

Start the CCOW service:
```
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn ccow.main:app --port 8001 --reload
```

In another terminal, test the endpoints:
```
# Health check
curl http://localhost:8001/ccow/health

# Try to get active patient (should be 404 initially)
curl http://localhost:8001/ccow/active-patient

# Set active patient
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "1234567V890123", "set_by": "med-z1"}'

# Get active patient (should work now)
curl http://localhost:8001/ccow/active-patient

# To see the http response code, add the -i parameter
curl -i http://localhost:8001/ccow/active-patient

# To see even more, use the -v parameter
curl -v http://localhost:8001/ccow/active-patient

# View history
curl http://localhost:8001/ccow/history
```

View auto-generated docs in browser:
```
http://localhost:8001/docs
```
