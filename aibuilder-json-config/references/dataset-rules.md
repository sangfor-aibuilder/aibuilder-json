# Dataset Retrieval Rules

Use this reference when the workflow needs FastGPT knowledge-base retrieval.

## 1. Supported Retrieval Patterns

There are two valid patterns:

- Explicit retrieval node flow:
  - `datasetSearchNode` for retrieval
  - optional `datasetConcatNode` for merging multiple retrieval results
  - downstream `chatNode.quoteQA` references retrieval output
- Inline retrieval on `chatNode` / `agent` by configuring dataset-related inputs such as `datasetSelectList`.

Do not treat `quoteQA` as a standalone retrieval source. It is a reference target for dataset quote results.

Strict default:

- Prefer explicit retrieval node flow by default.
- Only use inline retrieval on `chatNode` / `agent` when the user explicitly requests a simpler inline structure.
- If the requirement contains knowledge-base Q&A, RAG, policy lookup, FAQ retrieval, or multi-dataset retrieval, explicit nodes are the default.

## 2. datasetSearchNode Required Inputs

`datasetSearchNode` must be fully configured before use.

Required inputs:

- `datasetSelectList`
- `userChatInput`

Common retrieval parameters:

- `datasetSimilarity`
- `datasetMaxTokens`
- `datasetSearchMode`
- `datasetSearchEmbeddingWeight`
- `datasetSearchUsingReRank`
- `datasetSearchRerankModel`
- `datasetSearchRerankWeight`
- `datasetSearchUsingExtensionQuery`
- `datasetSearchExtensionModel`
- `datasetSearchExtensionBg`
- `collectionFilterMatch`

Expected output:

- `datasetQuoteQA`

## 3. Correct Downstream Usage

If downstream AI needs knowledge-base references, use:

```json
{
  "key": "quoteQA",
  "valueType": "datasetQuote",
  "value": ["datasetSearch-xxx", "datasetQuoteQA"]
}
```

Do not point `quoteQA` at unrelated string outputs.

## 4. datasetConcatNode

Use `datasetConcatNode` when multiple retrieval branches need to be merged.

Required behavior:

- Input list items must be dataset quote references.
- Output is `datasetQuoteQA`.
- Downstream `chatNode.quoteQA` can reference the merged output.
- If two or more dataset retrieval outputs exist, merging through `datasetConcatNode` is the default strict behavior.

## 5. Dataset Selection Quality

When generating importable JSON:

- Do not invent fake dataset business semantics.
- If the user names concrete knowledge bases, preserve those names and IDs when provided.
- If dataset IDs are unknown, clearly mark them as placeholders that the user must replace.
- Keep retrieval node names, labels, and descriptions in Chinese.

## 6. Retrieval Query Source

The retrieval query should come from the real business question or normalized upstream text.

Preferred sources:

- `workflowStart.userChatInput`
- `formInput` output fields
- parsed file text if retrieval depends on uploaded document content
- upstream AI extraction output when retrieval is based on extracted keywords

Do not leave `datasetSearchNode.userChatInput` empty.
