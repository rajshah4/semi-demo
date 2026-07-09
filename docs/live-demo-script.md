# Live Demo Script

## Demo Goal

Show that OpenHands is more than an IDE coding assistant:

> OpenHands is an event-driven engineering automation runtime that can launch parent/child conversations, route tasks to the right model, call domain specialists, run EDA tools, and preserve an audit trail.

## Audience Takeaway

For foundry IT, the value is controlled automation:

- approved event triggers
- approved models
- approved EDA tools
- approved deployment boundary
- visible human gates
- auditable traces

## Critical Features To Show

| Moment | Feature | Why it matters |
|---|---|---|
| Trigger from issue/webhook | OpenHands Automations | Work starts from enterprise systems, not only an IDE chat |
| Parent launcher conversation | Parent agent orchestration | One visible owner for audit, routing, and decisions |
| Child scout conversations | Multi-conversation workflows | Bounded agents gather context without mutating code |
| Model routing table | Intelligent model routing | Right model for each task: Sonnet, SambaNova, ChipCraftX, local/private |
| RTL generation | Specialist model support | OpenHands can call a fine-tuned RTL/Verilog model |
| Fast log triage | SambaNova fast inference | Low-latency loops make agentic work feel interactive |
| Verilator/Yosys/cocotb step | Toolchain grounding | EDA tools judge correctness, not model confidence |
| Final summary | Audit trail and human gate | Enterprise workflow remains reviewable and controlled |
| Local/cloud/air-gap note | Deployment flexibility | Fits foundry IT constraints |

## 12-15 Minute Flow

### 0. Setup Before The Call

Have these ready:

- repo open: `~/Code/semi-demo`
- Agent Canvas open
- the ChipCraftX profile smoke-tested: `HF-ChipCraftX-RTLGen-7B`
- SambaNova profile available or ready to describe
- sample event: `events/new-rtl-block.json`
- sidekick label visible: `openhands-rtl-sidekick`
- routing example open: `configs/meta-profile.semi-foundry-router.example.json`

Optional live links:

- SDK router PR: https://github.com/OpenHands/software-agent-sdk/pull/3744
- Canvas router PR: https://github.com/OpenHands/agent-canvas/pull/1395
- SDLC inspiration repo: https://github.com/rajshah4/sdlc-automation-github-demo

### 1. Open With The Problem

Show: `README.md` or one slide with the architecture.

Say:

> Foundry IT does not just need a chatbot that writes code. They need controlled engineering automation: approved triggers, approved models, approved tools, and an audit trail. This demo shows OpenHands as that runtime.

Feature:

- competitive framing
- enterprise workflow instead of IDE-only assistant

Contrast:

> Claude Code, Cursor, and Cline are excellent interactive coding assistants. This is a different lane: event-driven, model-routed engineering automation.

### 2. Show The Event Trigger

Show: `events/new-rtl-block.json` or a GitHub issue labeled `rtl-request`.

Say:

> The workflow starts from a system of record: a GitHub issue, Jira ticket, CI event, or internal design portal webhook. In foundry IT, this matters because work needs to be traceable and policy-controlled from the beginning.

Feature:

- OpenHands Automations
- webhook/event-driven workflow
- human-approved labels

Operator action:

```bash
cd ~/Code/semi-demo
scripts/simulate-event.sh
```

### 3. Launch The Parent Conversation

Show: parent conversation or the `openhands-rtl-sidekick` automation prompt.

Say:

> The first agent is not the implementation agent. It is the parent orchestrator. Its job is to unwrap the event, decide the workflow, launch or index child conversations, and keep the audit trail clean.

Feature:

- parent conversation
- conversation index
- audit ownership

Critical point:

> This is one of the places OpenHands separates from IDE tools. The system can coordinate multiple conversations, not just answer in one chat.

Expected visible marker:

```text
DEMO_STEP 0: Foundry RTL Sidekick Launcher
```

### 4. Show Child Conversations

Show: `docs/parent-child-conversations.md` or live child conversation links.

Say:

> The parent fans out bounded child conversations. These are intentionally scoped. Spec scout normalizes the request. Repo scout finds relevant RTL and tests. Toolchain scout checks what EDA tools are available. Model-route scout recommends the right model for each step.

Feature:

- subagents / child conversations
- bounded read-only scouts
- lower-risk context gathering

The child set:

- Step 2A: Spec Scout
- Step 2B: RTL Repo Scout
- Step 2C: Toolchain Scout
- Step 2D: Model Route Scout

Important line:

> Child scouts are read-only. The main implementation agent owns changes after the parent has enough context.

### 5. Show Intelligent Model Routing

Show: `configs/meta-profile.semi-foundry-router.example.json`.

Say:

> Different tasks need different models. The router policy maps task classes to saved LLM profiles. Planning can go to Sonnet. Fast log triage can go to SambaNova. RTL generation can go to ChipCraftX. Sensitive or air-gapped work can go to a local/private model.

Feature:

- intelligent model routing
- meta-profiles
- saved LLM profiles
- SDK `classify_and_switch_llm`
- Canvas Model Router settings tab

Product hook:

> This connects directly to the OpenHands Model Router work: the SDK adds `classify_and_switch_llm` and meta-profile APIs, and Canvas adds a Model Router settings page. Even if we do this lightly today, the architecture is becoming first-class.

Routing table to narrate:

| Task | Route |
|---|---|
| ambiguous planning | Sonnet |
| fast log summary | SambaNova Llama 3.3 70B |
| Verilog/RTL generation | ChipCraftX RTLGen 7B |
| sensitive IP | local/private model |
| pass/fail correctness | EDA tools |

### 6. Generate RTL With ChipCraftX

Show: ChipCraftX profile or an OpenHands step calling the specialist.

Say:

> Here OpenHands is not locked into one model. The orchestrator can call a fine-tuned RTL model for the one thing it is good at: generating or repairing Verilog/SystemVerilog.

Feature:

- external/specialist model support
- fine-tuned Verilog model
- model-as-tool pattern

Important caveat:

> ChipCraftX is not the full agent brain. It is the RTL specialist. OpenHands orchestrates; ChipCraftX proposes RTL; tools validate.

### 7. Run EDA Validation

Show: validation command or planned toolchain image doc.

Say:

> This is the most important engineering point: the model does not get to declare victory. We run the toolchain.

Feature:

- Verilator / Icarus / Yosys / Verible / cocotb
- deterministic checks
- toolchain-grounded agent loop

Ideal command examples:

```bash
verilator --lint-only rtl/sync_fifo.sv
iverilog -g2012 -o build/sync_fifo_tb rtl/sync_fifo.sv tb/sync_fifo_tb.sv
yosys -p "read_verilog -sv rtl/sync_fifo.sv; synth; stat"
```

Say:

> In production, this runs inside a pre-approved EDA image with the right tools, PDKs, scripts, and license configuration already baked in.

### 8. Show Failure Triage And Fast Inference

Show: a lint/test failure or simulated failure summary.

Say:

> Agentic coding is latency-sensitive. The agent may need to read logs, summarize errors, patch, and rerun. This is where SambaNova fast inference becomes useful: repeated short loops become interactive instead of feeling like batch jobs.

Feature:

- SambaNova fast inference
- log triage
- edit/test loop acceleration

Narration:

> Fast inference does not replace the specialist model. It handles the high-volume general reasoning steps around the specialist and the tools.

### 9. Patch And Rerun

Show: patch or final validation summary.

Say:

> The parent consumes the child outputs and validation results, then decides whether to patch, rerun, or ask for human input. The workflow keeps evidence at every step.

Feature:

- parent consumes child summaries
- repair loop
- human escalation
- final audit

### 10. Close With Deployment Story

Show: `docs/local-cloud-airgap.md` or `docs/toolchain-image.md`.

Say:

> The same pattern can run locally for a demo, in cloud for webhook integrations, or inside an air-gapped/private environment for real foundry IT. The models, tools, secrets, and policies are part of the runtime.

Feature:

- local/cloud/air-gapped story
- pre-baked toolchain image
- enterprise controls

Final line:

> The differentiator is not just better code generation. It is controlled model-routed automation across conversations, tools, and deployment boundaries.

## Short Version If Time Is Tight

Use this 6-minute version:

1. Show event payload.
2. Show parent launcher and child conversation diagram.
3. Show model routing meta-profile.
4. Show ChipCraftX as RTL specialist.
5. Show EDA validation as judge.
6. Close with local/cloud/air-gap deployment.

Say:

> OpenHands receives an event, launches a parent workflow, routes sub-tasks to the right models, validates with EDA tools, and returns auditable evidence.

## Fallback Plan

If live child conversations are not wired yet:

- show `docs/parent-child-conversations.md`
- show `workflows/foundry-rtl-sidekick-workflow.yaml`
- run `scripts/simulate-event.sh`
- show the `openhands-rtl-sidekick` prompt
- explain that the SDLC demo already uses this parent/child pattern

If live Model Router is not available:

- show `configs/meta-profile.semi-foundry-router.example.json`
- show the SDK and Canvas PRs
- manually narrate the route

If EDA tools are not installed:

- show `docs/toolchain-image.md`
- explain the pre-baked image story
- use a captured or mocked validation transcript

## What Not To Overclaim

- Do not say ChipCraftX is better than Claude at all coding.
- Do not say generated RTL is correct without EDA evidence.
- Do not imply public model APIs are required for foundry IT.
- Do not make the demo about replacing human review.

## One-Slide Summary

```text
Event -> Parent Agent -> Child Scouts -> Model Router -> RTL Specialist -> EDA Validation -> Audit Summary

Features:
- OpenHands Automations
- parent/child conversations
- intelligent model routing
- SambaNova fast inference
- ChipCraftX RTL specialist
- EDA toolchain grounding
- local/cloud/air-gapped deployment
```

