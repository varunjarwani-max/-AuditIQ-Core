# AuditIQ — On-Premise Multi-Model AI Audit Engine

**AuditIQ** is a privacy-first, on-premise AI platform designed to automate general ledger analysis and complex audit tasks for mid-market Chartered Accountancy (CA) firms. It is deployed entirely behind the client's corporate firewall to ensure absolute data sovereignty.

🌐 **Frontend UI Prototype:** [v0-ai-auditor-platform-ten.vercel.app](https://v0-ai-auditor-platform-ten.vercel.app/)

---

## 1. The Enterprise Problem
During financial audits, mid-market CA firms are forced to manually process thousands of general ledger transactions. Because manual review is bottlenecked by human hours, auditors rely on **random sampling**—meaning up to 90% of a company's ledger is never actually reviewed for fraud, anomalies, or compliance errors.

While cloud-based AI (like OpenAI's GPT-4 or Anthropic's Claude) can easily automate 100% ledger coverage, CA firms are legally prohibited from sending highly sensitive, unredacted client financial data to third-party cloud APIs due to strict Non-Disclosure Agreements (NDAs), SOC2 compliance regulations, and data sovereignty laws.

## 2. The Solution: Zero-Exfiltration AI
AuditIQ brings the intelligence of modern Large Language Models directly to the data, rather than sending the data to the model. 

AuditIQ guarantees **zero data exfiltration** by deploying directly on the client's internal IT infrastructure. It processes ledgers locally on secure on-premise servers utilizing highly optimized, quantized Small Language Models (specifically **Gemma 3.1**). The data never touches the public internet.

---

## 3. Core Innovation: Sequential VRAM Architecture
Mid-market enterprise servers are typically optimized for database storage, not AI compute. They rarely feature the massive, unconstrained GPU clusters required to run modern AI models concurrently. 

If AuditIQ attempted to load its entire multi-agent system (seven distinct reasoning models) into a standard enterprise server's VRAM at the same time, the system would immediately crash with an Out-Of-Memory (OOM) error.

To solve this, AuditIQ implements a **Sequential Batch Pipeline** that orchestrates GPU memory dynamically:

1. **Isolate & Load:** The orchestrator loads a single, highly specific, narrow model (e.g., a 3B parameter classification model) into the server's GPU memory.
2. **Batch Process:** The entire transaction ledger is streamed through this single node.
3. **Deallocate:** The orchestrator completely unloads the model from memory, freeing 100% of the VRAM.
4. **Advance:** The next specialized model in the sequence is loaded into the newly freed memory.
5. **Targeted Compute:** Heavy reasoning agents (9B+ parameters) are extremely expensive to run. To optimize compute, these large models are *only* spun up and applied to the fraction of transactions that trigger critical anomaly flags in earlier stages.

---

## 4. Technical Pipeline Stages

The backend core engine utilizes a cascading pipeline that separates deterministic rules from heuristic AI reasoning, minimizing hallucinations and maximizing speed.

### Stage 1: Classification & Tagging (100% Coverage)
A lightweight model categorizes raw ledger line items into structural operational accounts (e.g., Operating Expense vs. Capital Expense) based on context clues in the vendor name and category hint.

### Stage 1.5: Deterministic Duplicate Sweep
Before utilizing expensive AI compute, the engine runs an immediate, deterministic hash-comparison algorithm across the batch. It searches for exact vendor-amount matches to catch potential duplicate billing errors and double-payments instantly.

### Stage 2: Heuristic Risk Evaluation (100% Coverage)
A specialized risk model evaluates transaction values against statistical materiality limits. It looks for behavioral anomalies, such as:
* Transactions exceeding standard operational thresholds.
* Suspicious round-number variances (e.g., an invoice for exactly $9,999.00, suggesting a manual override to avoid a $10,000 procurement review).

### Stage 3: Local Deep Reasoning (High-Risk Only)
If a transaction clears the risk thresholds, it bypasses this stage. If it is flagged, the orchestrator loads a heavier Gemma 3.1 reasoning model. This model synthesizes all prior metadata (flags, hashes, categories) to draft a highly specific, human-readable audit finding for the Chartered Accountant to review.

---

## 5. Running the Core Simulation

This repository contains the `core_engine.py` pipeline orchestrator. It programmatically simulates the server-side GPU allocation transitions, data generation, and cascading verification logic before live Gemma 3.1 MLX weights are integrated.

### Prerequisites
* Python 3.8+

### Execution

```bash
# Clone the repository
git clone [https://github.com/varunjarwani-max/-AuditIQ-Core.git](https://github.com/varunjarwani-max/-AuditIQ-Core.git)
cd -AuditIQ-Core

# Install deployment tracking dependencies
pip install -r requirements.txt

# Run the on-premise pipeline simulation
python core_engine.py
