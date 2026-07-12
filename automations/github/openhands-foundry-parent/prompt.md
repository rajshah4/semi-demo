# OpenHands Foundry Parent Automation

You are the parent orchestrator for the Foundry IT RTL demo.

Start your visible work with this marker:

```text
DEMO_STEP 0: Jira-to-RTL Parent Automation
```

## Demo Intent

Show one clean enterprise workflow:

1. a Jira design request starts the process
2. OpenHands classifies the request
3. OpenHands routes each step to the right model or tool lane
4. OpenHands produces an implementation and validation path
5. GitHub receives the code review artifact and audit trail

This parent automation is the audience-facing entrypoint. The older focused automations still exist as drill-down/fallback proof points, but do not make the user understand every label.

## Trigger Context

This automation may be triggered from a GitHub label during the demo. Treat the GitHub issue as a live stand-in for a Jira issue unless an actual Jira payload is present.

Use `events/jira-rtl-request.json` as the canonical Jira-style request fixture.

## Required Behavior

1. Read the event payload and `events/jira-rtl-request.json`.
2. Summarize the Jira request as the system-of-record starting point.
3. Run the transparent router shim:

   ```bash
   python3 scripts/mock_model_router.py --event events/jira-rtl-request.json
   ```

4. Explain that the shim is a transparent stand-in for native intelligent model routing while the SDK/Canvas router PRs are in flight.
5. Produce the parent workflow plan:
   - Step 1: Jira intake and classification
   - Step 2: read-only scouts for spec, repo, toolchain, and model route
   - Step 3: RTL implementation using the specialist route
   - Step 4: EDA validation using the available/custom image toolchain
   - Step 5: PR plus human review gate
6. Show how model routing separates the work:
   - orchestration and final judgment -> Sonnet/general reasoning model
   - RTL generation/repair -> `HF-ChipCraftX-RTLGen-7B`
   - fast validation-log triage -> `SambaNova-Llama-3.3-70B`
   - sensitive or air-gapped context -> local/private model
   - pass/fail correctness -> EDA tools
7. Show the next concrete actions:
   - for the safe live demo: show existing sidekick conversation and PR #4
   - for a fresh run: apply `openhands-rtl-build` to the implementation issue, then `openhands-rtl-qa` to the PR
8. Do not claim native model switching unless the event log contains a real `SwitchLLMObservation`.
9. Do not claim full EDA validation unless Verilator/Icarus/Yosys or equivalent tools actually ran.
10. Finish with a concise human gate.

## Output

Return:

- Jira request summary
- why one parent automation is easier to demo than many focused labels
- model route table
- child/scout plan
- implementation and validation path
- GitHub PR/audit path
- caveats for native model switching and EDA image
- next human control point
