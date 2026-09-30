"""
Export Curated OpenAPI Specification for ChatGPT Custom Actions

OpenAI Custom GPT enforces a strict platform limit:
  "OpenAPI spec can have a maximum of 30 operations"

This script extracts 25 flagship operations covering all 10 domain
intelligence engines, prunes unreferenced schemas to keep the spec lean,
and outputs a compliant gpt/actions.yaml ready for ChatGPT.
"""

import os
import yaml
from app.main import app

def build_curated_spec():
    raw_spec = app.openapi()

    # Exact curated list of operation IDs / paths & methods
    # Targeting ~25 operations across all 10 specializations
    TARGET_ENDPOINTS = [
        # 1. System & Workspace (2 operations)
        ("/health", "get"),
        ("/workspace/me", "get"),

        # 2. Knowledge Graph Memory (3 operations)
        ("/memory/store", "post"),
        ("/memory/recall", "post"),
        ("/memory/entity/{entity_id}", "get"),

        # 3. Graph Intelligence & Lineage (2 operations)
        ("/intelligence/graph/lineage/{entity_id}", "get"),
        ("/intelligence/graph/query", "post"),

        # 4. Requirement Intelligence (2 operations)
        ("/intelligence/requirements/analyze", "post"),
        ("/intelligence/requirements/ingest", "post"),

        # 5. Decision Intelligence (2 operations)
        ("/intelligence/decisions/evaluate", "post"),
        ("/intelligence/decisions/record", "post"),

        # 6. PRD Specification Engine (3 operations)
        ("/intelligence/prd/assess", "post"),
        ("/intelligence/prd/generate", "post"),
        ("/intelligence/prd/save", "post"),

        # 7. Strategic Roadmap Intelligence (3 operations)
        ("/strategy/bets/evaluate", "post"),
        ("/strategy/roadmap", "post"),
        ("/strategy/align", "post"),

        # 8. Engineering Intelligence (3 operations)
        ("/engineering/analyze", "post"),
        ("/engineering/breakdown", "post"),
        ("/engineering/handoff", "post"),

        # 9. QA & Release Intelligence (3 operations)
        ("/qa/test-strategy", "post"),
        ("/qa/test-cases", "post"),
        ("/qa/release-readiness", "post"),

        # 10. Analytics & Outcome Intelligence (2 operations)
        ("/analytics/kpi", "post"),
        ("/analytics/scorecard", "post"),

        # 11. Customer Intelligence (2 operations)
        ("/customer/signals", "post"),
        ("/customer/problems/extract", "post"),
    ]

    filtered_paths = {}
    total_ops = 0

    for path, method in TARGET_ENDPOINTS:
        if path not in raw_spec["paths"] or method not in raw_spec["paths"][path]:
            raise ValueError(f"Endpoint not found: {method.upper()} {path}")
        
        if path not in filtered_paths:
            filtered_paths[path] = {}
        
        filtered_paths[path][method] = raw_spec["paths"][path][method]
        total_ops += 1

    print(f"Total curated paths: {len(filtered_paths)}")
    print(f"Total curated operations: {total_ops} (Strictly under OpenAI limit of 30)")

    # Find all referenced schemas recursively
    all_schemas = raw_spec.get("components", {}).get("schemas", {})
    referenced_schemas = set()

    def find_refs(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "$ref" and isinstance(v, str) and v.startswith("#/components/schemas/"):
                    schema_name = v.split("/")[-1]
                    if schema_name not in referenced_schemas:
                        referenced_schemas.add(schema_name)
                        if schema_name in all_schemas:
                            find_refs(all_schemas[schema_name])
                else:
                    find_refs(v)
        elif isinstance(node, list):
            for item in node:
                find_refs(item)

    find_refs(filtered_paths)

    pruned_schemas = {
        name: all_schemas[name]
        for name in sorted(referenced_schemas)
        if name in all_schemas
    }

    print(f"Pruned schemas count: {len(pruned_schemas)} (from {len(all_schemas)})")

    curated_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": raw_spec["info"]["title"],
            "description": raw_spec["info"]["description"],
            "version": raw_spec["info"]["version"],
        },
        "servers": [
            {
                "url": "https://carriers-crafts-inflation-zealand.trycloudflare.com",
                "description": "TPG Live Intelligence Backend (Cloudflare Tunnel)"
            }
        ],
        "paths": filtered_paths,
        "components": {
            "schemas": pruned_schemas
        }
    }

    output_dir = "gpt"
    os.makedirs(output_dir, exist_ok=True)

    # Backup the full spec
    with open(os.path.join(output_dir, "actions.all.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(raw_spec, f, sort_keys=False, allow_unicode=True)

    # Save the curated 27-operation spec
    with open(os.path.join(output_dir, "actions.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(curated_spec, f, sort_keys=False, allow_unicode=True)

    print("Successfully exported 27 curated actions to gpt/actions.yaml and backed up full spec to gpt/actions.all.yaml!")

if __name__ == "__main__":
    build_curated_spec()
