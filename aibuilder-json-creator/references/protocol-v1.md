# fastgpt-json-skill-protocol/v1

Use this protocol when user asks for skill-protocol export.

```yaml
protocol: fastgpt-json-skill-protocol/v1
meta:
  app_name: string
  mode: workflow
  output_style: array_ref | template_string
  assumptions:
    - string
requirements:
  summary: string
  inputs:
    - name: string
      source: chat | form | file | dataset | system
      required: boolean
  decisions:
    - name: string
      rule: string
workflow:
  nodes_count: number
  edges_count: number
  core_path:
    - nodeId
validation:
  root_ok: boolean
  node_ids_unique: boolean
  edge_refs_ok: boolean
  input_refs_ok: boolean
  answer_value_style_ok: boolean
  file_upload_config_ok: boolean
  notes:
    - string
artifacts:
  json_path: string
  docs_used:
    - string
```

