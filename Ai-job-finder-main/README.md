# 🚀 AI Resume Job Matcher

**A Free, AI-Powered Recruitment Tool.**

This project is a full-stack Python application that takes a PDF resume, "reads" it using Natural Language Processing (NLP), automatically searches for relevant global remote jobs, and ranks them based on Semantic Similarity using Deep Learning embeddings.

---

## 🤖 How I Built This (The AI-First Approach)

This project was built using an **AI-Assisted Development workflow**. Acting as the Technical Architect, I orchestrated a Large Language Model (Gemini) to accelerate development from concept to deployment.

**The Workflow:**
1.  **Architectural Prompting:** I defined strict constraints (Zero Cost, No Paid APIs, Local Processing) and prompted the AI to design a modular architecture (`parsers`, `nlp`, `matching`).
2.  **Automated Scaffolding:** Instead of manually creating files, I engineered a Python script (`setup_final.py`) to generate the entire project structure, environment configurations, and boilerplate code instantly.
3.  **Iterative Debugging:** When external APIs (Remotive) failed with `526 Errors`, I analyzed the logs and prompted the AI to implement a robust "Fallback Mechanism," integrating the **Jobicy API** and a safety-net search logic to guarantee results.

This approach demonstrates **Rapid Prototyping** and **AI Orchestration** skills.

---

## 🧠 How It Works (Architecture)

The system operates in a 4-step pipeline:

```mermaid
graph LR
A[PDF Resume] --> B(Parser - PyMuPDF)
B --> C{NLP Engine - spaCy}
C --> D[Extract Top Skill]
D --> E[API Job Fetcher]
E --> F[Vector Embedding - BERT]
F --> G[Ranked Results]