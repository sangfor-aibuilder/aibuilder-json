# Required Input Rules

Required user-provided information must be collected through workflow configuration, not only through prompt instructions.

## Collection Mechanisms

Use these mechanisms:

- App-level required values: system config global variables.
- Structured required inputs: `formInput` node fields.
- Required file uploads: `workflowStart.userFiles` plus `chatConfig.fileSelectConfig` with at least one file channel switch matching the required file categories (documents `canSelectFile`, images `canSelectImg`, audio `canSelectAudio`, video `canSelectVideo`, custom extensions `canSelectCustomFileExtension` with non-empty `customFileExtensionList`; see `references/file-format-rules.md`).
- Parsed file content: `readFiles.fileUrlList` references `workflowStart.userFiles`, then downstream nodes reference `readFiles.system_text`; images are understood by a vision-capable `chatNode`/`tools` through `fileUrlList`, not by `readFiles`.

Do not rely only on `systemPrompt`, `welcomeText`, node descriptions, or answer text to tell the user to provide required data.

## Required Guidance

Every required input must include clear Chinese guidance:

- `label`: concise Chinese field name.
- `description` or help text: what to enter and expected format.
- `required: true` where the platform supports it.
- default value, range, enum options, or placeholder where useful.

## Adjustable Parameters

For adjustable parameters and thresholds, do not generate `value`.

- Numeric inputs, score thresholds, year limits, confidence thresholds, and similar fields must include editable metadata such as `defaultValue`, `min`, and `max` when the schema supports them.
- Do not generate `step` for adjustable parameters.
- Environment/config variables that users may tune after import must expose default value and allowed range/options instead of a fixed value only.
- Parameter descriptions must explain the meaning of the threshold and how to adjust it in Chinese.

## Example Form Field

```json
{
  "type": "textarea",
  "key": "job_description",
  "label": "<Chinese label>",
  "description": "<Chinese guidance for what to enter>",
  "value": "",
  "valueType": "string",
  "required": true,
  "maxLength": 20000
}
```

## Example Numeric Threshold Field

```json
{
  "type": "numberInput",
  "key": "min_years_experience",
  "label": "<Chinese label>",
  "description": "<Chinese description explaining this threshold>",
  "defaultValue": 3,
  "valueType": "number",
  "required": true,
  "min": 0,
  "max": 40
}
```

## Invalid Pattern

Do not only write this in a prompt:

```text
Ask the user to provide the required job description and resume.
```

Instead, create actual `formInput` fields for text data and file-upload configuration for resume files.
