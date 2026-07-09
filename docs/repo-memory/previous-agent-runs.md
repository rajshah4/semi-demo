# Previous Agent Runs

Use this file to capture durable lessons from demo rehearsals.

## 2026-07-06 Initial Findings

- ChipCraftX RTLGen 7B is useful as an RTL specialist model.
- The model should not be treated as the primary OpenHands agent brain.
- Direct Hugging Face inference worked after the HF token permission was updated.
- The working OpenHands profile name is `HF-ChipCraftX-RTLGen-7B`.
- The working LiteLLM model string is `huggingface/featherless-ai/chipcraftx-io/chipcraftx-rtlgen-7b`.
- The right architecture is: orchestrator agent plus specialist model plus deterministic EDA tools.

## 2026-07-08 Model Router Check

- SDK PR `OpenHands/software-agent-sdk#3744` adds `classify_and_switch_llm` plus `/api/meta-profiles`.
- Agent Canvas PR `OpenHands/agent-canvas#1395` adds the Model Router settings UI.
- The current local Agent Canvas/Agent Server openapi check does not expose `/api/meta-profiles` yet.
- For the near-term demo, show lightweight routing through config/docs or manual profile switching unless running a build that includes those PRs.
