# Multi-Format File Support Rules

This reference defines how to model workflows that let users upload and process files in multiple formats and categories. Load it whenever the requirement mentions uploading, reading, recognizing, or converting user files (documents, images, audio, video, or custom file extensions).

Field-level authority: `official-default-node-templates.json` (node IO) and `json-config-specification.md` sections 6.1/6.2 (`fileSelectConfig` switches). Do not invent keys outside those two sources.

## 1. File Categories And Channels

A workflow collects every user-uploaded file through one runtime output: `workflowStart.userFiles` (add it to `workflowStart.outputs` only when the workflow needs chat file upload). Which file categories the chat input accepts is decided separately by the root `chatConfig.fileSelectConfig` switches. Each category maps to a distinct processing channel.

| Category | Common extensions (examples) | fileSelectConfig switch | Processing channel | Consume |
|---|---|---|---|---|
| Documents (text-parsable) | `.txt`, `.md`, `.csv`, `.pdf`, `.doc`/`.docx`, `.xls`/`.xlsx`, `.html` | `canSelectFile: true` | `readFiles` (文档解析) parses the document text | downstream uses `readFiles.system_text` |
| Images | `.png`, `.jpg`/`.jpeg`, `.gif`, `.webp`, `.bmp` | `canSelectImg: true` | vision-capable model node (`chatNode`/`tools` with a multimodal model), `fileUrlList` references `userFiles` | the vision `chatNode` reads image URLs from `fileUrlList` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` | `canSelectAudio: true` | only when the requirement names a real speech/audio tool or a multimodal audio model; otherwise open the upload channel only and let the AI chat node handle it | do not fabricate a system node for audio transcription |
| Video | `.mp4`, `.webm`, `.mov`, `.mkv`, `.avi` | `canSelectVideo: true` | only when the requirement names a real video tool or multimodal video model; otherwise open the upload channel only | do not fabricate a system node for video understanding |
| Custom extensions | platform types not opened by the switches above: e.g. `.eml`, `.log`, `.sql`, `.ipynb`, `.xml`, `.jsonl` | `canSelectCustomFileExtension: true` + `customFileExtensionList: [".eml", ".log", ...]` | depends on the category: text-extractable custom documents go through `readFiles`; others follow the image/audio/video rules | same as the category they belong to |

Whether a specific document format is text-extractable at runtime is decided by the FastGPT platform's parser, not by this skill. The extension examples above are guidance for the generation conversation, not a runtime guarantee.

## 2. fileSelectConfig Rules (hard rules)

- Any workflow whose `workflowStart.outputs` includes `userFiles` must set `chatConfig.fileSelectConfig` to an object with **at least one file channel switch enabled**; the enabled switches must match the file categories the requirement asks the user to upload. Do not enable switches for categories the workflow never consumes.
- Required channel switches:
  - documents that must be parsed as text → `canSelectFile: true` and route through `readFiles`;
  - images that must be understood → `canSelectImg: true` and route to a vision-capable `chatNode`/`tools`;
  - audio → `canSelectAudio: true`;
  - video → `canSelectVideo: true`;
  - custom extensions → `canSelectCustomFileExtension: true` plus a non-empty `customFileExtensionList` whose items start with `.` and do not contain wildcards.
- Batch or multi-file upload requirements (上传多份/批量/一次上传多份简历…) → set `maxFiles` to a value greater than `1` (10 is a safe default; `1` is the sample default for single-file upload).
- `canLocalUpload` (default upload source) stays `true` unless the requirement restricts it; a requirement that mentions pasting/importing by URL additionally opens `canUrlUpload: true`.
- A pure-document channel does not require `canSelectImg`, and a pure-image workflow does not require `canSelectFile`. Do not copy the old one-switch default blindly.
- Do not add `userFiles` when no uploaded file is consumed anywhere in the workflow; do not open file channels when `userFiles` is absent.

## 3. Category Routing Decision Table

| Requirement shape | workflowStart | fileSelectConfig | Typical chain |
|---|---|---|---|
| "Upload a document (e.g. resume PDF) and summarize/QA/filter it" | + `userFiles` | `canSelectFile: true` (+ `maxFiles` when batch) | `workflowStart → readFiles → contentExtract → textEditor → chatNode → answerNode`; text consumers reference `readFiles.system_text` |
| "Upload images (screenshots/photos) and recognize/describe them" | + `userFiles` | `canSelectImg: true` | `workflowStart → chatNode` (multimodal model, `fileUrlList` references `userFiles`) `→ answerNode`; no `readFiles` |
| "Upload documents or images and let the AI understand them" | + `userFiles` | `canSelectFile: true`, `canSelectImg: true` | documents → `readFiles.system_text` chain; images → vision `chatNode.fileUrlList`. Make sure at least one `chatNode` consumes `system_text` and that a vision-capable model node receives `fileUrlList` |
| "Upload audio/video and transcribe or analyze it" | + `userFiles` | `canSelectAudio` / `canSelectVideo` | open the matching channel; only add a dedicated processing node when the requirement names a real tool or model that can consume audio/video |
| "Only allow uploading files with extension .eml/.log/..." | + `userFiles` | `canSelectCustomFileExtension: true` + list | follow the category rules above |

## 4. Channel Separation Rules

- `readFiles` is for text-bearing documents only. Its input `fileUrlList` must reference `["<workflowStartNodeId>", "userFiles"]`.
- Raw `userFiles` must never be consumed directly by text-reasoning nodes (contentExtract, classifyQuestion, chatNode prompt logic). Only `readFiles.system_text` carries parsed content.
- A vision-capable `chatNode`/`tools` node consumes uploaded images through its own `fileUrlList` input (official default value `[["<workflowStartNodeId>", "userFiles"]]`); pick a model that supports vision/multimodal input when image understanding is required.
- Never route images as the only input into `readFiles`, and never parse documents by feeding `system_text` back through `readFiles`.
- Keep `readFiles.system_text` as the single parsed-document source; do not generate extra outputs or reference `system_rawResponse` for business logic.

## 5. Validation

`scripts/validate_fastgpt_json.py` enforces the deterministic part:

- `workflowStart.userFiles` requires at least one enabled channel in `chatConfig.fileSelectConfig` (old rule required `canSelectFile` only).
- A `readFiles` node requires `canSelectFile: true`.
- `canSelectCustomFileExtension: true` requires a non-empty `customFileExtensionList`.

Copy-test the category routing with the samples under `samples/` (`multiformat-docs-images-workflow.json`, `image-only-workflow.json`) before reporting a workflow as import-ready.
