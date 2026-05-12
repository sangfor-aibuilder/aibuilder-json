# FastGPT Workflow Runtime Reference

This reference is source-aligned with `packages/global/core/workflow`.

Use this file as the final authority when generating node `flowNodeType`, input `key`, output `key`, and references.

## 1. Core Enum Values

These values come from `packages/global/core/workflow/node/constant.ts`.

| Concept | JSON `flowNodeType` |
|---|---|
| System config | `userGuide` |
| Workflow start | `workflowStart` |
| AI chat | `chatNode` |
| Dataset search | `datasetSearchNode` |
| Dataset concat | `datasetConcatNode` |
| Assigned answer | `answerNode` |
| Question classify | `classifyQuestion` |
| Content extract | `contentExtract` |
| HTTP request | `httpRequest468` |
| Query extension / question optimization | `cfr` |
| Agent | `agent` |
| Tool call | `tools` |
| Tool params | `toolParams` |
| Stop tool | `stopTool` |
| Laf function | `lafModule` |
| If/else | `ifElseNode` |
| Variable update | `variableUpdate` |
| Code execution | `code` |
| Text editor / text concat | `textEditor` |
| Custom feedback | `customFeedback` |
| Read files | `readFiles` |
| User select | `userSelect` |
| Loop | `loop` |
| Loop start | `loopStart` |
| Loop end | `loopEnd` |
| Form input | `formInput` |
| Plugin config | `pluginConfig` |
| Plugin input | `pluginInput` |
| Plugin output | `pluginOutput` |
| Run app node | `appModule` |
| Run plugin node | `pluginModule` |
| Tool node | `tool` |
| Tool set node | `toolSet` |
| Empty node | `emptyNode` |
| Comment node | `comment` |
| Deprecated app call | `app` |

Strict rule:

- Do not use enum member names as JSON values when they differ from runtime values.
- The query extension node must use `"flowNodeType": "cfr"`, not `"queryExtension"`.
- The tool call node must use `"flowNodeType": "tools"`, not `"toolCall"`.
- The system config node must use `"flowNodeType": "userGuide"`, not `"systemConfig"`.

## 2. Shared Input and Output Keys

These values come from `NodeInputKeyEnum` and `NodeOutputKeyEnum` in `packages/global/core/workflow/constants.ts`.

Important input keys:

| Meaning | Input key |
|---|---|
| AI model | `model` |
| System prompt | `systemPrompt` |
| Description | `description` |
| History | `history` |
| User chat input | `userChatInput` |
| File URL list | `fileUrlList` |
| Textarea / text concat input | `system_textareaInput` |
| Answer text input | `text` |
| Content extract input | `content` |
| Extract keys | `extractKeys` |
| Dataset select list | `datasets` |
| Dataset max tokens | `limit` |
| Dataset quote list | `system_datasetQuoteList` |
| If/else list | `ifElseList` |
| Variable update list | `updateList` |
| HTTP URL | `system_httpReqUrl` |
| HTTP method | `system_httpMethod` |
| HTTP timeout | `system_httpTimeout` |
| HTTP headers | `system_httpHeader` |
| HTTP params | `system_httpParams` |
| HTTP JSON body | `system_httpJsonBody` |
| HTTP form body | `system_httpFormBody` |
| HTTP content type | `system_httpContentType` |
| Code type | `codeType` |
| Code body | `code` |
| User select options | `userSelectOptions` |
| Form input definitions | `userInputForms` |
| Selected tools | `agent_selectedTools` |
| Agent skills | `skills` |
| Tool params data | `system_toolData` |
| Tool set data | `system_toolSetData` |
| Comment text | `commentText` |
| Comment size | `commentSize` |
| Loop input array | `loopInputArray` |
| Loop start input | `loopStartInput` |
| Loop start index | `loopStartIndex` |
| Loop end input | `loopEndInput` |

Important output keys:

| Meaning | Output key |
|---|---|
| Workflow user question | `userChatInput` |
| Workflow user files | `userFiles` |
| AI answer | `answerText` |
| AI reasoning | `reasoningText` |
| New history | `history` |
| Generic text output | `system_text` |
| Generic raw response | `system_rawResponse` |
| Error text | `system_error_text` |
| Dataset quote | `quoteQA` |
| Classify result | `cqResult` |
| Content extract success | `success` |
| Content extract fields | `fields` |
| HTTP raw response | `httpRawResponse` |
| If/else result | `ifElseResult` |
| User select result | `selectResult` |
| Form input result | `formInputResult` |
| Loop result array | `loopArray` |
| Loop start index | `loopStartIndex` |

Strict rule:

- References must point to runtime output keys, not display labels.
- For file parsing text, use `["readFilesNodeId", "system_text"]`.
- For content extraction result, use `["contentExtractNodeId", "fields"]`.
- For query extension result, use `["cfrNodeId", "system_text"]`.
- For text editor result, use `["textEditorNodeId", "system_text"]`.

## 3. Node Contracts

### 3.1 `workflowStart`

Runtime:

- `flowNodeType`: `workflowStart`
- input: `userChatInput`
- output: `userChatInput`
- optional file output used by chat upload: `userFiles`

Strict rules:

- If chat file upload is required, enable `chatConfig.fileSelectConfig.canSelectFile = true`.
- File flows should reference `["workflowStartNodeId", "userFiles"]`.

### 3.2 `userGuide`

Runtime:

- `flowNodeType`: `userGuide`
- inputs: `[]`
- outputs: `[]`

Strict rules:

- Include one system config node by default.

### 3.3 `chatNode`

Runtime:

- `flowNodeType`: `chatNode`
- runtime controls include `model` and `isResponseAnswerText`
- official AI dialogue input configuration keys only: `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, `userChatInput`
- outputs: `history`, `answerText`, `reasoningText`, `system_error_text`

Strict rules:

- At least one business input must be configured: `userChatInput`, `fileUrlList`, or `quoteQA`.
- `systemPrompt` alone is invalid.
- If document text is needed, prefer parsed text such as `["readFilesNodeId", "system_text"]`.
- Do not add separate `chatNode` inputs for form fields, extracted fields, HTTP results, variables, or custom context; fold them into `systemPrompt` or `userChatInput`, usually via `textEditor.system_text`.

### 3.4 `textEditor`

Runtime:

- `flowNodeType`: `textEditor`
- required input: `system_textareaInput`
- output: `system_text`

Strict rules:

- All concatenation content and variable references must be placed inside the `system_textareaInput` input.
- Do not create extra custom input fields for context and leave `system_textareaInput` empty.
- The node only has one real required input. If `system_textareaInput.value` is empty, the node is invalid.
- Use template references inside `system_textareaInput.value`.

Example:

```json
{
  "key": "system_textareaInput",
  "renderTypeList": ["textarea"],
  "valueType": "string",
  "required": true,
  "label": "拼接文本",
  "value": "候选人信息：{{$contentExtract-001.fields$}}\n岗位要求：{{$formInput-001.formInputResult$}}"
}
```

### 3.5 `contentExtract`

Runtime:

- `flowNodeType`: `contentExtract`
- required/default input keys: `model`, `description`, `history`, `content`, `extractKeys`
- outputs: `success`, `fields`, `system_error_text`

Strict rules:

- The default "需要提取的文本" field is the input with key `content`.
- The extraction source must be configured in `content.value`.
- Do not create a new custom input to hold extraction text while leaving `content` empty.
- `extractKeys.value` must be a non-empty field config array.
- Each `extractKeys.value` item should follow `{ key, desc, valueType, required, defaultValue?, enum? }`.
- Allowed extract value types are `string`, `number`, `boolean`, `arrayString`, `arrayNumber`, `arrayBoolean`.
- For uploaded documents, `content.value` should usually reference `["readFilesNodeId", "system_text"]`.

Example:

```json
{
  "key": "content",
  "renderTypeList": ["reference", "textarea"],
  "label": "需要提取的文本",
  "required": true,
  "valueType": "string",
  "value": ["readFiles-001", "system_text"]
}
```

### 3.6 `cfr` query extension

Runtime:

- `flowNodeType`: `cfr`
- inputs: `model`, `systemPrompt`, `history`, `userChatInput`
- output: `system_text`

Strict rules:

- Use `"flowNodeType": "cfr"`.
- Do not use `"flowNodeType": "queryExtension"`.
- The optimized query output is `system_text`.
- Downstream dataset search should reference `["cfrNodeId", "system_text"]`.

### 3.7 `answerNode`

Runtime:

- `flowNodeType`: `answerNode`
- required input: `text`
- outputs: `[]`

Strict rules:

- `answerNode.text.value` should use template reference style by default: `{{$nodeId.outputKey$}}`.
- Do not use `answerText` as the input key.

### 3.8 `readFiles`

Runtime:

- `flowNodeType`: `readFiles`
- required input: `fileUrlList`
- outputs: `system_text`, `system_rawResponse`, `system_error_text`

Strict rules:

- `fileUrlList.value` must reference a file array, usually `["workflowStartNodeId", "userFiles"]`.
- Downstream text nodes should consume `system_text`, not raw `userFiles`.

### 3.9 `datasetSearchNode`

Runtime:

- `flowNodeType`: `datasetSearchNode`
- important inputs: `datasets`, `similarity`, `limit`, `searchMode`, `embeddingWeight`, `usingReRank`, `rerankModel`, `rerankWeight`, `datasetSearchUsingExtensionQuery`, `datasetSearchExtensionModel`, `datasetSearchExtensionBg`, `authTmbId`, `userChatInput`, `collectionFilterMatch`
- outputs: `quoteQA`, `system_error_text`

Strict rules:

- `datasets` and `userChatInput` must be configured.
- Downstream AI quote input should reference `["datasetSearchNodeId", "quoteQA"]`.

### 3.10 `datasetConcatNode`

Runtime:

- `flowNodeType`: `datasetConcatNode`
- inputs: `limit`, `system_datasetQuoteList`, editable quote inputs generated by the UI/source helper
- output: `quoteQA`

Strict rules:

- Use only to merge dataset quote outputs.
- Downstream `chatNode.quoteQA` should reference the concat output `quoteQA`.

### 3.11 `classifyQuestion`

Runtime:

- `flowNodeType`: `classifyQuestion`
- inputs: `model`, `systemPrompt`, `history`, `userChatInput`, `agents`
- output: `cqResult`

Strict rules:

- `agents.value` must be non-empty.
- Branch handles must align with category keys when routing is generated.

### 3.12 `ifElseNode`

Runtime:

- `flowNodeType`: `ifElseNode`
- input: `ifElseList`
- output: `ifElseResult`

Strict rules:

- `ifElseList.value` items must include group `condition` and every rule must include `variable`, `condition`, and `value` when the operator requires comparison input.

### 3.13 `httpRequest468`

Runtime:

- `flowNodeType`: `httpRequest468`
- inputs: `system_addInputParam`, `system_httpMethod`, `system_httpTimeout`, `system_httpReqUrl`, `system_header_secret`, `system_httpHeader`, `system_httpParams`, `system_httpJsonBody`, `system_httpFormBody`, `system_httpContentType`
- outputs: dynamic `system_addOutputParam`, `httpRawResponse`, `error`

Strict rules:

- URL, method, timeout, content type, and required request data must be configured.
- Prefer dynamic outputs when downstream nodes need extracted response fields.

### 3.14 `variableUpdate`

Runtime:

- `flowNodeType`: `variableUpdate`
- input: `updateList`
- outputs: `[]`

Strict rules:

- Every update item must include target `variable`, source/value, `valueType`, and render type.
- `renderType` must be `input` or `reference`.
- For literal input values, use `value: ["", literalValue]`.
- For reference values, use `value: ["nodeId", "outputKey"]`.

### 3.15 `code`

Runtime:

- `flowNodeType`: `code`
- inputs: dynamic inputs such as `data1`, `data2`, `codeType`, `code`
- outputs: dynamic outputs, `system_rawResponse`, `error`

Strict rules:

- Declared dynamic inputs and outputs must match the code body.

### 3.16 `tools` tool call

Runtime:

- `flowNodeType`: `tools`
- inputs are close to `chatNode`, with additional `useAgentSandbox`
- outputs: `answerText`, `system_error_text`

Strict rules:

- Use `"flowNodeType": "tools"`.
- Do not use `"flowNodeType": "toolCall"`.

### 3.16.1 `agent`

Runtime:

- `flowNodeType`: `agent`
- important inputs: `model`, `temperature`, `maxToken`, `isResponseAnswerText`, `aiChatVision`, `aiChatReasoning`, `aiChatTopP`, `aiChatStopSign`, `aiChatResponseFormat`, `aiChatJsonSchema`, `systemPrompt`, `fileUrlList`, `userChatInput`, `skills`, `agent_selectedTools`, `datasets`, and dataset search settings
- outputs: `answerText`, `system_error_text`

Strict rules:

- Use `agent` only when agent planning/tool/skill orchestration is required.
- Do not use `agent` as a plain AI chat replacement.
- At least one real business input must be configured.
- If `skills`, `agent_selectedTools`, or `datasets` are used, they must point to real configured resources.
- If no tool/skill/dataset context exists, prefer `chatNode`.

### 3.16.2 `toolParams`

Runtime:

- `flowNodeType`: `toolParams`
- template inputs: dynamic, initially `[]`
- template outputs: dynamic, initially `[]`

Strict rules:

- Use only inside tool/plugin contexts where parameter schema is known.
- Do not generate empty standalone `toolParams` nodes in ordinary app workflows.
- Do not invent tool parameter schemas without a provided tool contract.

### 3.16.3 `stopTool`

Runtime:

- `flowNodeType`: `stopTool`
- inputs: `[]`
- outputs: `[]`

Strict rules:

- Use only in tool-call flows to intentionally terminate tool execution.
- Do not use as a generic workflow stop/final answer node.

### 3.17 `userSelect`

Runtime:

- `flowNodeType`: `userSelect`
- inputs: `description`, `userSelectOptions`
- output: `selectResult`

Strict rules:

- Options must be non-empty `{ key, value }` items.

### 3.18 `formInput`

Runtime:

- `flowNodeType`: `formInput`
- inputs: `description`, `userInputForms`
- output: `formInputResult`

Strict rules:

- Form definitions go in `userInputForms.value`.
- Do not invent sibling inputs for each form field.
- Runtime form item fields include `type`, `key`, `label`, `value`, `valueType`, `description`, `defaultValue`, and `required`.

### 3.19 `loop`, `loopStart`, `loopEnd`

Runtime:

- `loop` input: `loopInputArray`
- `loop` output: `loopArray`
- `loopStart` inputs: `loopStartInput`, `loopStartIndex`
- `loopStart` output: `loopStartIndex`
- `loopEnd` input: `loopEndInput`

Strict rules:

- Batch output should be collected through `loopEndInput` and consumed from `loopArray`.

### 3.20 `lafModule`

Runtime:

- `flowNodeType`: `lafModule`
- inputs: dynamic inputs, `system_httpReqUrl`
- outputs: `httpRawResponse`, dynamic outputs, `system_error_text`

### 3.21 `customFeedback`

Runtime:

- `flowNodeType`: `customFeedback`
- input: `system_textareaInput`
- outputs: `[]`

Strict rules:

- Feedback text must be configured in `system_textareaInput`.

### 3.22 `pluginConfig`, `pluginInput`, `pluginOutput`

Runtime:

- `pluginConfig` inputs/outputs: `[]`
- `pluginInput` inputs/outputs: dynamic, initially `[]`
- `pluginOutput` inputs/outputs: dynamic, initially `[]`

Strict rules:

- Use these only when generating a plugin workflow, not a normal app workflow.
- `pluginInput` defines externally supplied plugin parameters.
- `pluginOutput` defines plugin return fields.
- Do not leave a plugin workflow without meaningful `pluginInput`/`pluginOutput` definitions when the plugin contract requires them.
- Do not add these nodes to normal app JSON unless the user explicitly requests plugin generation.

### 3.23 `appModule`, `pluginModule`, `tool`, `toolSet`

Runtime:

- `appModule` calls another app. Inputs/outputs are dynamically produced from the selected app's chat config.
- `pluginModule` calls a plugin. Inputs/outputs are dynamically produced from the target plugin's input/output contract.
- `tool` represents a single configured tool. Inputs/outputs and `toolConfig` are dynamic.
- `toolSet` represents a configured tool set. Inputs/outputs and `toolConfig` are dynamic.

Strict rules:

- Do not generate these nodes without a concrete target app/plugin/tool/toolSet contract.
- Do not invent dynamic inputs/outputs when the target contract is unknown.
- If the user asks to call another app/plugin/tool, require or infer the concrete target metadata before generating an import-ready JSON.
- `tool` / `toolSet` must include valid `toolConfig` when used.

### 3.24 `emptyNode`

Runtime:

- `flowNodeType`: `emptyNode`
- inputs: `[]`
- outputs: `[]`

Strict rules:

- Use only as a placeholder/import compatibility node.
- Do not use in production generated workflows unless explicitly requested.

### 3.25 `comment`

Runtime:

- `flowNodeType`: `comment`
- inputs: `commentText`, `commentSize`
- outputs: `[]`

Strict rules:

- Use only for canvas annotation.
- `commentText.value` should be Chinese if shown to users.
- `commentSize.value` must include numeric `width` and `height`.

### 3.26 Deprecated `app`

Runtime:

- `flowNodeType`: `app`
- inputs: `app`, `history`, `userChatInput`
- outputs: `history`, `answerText`

Strict rules:

- This is an abandoned legacy app-call node.
- Do not use it for new workflows unless the user explicitly requires legacy compatibility.
- Prefer `appModule` only when a concrete target app contract is available.

### 3.27 Complete System Template Coverage

`moduleTemplatesFlat` includes these templates:

- `chatNode`
- `textEditor`
- `answerNode`
- `datasetSearchNode`
- `classifyQuestion`
- `contentExtract`
- `datasetConcatNode`
- `tools`
- `toolParams`
- `stopTool`
- `agent`
- `readFiles`
- `httpRequest468`
- `cfr`
- `lafModule`
- `ifElseNode`
- `variableUpdate`
- `code`
- `loop`
- `customFeedback`
- `userSelect`
- `formInput`
- `pluginConfig`
- `pluginInput`
- `pluginOutput`
- `emptyNode`
- `pluginModule`
- `appModule`
- `app`
- `loopStart`
- `loopEnd`
- `tool`
- `toolSet`

Any generated node outside this list must be backed by a user-provided plugin/app/tool contract.

## 4. Reference Rules

Array references:

```json
["nodeId", "outputKey"]
```

Template references:

```json
"{{$nodeId.outputKey$}}"
```

Strict rules:

- For normal node input references, array reference style is safe and source-aligned.
- For `answerNode.text.value`, use template reference style by default.
- For `textEditor.system_textareaInput.value`, use template reference style inside the text body.
- For `contentExtract.content.value`, use array reference style unless the field is intentionally a text literal.

