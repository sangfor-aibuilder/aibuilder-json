#!/usr/bin/env python3
"""Validate FastGPT workflow JSON against runtime contracts and workflow topology."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_TEMPLATE_PATH = ROOT / "references" / "official-default-node-templates.json"

ALLOWED_OUTPUTS: dict[str, set[str]] = {
    "workflowStart": {"userChatInput", "userFiles"},
    "userGuide": set(),
    "formInput": {"formInputResult"},
    "userSelect": {"selectResult"},
    "ifElseNode": {"ifElseResult"},
    "textEditor": {"system_text"},
    "chatNode": {"history", "answerText", "reasoningText", "system_error_text"},
    "httpRequest468": {"httpRawResponse", "error", "system_error_text"},
    "readFiles": {"system_text", "system_rawResponse", "system_error_text"},
    "contentExtract": {"success", "fields", "system_error_text"},
    "datasetSearchNode": {"quoteQA", "system_error_text"},
    "datasetConcatNode": {"quoteQA"},
    "classifyQuestion": {"cqResult"},
    "cfr": {"system_text"},
    "answerNode": set(),
    "variableUpdate": set(),
}

REQUIRED_INPUTS: dict[str, set[str]] = {
    "workflowStart": {"userChatInput"},
    "formInput": {"description", "userInputForms"},
    "userSelect": {"description", "userSelectOptions"},
    "ifElseNode": {"ifElseList"},
    "textEditor": {"system_textareaInput"},
    "chatNode": {"model", "systemPrompt", "history", "isResponseAnswerText"},
    "httpRequest468": {"system_httpReqUrl", "system_httpMethod", "system_httpTimeout"},
    "contentExtract": {"model", "description", "history", "content", "extractKeys"},
    "readFiles": {"fileUrlList"},
    "answerNode": {"text"},
}

CHAT_DIALOG_KEYS = {"systemPrompt", "history", "quoteQA", "fileUrlList", "userChatInput"}
CHAT_CONTROL_KEYS = {"model", "isResponseAnswerText"}
BUSINESS_HANDLE_KEYS = {
    "userFiles",
    "system_text",
    "answerText",
    "userChatInput",
    "fileUrlList",
    "system_textareaInput",
    "text",
}
MOJIBAKE_MARKERS = ("\ufffd", "\u9422", "\u93c2", "\u7eef", "\u920b", "\u95bb", "\u95ba")
MIN_CONNECTED_X_GAP = 1500
MIN_SIBLING_Y_GAP = 1000
NON_RUNTIME_NODE_TYPES = {"userGuide"}


def load_official_contracts() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    data = json.loads(OFFICIAL_TEMPLATE_PATH.read_text(encoding="utf-8-sig"))
    nodes = data.get("nodes", data if isinstance(data, list) else [])
    inputs_by_type: dict[str, set[str]] = {}
    outputs_by_type: dict[str, set[str]] = {}
    for node in nodes:
        node_type = node.get("flowNodeType")
        if not isinstance(node_type, str):
            continue
        inputs_by_type[node_type] = {
            item.get("key")
            for item in node.get("inputs", [])
            if isinstance(item, dict) and isinstance(item.get("key"), str)
        }
        outputs_by_type[node_type] = {
            item.get("key")
            for item in node.get("outputs", [])
            if isinstance(item, dict) and isinstance(item.get("key"), str)
        }
    return inputs_by_type, outputs_by_type


def iter_template_refs(value: Any) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    if isinstance(value, str):
        refs.extend(re.findall(r"\{\{\$([A-Za-z0-9_-]+)\.([^$]+)\$\}\}", value))
    elif isinstance(value, list):
        for item in value:
            refs.extend(iter_template_refs(item))
    elif isinstance(value, dict):
        for item in value.values():
            refs.extend(iter_template_refs(item))
    return refs


def input_by_key(inputs: list[Any]) -> dict[str, dict[str, Any]]:
    return {item.get("key"): item for item in inputs if isinstance(item, dict)}


def has_upstream_path(
    *,
    upstream: str,
    downstream: str,
    incoming: dict[str, set[str]],
) -> bool:
    """Return whether upstream can reach downstream through visual edges."""
    if upstream == downstream:
        return True
    seen: set[str] = set()
    stack = list(incoming.get(downstream, set()))
    while stack:
        current = stack.pop()
        if current == upstream:
            return True
        if current in seen:
            continue
        seen.add(current)
        stack.extend(incoming.get(current, set()) - seen)
    return False


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_fastgpt_json.py <workflow.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    errors: list[str] = []
    official_inputs, official_outputs = load_official_contracts()
    allowed_outputs = {**ALLOWED_OUTPUTS, **official_outputs}
    try:
        raw_text = path.read_text(encoding="utf-8-sig")
        data = json.loads(raw_text)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        return 1

    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("root.nodes must be a non-empty array")
        nodes = []

    edges = data.get("edges", [])
    if not isinstance(edges, list):
        errors.append("root.edges must be an array")
        edges = []

    chat_config = data.get("chatConfig")
    if not isinstance(chat_config, dict):
        errors.append("root.chatConfig must be an object")
        chat_config = {}
    else:
        welcome_text = chat_config.get("welcomeText")
        if not isinstance(welcome_text, str) or not welcome_text.strip():
            errors.append("chatConfig.welcomeText must be non-empty")

    node_by_id: dict[str, dict[str, Any]] = {}
    positions: dict[str, tuple[int, int]] = {}
    workflow_start_count = 0
    user_guide_count = 0

    for node in nodes:
        node_id = node.get("nodeId")
        if not node_id:
            errors.append("node missing nodeId")
            continue
        if node_id in node_by_id:
            errors.append(f"duplicate nodeId: {node_id}")
        node_by_id[node_id] = node

        position = node.get("position", {})
        if isinstance(position, dict):
            x = position.get("x")
            y = position.get("y")
            if isinstance(x, int) and isinstance(y, int):
                positions[node_id] = (x, y)
            else:
                errors.append(f"{node_id}: position.x and position.y must be integers")
        else:
            errors.append(f"{node_id}: position must be an object")

        if node.get("flowNodeType") == "workflowStart":
            workflow_start_count += 1
        if node.get("flowNodeType") == "userGuide":
            user_guide_count += 1

    if workflow_start_count != 1:
        errors.append("workflow must contain exactly one workflowStart node")
    if user_guide_count != 1:
        errors.append("workflow must contain exactly one userGuide node")

    seen_positions: dict[tuple[int, int], str] = {}
    for node_id, pos in positions.items():
        if pos in seen_positions:
            errors.append(f"node positions overlap: {seen_positions[pos]} and {node_id} at {pos}")
        seen_positions[pos] = node_id

    edge_pairs: set[tuple[str, str]] = set()
    outgoing: dict[str, set[str]] = {node_id: set() for node_id in node_by_id}
    incoming: dict[str, set[str]] = {node_id: set() for node_id in node_by_id}

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        source_handle = edge.get("sourceHandle")
        target_handle = edge.get("targetHandle")

        if source not in node_by_id:
            errors.append(f"edge source does not exist: {source}")
        if target not in node_by_id:
            errors.append(f"edge target does not exist: {target}")
        if not source_handle or not target_handle:
            errors.append(f"edge missing handles: {source}->{target}")
        if isinstance(source, str) and "-source-" in source:
            errors.append(f"edge.source contains handle: {source}")
        if isinstance(target, str) and "-target-" in target:
            errors.append(f"edge.target contains handle: {target}")
        if source_handle in BUSINESS_HANDLE_KEYS:
            errors.append(f"edge {source}->{target} sourceHandle uses business key: {source_handle}")
        if target_handle in BUSINESS_HANDLE_KEYS:
            errors.append(f"edge {source}->{target} targetHandle uses business key: {target_handle}")

        if isinstance(source, str) and isinstance(target, str) and source in node_by_id and target in node_by_id:
            edge_pairs.add((source, target))
            outgoing[source].add(target)
            incoming[target].add(source)
            if source in positions and target in positions:
                source_x, source_y = positions[source]
                target_x, target_y = positions[target]
                if abs(target_x - source_x) < MIN_CONNECTED_X_GAP:
                    errors.append(f"edge {source}->{target} x spacing too small: {abs(target_x - source_x)}")
                if source_x == target_x and abs(target_y - source_y) < MIN_SIBLING_Y_GAP:
                    errors.append(f"edge {source}->{target} y spacing too small: {abs(target_y - source_y)}")
            if node_by_id[source].get("flowNodeType") not in {"ifElseNode", "classifyQuestion"}:
                expected_source = f"{source}-source-right"
                expected_target = f"{target}-target-left"
                if source_handle != expected_source:
                    errors.append(f"edge {source}->{target} sourceHandle should be {expected_source}, got {source_handle}")
                if target_handle != expected_target:
                    errors.append(f"edge {source}->{target} targetHandle should be {expected_target}, got {target_handle}")

    workflow_starts = [node_id for node_id, node in node_by_id.items() if node.get("flowNodeType") == "workflowStart"]
    answer_nodes = [node_id for node_id, node in node_by_id.items() if node.get("flowNodeType") == "answerNode"]
    if not answer_nodes:
        errors.append("workflow must contain at least one answerNode")

    reachable_from_start: set[str] = set()
    stack = list(workflow_starts)
    while stack:
        current = stack.pop()
        if current in reachable_from_start:
            continue
        reachable_from_start.add(current)
        stack.extend(outgoing.get(current, set()) - reachable_from_start)

    can_reach_answer: set[str] = set()
    stack = list(answer_nodes)
    while stack:
        current = stack.pop()
        if current in can_reach_answer:
            continue
        can_reach_answer.add(current)
        stack.extend(incoming.get(current, set()) - can_reach_answer)

    for node_id, node in node_by_id.items():
        node_type = node.get("flowNodeType")
        if node_type in NON_RUNTIME_NODE_TYPES:
            continue
        if node_type != "workflowStart" and node_id not in reachable_from_start:
            errors.append(f"{node_id}: node is not reachable from workflowStart")
        if node_type != "answerNode" and node_id not in can_reach_answer:
            errors.append(f"{node_id}: node cannot reach answerNode")

    for node in nodes:
        node_id = node.get("nodeId", "<unknown>")
        node_type = node.get("flowNodeType")
        inputs = node.get("inputs", [])
        outputs = node.get("outputs", [])
        if not isinstance(inputs, list):
            errors.append(f"{node_id}: inputs must be an array")
            inputs = []
        if not isinstance(outputs, list):
            errors.append(f"{node_id}: outputs must be an array")
            outputs = []

        by_key = input_by_key(inputs)
        input_keys = set(by_key)

        if "props" in node:
            errors.append(f"{node_id}: props is not allowed for runtime config")

        for key in REQUIRED_INPUTS.get(node_type, set()):
            if key not in input_keys:
                errors.append(f"{node_id}({node_type}) missing required input: {key}")

        if node_type == "userGuide" and outputs:
            errors.append(f"{node_id}: userGuide should have empty outputs")

        if node_type in allowed_outputs:
            for output in outputs:
                key = output.get("key") if isinstance(output, dict) else None
                if key not in allowed_outputs[node_type]:
                    errors.append(f"{node_id}({node_type}) invalid output key: {key}")
        if node_type in official_inputs:
            unknown_inputs = input_keys - official_inputs[node_type]
            if unknown_inputs:
                errors.append(f"{node_id}({node_type}) input keys not in official template: {sorted(unknown_inputs)}")

        if node_type == "workflowStart":
            for key in ("userChatInput",):
                if not any(isinstance(output, dict) and output.get("key") == key for output in outputs):
                    errors.append(f"{node_id}(workflowStart) missing required output: {key}")
            has_user_files = any(isinstance(output, dict) and output.get("key") == "userFiles" for output in outputs)
            if has_user_files and not bool(chat_config.get("fileSelectConfig", {}).get("canSelectFile")):
                errors.append(f"{node_id}: userFiles output requires chatConfig.fileSelectConfig.canSelectFile = true")

        if node_type == "contentExtract":
            extract_keys = by_key.get("extractKeys", {}).get("value")
            if not extract_keys:
                errors.append(f"{node_id}: extractKeys must not be empty")

        if node_type == "ifElseNode":
            if_else = by_key.get("ifElseList")
            for group in (if_else or {}).get("value", []):
                if not isinstance(group, dict):
                    errors.append(f"{node_id}: ifElseList group must be object")
                    continue
                if "conditionList" in group:
                    errors.append(f"{node_id}: use ifElseList[].list, not conditionList")
                if "condition" not in group:
                    errors.append(f"{node_id}: ifElseList group missing condition")
                if "list" not in group:
                    errors.append(f"{node_id}: ifElseList group missing list")
                for rule in group.get("list", []):
                    if not all(k in rule for k in ("variable", "condition")):
                        errors.append(f"{node_id}: ifElse rule missing variable/condition")

        if node_type == "httpRequest468":
            url = by_key.get("system_httpReqUrl", {}).get("value")
            if url is None or (isinstance(url, str) and not url.strip()):
                errors.append(f"{node_id}: system_httpReqUrl must not be empty")
            body = by_key.get("system_httpJsonBody", {}).get("value")
            if "system_httpJsonBody" in by_key and body is not None and isinstance(body, str) and body == "":
                errors.append(f"{node_id}: system_httpJsonBody must not be empty when present")

        if node_type == "chatNode":
            official_chat_keys = official_inputs.get("chatNode", CHAT_DIALOG_KEYS | CHAT_CONTROL_KEYS)
            invalid_keys = input_keys - official_chat_keys
            if invalid_keys:
                errors.append(f"{node_id}: chatNode has input keys not in official template: {sorted(invalid_keys)}")
            for key in CHAT_DIALOG_KEYS:
                if key not in input_keys:
                    errors.append(f"{node_id}: chatNode missing standard input key: {key}")
            model = by_key.get("model", {})
            if "settingLLMModel" not in model.get("renderTypeList", []):
                errors.append(f"{node_id}: model.renderTypeList should include settingLLMModel")
            if not any(by_key.get(key, {}).get("value") not in (None, "", []) for key in ("userChatInput", "fileUrlList", "quoteQA")):
                errors.append(f"{node_id}: chatNode missing business input")

        if node_type == "answerNode":
            text_input = by_key.get("text", {})
            text_value = text_input.get("value")
            if isinstance(text_value, list):
                errors.append(
                    f"{node_id}.text.value must be string template style, not array reference; "
                    "use {{$nodeId.outputKey$}}"
                )
            elif text_value is None or not isinstance(text_value, str):
                errors.append(f"{node_id}.text.value must be a string")

        for input_item in inputs:
            if not isinstance(input_item, dict):
                continue
            value = input_item.get("value")
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                ref_node, ref_key = value
                source = node_by_id.get(ref_node)
                if source:
                    source_type = source.get("flowNodeType")
                    if source_type in allowed_outputs and ref_key not in allowed_outputs[source_type]:
                        errors.append(
                            f"array reference invalid output in {node_id}.{input_item.get('key')}: "
                            f"{ref_node}.{ref_key} for {source_type}"
                        )
                    if ref_node != node_id and not has_upstream_path(
                        upstream=ref_node,
                        downstream=node_id,
                        incoming=incoming,
                    ):
                        errors.append(
                            f"{node_id}.{input_item.get('key')}: reference is not upstream in visual graph: "
                            f"{ref_node}->{node_id}"
                        )
            for ref_node, ref_key in iter_template_refs(value):
                source = node_by_id.get(ref_node)
                if not source:
                    errors.append(f"template reference unknown node: {ref_node}.{ref_key}")
                    continue
                source_type = source.get("flowNodeType")
                if source_type in allowed_outputs and ref_key not in allowed_outputs[source_type]:
                    errors.append(f"template reference invalid output: {ref_node}.{ref_key} for {source_type}")
                if ref_node != node_id and not has_upstream_path(
                    upstream=ref_node,
                    downstream=node_id,
                    incoming=incoming,
                ):
                    errors.append(
                        f"{node_id}.{input_item.get('key')}: template reference is not upstream in visual graph: "
                        f"{ref_node}->{node_id}"
                    )

    if re.search(r"\{\{(?!\$)", raw_text):
        errors.append("legacy moustache reference found")
    if "userGuide.variables" in raw_text:
        errors.append("invalid userGuide.variables reference found")
    if any(marker in raw_text for marker in MOJIBAKE_MARKERS):
        errors.append("mojibake marker found in generated text")

    if errors:
        for error in sorted(set(errors)):
            print(f"ERROR: {error}")
        return 1

    print("VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
