# Model Router Shim

The native intelligent model-router work is still in PRs, so this repo includes a transparent mock for demo rehearsal:

```bash
python3 scripts/mock_model_router.py
```

The shim reads:

- `events/new-rtl-block.json`
- `examples/rtl_spec/fifo_request.md`
- `configs/meta-profile.semi-foundry-router.example.json`

It emits route decisions and clearly marked mock observations:

```text
MODEL_ROUTER_SHIM_START
Native router status: simulated. No live model switch is claimed.
MOCK_ROUTE_DECISION ...
MOCK_SWITCHLLM_OBSERVATION simulated=true ...
MODEL_ROUTER_SHIM_END
```

## What This Proves

- the route policy is concrete
- the model responsibilities are easy to explain
- the future native `classify_and_switch_llm` UX has a visible stand-in
- the demo can show intelligent routing without claiming the current runner switched models

## What This Does Not Prove

- it does not call ChipCraftX
- it does not call SambaNova
- it does not create a real `SwitchLLMObservation`
- it does not prove the SDK/Canvas router PRs are present in the running instance

## Talk Track

> The native model-router UX is in flight. For this environment I am using a transparent shim: it classifies the foundry task, selects the saved profile that would own each step, and records a mock switch observation. The point is to show the enterprise workflow shape without pretending this runner has a feature that has not landed yet.

## Stronger Mock

If we want a stronger proof before the native router lands, use a custom SDK automation that launches separate child conversations with explicit model configuration per child:

- parent conversation on Sonnet
- RTL child on `HF-ChipCraftX-RTLGen-7B`
- log-triage child on `SambaNova-Llama-3.3-70B`
- QA child on the default model plus EDA tools

That would prove model routing through conversation orchestration, even without mid-conversation switching.
