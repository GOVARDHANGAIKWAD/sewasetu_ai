# Design Note: Re-imagining Sewa Setu in an Agentic World
**Build for Bharat Fellow — AI Track**  
**Department of Social Welfare, Government of Purvanchal**  
*System: Sewa Setu Old Age Pension Service*

---

## Executive Summary
Sewa Setu serves over 100,000 elderly citizens across Purvanchal. Navigating complex government portals, filling multi-step English forms, uploading certificates, and monitoring statutory SLAs are daunting barriers for rural, low-literacy senior citizens. By re-imagining the portal as an agentic service with dual streamable HTTP Model Context Protocol (MCP) servers and an automated continuous evaluation engine, we maintain the portal as the authoritative system of record while empowering applicants and block officers with purpose-built AI assistants.

---

## The Three Decisions That Mattered Most

### 1. Architectural Bifurcation of MCP Servers over Streamable HTTP
**Decision:** We implemented two independent MCP endpoints (`/mcp/citizen` and `/mcp/officer`) rather than a single unified server with role-based filtering.  
**Rationale:** In high-stakes public welfare systems, security and prompt-injection defense must be enforced at the transport and schema layer, not delegated to model compliance. A citizen's assistant (whether run via Claude Code, phone agent, or WhatsApp bot) is fundamentally incapable of querying administrative queues, inspecting neighboring citizens' files, or altering decision statuses because officer tools (`approve_application`, `reject_application`, `trigger_sla_deemed_approvals`) simply do not exist in the citizen schema (`tools/list`). Both servers implement standard MCP 2024-11-05 protocols over Streamable HTTP and Server-Sent Events (SSE), ensuring compatibility across all clients.

### 2. Single Source of Truth: Portal as System of Record
**Decision:** The AI assistants never maintain an independent database, separate state, or shadow queue. All tool executions invoke identical core business rules (`validate_application`, `create_application`, `active_application`) and transact directly with the central database.  
**Rationale:** Administrative integrity is non-negotiable. If an assistant admits an application, it must provision the status portal account (`portal_users` with DOB password hash), log an immutable audit event (`audit_log`), and queue telecom dispatch (`sms_gateway`). The portal remains the single system of record, guaranteeing that web applications, mobile apps, and autonomous agents obey identical statutory standards.

### 3. Empirical Persona Evals Coupled with Database State Assertions
**Decision:** We built an empirical evaluation harness at `/eval-dashboard` driven by 7 specific personas (such as 68-year-old rural farmer Bhabesh Kalita and 57-year-old underage applicant Tarun Gogoi) that evaluates real multi-turn conversations and asserts on post-conversation database states rather than model sentiment.  
**Rationale:** Public service AI cannot be evaluated by generic benchmarks. What matters is: *Did the database reject the underage applicant? Was the duplicate phone number blocked? Did the widow's marital status record accurately?* Our evaluation framework continuously validates that after every simulated citizen interaction, the database transitions to the exact required legal state with 100% assertion pass rates.

---

## The One Decision We Would Make Differently with More Time

### Conversational Document Vision Extraction & OCR Pipeline
**Current Approach:** The citizen assistant accepts document references or pre-uploaded file identifiers, validating their presence before triggering application creation.  
**With More Time:** We would integrate an in-process, privacy-preserving multimodal OCR tool directly into the Citizen MCP pipeline (using local lightweight vision models). Elderly citizens in rural Purvanchal frequently present blurred, low-resolution phone photos of handwritten gaon-bura certificates, voter ID cards, or torn passbooks. An agentic vision tool that can converse in Assamese/Bengali to guide the citizen ("Please tilt the phone slightly and wipe the camera lens—I cannot read the last 3 digits of your account number") before submitting would eliminate the primary cause of departmental rejection at the first mile.

---

## Submission Summary & Endpoints
- **Portal URL:** `http://localhost:8000`
- **Citizen MCP Server (Streamable HTTP):** `http://localhost:8000/mcp/citizen`
- **Citizen MCP SSE Handshake:** `http://localhost:8000/mcp/citizen/sse`
- **Block Officer MCP Server (Streamable HTTP):** `http://localhost:8000/mcp/officer`
- **Block Officer MCP SSE Handshake:** `http://localhost:8000/mcp/officer/sse`
- **Evaluation Dashboard:** `http://localhost:8000/eval-dashboard`
- **Departmental Officer Login:** User `admin`, Password `admin123`
- **Simulated SMS Gateway:** `http://localhost:8000/__gateway/`
