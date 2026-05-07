# FastGPT JSON Generation Hard Rules

These rules override older examples when generating import-ready workflow JSON.

## 1. chatNode Business Input

Every `chatNode` must include at least one effective business data input. A `chatNode` with only `systemPrompt` is invalid.

At least one of these inputs must be configured with a non-empty value:

- `userChatInput.value`: reference `workflowStart.userChatInput`, parsed file text, form output, or upstream AI output.
- `fileUrlList.value`: reference `workflowStart.userFiles` or another file array output.
- `quoteQA.value`: explicit dataset quote configuration for knowledge-base retrieval.

Recommended file workflow:

```json
{
  "key": "fileUrlList",
  "renderTypeList": ["reference", "input"],
  "label": "文件",
  "valueType": "arrayString",
  "value": ["workflowStart-xxx", "userFiles"]
}
```

Recommended text workflow:

```json
{
  "key": "userChatInput",
  "renderTypeList": ["reference", "textarea"],
  "label": "用户输入",
  "toolDescription": "用户问题",
  "valueType": "string",
  "required": true,
  "value": ["readFiles-xxx", "system_text"]
}
```

If the user uploads files and downstream logic needs document content, parse files first and reference the parsed text output instead of the raw file array.

Correct pattern:

```json
{
  "file_parser": ["workflowStart-xxx", "userFiles"],
  "chat_input": ["readFiles-xxx", "system_text"]
}
```

Invalid pattern for text reasoning:

```json
{
  "chat_input": ["workflowStart-xxx", "userFiles"]
}
```

## 2. answerNode Text Input

`answerNode` must use the sample-compatible `text` input shape.

```json
{
  "key": "text",
  "renderTypeList": ["textarea", "reference"],
  "valueType": "any",
  "required": true,
  "isRichText": false,
  "maxLength": 100000,
  "label": "回复内容",
  "value": "{{$chatNode-xxx.answerText$}}"
}
```

Use template variable style for `answerNode.text.value` by default. Do not use array style such as `["chatNode-xxx", "answerText"]` unless the user explicitly requests it.

## 3. Canvas Layout Spacing

Generated node positions must use large spacing for readability.

- Connected nodes must have x spacing >= `1500`.
- Branch or sibling nodes must have y spacing >= `1000`.
- Prefer column x positions such as `0`, `1500`, `3000`, `4500`, `6000`.
- Prefer branch y positions such as `-1000`, `0`, `1000`, `2000`.

Example:

```json
[
  { "nodeId": "workflowStart-001", "position": { "x": 0, "y": 0 } },
  { "nodeId": "readFiles-001", "position": { "x": 1500, "y": 0 } },
  { "nodeId": "chatNode-001", "position": { "x": 3000, "y": 0 } },
  { "nodeId": "answerNode-pass-001", "position": { "x": 4500, "y": -1000 } },
  { "nodeId": "answerNode-fail-001", "position": { "x": 4500, "y": 1000 } }
]
```

## 4. UTF-8 File Encoding

All reads and writes must use UTF-8.

- Read user-provided samples, reference JSON, and imported workflow files as UTF-8.
- Write generated JSON, Markdown, and protocol exports as UTF-8.
- Do not preserve mojibake in generated output. If a referenced sample appears garbled, infer structure only and regenerate human-facing labels/prompts as clean UTF-8 text.
- If a source file cannot be safely decoded as UTF-8, do not rewrite it in-place unless the user explicitly asks for encoding repair.

## 5. Chinese User-Facing Text

All user-facing text in generated node configuration must be Chinese.

This includes:

- Node `name`.
- Input/output `label`, `description`, `toolDescription`, and `debugLabel`.
- Form field labels, option labels, descriptions, and help text.
- `systemPrompt`, user-facing prompt text, `welcomeText`, `instruction`, and answer labels.
- Variable display names and business field names.

Schema-required technical identifiers must remain compatible with FastGPT and may stay English:

- `nodeId`
- `key`
- `flowNodeType`
- source/target handle names
- enum values required by the platform

Do not output English placeholder labels such as `User input`, `Files`, or `Reply content`; use Chinese equivalents such as `用户输入`, `文件`, and `回复内容`.

## 6. Default JSON File Save

Generated FastGPT workflow JSON must be saved to disk by default.

- Save the final import-ready JSON as a `.json` file.
- Use UTF-8 encoding for the write.
- If the user provides a target file path, use it.
- If no target path is provided, derive a concise kebab-case filename from the workflow purpose, for example `hr-resume-screening.json`.
- Save in the current workspace or the closest relevant project/sample directory.
- Do not only print JSON in chat unless the user explicitly requests no file write.
- The final response must include the saved absolute path.

## 7. Markdown Welcome Text

`chatConfig.welcomeText` must use Markdown format by default.

Rules:

- Start with a Chinese top-level heading such as `# 企业智能报销助手`.
- Use short sections such as `## 你可以这样使用`, `## 示例`, and `## 提醒` when suitable.
- Include the app purpose and supported usage modes.
- Include 1-3 realistic Chinese example inputs, preferably using blockquote syntax.
- Include upload, file, attachment, or required-input reminders when the workflow supports those capabilities.
- Mention fallback or verification notes when the workflow may produce draft results, require review, or depend on knowledge-base coverage.
- Do not generate a dense single-line plain-text welcome unless the user explicitly requests minimal/plain text.

Example:

```json
{
  "chatConfig": {
    "welcomeText": "# 企业智能报销助手\n\n我可以帮你生成报销单、识别发票，并基于公司报销政策回答问题。\n\n## 你可以这样使用\n\n### 1. 直接生成报销单\n直接描述行程或费用事项即可生成报销单草稿。\n\n**示例：**\n> 我4月9日到12日到北京出差，请帮我生成报销单。\n\n## 提醒\n- 未上传发票时，也可以先生成草稿。\n- 正式提交前，请补充合规发票和相关附件。"
  }
}
```
