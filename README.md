# 🚀 "Bob — Mission Readiness & Predictive Maintenance Copilot"   

> ⚠️ **Replace everything in `[ ]` brackets with your actual content before submission.**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | CodeNova4 |
| **Track** | AI |
| **Team Lead** | Aarohi Patel — 26it049@charusat.edu.in |
| **Members** | Aastha Patel, Krisha Patel, Purva Patel |

---

## 🎯 Problem Statement

>  What problem does your project solve? Who experiences this problem?
>  Military organisations cannot reliably determine whether aircraft, vehicles,
    and equipment are mission-ready. Maintenance runs on fixed calendar schedules
    regardless of actual component condition, and HUMS (Health & Usage Monitoring
    System) sensor data that could predict failures weeks in advance sits
    unanalysed — so platforms fail unexpectedly, readiness drops, and recovery
    takes weeks.






## 💡 Solution

> In 2–3 sentences: What did you build? How does it solve the problem above?

A Bob Copilot that ingests HUMS sensor data and service records, flags which
    assets are not mission-ready, explains each readiness issue in plain
    language, predicts which components will breach failure thresholds before
    the next mission window, and produces one fleet-wide prioritized maintenance
    plan ranked by urgency.




## ✨ Key Features

- "Fleet-wide readiness snapshot — Mission Ready / At Risk / Non-Mission-Capable counts at a glance"
-  "Automated non-ready asset detection against per-component sensor thresholds"
- "Plain-language issue explanations for every flagged component, generated via IBM watsonx.ai (Granite) with a rule-based fallback"
- "Predictive failure timing — projects days-to-breach per component and checks it against the next mission window"
-  "Fleet-wide prioritized maintenance plan ranking every flagged component by urgency with a recommended action"



---

## 🛠️ Tech Stack

    languages: ["JavaScript (JSX)", "HTML5", "CSS3"]
    frameworks: ["React 18", "Babel Standalone", "Recharts"]
    ibm_technologies: ["watsonx.ai (Granite model)", "IBM Db2 / Cloudant", "IBM Cloud IAM"]
    databases: ["IBM Db2 / Cloudant (live mode)", "In-memory seeded mock data (demo mode)"]
    other: ["Google Fonts (CDN)", "cdnjs (React/ReactDOM/Babel CDN delivery)"]



---

## 📁 Repository Structure

```
├── src/                  # All source code
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   └── demo-video-link.txt  # Link to demo video
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/[your-repo].git
cd [your-repo]

# 2. Install dependencies
[your install command here]

# 3. Configure environment
cp .env.example .env
# Edit .env with your values

# 4. Run the project
[your run command here]
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

---

## ⚠️ Known Limitations

    Sensor and service-record data is currently synthetic (seeded mock data) —
    real HUMS/Db2 integration is scaffolded (see src/) but not populated with
    live data. The watsonx.ai and Db2/Cloudant integrations are implemented and
    toggle-ready in code but were not tested against live IBM Cloud credentials
    in this environment. Failure prediction uses a linear trend-rate projection
    rather than a trained ML model.


---

## 🏅 What We're Most Proud Of

    The explainability layer: every readiness flag is backed by a plain-language
    reason (current reading, % of threshold, trend rate, days-to-breach relative
    to the next mission window) rather than a black-box score, so a maintenance
    officer can trust and act on the recommendation immediately. The app also
    degrades gracefully — it runs fully on rule-based logic and mock data out of
    the box, and upgrades automatically to live watsonx.ai explanations and
    Db2/Cloudant data once credentials are supplied, without any code changes.



---
