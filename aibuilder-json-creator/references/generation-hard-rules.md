# FastGPT JSON Generation Hard Rules

These rules override examples, model memory, and imported broken JSON.

## 1. Runtime Compatibility

- Use runtime `flowNodeType` values only.
- Treat `references/official-default-node-templates.json` as the highest-priority single-node default template source.
- When a node type exists in the official template JSON, copy its default `inputs`, `outputs`, render types, value types, and dynamic system fields before filling scenario values.
- Use input/output keys from the official template JSON first. `runtime-node-templates.md`, `node-field-contracts.md`, and `json-config-runtime-reference.md` are only secondary explanations and must not override official defaults.
- Do not invent inputs, outputs, handles, dynamic schemas, or variable syntax.
- Declaring an output in JSON does not make it valid. The key must be valid for that node type.
- Runtime configuration must be in `node.inputs`, not `props`.

## 2. Required Skeleton

- Include one `workflowStart` node.
- Include one `userGuide` node.
- `workflowStart` must include `userChatInput` input and output `userChatInput`; add `userFiles` only for file-upload workflows.
- `userGuide` must follow the official default system config inputs and have no business outputs.
- Root `chatConfig.welcomeText` must be Markdown with Chinese title, usage, examples, and reminders.

## 3. Edges

- Every edge must contain `source`, `sourceHandle`, `target`, `targetHandle`.
- `source` and `target` must be node IDs only, never handle IDs.
- Normal handles use `{nodeId}-source-right` and `{nodeId}-target-left`.
- Do not use business data keys as visual edge handles. Invalid handles include `userFiles`, `system_text`, `answerText`, `userChatInput`, `fileUrlList`, `system_textareaInput`, and `text`.
- Data references belong in node input values such as `["readFiles-001", "system_text"]`; edge handles are only canvas connection handles.
- `ifElseNode` branch handles use `{nodeId}-source-IF`, `{nodeId}-source-ELSE IF 1`, or `{nodeId}-source-ELSE`.
- `classifyQuestion` branch handles use `{nodeId}-source-{agentKey}`.
- Every edge endpoint must exist.

## 4. References

- Normal inputs use array references: `["nodeId", "outputKey"]`.
- `answerNode.text.value` must be a string and must use template references such as `{{$nodeId.outputKey$}}`.
- Never use array references such as `["nodeId", "outputKey"]` for `answerNode.text.value`.
- `textEditor.system_textareaInput` uses template references: `{{$nodeId.outputKey$}}`.
- Reject legacy references: `{{nodeId.outputKey}}`.
- Reject display labels and invented output keys.
- Reject `userGuide.variables.*`; `userGuide` is not a runtime variable emitter.
- Reject dotted subpaths on invalid outputs, such as `{{$formInput.result.bookingDate$}}`.
- Every reference must point to a node that is upstream of the consuming node in the visual edge graph.
- A direct edge from the referenced node to the consuming node is not required when both nodes are already on the same connected upstream chain.
- Do not create star-shaped direct edges merely because one downstream node consumes several upstream outputs.
- Do not create input references to a node that is not upstream in the edge graph.
- Do not create business nodes that are not reachable from `workflowStart`.
- Every business path must be able to reach an `answerNode`.

## 5. Output Key Whitelist

Use only these common fixed-template outputs:

- `workflowStart`: `userChatInput`, `userFiles`
- `formInput`: `formInputResult`
- `userSelect`: `selectResult`
- `ifElseNode`: `ifElseResult`
- `textEditor`: `system_text`
- `chatNode`: `history`, `answerText`, `reasoningText`, `system_error_text`
- `httpRequest468`: `httpRawResponse`, `error`, known dynamic outputs only
- `readFiles`: `system_text`, `system_rawResponse`, `system_error_text`
- `contentExtract`: `success`, `fields`, `system_error_text`
- `datasetSearchNode`: `quoteQA`, `system_error_text`
- `datasetConcatNode`: `quoteQA`
- `classifyQuestion`: `cqResult`
- `cfr`: `system_text`
- `answerNode`, `userGuide`, `variableUpdate`: no business outputs

Reject these recurring invalid keys:

- `formInput.result`
- `chatNode.aiResponse`, `chatNode.newTitle`, `chatNode.quoteList`
- `httpRequest468.system_httpResult`
- `ifElseNode.IF`, `ifElseNode.ELSE`
- Any field-level `contentExtract` output copied from `extractKeys`, such as `courseName`, `bookingDate`, `recommendedClassroom`, or `reason`

## 6. Node-Specific Musts

- `chatNode`: include required runtime controls `model` and `isResponseAnswerText`, and keep AI dialogue input configuration to the official five keys only: `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, and `userChatInput`. At least one of `userChatInput`, `fileUrlList`, or `quoteQA` must be configured.
- `chatNode`: start from the full official default input list. You may fill the core copy-safe fields `model`, `isResponseAnswerText`, `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, and `userChatInput`, but do not delete official control inputs such as `temperature`, `maxToken`, quote settings, vision/reasoning/top-p/stop/response-format/json-schema fields unless a known FastGPT export proves they are safely omitted.
- `chatNode.model`: use a FastGPT LLM selector shape such as `renderTypeList: ["settingLLMModel", "reference"]`; avoid plain `["select"]` for generated import configs.
- `chatNode`: do not add extra input keys for form fields, extracted fields, API responses, variables, scoring criteria, role data, metadata, or custom context. Put that content into `systemPrompt.value` or `userChatInput.value` manually, usually by referencing a prepared `textEditor.system_text`.
- `chatNode -> answerNode`: set `isResponseAnswerText.value = false`.
- `answerNode`: input key is `text`; use full sample-compatible text shape; `text.value` must be a string, not an array reference.
- `textEditor`: put actual concat text in `system_textareaInput.value`; output `system_text`.
- `contentExtract`: fill `content.value`; `extractKeys.value` must be non-empty; downstream uses `fields`, not per-field outputs.
- `ifElseNode`: `ifElseList.value[]` group shape is `condition` + `list`; do not use `conditionList`; branch names are edge handles only.
- `httpRequest468`: use `system_httpReqUrl`, `system_httpMethod`, `system_httpTimeout`; URL must not be empty; JSON body uses `system_httpJsonBody`; raw response is `httpRawResponse`.
- `formInput`: fields stay in `userInputForms.value`; output `formInputResult`.
- `userSelect`: options stay in `userSelectOptions.value`; output `selectResult`.
- `readFiles`: downstream text logic uses `system_text`, not raw `userFiles`.
- `cfr`: use `flowNodeType: "cfr"`, not `queryExtension`.
- `tools`: use `flowNodeType: "tools"`, not `toolCall`.

## 7. Required Input Collection

- Required user-provided text/number/select/switch/object data must be modeled as `formInput` fields or supported global config metadata.
- Required file uploads must use `workflowStart.userFiles` plus the matching `chatConfig.fileSelectConfig` file channels: documents `canSelectFile`, images `canSelectImg`, audio `canSelectAudio`, video `canSelectVideo`, custom extensions `canSelectCustomFileExtension` with a non-empty `customFileExtensionList` (see `references/file-format-rules.md`). Use `readFiles` when document text content is needed; images go to a vision-capable `chatNode`/`tools` through `fileUrlList`.
- Do not rely on `systemPrompt`, `welcomeText`, node descriptions, or final answer text as the only collection mechanism.

## 8. Retrieval And Routing

- Knowledge-base workflows default to explicit `datasetSearchNode`.
- Multiple retrieval sources use `datasetConcatNode` before downstream AI.
- Downstream AI consumes dataset quotes through `quoteQA`.
- Classification/routing workflows default to `classifyQuestion`, not free-text `chatNode` plus string matching.
- `classifyQuestion.agents` must be non-empty with stable unique keys and Chinese values.

## 9. Dynamic And Restricted Nodes

- Do not generate `appModule`, `pluginModule`, `tool`, `toolSet`, `toolParams`, `pluginInput`, or `pluginOutput` without a concrete target contract.
- Do not use `agent` as a plain chat replacement; use it only with real tools, skills, datasets, or planning requirements.
- Do not use `emptyNode`, `comment`, `stopTool`, or deprecated `app` in normal workflows unless explicitly required.

## 10. Usability And Encoding

- All user-facing text must be Chinese.
- Read and write JSON/Markdown as UTF-8.
- Do not preserve mojibake.
- Connected nodes should differ by at least `1500` on x.
- Branch/sibling nodes should differ by at least `1000` on y.
- Save generated JSON to disk by default and report the absolute path.

## 11. Validation Is Mandatory

- Run `scripts/validate_fastgpt_json.py <generated-file>` after writing JSON.
- Any `ERROR:` output is a blocking failure.
- Fix and rerun until the script prints `VALIDATION_OK`.
- Also apply `validation-checklist.md` for scenario-specific checks.
- If the validator is missing, blocked, or not run, the output status is `未验证`, not `VALIDATION_OK`, and the JSON must not be described as directly import-ready.

## 12. Universal Generation Safety Mode

- Generate a node inventory first, then copy runtime templates, then fill values, then generate edges last.
- Copy runtime templates means copy the node object from `official-default-node-templates.json` first, then adjust `nodeId`, `name`, `position`, and scenario-specific `inputs[].value`.
- Reject `workflowStart.inputs: []`.
- Reject `chatNode` without `isResponseAnswerText`.
- Reject normal edges whose handles are business keys instead of `{nodeId}-source-right` and `{nodeId}-target-left`.
- Reject generated text containing mojibake markers such as `鐢`, `鏂`, `绯`, `鈫`, or `�`.
- The final response must state one of: `VALIDATION_OK`, `未验证：未能运行校验脚本`, or `未通过：存在 ERROR`.
- Never state that JSON can be imported directly if the deterministic validator was not run or did not pass.


