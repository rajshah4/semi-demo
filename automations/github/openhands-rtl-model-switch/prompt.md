# OpenHands RTL Model Switch Proof

You are running a focused model-routing proof for the foundry workflow.

## Goal

Prove whether this automation runtime exposes the LLM switch tool to an OpenHands conversation. This run is intentionally small so it is easy to inspect in the event log.

## Required Behavior

1. Do not edit files, create branches, open pull requests, or post speculative model-use claims.
2. Start your final answer with `MODEL_SWITCH_PROOF_START`.
3. Inspect the tools available to you from the current conversation context.
4. If a tool named `switch_llm` is available, call it with:
   - `profile_name="HF-ChipCraftX-RTLGen-7B"`
   - reason: `Focused proof that the RTL specialist profile can be selected for Verilog generation.`
5. After the tool observation, report only what the observation proves.
6. If the ChipCraftX switch succeeded, ask a tiny RTL-only question while on that profile:
   - "Name two implementation details a synchronous FIFO must get right."
7. If a tool named `switch_llm` is available, call it again with:
   - `profile_name="SambaNova-Llama-3.3-70B"`
   - reason: `Focused proof that the fast general profile can be selected for log triage.`
8. After the tool observation, report only what the observation proves.
9. If the SambaNova switch succeeded, ask a tiny log-triage question while on that profile:
   - "Summarize this failure in one sentence: verilator lint failed because full and empty can both assert after reset."
10. If `switch_llm` is unavailable, inaccessible, or blocked, finish with `MODEL_SWITCH_PROOF_UNAVAILABLE` and list the tools you could actually use.

## Evidence Rule

Do not say a model switch worked unless the conversation produced direct switch evidence. Direct evidence means a successful tool observation from a `switch_llm` call, and the external event log should ideally contain a `SwitchLLMObservation`.

Use these exact fields in the final answer:

- `ChipCraftX switch: succeeded | unavailable | failed`
- `SambaNova switch: succeeded | unavailable | failed`
- `Direct switch evidence: yes | no`
- `Observed limitation: ...`
- `Operator recommendation: ...`
