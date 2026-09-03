# Node Field Contracts

Use this file to reject invalid node fields, invented IO keys, and unsafe references. For copyable node shapes, use `official-default-node-templates.json` first. `runtime-node-templates.md` is only an explanatory guide and must not override official default fields.

## 1. Global Field Rules

- Runtime configuration belongs in `node.inputs`, not `props`.
- Do not create custom inputs that duplicate source-defined inputs.
- Do not invent outputs to make references work.
- Validate references against the upstream node type's runtime outputs, not against outputs declared by the generated JSON.
- `userGuide` is not a variable emitter. Do not reference `userGuide.variables.*`.

## 2. Reference Rules

Allowed reference styles:

- Normal input reference: `["nodeId", "outputKey"]`
- `answerNode.text.value`: string template style only, for example `{{$nodeId.outputKey$}}`
- `textEditor.system_textareaInput.value`: template body with `{{$nodeId.outputKey$}}`

Visual edge requirement:

- The referenced node must be upstream of the consuming node in the edge graph.
- A direct edge from the referenced node to the consuming node is not required when the referenced node is already on the same upstream path.
- Prefer one readable chain over many cross-links into a single node.

Rejected:

- Legacy moustache: `{{nodeId.outputKey}}`
- Array reference in `answerNode.text.value`, such as `["nodeId", "outputKey"]`
- Display-label references
- Invented subpaths such as `{{$formInput.result.bookingDate$}}`
- `{{$userGuide.variables.apiBaseUrl$}}`
- Any output key not listed in the runtime whitelist.

## 3. Runtime Output Whitelist

| Node type | Valid outputs |
|---|---|
| `workflowStart` | `userChatInput`, `userFiles` |
| `userGuide` | none |
| `formInput` | `formInputResult` |
| `userSelect` | `selectResult` |
| `ifElseNode` | `ifElseResult` |
| `textEditor` | `system_text` |
| `chatNode` | `history`, `answerText`, `reasoningText`, `system_error_text` |
| `httpRequest468` | `httpRawResponse`, `error`, known dynamic outputs only |
| `readFiles` | `system_text`, `system_rawResponse`, `system_error_text` |
| `contentExtract` | `success`, `fields`, `system_error_text` |
| `datasetSearchNode` | `quoteQA`, `system_error_text` |
| `datasetConcatNode` | `quoteQA` |
| `classifyQuestion` | `cqResult` |
| `cfr` | `system_text` |
| `answerNode` | none |

Common invalid keys:

- `formInput.result`
- `chatNode.aiResponse`, `chatNode.newTitle`, `chatNode.quoteList`
- `httpRequest468.system_httpResult`
- `ifElseNode.IF`, `ifElseNode.ELSE`
- `contentExtract.courseName`, `contentExtract.bookingDate`, `contentExtract.recommendedClassroom`, or any other per-field extraction output

## 4. Node-Specific Contracts

### `workflowStart`

- Must include input `userChatInput`.
- Must output `userChatInput`.
- Add `userFiles` only when chat file upload is enabled, and enable the matching `chatConfig.fileSelectConfig` file channels for the required file categories (documents `canSelectFile`, images `canSelectImg`, audio `canSelectAudio`, video `canSelectVideo`, custom extensions `canSelectCustomFileExtension` with non-empty `customFileExtensionList`; see `references/file-format-rules.md`).

### `userGuide`

- Must use the official default system config inputs.
- Must use `outputs: []`.
- Put welcome text, file settings, voice settings, and variables metadata in root `chatConfig`.

### `chatNode`

- Required runtime controls: `model`, `isResponseAnswerText`.
- Official AI dialogue input configuration whitelist: `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, `userChatInput`.
- Start from the official default `chatNode` template and preserve official control fields such as `temperature`, `maxToken`, quote settings, vision/reasoning/top-p/stop/response-format/json-schema fields unless a known FastGPT export proves they are safely omitted.
- Must include `systemPrompt`, `history`, and at least one business input: `userChatInput`, `fileUrlList`, or `quoteQA`.
- `fileUrlList` carries the user-uploaded documents and images; image understanding requires a vision-capable model on this `chatNode` (`canSelectImg` must be enabled in `chatConfig.fileSelectConfig`).
- Do not add any other `chatNode.inputs[].key` for business/context data, including form fields, extraction fields, HTTP responses, variables, user profile fields, scoring dimensions, search text, or custom metadata.
- When extra context is needed, assemble it before the AI node and reference it through `systemPrompt.value` or `userChatInput.value`; for deterministic assembly use `textEditor.system_text`, then bind that output to `userChatInput` or embed it in the prompt.
- If followed by `answerNode`, `isResponseAnswerText.value` must be `false`.
- Output only `answerText` for answer content; never `aiResponse`.

### `answerNode`

- Input key must be `text`.
- Use full answer text shape: `renderTypeList`, `valueType`, `required`, `isRichText`, `maxLength`, `label`, `value`.
- `text.value` must be a string. If referencing a `chatNode`, use `{{$chatNodeId.answerText$}}`.
- Do not use `text.value: ["chatNodeId", "answerText"]`.

### `textEditor`

- Required input: `system_textareaInput`.
- Put the actual concat/template content in `system_textareaInput.value`.
- Output only `system_text`.

### `contentExtract`

- Required inputs: `model`, `description`, `history`, `content`, `extractKeys`.
- Extraction source must be in `content.value`.
- `extractKeys.value` must be non-empty.
- Do not generate separate outputs for extracted fields. Downstream nodes must consume `fields`.

### `formInput`

- Required inputs: `description`, `userInputForms`.
- Field definitions stay inside `userInputForms.value`.
- Output key is `formInputResult`; never `result`.

### `userSelect`

- Required inputs: `description`, `userSelectOptions`.
- Options stay inside `userSelectOptions.value`.
- Output key is `selectResult`.

### `ifElseNode`

- Required input: `ifElseList`.
- `ifElseList.value[]` group shape is `condition` + `list`.
- Do not use `conditionList`.
- Branch names (`IF`, `ELSE IF N`, `ELSE`) are edge handles only, not outputs.
- Output only `ifElseResult`.

### `httpRequest468`

- Required inputs: `system_httpReqUrl`, `system_httpMethod`, `system_httpTimeout`.
- URL key is `system_httpReqUrl`, not `system_httpUrl`.
- `system_httpReqUrl.value` must not be empty; use a replaceable placeholder if needed.
- JSON request body uses `system_httpJsonBody`; it must not be empty when upstream data is sent.
- Raw response output is `httpRawResponse`, not `system_httpResult`.

### `readFiles`

- Required input: `fileUrlList`.
- Parsed text output is `system_text`.
- Downstream text logic must consume `system_text`, not raw `userFiles`.
- Parses text-bearing documents only; images and other non-text files are understood through vision-capable `chatNode`/`tools` nodes via `fileUrlList` (see `references/file-format-rules.md`).

### `cfr`

- Runtime type is `cfr`, not `queryExtension`.
- Output is `system_text`.

### `tools`

- Runtime type is `tools`, not `toolCall`.
- Must include model/prompt/history plus real tool-use business input.

### Dynamic Nodes

Only generate these with a concrete supplied contract: `appModule`, `pluginModule`, `tool`, `toolSet`, `toolParams`, `pluginInput`, `pluginOutput`.

Do not guess dynamic inputs, outputs, or `toolConfig`.

### Agent

Use `agent` only when real planning, tool use, skills, or datasets are configured. Otherwise use `chatNode`.

### Placeholder/Deprecated Nodes

- `emptyNode`: placeholder only.
- `comment`: annotation only.
- `stopTool`: tool termination only.
- `app`: deprecated; use only when explicitly requested for legacy compatibility.

