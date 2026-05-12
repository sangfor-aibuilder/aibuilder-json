# Question Classification Rules

Use this reference when the workflow needs FastGPT question classification.

## 1. Node Type and Core Behavior

Question classification uses `flowNodeType: "classifyQuestion"`.

This node is not just an LLM text node. Its classification list is stored in the `agents` input, and each item key is used as a source handle for branch routing.

## 2. Required Inputs

`classifyQuestion` must be fully configured before use.

Required inputs:

- `model`
- `systemPrompt`
- `history`
- `userChatInput`
- `agents`

Required output:

- `cqResult`

## 3. agents Input Structure

`agents` must be a non-empty array. Each item must include:

- `key`: stable unique branch key
- `value`: Chinese category name or category description

Correct pattern:

```json
[
  { "key": "faq", "value": "常见问题" },
  { "key": "product", "value": "产品咨询" },
  { "key": "other", "value": "其他问题" }
]
```

Invalid patterns:

- empty `agents` array
- missing `key`
- missing `value`
- duplicated `key`
- English-only user-facing category labels

## 4. Branch Routing Rules

Each classification item key is also a branch handle suffix.

That means:

- every branch category should have a stable `key`
- downstream edges should connect from `getHandleId(nodeId, "source", agent.key)` semantics
- classification keys should not be regenerated inconsistently after branch design is established

If the workflow uses classification for routing, generate one branch per meaningful category and avoid placeholder categories with no downstream path unless clearly intended.

## 5. Classification Prompt Quality

`systemPrompt` must explicitly describe:

- the classification goal
- each category meaning
- how to classify ambiguous inputs
- how to fall back to a default category such as `其他问题`

Do not leave `systemPrompt` empty or generic.

## 6. Query Source

`userChatInput` must point to the real text to classify.

Preferred sources:

- `workflowStart.userChatInput`
- `formInput` output
- parsed file text such as `readFiles.system_text`
- upstream extraction result when classification is based on normalized content

Do not classify raw file arrays.

## 7. Strict Default Behavior

When the requirement mentions intent routing, question triage, FAQ routing, ticket dispatch, issue categorization, customer-service shunting, or problem classification:

- prefer `classifyQuestion` over ad hoc `chatNode + ifElseNode` text matching
- define explicit category list in `agents`
- connect branch outputs using category keys
- keep one fallback category such as `其他问题` unless the user explicitly excludes it
