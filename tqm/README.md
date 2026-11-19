# Total Quality Management (TQM) Artefacts

**Course:** BBAT104 — Fundamentals of Total Quality Management  
**Baseline:** Baseline No. 9 (Quality Goal Implementation)  
**Project:** Online Quiz System — Quality-Engineered Multi-Tier Anti-Duplicate Architecture  
**Milestone:** Stage 8 — Capstone TQM Quality Artefacts  
**Standard Compliance:** ISO 9001:2015, ISO 9004:2018, AIAG & VDA FMEA Standard  

---

## Executive Index of TQM Artefacts

This directory contains the formal Total Quality Management analysis and verification documents synthesizing the engineering achievements of the 8-stage pipeline:

| Artefact | Document | Graphical Assets | Key Highlights & Outcomes |
| :--- | :--- | :--- | :--- |
| **1. SIPOC Process Map** | [sipoc.md](sipoc.md) | Mermaid Flowcharts | High-level process boundaries, input/output criteria, and CTQ measures for both *Quiz Authoring* and *Assessment Delivery* lifecycles. |
| **2. FMEA Matrix** | [fmea.md](fmea.md) | Mermaid Risk Chart | Comprehensive Failure Mode and Effects Analysis evaluating 8 failure modes. Quantifies a **$98.97\%$ overall RPN risk reduction** (from 2,626 to 27). |
| **3. Pareto Analysis** | [pareto.md](pareto.md) | [pareto_chart.png](pareto_chart.png) (300 DPI) | Statistical Quality Control (SQC) Pareto distribution of empirical defects from `docs/defect-log.md`. Shows the **vital few** categories (62.5% of defects) and Juran analysis. |
| **4. Ishikawa (Fishbone)** | [fishbone.md](fishbone.md) | [ishikawa_fishbone.png](ishikawa_fishbone.png) (300 DPI) | Cause-and-Effect root-cause analysis of duplicate entries across the **6M framework** (Man, Machine, Method, Material, Measurement, Milieu). |
| **5. Deming PDCA Cycle** | [pdca.md](pdca.md) | Mermaid Cyclic Flowchart | Synthesis of the Plan-Do-Check-Act closed-loop governance cycle across Stages 1–8, detailing four iterative **Kaizen** improvements and the future production roadmap. |

---

## Regenerating Visual Assets

To regenerate the high-resolution 300 DPI charts:

```powershell
# In project root:
.\venv\Scripts\activate

# 1. Regenerate Pareto Chart:
python tqm/generate_pareto.py

# 2. Regenerate Ishikawa Fishbone Diagram:
python tqm/generate_fishbone.py
```
