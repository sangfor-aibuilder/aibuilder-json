# ifElse Rules

`ifElseNode` conditions must be fully configured.

## Required Condition Parts

Every condition item must include:

- `variable`: upstream reference or supported variable source
- `condition`: explicit operator such as `include`, `equalTo`, `notEqualTo`, `greaterThan`
- `value`: comparison input when the operator requires one

Do not generate variable-only condition entries.

## Correct Pattern

```json
{
  "condition": "AND",
  "list": [
    {
      "variable": ["chatNode-xxx", "answerText"],
      "condition": "include",
      "value": "通过",
      "valueType": "string"
    }
  ]
}
```

## Invalid Pattern

```json
{
  "conditionList": [
    {
      "variable": ["chatNode-xxx", "answerText"],
      "condition": "include",
      "value": "通过"
    }
  ]
}
```

```json
{
  "variable": ["chatNode-xxx", "answerText"]
}
```

`conditionList` is invalid for generated JSON. Always use `ifElseList.value[].list`.

## Branch Design Notes

- The compared field should be a stable upstream structured output or answer field.
- The operator must match the data type and business meaning.
- The comparison value must be explicit and deterministic.
- Keep `IF / ELSE IF / ELSE` branches mutually understandable and testable.
- `IF / ELSE IF / ELSE` are edge handles only. They must not be declared as node outputs.
- The node output must be `ifElseResult` only.
