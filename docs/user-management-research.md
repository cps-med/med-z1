PROMPT 1: 
The med-z1 application that I am developing uses a Python based technology stack that includes FastAPI, HTMX, and Jinja2 templates. Currently, the root route ("/") takes users to the main dashboard landing page. The application does not yet include user login, authorization, and authentication, but I would like to enhance the application to add this capability. I would like to simulate the current single sign-on processing flow that the legacy VA Joint Longitudinal Viewer (JLV) uses to grant users access to the JLV application. This mechanism involves the VA Identity and Access Management (IAM) service and the registered VistA site or sites that a user has access to. There is also a concept of a "home site" that plays into the login workflow. I don't fully understand the current login flow, but have attached two JLV documents that may provide insight: a JLV user guide and a JLV design document. In addition to the current user login mechanism and flow, I would like to better understand any new direction that VA is heading with respect to user access and authorization, for example the use of Microsoft Entra ID. I would like to understand both technologies and workflows so that I can decide which version I should implement with med-z1. I have also attached a few technical specification and design documents that describe the med-z1 application, including the "app" subsystem, which implements the web-browser based UI. Please provide any guidance and advice as I begin to create a technical approach and design for adding user login to the med-z1 application. In addition to basic login functionality, I would also like to maintain a user profile and user preferences. Both of these will likely be implemented as part of the PostgreSQL serving database, e.g., as one or more tables. Please ask any clarification questions that you have.

RESPONSE 1: 
Adding user login and authentication to **med-z1** will involve bridging legacy VA patterns with modern, Python-based web development. Below is guidance on how to simulate the current JLV login flow and integrate it into your FastAPI/HTMX stack, along with insights into the VA's strategic shift toward Microsoft Entra ID.

### 1. Understanding the JLV Login Flow

The current JLV authentication mechanism relies on **Single Sign-On Internal (SSOi)**, managed by VA Identity and Access Management (IAM). This flow is characterized by the following steps:

* **Initial Redirection**: When a user accesses the JLV URL, they are redirected to the VA SSOi page.
* **PIV Authentication**: The user must present their Personal Identity Verification (PIV) card and PIN.
* **Identity Linking**: To bypass secondary login screens, a user's PIV card must be linked to their VistA account in IAM. If not linked, the user is prompted for their **VistA Access and Verify codes**.
* **Site and Role Selection**: Users select their "User Type" (e.g., CPRS user, VBA user). For VHA/CPRS users, they must also select a **"home site"**—the specific VA Medical Center where their access is valid.
* **Token Retrieval**: Upon successful authentication, the system checks for a valid IAM Security Assertion Markup Language (SAML) token, which must be periodically renewed.

### 2. VA's Future Direction: Microsoft Entra ID

The VA is actively modernizing its identity infrastructure by transitioning to **Microsoft Entra ID** (formerly Azure AD).

* **Centralized Identity**: Entra ID serves as the central identity management solution for approximately 850,000 VA employees and contractors.
* **Standards-Based**: Unlike the older, more complex SAML-based SSOi, Entra ID leverages modern protocols like **OpenID Connect (OIDC)** and **OAuth 2.0**, which are natively supported by modern Python libraries like `authlib`.
* **Phish-Resistant MFA**: A major driver for this move is meeting federal mandates for phish-resistant multifactor authentication, such as Entra Certificate-Based Authentication (CBA).

### 3. Recommended Technical Approach for med-z1

For your FastAPI application, it is recommended to design an authentication layer that can support both workflows, starting with a simulation of the JLV flow for local development.

#### A. Simulating the JLV Flow (Development)

You can mock the "Site" and "Access/Verify" login pattern using a dedicated login route in FastAPI:

* **Login View**: Use a Jinja2 template to render a selection list of VistA sites (matching your mock `CDWWork` stations).
* **HTMX Integration**: Use `hx-post` to send the Access/Verify codes to a `/login` endpoint.
* **Session Management**: Store the authenticated user's ICN, selected "home site," and role in a secure, signed session cookie or a `Redis` store, mirroring JLV's use of **ElastiCache for Redis** for session management.

#### B. Implementing Profile & Preferences in PostgreSQL

You should establish a `users` schema in your PostgreSQL serving database. Based on the JLV design, your schema should include:

* **User Profile Table**: Columns for `user_id`, `email`, `default_home_site`, and `last_login_date`.
* **Preferences Table**: Store UI settings like `theme` (Blue, Green, Accessible), `audible_alert` toggles, and `date_filters`.
* **Audit Table**: VA policy requires detailed auditing of patient data access. Maintain a table to record `timestamp`, `user_id`, `patient_icn`, and `action_performed`.

### 4. Clarification Questions

To refine the design, could you provide more detail on:

1. **Mock Identity Mapping**: Do you have a mapping file that links your synthetic users to specific mock sites in the `CDWWork` environment?
2. **Context Management Integration**: Will your login flow need to immediately trigger a patient context set in your `ccow-vault` service?
3. **Future Entra ID Support**: Do you want the initial design to be "OIDC-ready," allowing you to plug in real Entra ID credentials once you move beyond the mock environment?

PROMPT 2: 
Answers to clarification questions. Question 1: No, I do not yet have a mapping file, but would like to create one and use this as part of the solution. Question 2: The current CCOW simulation service that I built into med-z1 accounts for the patient user ID value and the med-z1 user ID, but a multi-user version of this CCOW utility has not been implemented yet. Currently, it is single threaded in that a change to the CCOW vault is treated universally for all users. To answer your specific question, no, thelogin flow does not need to immediately triger a patient context set in the ccow-vault service. I will consider this as a possible future enhancement. Question 3: I would actually like to only focus on the new Entra ID direction that VA is headed. I would like for the med-z1 login flow to align with this (to the extent possible). A few other notes to consider: The MVP med-z1 application and login flow WILL NOT require a PIV card, but I am open to simulating this to the extent possible. Another twist is that I am working on a design to build out med-z1 to support both the current CDWWork database (VistA site data) and the new Oracle Cerner Health EHR data, which will be managed in a new and separate med-z1 mock SQL Database called CDWWork2. So, it may be necessar to build in capability to manage users without being tightly tied to CDWWork or CDWWork2. For example, a new database for any functionality and user management that is not specific to CDWWork or CDWWork2 data. 

RESPONSE 2: 
Based on your focus on **Microsoft Entra ID** and the need for a vendor-neutral user management system (independent of `CDWWork` or `CDWWork2`), here is a technical approach and design guidance for adding user login to **med-z1**.

### 1. Architectural Strategy: The "Auth Database"

Since you are supporting both VistA (`CDWWork`) and Oracle Health (`CDWWork2`), you should avoid coupling user identities to a specific EHR database. Instead, implement a **User Management Schema** within your existing **PostgreSQL serving database**. This aligns with your plan to maintain profiles and preferences there.

#### Recommended Schema Design

Create a new `users` schema with the following tables:

* **`users`**: Stores the primary identity.
* `user_uuid` (Primary Key)
* `entra_id_oid`: The unique Object ID from Microsoft Entra ID.
* `email`, `display_name`


* **`user_profiles`**: Linked to `user_uuid`.
* `default_home_site`: The primary VA site code (e.g., "508").
* `role`: (e.g., Physician, Nurse, Admin).


* **`user_preferences`**: JSONB column for UI settings (Theme, Dashboard layout).

### 2. Simulating the Microsoft Entra ID Flow

VA's move to Entra ID shifts away from complex legacy SAML/SSOi toward **OpenID Connect (OIDC)**. In your FastAPI stack, you can simulate this flow without requiring a physical PIV card.

**The Workflow:**

1. **Login Route**: User visits `/login`. If not authenticated, FastAPI redirects to a mock Entra ID login page.
2. **Mock Entra ID Provider**: Create a simple Jinja2 page that mimics the VA/Microsoft sign-in screen.
* Instead of a PIV card, provide a "Simulate PIV Login" button that selects a mock Entra ID token.


3. **Token Exchange**: Upon "login," the mock provider redirects back to `/auth/callback` with a JWT (JSON Web Token).
4. **Session Creation**: FastAPI verifies the JWT, retrieves the `entra_id_oid`, and looks up the user in your PostgreSQL `users` table.
5. **Profile Retrieval**: The application loads the user's "Home Site" and preferences into the session cookie.

### 3. Implementing with FastAPI, HTMX, and Jinja2

To keep the UI fast and "server-side first," use the following patterns:

* **Middleware for Auth**: Implement a FastAPI `BaseHTTPMiddleware` that checks for a session cookie on every request to `/` or `/api`. If missing, it triggers an HTMX-aware redirect to `/login`.
* **HTMX Login Handling**: If an unauthenticated user triggers an HTMX request (like clicking a dashboard widget), your backend should return a `HX-Trigger: "unauthorized"` header. Your `app.js` can listen for this and redirect the full page to login.
* **Profile/Preferences Component**:
* **Preferences UI**: Use HTMX `hx-post` to update individual settings (e.g., toggling a "Dark Mode" setting). This updates the PostgreSQL `user_preferences` table and returns the updated Jinja2 partial for the settings menu.



### 4. Mapping Users to Sites (CDWWork & CDWWork2)

As you requested, you can create a **Mock Identity Mapping File** to bridge your users to the clinical data.

**Sample `mock_user_mapping.json`:**

```json
{
  "users": [
    {
      "email": "clinician.alpha@va.gov",
      "home_site": "508", 
      "authorized_sites": ["508", "630"],
      "ehr_access": ["CDWWork", "CDWWork2"]
    }
  ]
}

```

* **Design Guidance**: During the login flow, read this mapping to populate the user's initial permissions. When the user queries data, your API routes should filter by the `authorized_sites` found in this mapping to ensure they only see data for stations they have access to.

### 5. Next Steps & Clarification

1. **Session Security**: For the MVP, are you comfortable using **Signed Session Cookies** (stored in the browser) for user state, or would you prefer a server-side session store in **PostgreSQL** to allow for easy session revocation?
2. **Role Simulation**: Do you want to implement different Dashboard layouts based on the user's role (e.g., a "Nurse View" vs. a "Physician View") as part of the profile/preferences work?

PROMPT 3: 
Answers to section 5 questions. Question 1: I would prefer a server-side session store in PostgreSQL. Question 2: No, role simulation functionality is not a requirement.

RESPONSE 3: 
To finalize your technical approach for the **med-z1** login flow using **Microsoft Entra ID** and **PostgreSQL**, I have outlined a refined design below. This approach ensures a clean separation between user management and clinical data while aligning with the VA's modern identity direction.

### 1. Server-Side Session Architecture

By choosing a **PostgreSQL session store**, you enhance security and control, as sessions can be invalidated instantly by the administrator if a security event occurs.

**Session Table Schema (`users.sessions`):**

* **`session_id`**: A secure, randomly generated UUID (Primary Key).
* **`user_uuid`**: Foreign key to your new `users` table.
* **`created_at` / `expires_at**`: To manage session timeouts.
* **`context_data`**: A JSONB field to store the user's active site or temporary session-specific metadata.

**FastAPI Implementation:**

* **Middleware**: Create an authentication middleware that extracts the `session_id` from a signed cookie.
* **Validation**: On every request, the middleware queries the PostgreSQL session table to verify the ID is valid and not expired.
* **HTMX Integration**: If a session is expired or invalid, the backend returns an `HX-Trigger: "unauthorized"` header, prompting the browser to redirect the full page to the login screen.

### 2. Microsoft Entra ID Simulation (OIDC Flow)

Since you are focusing strictly on the **Entra ID** direction, the login flow will follow the **OpenID Connect (OIDC)** standard rather than the legacy SAML/SSOi process.

**The Simulated Login Process:**

1. **Initiation**: The user clicks "Login" on the med-z1 landing page.
2. **Redirect**: FastAPI redirects the user to a mock "VA Entra ID" login portal (a Jinja2 template).
3. **Authentication**: The user enters their email or clicks "Simulated PIV Login."
4. **Callback**: The mock portal redirects back to `app/routes/auth.py` with an **ID Token** (JWT).
5. **User Verification**: The app decodes the JWT to find the `entra_id_oid` (Object ID) and checks if the user exists in the `users` table.
* *If the user is new*, the system creates a new record in your PostgreSQL `users` and `user_profiles` tables based on your **Mock Identity Mapping File**.


6. **Session Establishment**: A new session is written to PostgreSQL, and the `session_id` is set in the user's browser cookie.

### 3. User Profiles and Preferences

Your user management will reside in a dedicated schema within the PostgreSQL serving database, keeping it independent of the clinical data in `CDWWork` or `CDWWork2`.

* **User Profiles**: This table will store non-clinical metadata such as the user's `default_home_site` (e.g., "508") and their `authorized_sites` list derived from your mapping file.
* **User Preferences**: Implemented as a JSONB column, this allows you to store UI settings like a preferred theme (Light/Dark) or a specific "Home" dashboard configuration without needing complex schema changes in the future.

### 4. Implementation Guidance for HTMX & Jinja2

To manage the login state across the dashboard, use a **Jinja2 partial** for the top-right corner of the topbar:

* **Logged-In State**: Displays the user's name and a "Logout" button.
* **Logged-Out State**: Displays a "Login" button.
* **HTMX Refresh**: When the user logs in or out, use HTMX `hx-swap` to update only that portion of the header, ensuring the rest of the dashboard remains intact if needed.

### Next Steps for Your Technical Design:

1. **Mock Mapping File**: Create a `user_site_mapping.json` file to define which mock users have access to which VistA (`CDWWork`) or Oracle Health (`CDWWork2`) sites.
2. **Auth Router**: Build the `app/routes/auth.py` file to handle the OIDC redirect and callback logic.
3. **Session Middleware**: Implement the PostgreSQL-backed session verification logic.
