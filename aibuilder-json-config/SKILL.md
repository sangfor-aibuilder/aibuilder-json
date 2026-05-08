---
name: aibuilder-json-config
description: Generate and validate import-ready FastGPT workflow JSON from natural-language requirements. Use when users ask to build agents/workflows (for example HR resume screening), fix broken JSON, or convert business process descriptions into FastGPT nodes/edges/chatConfig with strict node IO, handle naming, and connectivity checks.
---

# FastGPT JSON Config Skill

Use this skill to transform user requirements into FastGPT-importable JSON with deterministic checks.

## Inputs to Read First

Always prefer bundled references in this skill folder (export-safe).

1. Read `references/generation-hard-rules.md` first. These rules override older examples.
2. Read `references/required-input-rules.md` for required user input collection rules.
3. Read `references/ifelse-rules.md` for `ifElseNode` condition completeness rules.
4. Read `references/dataset-rules.md` for knowledge-base retrieval node rules.
5. Read `references/classify-rules.md` for question-classification node rules.
6. Read `references/node-selection-rules.md` for strict node selection and node-specific configuration rules.
7. Read `references/node-field-contracts.md` for field-level runtime contracts that prevent invalid nodes.
8. Read `references/json-import-feature-guide.md` for import entry and type recognition.
9. Read `references/json-config-specification.md` for schema, node types, IO, edges.
10. Read `references/json-config-troubleshooting.md` for common failure patterns.
11. Read `references/json-config-runtime-reference.md` for runtime-accurate template behaviors from source code.
12. If the user gives a target sample, read it and align style/field conventions.

## Required Workflow

1. Requirement analysis:
   - Read all user-provided samples, reference JSON, and output targets as UTF-8.
   - Parse business goal, actor, input modality, decision branches, output format.
   - Decompose the requirement into input collection, parsing, retrieval, deterministic transformation, model reasoning, branching, state update, human interaction, and final reply stages.
   - Select the most appropriate node for each stage according to `references/node-selection-rules.md`.
   - Expand implicit requirements (error path, default config, file upload strategy, user guidance text).
   - Perform requirement enrichment before JSON generation:
     - Add missing upstream/downstream stages (input normalization, extraction, decision, final rendering).
     - Add failure-handling path (parse failure, empty result, model fallback message).
     - Add output constraints (structured fields, scoring/rationale, actionable conclusion).
     - Add operational fields when useful (confidence, hit rules, trace summary).
2. Requirement confirmation:
   - Present a concise implementation summary and explicit assumptions.
   - Ask for confirmation on critical options:
     - Input mode (chat upload vs form upload).
     - Branch thresholds/rules.
     - Required system config options (file upload, welcome text, variables).
     - Retrieval mode when the requirement involves knowledge bases: explicit `datasetSearchNode` flow is the default.
   - If user requirement is very brief, provide an "enhanced interpretation" and generate from it by default unless user requests minimal flow.
3. JSON generation:
   - Build `nodes`, `edges`, `chatConfig`.
   - Always include one default system config node: `flowNodeType: "userGuide"`.
   - Configure `chatConfig.welcomeText` as readable Markdown by default:
     - use Chinese headings, short sections, examples, and concise reminders
     - include the app purpose, supported usage modes, example user inputs, required upload/attachment guidance, and fallback/verification notes when applicable
     - keep technical identifiers out of user-facing welcome text unless the user explicitly asks for them
     - do not generate a single plain paragraph welcome text unless the user explicitly requests minimal/plain text
   - Model every required user input as an actual input source:
     - Use system config global variables for app-level required values.
     - Use `formInput` node fields for structured text, number, select, switch, and other form data.
     - Use `workflowStart.userFiles` plus `readFiles` for required file uploads.
     - Do not only tell users in `systemPrompt`, `welcomeText`, or node prompt text to provide required inputs.
     - Each required input must have a clear Chinese label, description, placeholder/help text, and validation/defaults where applicable.
   - Configure every user-adjustable parameter with editable metadata:
     - numeric thresholds, score cutoffs, and environment/config variables must not generate `value`
     - include editable metadata such as `defaultValue`, `min`, and `max` where applicable
     - do not generate `step`
     - ensure imported workflows can still modify those parameters in the UI
   - Configure every `chatNode` with at least one effective business input:
     - `userChatInput.value` references `workflowStart.userChatInput` or an upstream text output.
     - or `fileUrlList.value` references `workflowStart.userFiles` or an upstream file array output.
     - or `quoteQA.value` / dataset quote config is explicitly configured for knowledge-base retrieval.
     - `systemPrompt` alone is not a valid business input.
   - Configure knowledge-base retrieval nodes completely when retrieval is required:
     - default to explicit `datasetSearchNode` flow instead of inline dataset config on `chatNode` / `agent`
     - `datasetSearchNode` must include `datasetSelectList` and `userChatInput`
     - unknown knowledge-base IDs must use 24-character numeric placeholders such as `000000000000000000000001`; never use Chinese text as a dataset ID placeholder
     - downstream AI nodes must reference dataset quote outputs such as `["datasetSearch-xxx","datasetQuoteQA"]`
     - use `datasetConcatNode` when multiple retrieval outputs need merging
     - only use inline dataset config on `chatNode` / `agent` if the user explicitly asks for that simpler structure
   - Route file inputs through parsing before text-based downstream usage:
     - when downstream node needs resume/document content, use `readFiles.system_text` or another parsed text output
     - do not pass raw uploaded files directly as the main text/business input when the node actually needs extracted content
     - reserve raw `userFiles` references for file-aware nodes or file parsing nodes
   - Configure every `ifElseNode` condition completely:
     - each condition item must contain a referenced variable
     - each condition item must contain an explicit operator/condition
     - each condition item must contain an input comparison value when the operator requires one
     - variable-only condition entries are invalid
   - Configure every `classifyQuestion` node completely when classification is required:
     - include `model`, `systemPrompt`, `history`, `userChatInput`, and non-empty `agents`
     - each `agents` item must include stable unique `key` and Chinese `value`
     - if classification drives routing, branch handles must align with `agents[].key`
     - use parsed text instead of raw file arrays when classifying uploaded document content
   - Configure every node according to its source-aligned minimum contract:
     - `contentExtract`: `model`, `description`, `history`, `content`, `extractKeys`; the default "需要提取的文本" field is `content` and must be filled directly
     - `tools`: `model`, `systemPrompt`, `history`, actual business input, and explicit tool-use intent
     - `userSelect`: `description`, non-empty options with stable keys and Chinese values
     - `formInput`: `description`, complete `userInputForms`, Chinese labels, descriptions, placeholders
     - `textEditor`: deterministic `system_textareaInput`, not model reasoning; all concat content and references must be placed in this input
     - `answerNode`: final reply only, `text` input shape must match the strict sample-compatible structure
     - `readFiles`: real `fileUrlList` reference before document-content reasoning
     - `httpRequest468`: full request essentials including URL, method, timeout, and required request payload metadata
     - `variableUpdate`: complete `updateList` target/value mapping
     - `code`: use only when simpler dedicated nodes cannot satisfy the deterministic transformation
     - `loop`: only for true array iteration and must include valid internal `loopStart` / `loopEnd` structure
     - `cfr`: use for query rewrite/optimization before retrieval or downstream reasoning when needed; never output `flowNodeType: "queryExtension"`
     - `lafModule`: use only for Laf-specific function invocation
     - `customFeedback`: use only when the workflow truly needs feedback capture
   - Prefer enhanced workflow over minimal chain:
     - Use at least one processing node before final answer in non-trivial scenarios.
     - Use branching (`ifElseNode`) when result requires tiered decisions (pass/review/reject or high/medium/low).
     - Use `classifyQuestion` when the requirement is intent routing, issue triage, or question dispatch.
     - Keep answer content grounded in upstream structured outputs (not only fixed text).
   - Keep node spacing readable and branch structure clear:
     - Adjacent connected nodes must differ by at least `1500` on the x axis.
     - Branch/sibling nodes must differ by at least `1000` on the y axis.
     - Use wide column layout such as x = `0, 1500, 3000, 4500...`.
   - Prefer source-template-compatible fields from runtime reference.
4. Full validation:
   - Run checklist in `references/validation-checklist.md`.
   - Verify each node input/output, each edge, each reference, each branch handle.
   - Verify root structure meets workflow app recognition requirements.
5. Output:
   - Provide final JSON and a short validation report.
   - Save the final JSON to disk by default using UTF-8 encoding.
   - If the user provides a target path, write to that path.
   - If the user does not provide a target path, create a clear kebab-case `.json` file name from the workflow purpose, such as `hr-resume-screening.json`, and save it under the current workspace or the closest relevant project/sample directory.
   - Report the saved absolute file path in the `文件落盘` section.

## Hard Rules

1. Never invent unknown node keys when template/source defines concrete keys.
2. `nodeId` must be unique across the workflow.
3. Every edge `source/target` must exist.
4. Normal edges must use `{nodeId}-source-right` -> `{nodeId}-target-left`.
5. `ifElseNode` branch edges must use `IF / ELSE IF N / ELSE` source handles.
6. For `answerNode`, input key must be `text`.
7. For designated final reply content in `answerNode`, use the sample-compatible complete input config:
   - `key: "text"`
   - `renderTypeList: ["textarea", "reference"]`
   - `valueType: "any"`
   - `required: true`
   - `isRichText: false`
   - `maxLength: 100000`
   - `label: "回复内容"` or equivalent localized label
   - `value: "{{$nodeId.outputKey$}}"`
   - Do not use array style (`["nodeId", "outputKey"]`) for `answerNode.text` unless user explicitly asks for it.
8. If workflow depends on chat file upload, enable:
   - `chatConfig.fileSelectConfig.canSelectFile = true`
9. If using chat-upload files, route through `workflowStart.userFiles` and parsing node (`readFiles`) before downstream AI extraction/evaluation.
10. Default workflow skeleton must include both:
   - one `workflowStart` node
   - one system config node (`flowNodeType: "userGuide"`)
11. `chatConfig.welcomeText` must use Markdown format by default:
   - include a top-level Chinese title (`# ...`)
   - use sections such as `## 使用方式`, `## 示例`, and `## 提醒` when suitable
   - provide 1-3 realistic Chinese example inputs
   - include upload/file/attachment reminders when the workflow supports files
   - avoid a dense single-line plain-text opening
12. Default generation target is "production-usable enriched workflow", not "minimum runnable demo".
13. Unless user explicitly asks for a minimal demo, include:
   - explicit error/fallback handling path
   - at least one structured intermediate output field for downstream reference
14. Every `chatNode` must include at least one configured non-empty input among `quoteQA`, `fileUrlList`, and `userChatInput`; otherwise the JSON is invalid.
15. Node layout must satisfy spacing constraints:
   - connected nodes: `abs(target.position.x - source.position.x) >= 1500`
   - sibling branch nodes: `abs(nodeA.position.y - nodeB.position.y) >= 1000`
16. All file reads and writes must use UTF-8 encoding:
   - read samples/reference JSON as UTF-8
   - write generated JSON/Markdown as UTF-8
   - do not emit or preserve mojibake text in generated output
17. All user-facing node configuration text must be Chinese:
   - node `name`
   - input/output `label`, `description`, `toolDescription`, `debugLabel`
   - form field labels/options/descriptions
   - system prompts, user prompts, welcome text, instructions, answer labels
   - variable display names and business field names
   - technical keys such as `nodeId`, `key`, `flowNodeType`, and handle names must remain schema-compatible and may stay English
18. Required user-provided data must be collected through configuration, not prompt-only instructions:
   - required text/number/select/switch/object inputs must use system config global variables or `formInput` fields
   - required files must use `workflowStart.userFiles`, `chatConfig.fileSelectConfig.canSelectFile = true`, and a downstream file parsing/reference path when needed
   - prompts may explain how data is used, but must not be the only place where required inputs are requested
   - every required input must include explicit Chinese input guidance
19. User-adjustable parameters must include editable metadata:
   - for environment variables, numeric inputs, and threshold-like fields, do not generate `value`
   - only configure `defaultValue`, `min`, and `max` when the schema supports them
   - do not configure `step`
   - parameter descriptions must explain the meaning of the threshold/range in Chinese
20. File-derived business logic must use parsed outputs:
   - if a workflow asks the user to upload files and downstream nodes need the document content, connect `workflowStart.userFiles` to `readFiles`
   - downstream `chatNode`, `ifElseNode`, and `answerNode` references should use parsed outputs such as `readFiles.system_text` or upstream extracted text fields, not the raw file array
21. `ifElseNode` conditions must be fully configured:
   - every rule item must include `variable`, `condition`, and `value` when the selected operator compares against an input
   - do not generate `ifElseNode` entries that only reference a variable without an operator or comparison value
22. Knowledge-base retrieval configuration must be source-aligned:
   - if using `datasetSearchNode`, configure `datasetSelectList` and `userChatInput` explicitly
   - unknown knowledge-base IDs must use 24-character numeric placeholders such as `000000000000000000000001`; do not use Chinese text, knowledge-base names, or descriptive words as `datasetId`
   - if downstream AI uses retrieval results, `quoteQA` must reference a valid `datasetQuote` output such as `datasetQuoteQA`
   - do not use `quoteQA` as a fake placeholder without an actual retrieval source
   - use `datasetConcatNode` when multiple dataset retrieval outputs need to be merged before downstream reference
23. Knowledge-base workflows must use strict explicit retrieval by default:
   - if the requirement mentions knowledge base, RAG, document retrieval, policy lookup, FAQ retrieval, or资料库问答, prefer `datasetSearchNode`
   - if two or more retrieval branches exist, prefer `datasetConcatNode` before downstream AI usage
   - do not default to inline dataset config on `chatNode` / `agent` unless the user explicitly requests it

24. Question-classification workflows must use strict explicit classification by default:
   - if the requirement mentions intent routing, FAQ routing, ticket dispatch, shunting, issue categorization, or problem classification, prefer `classifyQuestion`
   - do not replace structured classification with ad hoc `chatNode` free-text output plus downstream string matching unless the user explicitly requests that simpler design
   - `agents` must be non-empty, keys must be stable and unique, and values must be Chinese category labels/descriptions
   - when routing is required, generated edges must align to the category keys represented by the classification handles
25. Requirement decomposition and node selection must be explicit:
   - first split the requirement into stages such as required input collection, file parsing, retrieval, deterministic transformation, model reasoning, routing, state update, human interaction, and final reply
   - then choose the most specific matching node for each stage
   - do not collapse a multi-stage workflow into a single `chatNode`
   - do not use general-purpose nodes when a dedicated node exists and fits the task
26. Node-specific source-aligned strictness is mandatory:
   - `chatNode` is for open-ended reasoning and must not replace extraction/classification/template assembly/final fixed reply
   - `contentExtract` is mandatory for structured extraction requirements unless the user explicitly asks for free-text extraction
   - `userSelect` is mandatory for explicit human option selection requirements
   - `formInput` is mandatory for structured required user fields
   - `textEditor` is preferred for deterministic text concatenation/template assembly
   - `httpRequest468` is preferred for standard external HTTP calls
   - `variableUpdate` is preferred for simple state mutation
   - `loop` is mandatory for real batch/per-item execution over arrays
   - `cfr` is preferred for explicit problem/query optimization before retrieval
   - `lafModule` is only valid for Laf-specific integrations
   - `customFeedback` is only valid for actual feedback collection
27. Reject under-configured nodes:
   - do not emit nodes with placeholder-only inputs
   - do not emit `httpRequest468` without URL/method/timeout semantics
   - do not emit `contentExtract` without filling the default `content` input and explicit `extractKeys`
   - do not emit `userSelect` with empty options
   - do not emit `formInput` with missing field definitions
   - do not emit `variableUpdate` with incomplete variable/value pairs
   - do not emit `loop` without a valid array input and aggregation path
28. Generated JSON must be saved to a `.json` file by default:
   - save using UTF-8 encoding
   - use the user-provided target path when available
   - otherwise derive a concise kebab-case filename from the workflow purpose
   - do not stop at only printing JSON in chat unless the user explicitly requests no file write
   - always include the saved absolute path in the final response
29. Field-level runtime contracts are mandatory:
   - `textEditor` must put actual concat text and template references into `system_textareaInput.value`
   - `contentExtract` must put the extraction source into the default `content.value`
   - question optimization must use `flowNodeType: "cfr"` and output `system_text`
   - `readFiles` parsed text output is `system_text`, not `text`
   - `tools` is the runtime `flowNodeType` for tool call, not `toolCall`
   - `userGuide` is the runtime `flowNodeType` for system config, not `systemConfig`
   - never create replacement custom inputs for a value that belongs to a source-defined input key
30. All nodes must follow the complete runtime template coverage in `references/json-config-runtime-reference.md`:
   - fixed-template nodes must use the exact runtime `flowNodeType`, input keys, and output keys from source
   - dynamic contract nodes (`appModule`, `pluginModule`, `tool`, `toolSet`, `toolParams`, `pluginInput`, `pluginOutput`) must not be generated unless the concrete target contract is known
   - do not invent dynamic inputs, outputs, or `toolConfig`
   - `agent` requires real planning/tool/skill/dataset orchestration context; otherwise use `chatNode`
   - `emptyNode`, `comment`, `stopTool`, and deprecated `app` must not be used in normal production workflows unless explicitly required by the user scenario

## Protocol Export

When user asks to "export with skill protocol", output a fenced block with `fastgpt-json-skill-protocol/v1` using schema in `references/protocol-v1.md`.

## Output Style

Default output sections:

1. `需求确认` (assumptions + confirmation points)
2. `生成结果` (JSON)
3. `验证报告` (checklist pass/fail + risk notes)
4. `文件落盘` (saved absolute path by default)
