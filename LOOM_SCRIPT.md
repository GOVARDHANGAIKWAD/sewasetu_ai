# Loom Presentation Script: Re-imagining Sewa Setu in an Agentic World
**Format:** 3 Minutes &middot; Face and Screen Recording &middot; Build for Bharat Fellowship

---

### [0:00 - 0:35] Scene 1: Introduction & The Core Problem
**Visual:** Webcam in corner, screen showing the Sewa Setu Portal (`http://localhost:8000`).
> *"Respected Director and IAS Officers, I am your Build for Bharat fellow on the AI track. Today, I am proud to present the re-imagination of Sewa Setu—our state’s Old Age Pension portal—for an agentic world.*
>
> *Our portal maintains records for over 100,000 senior citizens across Purvanchal. But for a 68-year-old farmer in Namti or a 62-year-old widow in Sonari, filling multi-step English web forms, entering 11-digit IFSC codes, and tracking 15-day statutory SLAs is daunting. Our goal was not to replace the portal, but to turn it into an agentic public service that elderly citizens and block officers can converse with, while keeping the portal as the single, uncompromised system of record."*

---

### [0:35 - 1:20] Scene 2: Architectural Decision — Dual MCP Servers
**Visual:** Screen splits to show terminal connecting to `/mcp/citizen` and `/mcp/officer`, then showing tool lists.
> *"To achieve this, we made our most critical architectural decision: bifurcating into two independent Model Context Protocol (MCP) servers over streamable HTTP.
>
> At `/mcp/citizen`, an applicant's assistant has access only to empathetic, citizen-centric tools: `check_eligibility`, `get_scheme_guidelines`, `submit_application`, `check_application_status`, and `withdraw_application`. A citizen’s assistant is physically isolated from administrative actions.
>
> In contrast, at `/mcp/officer`, block officers access departmental tools: `list_applications`, `review_application_eligibility`, `approve_application`, and `trigger_sla_deemed_approvals`.
>
> Both endpoints support standard Streamable HTTP and SSE transports. Whether accessed via Claude Code, phone interactive voice, or a panchayat kiosk, the portal remains the authoritative system of record: applications update the central Postgres/SQLite database, generate status portal accounts, write immutable audit trails, and trigger simulated telecom SMS alerts."*

---

### [1:20 - 2:15] Scene 3: Personas, Evals & The Live Benchmark Dashboard
**Visual:** Screen switches to the Evaluation Dashboard (`http://localhost:8000/eval-dashboard`). Clicking *"Run Full Evaluation Suite"*.
> *"Now let’s look at `/eval-dashboard`. Instead of generic benchmark scores, we created 7 deeply realistic personas representing our state’s demographic reality:
> 
> 1. **Bhabesh Kalita (68, Namti):** A rural farmer who speaks Assamese-inflected English, submitting his first pension application.
> 2. **Shanti Devi (62, Sonari):** A widowed senior who needs her widow status and husband's name recorded.
> 3. **Tarun Gogoi (57, Rajapara):** An underage boundary test. Our assistant gently declines and guides him that he has 3 years remaining.
> 4. **Nogen Bora (65, Khelua):** An elder who made a mistake in his bank account. The assistant safely executes the withdrawal workflow so he can apply afresh without getting blocked by duplicate checks.
> 5. **Officer Ramesh Sharma:** Demonstrating block queue clearance and statutory SLA approvals.
>
> Notice what happens under the hood: our evaluation engine does not just evaluate conversational text. It executes strict **Before-and-After Database State Assertions**. We assert that the database actually contains the application in PENDING status, the portal user account was provisioned with DOB password hashing, and zero duplicate rows exist. All 14 assertions pass with 100% reliability."*

---

### [2:15 - 2:45] Scene 4: What We Learned & What We Changed
**Visual:** Zooming into the playground and audit trail details.
> *"What did our evals teach us, and what did we change?
>
> First, our initial tests showed elderly citizens describe their age colloquially ('born the year of the great flood' or '68 years old'). We updated `check_eligibility` to converse flexibly around date parsing while strictly enforcing the 60-year statutory boundary on the database write.
>
> Second, we identified the duplicate application trap: if an applicant typed a wrong bank account, the system locked their phone number. We engineered a conversational `withdraw_application` tool that moves the pending application to WITHDRAWN status, unlocking their mobile number to reapply safely."*

---

### [2:45 - 3:00] Scene 5: Conclusion & The Path Forward
**Visual:** Showing all running services: Portal, Dashboard, SMS Gateway, and MCP servers.
> *"With more time, our next leap will be integrating an in-process multimodal vision tool to converse with elders to fix blurry photos of handwritten certificates before submission.
>
> Sewa Setu is live, fully verified, and running on localhost with 100,000 real records. Thank you for this opportunity to build for Bharat!"*
