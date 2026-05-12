---
name: fastgpt-json-config
description: Generate, repair, and validate import-ready FastGPT workflow JSON from natural-language requirements or existing JSON. Use for FastGPT agents/workflows, broken JSON imports, node/edge/reference validation, strict runtime node IO, Markdown chatConfig, and deterministic acceptance checks.
---

# FastGPT JSON Config Skill

Treat this skill as a specification plus test suite: generate by copying templates, then prove the file passes deterministic checks.

## Required Resources

Load these first for every generation or repair task:

1. `references/generation-hard-rules.md`
2. `references/official-default-node-templates.json`
3. `references/official-node-contract-summary.md`
4. `references/runtime-node-templates.md`
5. `references/node-field-contracts.md`
6. `references/acceptance-spec.md`
7. `scripts/validate_fastgpt_json.py`

Load conditional references only when the requirement needs them:

- `references/required-input-rules.md`
- `references/ifelse-rules.md`
- `references/dataset-rules.md`
- `references/classify-rules.md`
- `references/node-selection-rules.md`
- `references/workflow-generation-playbook.md`
- `references/json-config-runtime-reference.md`
- `references/json-import-feature-guide.md` only for import UI/background behavior; do not copy node templates from it
- `references/json-config-specification.md` only for historical/background context; do not copy node templates or IO keys from it
- `references/json-config-troubleshooting.md` only when repairing a known broken file; do not copy node templates from it
- `references/protocol-v1.md`

## Execution Protocol

Follow this order exactly.

1. Decompose the request into stages.
2. Create a node inventory.
3. Copy node shapes from `official-default-node-templates.json`; use `runtime-node-templates.md` only as an override and usage guide.
4. Fill `inputs[].value` after node IDs are fixed.
5. Generate `edges` last.
6. Save JSON with UTF-8.
7. Run `python scripts/validate_fastgpt_json.py <generated-file>`.
8. Fix any `ERROR:` and rerun until `VALIDATION_OK`.
9. Apply readable layout before validation:
   - connected columns must be spaced at least `1500` on x
   - branch or sibling nodes must be spaced at least `1000` on y
   - prefer `0, 1500, 3000, 4500...` for x positions
   - do not stack connected nodes at the same position

## Node Inventory

Before writing JSON, record:

- `nodeId`
- `flowNodeType`
- purpose
- position
- required input keys
- output keys
- upstream data dependencies
- visual predecessor and visual successor

Include exactly one `workflowStart` and one `userGuide`.

## Copy Rules

- Keep runtime configuration in `node.inputs`, never `props`.
- Use `references/official-default-node-templates.json` as the source of truth for single-node default inputs, outputs, render types, value types, labels, hidden fields, and dynamic system fields.
- `runtime-node-templates.md` is not a competing template source. It only explains how to copy official defaults and which scenario values may be filled.
- Do not invent inputs, outputs, handles, or variable syntax.
- Generate clean UTF-8 Chinese user-facing text.
- Required files flow through `workflowStart.userFiles` and `readFiles.system_text`.
- Normal input references use `["nodeId", "outputKey"]`.
- `answerNode.text.value` must be a string. Variable references inside it must use `{{$nodeId.outputKey$}}`; never use array references such as `["nodeId", "outputKey"]` for `answerNode.text`.
- `textEditor.system_textareaInput` uses `{{$nodeId.outputKey$}}` when embedding upstream variables in text.
- Every runtime reference must point to a node that is upstream of the consuming node in the visual edge graph. A direct edge is not required when the referenced node and the consuming node are already on the same upstream chain.
- Do not leave business nodes isolated. Every non-`workflowStart` and non-`userGuide` node must be reachable from `workflowStart` through edges, and every final path must reach an `answerNode`.

## Edge Rules

- Edges are visual canvas connections, not data bindings.
- Normal edges must use:
  - `sourceHandle: "{sourceNodeId}-source-right"`
  - `targetHandle: "{targetNodeId}-target-left"`
- Never use business keys such as `system_text`, `answerText`, `userFiles`, `userChatInput`, `fileUrlList`, `system_textareaInput`, or `text` as edge handles.
- Branch nodes use their documented branch handles.
- Edges express the readable execution chain. Do not add a separate direct edge for every referenced input when the referenced node is already upstream of the consuming node through the chain.
- If node B references output from node A and A is not already upstream of B, add or reorder visual edges so A becomes upstream of B.
- Do not create unreferenced business nodes just to satisfy a design idea.

## Hard Requirements

- Official default `workflowStart` has input `userChatInput` and output `userChatInput`; add `userFiles` only when the workflow needs chat file upload.
- Every `chatNode` includes `model`, `isResponseAnswerText`, `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, and `userChatInput`.
- `chatNode.model.renderTypeList` includes `settingLLMModel`.
- If a `chatNode` eventually outputs through an `answerNode`, set `isResponseAnswerText.value = false`.
- `contentExtract` outputs only `success`, `fields`, and `system_error_text`.
- `textEditor` puts deterministic template text in `system_textareaInput.value`.
- `answerNode` is final reply only and uses input key `text`.
- `answerNode.text.value` must never be `["nodeId", "outputKey"]`; use `"{{$nodeId.outputKey$}}"` instead.
- `ifElseNode.ifElseList.value[]` uses `condition` plus `list`.
- `httpRequest468.system_httpReqUrl.value` is never empty.
- `userGuide` follows the official default system config inputs (`welcomeText`, `variables`, `questionGuide`, `tts`, `whisper`, `scheduleTrigger`) and has no business outputs.
- Generated JSON must not contain mojibake markers.
- Connected nodes must differ by at least `1500` on x.
- Branch/sibling nodes must differ by at least `1000` on y.
- Node layout must remain readable; avoid stacked or overlapping positions.
- Runtime references and edges must agree: every `["nodeId", "outputKey"]` and every `{{$nodeId.outputKey$}}` used inside a node must reference a node that is reachable upstream through the visual edge graph. Do not require direct source-to-target edges for all references.
- Every business node must be on the workflow path: reachable from `workflowStart` and able to reach an `answerNode`, unless it is `userGuide`.

## Validation

- Save the JSON to disk first unless the user explicitly requests chat-only output.
- Run the bundled validator from the skill directory or by absolute path.
- Any `ERROR:` is blocking.
- If the validator cannot run, report `未验证：未能运行校验脚本`.
- Do not call JSON import-ready unless validation passes.

## Final Response

Return a concise Chinese report:

1. `需求确认`
2. `生成结果` or `修复结果`
3. `验证报告`
4. `文件路径`

Do not paste large JSON unless the user asks.

## Protocol Export

When the user asks to "export with skill protocol", output a fenced block using `fastgpt-json-skill-protocol/v1` from `references/protocol-v1.md`.
