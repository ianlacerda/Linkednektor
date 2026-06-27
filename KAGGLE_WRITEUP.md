# Kaggle AI Agents Capstone Project: Writeup

**Track:** Freestyle
**Project Repository:** https://github.com/ianlacerda/Linkednektor
**Author:** Ian Lacerda

---

# Linkednektor: An Intelligent Desktop Automation Agent for Resilient LinkedIn Networking

### Subtitle:
*Applying course concepts of human simulation, state-persistence databases, and collaborative AI pair-programming with Google's Antigravity to build a robust, GUI-controlled networking agent.*

---

## 📋 1. Project Overview & Value Proposition

In the modern professional landscape, networking is paramount. Recruiters, sales representatives, and founders spend hours daily expanding their networks on LinkedIn. Doing this manually—searching for profiles, applying filters, clicking "Connect," typing personalized notes, and avoiding sending duplicate invites to past contacts—is highly repetitive, tedious, and time-consuming. 

**Linkednektor** solves this challenge by introducing an intelligent desktop automation agent that automates the entire LinkedIn networking pipeline. By simulating natural human behavior, utilizing a local state database to prevent duplicates, and dynamically adapting to responsive page layouts, Linkednektor turns hours of manual work into a single-click background task.

---

## 🛠️ 2. Core Concepts Applied (Course Connection)

We applied four key concepts from the **5-Day AI Agents: Intensive Vibe Coding Course**:

### A. Agent Architecture & Extensibility (ADK/MCP Ready)
The codebase is designed with a strict modular architecture separating:
- **GUI Engine (`src/gui.py`)**: A clean Tkinter interface managing user configurations, multithreaded runtime, and execution lifecycle.
- **State Database (`src/db.py`)**: An SQLite3 backend checking and caching contacted profiles.
- **Automation Controller (`src/bot.py`)**: The browser automation logic powered by Playwright.
This separation allows the automation controller's core functions (like `collect_profile_links` and `find_connect_button_on_profile`) to be easily exposed as **ADK Tools** or an **MCP (Model Context Protocol) Server**, enabling a LLM-based agent (like Gemini) to orchestrate professional outreach campaigns.

### B. Security & Privacy Guardrails
Security was built into the agent's core design:
- **Credential Masking**: The agent utilizes local persistent Chrome profiles (`linkednektor_profile/`), keeping user session cookies and login credentials secure and local.
- **Strict Git Protection**: The `.gitignore` is hardcoded to prevent pushing sensitive session cookies (`linkednektor_profile/`), local databases (`linkednektor.db`), and debug logs (`debug_dumps/`) to public repositories.
- **Accidental Action Prevention**: Before interacting, the agent scans dropdown elements. If a "Remove Connection" (or Portuguese "Desfazer conexão") option is detected, it closes the menu and flags the user as `already_connected` in the SQLite DB, protecting the user's active network from accidental removal.

### C. Antigravity & Vibe Coding Partnership
This project was developed through a direct pair-programming partnership with **Antigravity** (Google DeepMind's agentic AI coding assistant). By adopting the "Vibe Coding" philosophy, the developer focused on defining the high-level intent, while Antigravity executed complex responsive-layout selectors, implemented database schemas, and structured the project structure. This collaborative workflow drastically accelerated development from a simple script to a feature-rich, robust desktop agent.

---

## 📐 3. System Architecture & Solution Design

Below is the conceptual workflow showing how the agent coordinates search parsing, profile visits, layout detection, and state tracking:

```mermaid
graph TD
    A[GUI: User Input & Start] --> B[Playwright: Initialize Persistent Browser]
    B --> C[LinkedIn Search Page]
    C --> D[Scroll & Collect Cards]
    D -->|Filter out Mutual Connections| E[Extract Candidate URL]
    E --> F{DB: Contacted Already?}
    F -->|Yes| G[Skip Profile]
    F -->|No| H[Navigate to Profile Page]
    H --> I{Topcard Selector Match}
    I -->|Direct Button| J[Click Connect]
    I -->|No Button / Responsive Link| K[Scope Topcard a[href] or More Dropdown]
    J --> L[Handle Invitation Note Modal]
    K --> L
    L --> M[Log to SQLite DB as 'sent']
    M --> N[Return to Search Page]
    G --> D
```

### Technical Highlights
1. **Thread-Safe Pause/Resume Controls**: Using Python's `threading.Event`, the user can instantly pause the bot mid-run. The Playwright delay loops check this event state in 0.2s slices, making the GUI incredibly responsive.
2. **Layout Adaptability**: LinkedIn often renders a responsive (mobile-optimized) view instead of desktop inside automated instances. The agent handles this by checking container component keys (`[componentkey*='Topcard']`) and targeting responsive elements (like `<a>` tags with `custom-invite` hrefs) rather than relying on hardcoded desktop CSS classes.
3. **HTML/Screenshot Debug Dumps**: If any profile action fails, the bot dumps the page source and a PNG screenshot into a local `debug_dumps/` directory, logging clickable `file:///` links to the terminal to facilitate instant diagnosis.

---

## 🚀 4. How to Set Up & Reproduce

Follow these steps to run the agent locally on your machine:

1. **Clone the Project:**
   ```bash
   git clone https://github.com/ianlacerda/Linkednektor.git
   cd Linkednektor
   ```
2. **Create and Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/Mac:
   source venv/bin/activate
   ```
3. **Install Dependencies & Playwright Binaries:**
   ```bash
   pip install playwright
   playwright install chromium
   ```
4. **Run the Application:**
   ```bash
   python main.py
   ```
5. **Initial Run:**
   - Enter your search keyword and target city.
   - Click **Iniciar Buscas**. A browser window will open.
   - Log in manually to your LinkedIn account. Playwright will store the session in `linkednektor_profile/` so you only log in once.
   - To clear your prospecting history and run tests again, click the **🧹 Limpar Histórico** button.

---

## 📈 5. Conclusion & Future Outlook

Linkednektor successfully demonstrates how desktop browser automation and state management can be unified under a user-friendly interface. In the future, this project can be expanded into a multi-agent system where one agent researches candidate profiles, another uses Gemini to generate personalized invitation notes, and Linkednektor serves as the execution tool to send the invites.
