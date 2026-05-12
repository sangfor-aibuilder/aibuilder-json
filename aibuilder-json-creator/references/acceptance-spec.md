# FastGPT JSON Acceptance Spec

This is the public acceptance gate for every generated or repaired workflow JSON. A file is import-ready only when all gates pass and `scripts/validate_fastgpt_json.py` prints `VALIDATION_OK`.

## Gate 1. Root Shape

- Root object contains `nodes`, `edges`, and `chatConfig`.
- `nodes` is a non-empty array.
- `edges` is an array.
- `chatConfig.welcomeText` is Markdown Chinese text.
- If files are required, `chatConfig.fileSelectConfig.canSelectFile` is `true`.

## Gate 2. Required Skeleton

- Exactly one `workflowStart` node.
- Exactly one `userGuide` node.
- `workflowStart.inputs` contains `userChatInput`.
- Official default `workflowStart.outputs` contains `userChatInput`; add `userFiles` only when file upload is required.
- If `workflowStart.outputs` includes `userFiles`, `chatConfig.fileSelectConfig.canSelectFile` must be `true`.
- `userGuide.inputs` follows the official default system config inputs and `userGuide.outputs` is empty.

## Gate 3. Node Contracts

- Single-node default configuration comes from `references/official-default-node-templates.json`.
- Generated nodes must start from the matching official default template and then only fill scenario-specific values.
- For node types present in `official-default-node-templates.json`, generated `inputs` should preserve official default keys unless a known FastGPT export or explicit user requirement proves a key should be removed.
- Runtime configuration is in `node.inputs`, not `props`.
- Fixed-template outputs match the runtime whitelist.
- `chatNode` contains the full standard input set:
  - `model`
  - `isResponseAnswerText`
  - `systemPrompt`
  - `history`
  - `quoteQA`
  - `fileUrlList`
  - `userChatInput`
- `chatNode.model.renderTypeList` includes `settingLLMModel`.
- `chatNode` has at least one real business input among `userChatInput`, `fileUrlList`, and `quoteQA`.
- `contentExtract` outputs only `success`, `fields`, and `system_error_text`.
- `answerNode` uses input key `text` and is only final reply.

## Gate 4. References

- Normal input references use `["nodeId", "outputKey"]`.
- `answerNode.text.value` is a string and uses `{{$nodeId.outputKey$}}` for variable references.
- `answerNode.text.value` is never an array reference such as `["nodeId", "outputKey"]`.
- `textEditor.system_textareaInput.value` uses `{{$nodeId.outputKey$}}` for embedded variable references.
- Referenced nodes exist.
- Referenced output keys are valid for the upstream runtime node type.
- No legacy `{{nodeId.outputKey}}` references.
- No `userGuide.variables.*` references.
- Every reference inside a node points to a node that is upstream of the consuming node in the visual edge graph.
- Direct source-to-target visual edges are not required for references when the referenced node is already upstream through the same connected chain.
- Template references in `textEditor` and `answerNode` are checked against the consuming node's upstream path, not only its immediate incoming edges.

## Gate 5. Edges

- Every edge has `source`, `sourceHandle`, `target`, and `targetHandle`.
- `source` and `target` are node IDs only.
- Normal edge handles are:
  - `{sourceNodeId}-source-right`
  - `{targetNodeId}-target-left`
- Data keys are never used as edge handles.
- Every edge must exist because it participates in the readable execution path, a branch path, or a required dependency ordering.
- Do not add a separate direct visual edge for each consumed upstream value if the dependency is already represented by the upstream path.
- Every edge connects nodes that participate in the runtime path.
- No business node is isolated.

## Gate 5.1 Workflow Connectivity

- Every non-`workflowStart` and non-`userGuide` business node is reachable from `workflowStart`.
- Every business node can reach an `answerNode`, unless it is itself an `answerNode`.
- Workflows with reasoning or transformations must include at least one `answerNode`.

## Gate 6. Layout

- Connected nodes differ by at least `1500` on x.
- Branch or sibling nodes differ by at least `1000` on y.
- Preferred x positions are `0`, `1500`, `3000`, `4500`, `6000`, and so on.
- Node positions are readable and do not stack on top of each other.

## Gate 7. Encoding And Language

- Generated file is UTF-8.
- User-facing text is Chinese.
- Technical keys remain schema-compatible English where required.
- No mojibake markers exist.

## Gate 8. Validator

Run:

```bash
python scripts/validate_fastgpt_json.py <workflow.json>
```

Acceptance:

- Pass: prints exactly `VALIDATION_OK`.
- Fail: any `ERROR:` is blocking.
- Unknown: if the validator cannot be run, report `未验证：未能运行校验脚本`.

Never describe a file as import-ready unless this gate passes.
