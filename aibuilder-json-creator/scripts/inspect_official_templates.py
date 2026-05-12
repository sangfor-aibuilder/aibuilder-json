#!/usr/bin/env python3
"""Print node IO contracts from the bundled official default node templates."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "references" / "official-default-node-templates.json"


def main() -> int:
    data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8-sig"))
    nodes = data.get("nodes", data if isinstance(data, list) else [])
    for node in nodes:
        node_type = node.get("flowNodeType")
        inputs = [item.get("key") for item in node.get("inputs", []) if isinstance(item, dict)]
        outputs = [item.get("key") for item in node.get("outputs", []) if isinstance(item, dict)]
        print(f"{node_type}")
        print(f"  inputs: {', '.join(inputs)}")
        print(f"  outputs: {', '.join(outputs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
