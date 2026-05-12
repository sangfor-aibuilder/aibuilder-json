# Node Selection and Configuration Rules

Use this reference to decide which node type should be selected after requirement decomposition.

The workflow generator must first split the user requirement into:

- user inputs
- external resources
- deterministic transforms
- model reasoning tasks
- human interaction checkpoints
- routing / branching logic
- state updates
- final response

Do not map the whole requirement directly into one `chatNode`.

## 1. Global Selection Strategy

Apply these rules in order:

1. Identify every required user input and model it as `workflowStart`, `formInput`, `userSelect`, or system config global variable.
2. If the input is a file and downstream logic needs content, use `readFiles` before any text reasoning node.
3. If the task is deterministic transformation, use deterministic nodes first:
   - `textEditor`
   - `variableUpdate`
   - `httpRequest468`
   - `lafModule`
   - `code`
4. Use `chatNode`, `contentExtract`, `classifyQuestion`, or `cfr` only for genuine model reasoning tasks.
5. Use `ifElseNode` only for explicit rule branching with complete conditions.
6. Use `loop` only when the same subflow must run over an array input.
7. Use `answerNode` only as the final designated reply node, not as a substitute for intermediate processing.

Default principle:

- choose the simplest node that fully matches the business task
- do not use a more general node when a more specific node exists

Examples:

- structured field extraction -> `contentExtract`, not `chatNode` free-text output
- explicit user option selection -> `userSelect`, not `chatNode` or `ifElseNode`
- structured required user form -> `formInput`, not `systemPrompt`
- deterministic string assembly -> `textEditor`, not `chatNode`
- document content reasoning -> `readFiles` + downstream text node, not raw file array
- external API call -> `httpRequest468`, not `chatNode`
- variable/state mutation -> `variableUpdate`, not `chatNode`
- batch item processing -> `loop`, not duplicated node chains

## 2. AI 对话节点 `chatNode`

Use when:

- the workflow needs open-ended reasoning, generation, summarization, scoring explanation, or decision rationale
- the output is not limited to a fixed schema or a small set of classes

Must include:

- `model`
- `systemPrompt`
- `history`
- at least one business input among:
  - `userChatInput`
  - `fileUrlList`
  - `quoteQA`

Strict rules:

- `systemPrompt` alone is invalid
- if the node reasons over document content, prefer parsed text from `readFiles.system_text` or upstream extracted fields
- if retrieval is required, `quoteQA` must reference a real retrieval output
- if file references are used, the node must actually need file-aware input; otherwise prefer parsed text

Do not use when:

- the task is structured extraction with explicit output keys -> use `contentExtract`
- the task is intent/category routing -> use `classifyQuestion`
- the task is deterministic text assembly -> use `textEditor`
- the task is direct final fixed reply with no model reasoning -> use `answerNode`

## 3. 文本内容提取节点 `contentExtract`

Use when:

- the task is to extract structured fields from a text body
- the user requirement mentions extracting resume fields, invoice fields, contract clauses, entities, attributes, or other named items

Must include:

- `model`
- `description`
- `history`
- `content`
- `extractKeys`

Strict rules:

- `extractKeys` must be a non-empty explicit field list
- extracted field names and descriptions must be Chinese
- the extraction input must be configured in the default `content` input
- the extraction input must be the actual text to parse, usually `readFiles.system_text`, `cfr.system_text`, or another upstream text output
- do not use raw file arrays as the extraction input
- do not create a replacement custom field for the main extraction text

Do not use when:

- the task is free-form answer generation -> use `chatNode`
- the task is explicit routing/classification -> use `classifyQuestion`

## 4. 工具调用节点 `tools`

Use when:

- the business task requires agent-style tool orchestration
- the model must decide whether to call configured tools or run tool-enhanced reasoning

Must include:

- `model`
- `systemPrompt`
- `history`
- at least one business input among `userChatInput`, `fileUrlList`
- `useAgentSandbox` must be explicitly considered

Strict rules:

- only use when real tool capability is part of the requirement
- generated JSON must use `flowNodeType: "tools"`
- never use `flowNodeType: "toolCall"`
- do not replace a plain `chatNode` with `tools` unless tool invocation is actually needed
- file-driven tasks still require correct parsing/input planning

Do not use when:

- the requirement is simple Q&A or summarization with no tool need
- deterministic HTTP call or Laf call is enough

## 5. 用户选择节点 `userSelect`

Use when:

- the workflow requires the user to choose one explicit option before downstream routing
- the choice is interactive and should not be inferred by the model

Must include:

- `description`
- `userSelectOptions`

Strict rules:

- `userSelectOptions` must be non-empty
- every option must have stable `key` and Chinese `value`
- if downstream routing depends on the choice, the branch logic must map to those keys
- do not make the model guess a user preference that should be selected explicitly

Do not use when:

- the value is a structured form field -> use `formInput`
- the value should be inferred from user text -> use `classifyQuestion` or `chatNode`

## 6. 表单输入节点 `formInput`

Use when:

- the workflow needs required structured user inputs such as text, number, select, switch, object, or date-like fields
- the requirement includes multiple explicit fields

Must include:

- `description`
- `userInputForms`

Strict rules:

- every required business field must be explicitly modeled in `userInputForms`
- field labels, descriptions, placeholders, and options must be Chinese
- adjustable numeric inputs must not use `value` or `step`
- numeric/config fields should use `defaultValue`, `min`, and `max` when supported
- do not ask users to type required values only through prompts

Do not use when:

- the workflow only needs a single chat message already covered by `workflowStart.userChatInput`
- the interaction is a forced discrete option choice -> `userSelect` may be better

## 7. 文本拼接节点 `textEditor`

Use when:

- the task is deterministic text assembly, formatting, prompt template stitching, or fixed wrapper generation

Must include:

- `system_textareaInput`

Strict rules:

- use upstream references plus deterministic template text
- put the complete concatenation template and all variable references in `system_textareaInput.value`
- do not configure only a separate context/custom input while leaving `system_textareaInput` empty
- prefer this node over `chatNode` for stable string composition
- if the output becomes a prompt for downstream AI, assemble it here first when that improves clarity or reuse

Do not use when:

- the node is expected to reason, extract, or classify

## 8. 指定回复节点 `answerNode`

Use when:

- the workflow needs the final designated user reply

Must include:

- input key `text`
- sample-compatible full input shape
- `value` using template reference `{{$nodeId.outputKey$}}` by default

Strict rules:

- final content must come from upstream structured output or finalized text
- do not use `answerNode` as an intermediate storage node
- if the reply is branch-specific, each branch may have its own `answerNode`

## 9. 文档解析节点 `readFiles`

Use when:

- the user uploads files and downstream logic needs document text or parsed content

Must include:

- `fileUrlList`

Strict rules:

- `fileUrlList` must reference a real file array such as `workflowStart.userFiles`
- downstream text reasoning should use `readFiles.system_text`
- keep `rawResponse` available when later nodes need file parsing metadata

Do not use when:

- the workflow does not consume uploaded files

## 10. HTTP 请求节点 `httpRequest468`

Use when:

- the workflow must call an external HTTP API
- the requirement mentions webhook, REST API, third-party service, or remote system query

Must include:

- `httpMethod`
- `httpTimeout`
- `httpReqUrl`
- headers/body/query inputs as required by the API contract

Strict rules:

- do not use this node with an empty URL or half-configured request body
- timeouts and numeric request controls must use editable bounds/defaults where supported by the schema
- dynamic outputs must be mapped if downstream nodes consume specific fields
- prefer this node over `code` for ordinary API requests

Do not use when:

- only local deterministic transformation is needed
- Laf function integration is explicitly required -> use `lafModule`

## 11. 判断器节点 `ifElseNode`

Use when:

- the workflow requires explicit branch rules based on thresholds, status, flags, extracted fields, or model outputs

Must include:

- complete condition tuples for every branch rule

Strict rules:

- every condition item must include `variable`
- every condition item must include `condition`
- every operator that needs comparison input must include `value`
- branch labels and downstream semantics must be Chinese
- do not use `ifElseNode` for user choice collection; use `userSelect`
- do not use `ifElseNode` to emulate classification when `classifyQuestion` is the correct node

## 12. 变量更新节点 `variableUpdate`

Use when:

- the workflow needs to overwrite or assign global variables or prior node output aliases
- a later node requires normalized state values

Must include:

- `updateList`

Strict rules:

- every update item must specify target `variable` and source/value
- updated variable names and business descriptions must be Chinese where user-facing
- prefer this node over `code` for simple state assignment or value rewriting

Do not use when:

- the task is more naturally handled by `textEditor`, `httpRequest468`, or `code`

## 13. 代码运行节点 `code`

Use when:

- deterministic transformation is required but cannot be expressed cleanly through existing nodes
- the workflow needs structured data reshaping, custom parsing, merging, or calculation

Must include:

- explicit dynamic inputs
- `codeType`
- `code`

Strict rules:

- use only after ruling out simpler nodes such as `textEditor`, `variableUpdate`, `httpRequest468`, or `lafModule`
- input names and output names must be meaningful and Chinese where user-facing labels are shown
- code must match the declared inputs/outputs
- do not use `code` to compensate for missing node design

## 14. 批量执行节点 `loop`

Use when:

- the same child flow must run for each element in an array
- the requirement explicitly includes batch processing, per-item evaluation, or iterative handling

Must include:

- `loopInputArray`
- child node list and loop container metadata
- a valid internal `loopStart` -> child flow -> `loopEnd` structure

Strict rules:

- do not fake batch processing with repeated copied branches
- `loopStart` provides the current item and index
- `loopEnd` must collect the per-item result
- downstream nodes consuming batch results should reference `loopArray`

## 15. 知识库搜索引用合并 `datasetSearchNode` + `datasetConcatNode`

Handled separately by `dataset-rules.md`.

## 16. 问题优化节点 `cfr`

Use when:

- the task requires rewriting, expanding, or optimizing the user question before retrieval or answering
- the requirement mentions query rewrite, search optimization, retrieval enhancement, synonym expansion, or query normalization

Must include:

- `model`
- `systemPrompt`
- `history`
- `userChatInput`

Strict rules:

- generated JSON must use `flowNodeType: "cfr"`
- never use `flowNodeType: "queryExtension"`
- use this node before `datasetSearchNode` when retrieval quality depends on query rewriting
- the optimized query output `system_text` should feed retrieval or downstream analysis directly
- do not use `chatNode` for query rewrite when this node fits

Do not use when:

- the original query is already the final answer target and no rewrite step is needed

## 17. Laf 函数调用节点 `lafModule`

Use when:

- the workflow explicitly integrates a Laf function endpoint
- the business side already exposes logic through Laf and the workflow should call it directly

Must include:

- `httpReqUrl`
- required dynamic inputs

Strict rules:

- do not substitute generic HTTP logic with `lafModule` unless the target is actually a Laf function
- prefer `lafModule` over `httpRequest468` only when the business contract is Laf-specific

## 18. 自定义反馈节点 `customFeedback`

Use when:

- the workflow must collect a human feedback message after result delivery or at a checkpoint

Must include:

- `system_textareaInput`

Strict rules:

- feedback purpose and text guidance must be Chinese and explicit
- feedback text must be configured in `system_textareaInput.value`
- do not use this node as a generic reply node
- place it only where the workflow truly requires feedback capture

## 19. Strong Prohibitions

The generator must reject these patterns:

- using one `chatNode` to replace extraction, classification, routing, text assembly, and final answer all at once
- asking for required user inputs only through prompt text
- sending raw uploaded files into text-only reasoning when parsed text is required
- creating `ifElseNode` rules without complete condition tuples
- using `answerNode` to hold intermediate values
- using `code` when a dedicated node can solve the task cleanly
- using `tools` without an actual tool-use requirement
- using `queryExtension` as a JSON `flowNodeType`; use `cfr`
- leaving `textEditor.system_textareaInput` empty
- leaving `contentExtract.content` empty while filling an invented extraction input
