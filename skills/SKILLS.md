\# LinkedNektor — Project Skills \& Context



> Complete project context for use in AI harnesses (Claude Code, Antigravity, Cursor, etc.)



\## 🎯 Project Overview



\*\*LinkedNektor\*\* is a LinkedIn automation bot built in Python, focused on prospecting via bulk personalized connection requests. Designed for freelancers (especially web developers) who want to scale client outreach.



\### Goals

\- Automate LinkedIn keyword searches

\- Apply advanced filters (city, "Hiring now", job title)

\- Visit profiles individually and send connection requests

\- Support optional personalized note on requests

\- Simple GUI (Tkinter) for configuration

\- Bilingual support (PT-BR / EN)



\---



\## 🧰 Tech Stack



| Component | Technology | Reason |

|-----------|-----------|--------|

| Language | Python 3.x | Rich automation ecosystem |

| Web automation | Playwright (sync API) | More robust than Selenium, better for SPAs like LinkedIn |

| Browser | Chromium (persistent context) | Maintains login between sessions |

| GUI | Tkinter (stdlib) | No external deps, cross-platform |

| Threading | `threading` stdlib | Bot runs on a separate thread from UI |

| URL parsing | `urllib.parse` | Query param encoding |



\### External dependencies

```bash

pip install playwright

playwright install chromium

