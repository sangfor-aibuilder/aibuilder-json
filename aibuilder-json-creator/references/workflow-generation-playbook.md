# Workflow Generation Playbook

## 1. Requirement Decomposition

Convert user text into:

- Business objective
- Inputs (chat text, form fields, uploaded files, datasets)
- Processing stages
- Decision points (conditions and thresholds)
- Outputs (direct reply, structured report, branch-specific reply)

Mandatory stage decomposition before node selection:

- Input collection
- File parsing
- Query rewrite / question optimization
- Retrieval
- Deterministic transformation
- Structured extraction
- Open-ended reasoning
- Classification / routing
- State update
- Human choice / human feedback
- Final response

Enrich requirements by default:

- Fill missing constraints: validation, fallback, and exception handling.
- Fill missing business details: scoring dimensions, decision thresholds, and explanation format.
- Fill missing output contract: key fields to expose for downstream references.
- Convert every required user-provided value into an explicit collection mechanism (`formInput`, system config global variable, or file upload path).
- Do not leave required input collection as prompt-only instructions.

## 2. Node Mapping

Typical mapping:

- Start: `workflowStart`
- System defaults (required by default): `userGuide`
- User structured input: `formInput`
- File parsing: `readFiles`
- AI extraction/evaluation: `chatNode`
- Knowledge-base retrieval: `datasetSearchNode`
- Knowledge-base merge: `datasetConcatNode`
- Question classification: `classifyQuestion`
- Rule branching: `ifElseNode`
- Final response: `answerNode`

Strict node choice rules:

- Open-ended reasoning / explanation / summary / policy-based judgment: `chatNode`
- Structured field extraction from text: `contentExtract`
- Tool orchestration: `tools`
- Agent planning/tool/skill orchestration: `agent`
- App/plugin/tool contract calls: `appModule`, `pluginModule`, `tool`, `toolSet` only when target metadata is known
- Explicit human option selection: `userSelect`
- Structured required user fields: `formInput`
- Deterministic text assembly: `textEditor`
- Uploaded file parsing: `readFiles`
- External REST/webhook call: `httpRequest468`
- Rule-based branch judgment: `ifElseNode`
- Variable/state mutation: `variableUpdate`
- Deterministic custom transform/calculation: `code`
- Batch per-item execution: `loop`
- Query rewrite before retrieval/answering: `cfr`
- Laf-specific integration: `lafModule`
- Human feedback capture: `customFeedback`

Do not use `chatNode` as a substitute for `contentExtract`, `classifyQuestion`, `textEditor`, `userSelect`, `formInput`, `httpRequest468`, `variableUpdate`, or `answerNode` when those nodes fit the requirement better.

Dynamic contract rule:

- Do not generate `appModule`, `pluginModule`, `tool`, `toolSet`, `toolParams`, `pluginInput`, or `pluginOutput` unless a concrete target contract is known.
- Do not invent dynamic input/output keys for these nodes.
- Do not use `agent` unless the requirement needs planning, tool use, skill use, or agentic orchestration.

Required input mapping:

- Required text/long text: `formInput` field with Chinese label, description, and `required: true`.
- Required number/select/switch: `formInput` field with default/range/options and Chinese description.
- Adjustable thresholds and numeric parameters: omit `value` and `step`; include `defaultValue`, `min`, and `max` when supported.
- Required file: `workflowStart.userFiles` with the matching `chatConfig.fileSelectConfig` file channels (documents `canSelectFile`, images `canSelectImg`, audio `canSelectAudio`, video `canSelectVideo`, custom extensions `canSelectCustomFileExtension` with non-empty `customFileExtensionList`; see `references/file-format-rules.md`), then `readFiles` for text-bearing documents.
- App-level stable parameters: system config global variables.
- If downstream logic needs file content, reference parsed text outputs such as `readFiles.system_text`, not raw uploaded files.

## 3. Edge Strategy

- Keep main path left->right.
- Branch nodes fan out vertically.
- Use large spacing for manual maintenance:
  - Connected columns must be at least `1500` apart on x.
  - Branch/sibling rows must be at least `1000` apart on y.
  - Prefer column positions like `0, 1500, 3000, 4500...`.

## 4. Common Patterns

### Pattern A: Chat-upload file -> parse -> evaluate

`workflowStart(userFiles)` -> `readFiles(system_text)` -> `chatNode` -> `answerNode`

### Pattern B: Form + file combined

`formInput` + `readFiles` -> `chatNode` with:
- `userChatInput` from form output
- `fileUrlList` from user files

Every `chatNode` must include at least one effective business input:

- `userChatInput.value`: reference user question, form result, parsed file text, or upstream AI output.
- `fileUrlList.value`: reference `workflowStart.userFiles` or another file array output.
- `quoteQA.value`: explicit dataset quote configuration when knowledge-base retrieval is required.
- `systemPrompt` alone is invalid because it only defines rules, not user/business data.
- When the node is reasoning over resume/document content, prefer parsed text input over raw `userFiles`.

### Pattern C: Multi-branch screening

`chatNode` -> `ifElseNode` -> `answerNode` branches

### Pattern H: Structured extraction from document

`workflowStart(userFiles)` -> `readFiles(system_text)` -> `contentExtract(content)` -> `ifElseNode/chatNode/answerNode`

Rules:
- resume parsing, form extraction, clause extraction, and entity extraction should prefer `contentExtract`
- configure the extraction source in the default `content` input
- `extractKeys` must be explicit and non-empty
- downstream nodes must reference `contentExtract.fields`, not field-level outputs
- do not generate outputs named after `extractKeys` items

### Pattern I: Explicit user choice -> route

`userSelect` -> `ifElseNode or branch-specific downstream nodes`

Rules:
- use when the workflow should wait for the user to choose an option rather than infer it

### Pattern J: Structured form collection -> processing

`formInput` -> downstream nodes

Rules:
- use for required structured business inputs
- numeric/threshold fields should be editable through `defaultValue`, `min`, `max` when supported

### Pattern K: Deterministic text assembly

upstream references -> `textEditor(system_textareaInput)` -> downstream `chatNode` or `answerNode`

Rules:
- use for prompt stitching, fixed report assembly, or deterministic copy generation
- put all concat text and variable references in `system_textareaInput.value`

### Pattern L: External API call

upstream parameters -> `httpRequest468` -> downstream parse / answer

Rules:
- prefer `httpRequest468` over `code` for standard API calls
- never leave `system_httpReqUrl.value` empty
- if the real endpoint is unknown, use a clear placeholder URL and mark it replaceable
- use `system_httpJsonBody` for JSON request bodies and populate it from upstream `textEditor.system_text` or a concrete JSON template
- downstream nodes reference `httpRawResponse`

### Pattern M: Batch execution

array source -> `loop` -> loop child flow -> `loopArray` -> downstream summarize / answer

Rules:
- use for per-item scoring, per-document parsing, or per-record transformation
- do not copy-paste repeated branches for batch work

### Pattern N: Query optimization before retrieval

`workflowStart/formInput` -> `cfr` -> `datasetSearchNode` -> downstream answer

Rules:
- use when search quality depends on rewritten queries
- generated node `flowNodeType` must be `cfr`
- downstream retrieval should reference `cfr.system_text`

### Pattern O: State update

upstream outputs -> `variableUpdate` -> downstream consumers

Rules:
- use for simple state assignment/normalization instead of `code`

### Pattern G: Question classification routing

`workflowStart/formInput` -> `classifyQuestion` -> category branches

Rules:
- `classifyQuestion.model`, `systemPrompt`, `history`, `userChatInput`, and `agents` must be configured.
- `agents` must be a non-empty category list with stable unique keys.
- If uploaded document content is being classified, the node should consume parsed text such as `readFiles.system_text`.
- Use one fallback category such as `其他问题` by default unless the user explicitly excludes it.

### Pattern E: Knowledge-base retrieval -> AI answer

`workflowStart/formInput` -> `datasetSearchNode` -> `chatNode.quoteQA` -> `answerNode`

Rules:
- `datasetSearchNode.datasets` must be configured.
- `datasetSearchNode.userChatInput` must point to the real retrieval query.
- downstream `chatNode.quoteQA` must reference `["datasetSearch-xxx", "quoteQA"]`.
- This is the default strict pattern whenever the requirement includes knowledge-base retrieval.

### Pattern F: Multi-source retrieval merge

`datasetSearchNode A` + `datasetSearchNode B` -> `datasetConcatNode` -> `chatNode.quoteQA`

Rules:
- This is the default strict pattern for multi-knowledge-base retrieval.
- Do not skip `datasetConcatNode` when multiple retrieval outputs need to be consumed together.

`ifElseNode` rules must include complete condition tuples:
- `variable`
- `condition`
- `value` when the operator requires comparison input
- group shape must be `condition` + `list`
- do not use `conditionList`
- branch outputs are not `IF` or `ELSE`; branch routing uses edge handles

### Pattern D: Enriched production baseline (recommended default)

`workflowStart` -> `userGuide` (system defaults) -> `chatNode` (extract/evaluate structured fields) -> `ifElseNode` (tiered decision) -> `answerNode` (branch-specific reply/fallback)

## 5. Answer Value Style

Default for `answerNode.text` must match the sample-compatible shape:

```json
{
  "key": "text",
  "renderTypeList": ["textarea", "reference"],
  "valueType": "any",
  "required": true,
  "isRichText": false,
  "maxLength": 100000,
  "label": "回复内容",
  "value": "{{$chatNode-1.answerText$}}"
}
```

Never use array style (`["nodeId","outputKey"]`) for `answerNode.text`. Use string template style such as `{{$chatNode-1.answerText$}}`.

## 6. Node-Specific Minimum Contracts

- `chatNode`: `model`, `systemPrompt`, `history`, and at least one effective business input
- `contentExtract`: `model`, `description`, `history`, `content`, `extractKeys`
- `tools`: `model`, `systemPrompt`, `history`, and a real tool-use business input
- `userSelect`: `description`, non-empty options
- `formInput`: `description`, non-empty form definitions
- `textEditor`: `system_textareaInput`
- `answerNode`: full `text` input shape
- `readFiles`: `fileUrlList`
- `httpRequest468`: URL, method, timeout, request config
- `ifElseNode`: complete condition tuples
- `variableUpdate`: complete update mappings
- `code`: explicit inputs and executable transform
- `loop`: valid array input and loop child structure
- `cfr`: `model`, `systemPrompt`, `history`, `userChatInput`
- `lafModule`: URL and required dynamic inputs
- `customFeedback`: `system_textareaInput`
- `agent`: model/prompt/business input plus real tool/skill/dataset orchestration context
- `appModule` / `pluginModule` / `tool` / `toolSet`: concrete target contract and dynamic IO
- `pluginInput` / `pluginOutput`: plugin workflow contract fields
- `toolParams`: known tool parameter schema
- `comment`: `commentText`, `commentSize`
- `emptyNode`: placeholder only
- `stopTool`: tool termination only
