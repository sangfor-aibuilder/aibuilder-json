# Runtime Node Template Usage

This file is not an independent template source. For every node type that exists in `official-default-node-templates.json`, copy the official node object first, then fill scenario-specific values.

Priority:

1. `official-default-node-templates.json`
2. `official-node-contract-summary.md` for quick key lookup only
3. This file for scenario fill rules only

If this file conflicts with the official default JSON, the official default JSON wins.

## Copy Procedure

For each generated node:

1. Find the matching `flowNodeType` in `official-default-node-templates.json`.
2. Deep-copy the official node object.
3. Replace only:
   - `nodeId`
   - `name`
   - `position`
   - scenario-specific `inputs[].value`
   - scenario-specific dynamic input/output items when the official node exposes an add-field mechanism such as `system_addInputParam` or `system_addOutputParam`
4. Preserve official `inputs[].key`, `outputs[].key`, `renderTypeList`, `valueType`, labels, required flags, hidden fields, and dynamic system fields.
5. Do not replace an official full node with a hand-written minimal node.

## Workflow Skeleton

Every generated workflow must include:

- one `workflowStart`
- one `userGuide`
- at least one `answerNode`
- readable visual edges from start to final answer

`userGuide` must keep the official system config inputs:

- `welcomeText`
- `variables`
- `questionGuide`
- `tts`
- `whisper`
- `scheduleTrigger`

`workflowStart` official output is `userChatInput`. Add `userFiles` only when the workflow enables chat file upload and downstream file parsing needs it.

## Visual Edges Versus Data References

Edges are canvas execution/readability links. Input values are data bindings.

Do not create one direct edge for every data reference. If a downstream node consumes outputs from several previous nodes, the referenced nodes only need to be upstream on the same visual chain.

Valid pattern:

```text
workflowStart -> readFiles -> contentExtract -> textEditor -> chatNode -> answerNode
```

In that chain, `chatNode` may reference `workflowStart.userChatInput`, `readFiles.system_text`, `contentExtract.fields`, or `textEditor.system_text` as long as those nodes are upstream of `chatNode`. Do not add extra cross-links into `chatNode` unless the graph would otherwise not express the dependency order.

Normal edge handles:

```json
{
  "source": "textEditor-001",
  "sourceHandle": "textEditor-001-source-right",
  "target": "chatNode-001",
  "targetHandle": "chatNode-001-target-left"
}
```

Do not use business keys such as `system_text`, `answerText`, `userFiles`, `userChatInput`, `fileUrlList`, `system_textareaInput`, or `text` as edge handles.

## Reference Styles

Normal input references:

```json
["nodeId", "outputKey"]
```

Template references for `textEditor.system_textareaInput.value` and `answerNode.text.value`:

```text
{{$nodeId.outputKey$}}
```

Reject legacy moustache syntax:

```text
{{nodeId.outputKey}}
```

Reject array references in `answerNode.text.value`:

```json
["nodeId", "outputKey"]
```

## Scenario Fill Rules

### `chatNode`

Start from the full official `chatNode` default. Preserve official control inputs such as:

- `temperature`
- `maxToken`
- `aiChatQuoteRole`
- `quoteTemplate`
- `quotePrompt`
- `aiChatVision`
- `aiChatReasoning`
- `aiChatTopP`
- `aiChatStopSign`
- `aiChatResponseFormat`
- `aiChatJsonSchema`

Fill scenario values only for the relevant inputs:

- `model`
- `isResponseAnswerText`
- `systemPrompt`
- `history`
- `quoteQA`
- `fileUrlList`
- `userChatInput`

If the chat node feeds an `answerNode`, set `isResponseAnswerText.value = false`.

Do not add custom chat inputs for form fields, extraction fields, HTTP responses, variables, scoring criteria, or metadata. Put combined context into `systemPrompt.value` or `userChatInput.value`, often through an upstream `textEditor.system_text`.

### `answerNode`

Start from the official `answerNode` default. Fill only the `text.value`.

Default reference style:

```text
{{$chatNode-001.answerText$}}
```

`text.value` must remain a string. Do not use array reference style for the final reply node.

### `textEditor`

Start from the official `textEditor` default. Put deterministic assembled text in `system_textareaInput.value`.

Use template references inside the text body when combining upstream outputs.

### `contentExtract`

Start from the official `contentExtract` default.

Required scenario values:

- `description.value`
- `content.value`
- `extractKeys.value`

Use only these outputs:

- `success`
- `fields`
- `system_error_text`

Do not create per-field outputs such as `courseName`, `bookingDate`, or `reason`.

### `readFiles`

Start from the official `readFiles` default.

`fileUrlList.value` should reference `["workflowStart-xxx", "userFiles"]`.

Downstream text nodes should consume `system_text`, not raw `userFiles`.

### `httpRequest468`

Start from the official `httpRequest468` default and preserve dynamic system inputs:

- `system_addInputParam`
- `system_addOutputParam`
- `system_header_secret`
- `system_httpHeader`
- `system_httpParams`
- `system_httpJsonBody`
- `system_httpFormBody`
- `system_httpContentType`

`system_httpReqUrl.value` must be non-empty. Use `system_httpJsonBody` for JSON payloads.

### `ifElseNode`

Start from the official `ifElseNode` default.

`ifElseList.value[]` uses:

- `condition`
- `list`

Branch names are edge handles only. Do not create `IF`, `ELSE IF N`, or `ELSE` outputs.

### `datasetSearchNode`

Start from the official `datasetSearchNode` default.

Fill:

- `datasets`
- `userChatInput`
- retrieval settings requested by the user

Downstream `chatNode.quoteQA` references `["datasetSearchNodeId", "quoteQA"]`.

### `datasetConcatNode`

Start from the official `datasetConcatNode` default.

Use it only to merge multiple dataset quote outputs.

### `classifyQuestion`

Start from the official `classifyQuestion` default.

Fill:

- `model`
- `systemPrompt`
- `history`
- `userChatInput`
- `agents`

Branch handles use stable `agents[].key` values.
