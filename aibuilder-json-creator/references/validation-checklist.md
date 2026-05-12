# Validation Checklist

## A. Root and Type

- Root contains `nodes` and workflow includes at least one `workflowStart`.
- Workflow includes one system config node: `flowNodeType = "userGuide"` (default required).
- `edges` is array (optional but recommended for non-trivial workflow).

## B. Nodes

- `nodeId` unique.
- `flowNodeType` valid.
- `inputs` and `outputs` arrays exist.
- Declared outputs match the runtime output whitelist for the node type; invented outputs are not accepted just because they are declared in the JSON.
- `formInput` output key is `formInputResult`, not `result`.
- `chatNode` output keys are `history`, `answerText`, `reasoningText`, and `system_error_text`; no `aiResponse`, `newTitle`, or `quoteList`.
- `httpRequest468` output uses `httpRawResponse` for raw responses; no `system_httpResult` unless a real dynamic output contract is supplied.
- `ifElseNode` output is `ifElseResult`; no `IF`, `ELSE IF N`, or `ELSE` outputs.
- `userGuide` does not act as a runtime variable emitter and should normally have empty `inputs` and `outputs`.
- `contentExtract` outputs are only `success`, `fields`, and `system_error_text`; no per-field outputs copied from `extractKeys`.
- `workflowStart` includes the `userChatInput` input and official `userChatInput` output; `userFiles` output appears only for file-upload workflows.
- Required keys in node inputs are present (for node type).
- Every `chatNode` includes the required runtime controls `model` and `isResponseAnswerText`.
- Every generated `chatNode` includes the full standard set: `model`, `isResponseAnswerText`, `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, and `userChatInput`.
- `chatNode.model.renderTypeList` uses a FastGPT LLM selector such as `settingLLMModel`, not plain `select`.
- Every `chatNode` uses only the official AI dialogue input configuration keys: `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, and `userChatInput`; aside from required runtime controls, no other `inputs[].key` is accepted.
- Every `chatNode` has at least one configured business input among `quoteQA`, `fileUrlList`, and `userChatInput`.
- `chatNode.systemPrompt` alone does not count as business input.
- No `chatNode` adds separate inputs for form results, extraction fields, HTTP responses, variables, user profile fields, scoring dimensions, search text, or custom metadata; these must be manually folded into `systemPrompt` or `userChatInput`.
- If a `chatNode` connects downstream to an `answerNode`, its `isResponseAnswerText.value` is `false` to avoid duplicate AI-node output and assigned-answer output.
- If `datasetSearchNode` is used, it includes official `datasets` and `userChatInput` inputs.
- If `classifyQuestion` is used, it includes `model`, `systemPrompt`, `history`, `userChatInput`, and non-empty `agents`.
- If `contentExtract` is used, it includes `model`, `description`, `history`, filled `content`, and non-empty `extractKeys`.
- If `tools` is used, it includes `model`, `systemPrompt`, `history`, and actual business input.
- If `userSelect` is used, it includes non-empty `userSelectOptions`.
- If `formInput` is used, it includes non-empty `userInputForms`.
- If `textEditor` is used, it includes filled `system_textareaInput`.
- If `readFiles` is used, it includes a real `fileUrlList` reference.
- If `httpRequest468` is used, it includes request URL/method/timeout and required payload metadata.
- If `httpRequest468` is used, the URL key is `system_httpReqUrl`, not `system_httpUrl`.
- If `httpRequest468` sends JSON, the request body uses `system_httpJsonBody`, not query params unless params are truly intended.
- If `httpRequest468` is used, `system_httpReqUrl.value` is not empty.
- If an HTTP request depends on upstream business data, its `system_httpJsonBody.value` is not empty and references a real upstream output.
- If `variableUpdate` is used, every update item has a target variable and source/value.
- If `code` is used, inputs and outputs are coherent with the code body.
- If `loop` is used, it has a valid array input and a complete loop child structure.
- If question optimization is used, the node has `flowNodeType = "cfr"` and includes `model`, `systemPrompt`, `history`, and `userChatInput`.
- If `lafModule` is used, it includes the actual Laf endpoint URL and needed inputs.
- If `customFeedback` is used, it includes feedback text configuration.
- If `agent` is used, it has real orchestration context such as tools, skills, datasets, or explicit agent planning requirements.
- If `appModule`, `pluginModule`, `tool`, `toolSet`, `toolParams`, `pluginInput`, or `pluginOutput` is used, the dynamic contract is known and not invented.
- If `comment` is used, it is annotation-only and has `commentText` plus `commentSize`.
- `emptyNode` is not used unless explicitly requested as a placeholder.
- Deprecated `app` node is not used unless legacy compatibility is explicitly requested.

## C. References

- For array references: `["nodeId","outputKey"]`, `nodeId` exists.
- For template references: `{{$nodeId.outputKey$}}`, `nodeId` exists.
- Referenced nodes are upstream of the consuming node in the visual edge graph.
- A direct visual edge is not required for every reference when the referenced node is already upstream through the same chain.
- No legacy moustache references such as `{{nodeId.outputKey}}` exist anywhere in node input values or `chatConfig`.
- Referenced `outputKey` is defined by upstream node template or explicit output.
- Referenced `outputKey` is a valid runtime output for the upstream node type, not only an invented declared output.
- No references to invalid common keys: `formInput.result`, `chatNode.aiResponse`, `httpRequest468.system_httpResult`, `ifElseNode.IF`, or `ifElseNode.ELSE`.
- No references to field-level `contentExtract` outputs such as `contentExtract.courseName`, `contentExtract.bookingDate`, or `contentExtract.recommendedClassroom`; use `contentExtract.fields`.
- No template reference uses unsupported subpaths such as `{{$formInput.result.bookingDate$}}`; object outputs are passed through legal output keys such as `formInputResult`.
- No references treat `userGuide` or `chatConfig.variables` as node outputs, such as `{{$userGuide.variables.apiBaseUrl$}}`.
- `quoteQA` references valid dataset quote outputs such as `quoteQA` from `datasetSearchNode` or `datasetConcatNode` when knowledge-base retrieval is used.
- Classification routing uses stable category keys from `agents`.
- `contentExtract.content` references actual text, not raw file arrays.
- `textEditor` and `answerNode` references point to existing upstream outputs.
- `textEditor.system_textareaInput.value` contains the actual concat template and variable references.
- `readFiles` parsed text is referenced through `system_text`.
- `cfr` output is referenced through `system_text`.
- `loop` internal references are valid for `loopStart`, child nodes, and `loopEnd`.

## D. Edges

- `source` and `target` exist.
- Every edge has all four fields: `source`, `sourceHandle`, `target`, and `targetHandle`.
- `source` and `target` are node IDs only, not handles.
- No edge uses values like `workflowStart-source-right` as `source` or `chatNode-target-left` as `target`.
- Normal handles use `-source-right` and `-target-left`.
- Normal edge handles are full node-side handles such as `{nodeId}-source-right` and `{nodeId}-target-left`, not business keys such as `system_text`, `answerText`, `userFiles`, `userChatInput`, `fileUrlList`, `system_textareaInput`, or `text`.
- `ifElseNode` uses branch handles:
  - `...-source-IF`
  - `...-source-ELSE IF 1`
  - `...-source-ELSE`

## D2. ifElse Conditions

- Every `ifElseNode` rule item includes `variable`.
- Every `ifElseNode` rule item includes `condition`.
- Every `ifElseNode` rule item includes `value` when the operator requires comparison input.
- No variable-only condition entries exist.
- Every condition variable references an existing upstream runtime output key.
- Branch labels `IF`, `ELSE IF N`, and `ELSE` appear only in edge `sourceHandle`, not in `outputs`.
- `ifElseList.value[]` group objects use `condition` and `list`; `conditionList` is rejected.

## E. File Upload

- If file upload required, `chatConfig.fileSelectConfig.canSelectFile=true`.
- If using chat upload, file flow starts from `workflowStart.userFiles`.
- If parsing files, `readFiles.fileUrlList` references file array output.
- If downstream nodes need document text/content, they reference parsed outputs such as `readFiles.system_text` instead of raw `userFiles`.
- File-driven extraction, classification, and reasoning use parsed text outputs rather than raw file arrays unless the downstream node is explicitly file-aware.

## E2. Dataset Retrieval

- `datasetSearchNode.datasets` is not empty when knowledge-base retrieval is required.
- `datasetSearchNode.userChatInput` is configured with the real retrieval query source.
- `datasetConcatNode` only merges dataset quote references.
- Downstream `chatNode.quoteQA` references retrieval outputs rather than fake placeholders.
- Knowledge-base workflows default to explicit `datasetSearchNode` instead of inline dataset config on `chatNode` / `agent`.
- Multi-dataset retrieval defaults to `datasetConcatNode` before downstream AI usage.

## E3. Question Classification

- `classifyQuestion.agents` is a non-empty array.
- Every classification item contains unique `key`.
- Every classification item contains Chinese `value`.
- `classifyQuestion.userChatInput` points to the real text to classify.
- Uploaded document classification uses parsed text instead of raw file arrays.

## F. Answer Nodes

- `answerNode` input key must be `text`.
- Default `answerNode.text.value` uses template format: `{{$nodeId.outputKey$}}`.
- `answerNode.text.value` must be a string and must not use array reference style.
- If `answerNode.text.value` references a `chatNode`, the output key is `answerText`, not `aiResponse`.
- `answerNode.text` uses the sample-compatible full input shape:
  - `renderTypeList: ["textarea", "reference"]`
  - `valueType: "any"`
  - `required: true`
  - `isRichText: false`
  - `maxLength: 100000`
- `answerNode` is only used as the final designated reply node, not as intermediate storage.

## G. Usability

- Welcome text explains exact user actions.
- Form descriptions are explicit where form nodes are used.
- Connected nodes have x spacing >= `1500`.
- Branch/sibling nodes have y spacing >= `1000`.
- Node spacing is readable and branches are visually separated.

## H. Enrichment Quality

- Workflow is not only a minimal linear demo unless user explicitly requested minimal mode.
- Non-trivial requirements include at least one intermediate processing stage before final `answerNode`.
- Includes explicit fallback/error-handling path (for example parse failure or insufficient input).
- Final reply can trace back to upstream structured output fields.
- The workflow was decomposed into stages before node selection instead of being collapsed into one general-purpose node.
- The chosen node type for each stage is the most specific suitable node rather than a looser substitute.

## I. Encoding

- Input samples and reference JSON were read as UTF-8.
- Generated JSON/Markdown/protocol output is written as UTF-8.
- Generated labels, prompts, and welcome text do not contain mojibake.
- Generated JSON contains none of these mojibake markers: `鐢`, `鏂`, `绯`, `鈫`, `�`.
- Generated workflow JSON was saved to a `.json` file using UTF-8 unless the user explicitly requested no file write.

## J. Language

- User-facing node configuration text is Chinese.
- Node names, labels, descriptions, prompts, welcome text, instructions, and answer labels are Chinese.
- Technical identifiers (`nodeId`, `key`, `flowNodeType`, handles, enum values) remain schema-compatible.
- No English placeholder labels such as `User input`, `Files`, or `Reply content` remain in generated JSON.

## K. Required Input Collection

- Every required user-provided text/number/select/switch/object input is modeled as a system config global variable or `formInput` field.
- Every required file input is modeled with `workflowStart.userFiles` and `chatConfig.fileSelectConfig.canSelectFile = true`.
- Required file content is routed through `readFiles` when downstream nodes need parsed text.
- No required input is requested only through `systemPrompt`, `welcomeText`, node descriptions, or answer text.
- Every required input has clear Chinese label and input guidance.

## L. Adjustable Parameters

- User-adjustable numeric/config parameters do not contain `value`.
- Threshold-like fields include `defaultValue`, `min`, and `max` when the schema supports them.
- Threshold-like fields do not contain `step`.
- Environment/config variables that should remain editable after import expose defaults and bounds/options instead of fixed value only.
- Parameter labels and descriptions explain the adjustment meaning in Chinese.

## M. File Save

- Final workflow JSON is saved to disk by default.
- Saved file extension is `.json`.
- Saved file path is absolute and reported in the final response.
- If no target path was provided, filename is derived from workflow purpose in concise kebab-case.
- Chat-only JSON output is allowed only when the user explicitly requests not to write a file.

## N. Field-Level Runtime Contracts

- `flowNodeType` values use runtime enum values, not enum member names.
- System config uses `userGuide`, not `systemConfig`.
- Tool call uses `tools`, not `toolCall`.
- Query extension/question optimization uses `cfr`, not `queryExtension`.
- Runtime node configuration is not placed in `props`.
- Runtime node output keys are not invented or copied from legacy examples.
- `chatNode` has `model`, `systemPrompt`, `history`, `isResponseAnswerText`, and any official business inputs in `inputs`, not in `props`.
- `chatNode` outputs do not use legacy keys such as `aiResponse`, `newTitle`, or `quoteList`.
- `formInput` has `description` and `userInputForms` in `inputs`, not in `props`.
- `formInput` output is `formInputResult`, not `result`.
- `userSelect` has `description` and `userSelectOptions` in `inputs`, not in `props`.
- `ifElseNode` has `ifElseList` in `inputs`, not `props.conditions`.
- `ifElseNode` branch names are edge handles only and are not declared as outputs.
- `httpRequest468` URL key is `system_httpReqUrl`, not `system_httpUrl`.
- `httpRequest468` raw response output is `httpRawResponse`, not `system_httpResult`.
- System variables are not referenced through `userGuide.variables`.
- `contentExtract` extraction source is in `content.value`.
- No invented custom extraction input replaces `content`.
- `textEditor` concat content is in `system_textareaInput.value`.
- No separate context/custom text input replaces `system_textareaInput`.
- `formInput` field definitions are inside `userInputForms.value`.
- `userSelect` options are inside `userSelectOptions.value`.

## O. Dynamic Nodes

- Dynamic app/plugin/tool nodes are generated only with concrete target metadata.
- Dynamic inputs and outputs match the target contract.
- Tool nodes include valid `toolConfig`.
- Plugin workflows use `pluginConfig`, `pluginInput`, and `pluginOutput`; normal app workflows do not include them by default.
- `toolParams` is not emitted as an empty standalone node.
- `stopTool` appears only in tool-call termination flows.

## P. Deterministic Validator

- Run `scripts/validate_fastgpt_json.py <generated-file>` after saving the workflow JSON.
- The validator must print `VALIDATION_OK`.
- Any `ERROR:` line is a blocking failure; fix JSON and rerun.
- Do not mark a workflow as import-ready if the deterministic validator has not passed.
- If the validator cannot be run, final status must be `未验证`, not `VALIDATION_OK`.

