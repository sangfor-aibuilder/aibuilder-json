# Node Field Contracts

This file contains hard field-level rules for generated FastGPT workflow JSON.

It exists to prevent invalid workflows caused by placing values into invented inputs while leaving runtime-required default inputs empty.

## 1. No Invented Required Inputs

When a source template defines a concrete input key, generated JSON must configure that input key directly.

Never create an extra custom input to carry the same value if the template already has a required/default input.

Invalid pattern:

```json
{
  "inputs": [
    { "key": "context", "value": ["readFiles-001", "system_text"] },
    { "key": "content", "value": "" }
  ]
}
```

Valid pattern:

```json
{
  "inputs": [
    { "key": "content", "value": ["readFiles-001", "system_text"] }
  ]
}
```

## 2. Text Editor Must Fill `system_textareaInput`

The text concatenation node is `textEditor`.

Runtime contract:

- `flowNodeType`: `textEditor`
- required input key: `system_textareaInput`
- output key: `system_text`

Rules:

- Put the actual concat template in `system_textareaInput.value`.
- Include all variable references inside that text body.
- Do not put references only in a separate context or custom input.
- If `system_textareaInput.value` is empty, the node is invalid.

Example:

```json
{
  "flowNodeType": "textEditor",
  "inputs": [
    {
      "key": "system_textareaInput",
      "renderTypeList": ["textarea"],
      "valueType": "string",
      "required": true,
      "label": "拼接文本",
      "value": "请根据以下信息生成报告：\n\n用户问题：{{$workflowStart-001.userChatInput$}}\n解析内容：{{$readFiles-001.system_text$}}"
    }
  ],
  "outputs": [
    {
      "id": "system_text",
      "key": "system_text",
      "type": "static",
      "valueType": "string",
      "label": "拼接结果"
    }
  ]
}
```

## 3. Content Extract Must Fill `content`

The text content extraction node is `contentExtract`.

Runtime contract:

- `flowNodeType`: `contentExtract`
- required text input key: `content`
- extraction config key: `extractKeys`
- success output key: `success`
- fields output key: `fields`

Rules:

- The default "需要提取的文本" field is `content`.
- Put the source text reference in `content.value`.
- Do not create custom fields such as `extractText`, `inputText`, `context`, or `documentText` for the main extraction text.
- `extractKeys.value` must be non-empty.

Example:

```json
{
  "flowNodeType": "contentExtract",
  "inputs": [
    {
      "key": "content",
      "renderTypeList": ["reference", "textarea"],
      "label": "需要提取的文本",
      "required": true,
      "valueType": "string",
      "value": ["readFiles-001", "system_text"]
    },
    {
      "key": "extractKeys",
      "renderTypeList": ["custom"],
      "label": "",
      "valueType": "any",
      "value": [
        {
          "key": "姓名",
          "desc": "候选人姓名",
          "valueType": "string",
          "required": true
        }
      ]
    }
  ]
}
```

## 4. Query Extension Must Use `cfr`

The question optimization node is named query extension in source code, but its runtime `flowNodeType` is `cfr`.

Runtime contract:

- `flowNodeType`: `cfr`
- inputs: `model`, `systemPrompt`, `history`, `userChatInput`
- output: `system_text`

Rules:

- Always generate `"flowNodeType": "cfr"` for question optimization.
- Never generate `"flowNodeType": "queryExtension"`.
- Downstream query consumers must reference `["nodeId", "system_text"]`.

## 5. Read Files Output Must Use `system_text`

Runtime contract:

- `flowNodeType`: `readFiles`
- input: `fileUrlList`
- parsed text output: `system_text`
- raw parse output: `system_rawResponse`

Rules:

- Use `["readFilesNodeId", "system_text"]` for downstream text extraction, classification, judging, and answering.
- Do not use `readFiles.text`; it is not the runtime output key.

## 6. Answer Node Input Must Use `text`

Runtime contract:

- `flowNodeType`: `answerNode`
- input: `text`

Rules:

- Do not use input key `answerText`.
- Use full answer input shape and template reference style by default.

## 7. Tool Call Must Use `tools`

Runtime contract:

- `flowNodeType`: `tools`

Rules:

- Never generate `"flowNodeType": "toolCall"`.

## 8. System Config Must Use `userGuide`

Runtime contract:

- `flowNodeType`: `userGuide`

Rules:

- Never generate `"flowNodeType": "systemConfig"`.

## 9. Form Input Fields Must Stay Inside `userInputForms`

Runtime contract:

- `flowNodeType`: `formInput`
- form definitions input key: `userInputForms`
- output: `formInputResult`

Rules:

- Put field definitions inside `userInputForms.value`.
- Do not add separate sibling node inputs for each form field.

## 10. User Select Options Must Stay Inside `userSelectOptions`

Runtime contract:

- `flowNodeType`: `userSelect`
- options input key: `userSelectOptions`
- output: `selectResult`

Rules:

- Put options inside `userSelectOptions.value`.
- Do not add custom option inputs.

## 11. Dynamic Contract Nodes Need Real Contracts

These nodes have dynamic inputs/outputs and must not be generated with invented schemas:

- `appModule`
- `pluginModule`
- `tool`
- `toolSet`
- `toolParams`
- `pluginInput`
- `pluginOutput`

Rules:

- Use them only when the user provides a concrete app/plugin/tool contract or target metadata.
- Do not guess dynamic input keys.
- Do not guess dynamic output keys.
- For `tool` and `toolSet`, include valid `toolConfig`.
- For plugin workflows, define meaningful `pluginInput` and `pluginOutput` fields according to the plugin contract.

## 12. Agent Requires Real Orchestration Context

The `agent` node is not a plain chat node.

Rules:

- Use `agent` only when planning, tool use, skill use, or agentic orchestration is required.
- If no tool/skill/dataset context is configured, prefer `chatNode`.
- `skills`, `agent_selectedTools`, and `datasets` must reference real configured resources when used.

## 13. Placeholder and Annotation Nodes

Rules:

- `emptyNode` is for placeholder/import compatibility only; do not use in production workflows by default.
- `comment` is for canvas notes only; it must not participate in runtime logic.
- `stopTool` is only for terminating tool execution; it is not a final answer node.

## 14. Deprecated Nodes

Rules:

- `app` is a legacy abandoned app-call node.
- Do not use `app` unless the user explicitly requests legacy compatibility.
- Prefer modern dynamic app calls only with a real `appModule` target contract.
