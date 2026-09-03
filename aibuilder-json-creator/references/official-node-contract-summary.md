# Official Node Contract Summary

Source: `official-default-node-templates.json`. Use the JSON file for full default field shapes. This summary is for quick input/output key lookup.

| Node type | Inputs | Outputs |
|---|---|---|
| `userGuide` | `welcomeText`, `variables`, `questionGuide`, `tts`, `whisper`, `scheduleTrigger` | none |
| `workflowStart` | `userChatInput` | `userChatInput` |
| `chatNode` | `model`, `temperature`, `maxToken`, `isResponseAnswerText`, `aiChatQuoteRole`, `quoteTemplate`, `quotePrompt`, `aiChatVision`, `aiChatReasoning`, `aiChatTopP`, `aiChatStopSign`, `aiChatResponseFormat`, `aiChatJsonSchema`, `systemPrompt`, `history`, `quoteQA`, `fileUrlList`, `userChatInput` | `history`, `answerText`, `reasoningText`, `system_error_text` |
| `datasetSearchNode` | `datasets`, `similarity`, `limit`, `searchMode`, `embeddingWeight`, `usingReRank`, `rerankModel`, `rerankMethod`, `rerankWeight`, `datasetSearchUsingExtensionQuery`, `datasetSearchExtensionModel`, `datasetSearchExtensionBg`, `authTmbId`, `userChatInput`, `collectionFilterMatch`, `generateSqlModel`, `retrievalMode`, `agenticSearchLLMModel`, `agenticSearchRerankModel`, `agenticSearchReasoning` | `quoteQA`, `system_error_text` |
| `classifyQuestion` | `model`, `systemPrompt`, `history`, `userChatInput`, `agents` | `cqResult` |
| `contentExtract` | `model`, `description`, `history`, `content`, `extractKeys` | `success`, `fields`, `system_error_text` |
| `tools` | `model`, `temperature`, `maxToken`, `isResponseAnswerText`, `aiChatVision`, `aiChatReasoning`, `aiChatTopP`, `aiChatStopSign`, `aiChatResponseFormat`, `aiChatJsonSchema`, `systemPrompt`, `history`, `fileUrlList`, `userChatInput` | `answerText`, `system_error_text` |
| `stopTool` | none | none |
| `userSelect` | `description`, `userSelectOptions` | `selectResult` |
| `formInput` | `description`, `userInputForms` | `formInputResult` |
| `textEditor` | `system_textareaInput` | `system_text` |
| `answerNode` | `text` | none |
| `readFiles` | `fileUrlList` | `system_text`, `system_rawResponse`, `system_error_text` |
| `httpRequest468` | `system_addInputParam`, `system_httpMethod`, `system_httpTimeout`, `system_httpReqUrl`, `system_header_secret`, `system_httpHeader`, `system_httpParams`, `system_httpJsonBody`, `system_httpFormBody`, `system_httpContentType` | `system_addOutputParam`, `httpRawResponse`, `error` |
| `ifElseNode` | `ifElseList` | `ifElseResult` |
| `variableUpdate` | `updateList` | none |
| `code` | `system_addInputParam`, `data1`, `data2`, `codeType`, `code` | `system_addOutputParam`, `system_rawResponse`, `result`, `data2`, `error` |
| `loop` | `loopInputArray`, `childrenNodeIdList`, `nodeWidth`, `nodeHeight`, `loopNodeInputHeight` | `loopArray` |
| `loopStart` | `loopStartInput`, `loopStartIndex` | `loopStartIndex`, `loopStartInput` |
| `loopEnd` | `loopEndInput` | none |
| `datasetConcatNode` | `limit`, `system_datasetQuoteList` | `quoteQA` |
| `cfr` | `model`, `systemPrompt`, `history`, `userChatInput` | `system_text` |
| `customFeedback` | `system_textareaInput` | none |
| `lafModule` | `system_addInputParam`, `system_httpReqUrl` | `httpRawResponse`, `system_addOutputParam`, `system_error_text` |

## Rules

- Do not invent input keys outside this table for these node types.
- Do not invent output keys outside this table for these node types.
- Dynamic fields such as `system_addInputParam`, `system_addOutputParam`, and fields produced by custom dynamic configuration must still match the official default field mechanism.
- File upload workflows may require a runtime `workflowStart.userFiles` output even though the standalone official default node only lists `userChatInput`; add it only when `chatConfig.fileSelectConfig` enables the file channels matching the required file categories (documents `canSelectFile`, images `canSelectImg`, audio `canSelectAudio`, video `canSelectVideo`, custom extensions `canSelectCustomFileExtension` with non-empty `customFileExtensionList`) and the workflow actually consumes the uploads. `readFiles` parses text-bearing documents (`canSelectFile` required); images go to a vision-capable `chatNode`/`tools` via `fileUrlList` (see `references/file-format-rules.md`).
