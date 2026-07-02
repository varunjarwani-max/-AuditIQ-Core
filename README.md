# AuditIQ — Local Multi-Model AI Audit Platform

**AuditIQ** is a privacy-first, on-device AI platform designed to automate general ledger analysis and audit tasks for mid-market Chartered Accountancy (CA) firms. 

🌐 **Frontend UI Prototype:** [v0-ai-auditor-platform-ten.vercel.app](https://v0-ai-auditor-platform-ten.vercel.app/)

## The Problem
Mid-market CA firms process thousands of transactions manually. While AI can automate this, these firms cannot send highly sensitive client financial data to cloud APIs (like OpenAI) due to strict NDAs and compliance restrictions. 

## The Solution & Hardware Thesis
AuditIQ processes data entirely locally. By targeting modern silicon—specifically the **MacBook Pro with M4 Pro or M5 Pro**—AuditIQ runs highly optimized, quantized Small Language Models (like **Gemma 3.1**) directly on the auditor's machine. This guarantees 100% data privacy with zero latency.

### The Sequential VRAM Architecture
You cannot load seven distinct LLMs into a laptop's Unified Memory simultaneously. AuditIQ solves this using a **Sequential Batch Pipeline**:
1. Load a highly narrow model (e.g., 3B parameter classifier) into VRAM via Apple MLX.
2. Process the entire transaction ledger through this single node.
3. Unload the model from memory.
4. Load the next specialized model in the sequence.
5. *Heavy reasoning models (9B+) are only loaded and executed for transactions flagged as high-risk anomalies, saving massive compute cycles.*

## Running the Core Simulation

This repository contains the `core_engine.py` pipeline orchestrator. It programmatically simulates the sequential VRAM loading and cascading model logic before live quantized weights are swapped in.

```bash
# Install dependencies
pip install -r requirements.txt

# Run the simulation
python core_engine.py
