# Design Document: Embedded Docs Enrichment

## Overview

This design describes the approach for expanding 18 embedded systems knowledge articles from their current 300–600 line foundations to 1500+ lines of production-quality technical content. Each article is enriched in-place using `strReplace` to append new sections and expand existing ones. No new files are created outside the `knowledge/` tree except for this spec.

The enrichment is executed article-by-article. Each article follows a canonical section structure defined below, with topic-specific content filling each section.

## Architecture

```
.kiro/specs/embedded-docs-enrichment/
├── requirements.md   (approved)
├── design.md         (this file)
└── tasks.md          (implementation checklist)

knowledge/02-technologies/embedded/
├── 01-hardware-layer/
│   ├── 02-hardware-design-fundamentals/
│   │   ├── advanced/
│   │   │   ├── 03-fpga-basics.md          [ENRICH]
│   │   │   ├── 04-verilog-intro.md        [ENRICH]
│   │   │   └── 05-state-machine.md        [ENRICH]
│   │   └── intermediate/
│   │       └── 06-motor-driver-circuit.md [ENRICH]
│   ├── 04-sensor-technology/intermediate/
│   │   └── 04-accelerometer-gyroscope.md  [ENRICH]
│   └── 05-actuator-control/advanced/
│       ├── 01-smart-car-control.md        [ENRICH]
│       ├── 02-motion-control-algorithms.md[ENRICH]
│       ├── 03-multi-axis-sync.md          [ENRICH]
│       ├── 04-smart-gimbal-project.md     [ENRICH]
│       ├── 05-robot-arm-project.md        [ENRICH]
│       ├── 06-hexapod-robot.md            [ENRICH]
│       ├── 07-smart-socket-project.md     [ENRICH]
│       ├── 08-automation-system.md        [ENRICH]
│       └── 09-environment-control.md      [ENRICH]
├── 02-driver-bsp-layer/04-interrupt-exception-handling/intermediate/
│   └── 04-encoder-interface.md            [ENRICH]
├── 06-communication-networking/01-wireless-communication/intermediate/
│   └── 03-mqtt-protocol.md                [ENRICH]
└── 07-cloud-backend/03-data-analysis-visualization/beginner/
    └── 03-data-visualization.md           [ENRICH]
```

## Components and Interfaces

### Canonical Article Structure

Every enriched article MUST follow this section order. Sections already present are expanded; missing sections are appended.

```
1. YAML Front Matter          (preserve existing, update estimated_time)
2. 概述 (Overview)            (expand: add learning objectives table)
3. 背景知识 (Background)      (expand: deeper theory, history, comparisons)
4. 核心内容 (Core Content)    (expand: more subsections, more code)
   4.1 Theory / Principles
   4.2 Hardware Setup / Connections
   4.3 Basic Implementation
   4.4 Advanced Features
   4.5 Performance Optimization
5. 深入原理 (Deep Dive)       (NEW: internals, math, edge cases)
6. 完整项目实战 (Full Project) (NEW or EXPAND: end-to-end integration)
7. 性能调优 (Performance Tuning) (NEW: benchmarks, optimization tips)
8. 常见问题与调试 (Troubleshooting) (EXPAND: more failure modes)
9. 测试与验证 (Testing)       (NEW: how to verify correctness)
10. 延伸阅读 (Further Reading) (EXPAND: more internal + external links)
11. 参考资料 (References)     (EXPAND: more authoritative sources)
```

### Content Depth Standards per Article Category

**Hardware Articles** (FPGA, motor driver, IMU, encoder):
- Register map tables with bit-field descriptions
- Oscilloscope waveform descriptions for key signals
- Component selection decision trees
- PCB layout rules with layer stack recommendations
- Thermal calculations where relevant

**Protocol Articles** (MQTT, Modbus):
- Packet byte-level diagrams
- Wireshark/logic analyzer capture descriptions
- Security threat model
- Performance benchmarks (throughput, latency)
- Multi-device topology examples

**Project Articles** (gimbal, robot arm, hexapod, smart socket, automation):
- Full BOM with Taobao/LCSC part numbers
- Wiring harness diagrams
- Calibration procedures with acceptance criteria
- Failure mode and effects analysis (FMEA) table
- Video/demo description

**Algorithm Articles** (motion control, multi-axis sync, FSM):
- Mathematical derivations
- Pseudocode before C implementation
- Numerical stability analysis
- Real-time performance analysis (worst-case execution time)

## Data Models

### Article Metadata (YAML Front Matter)

All articles use this schema (existing fields preserved):

```yaml
title: string           # Chinese title
description: string     # 150-200 char summary
slug: string            # kebab-case URL slug
domain: string          # 所属领域
module: string          # 所属模块
content_type: article|tutorial|project
skill_level: beginner|intermediate|advanced
tags: [string]          # 5-10 tags
prerequisites: [string] # relative paths to prereq articles
related_contents: [string] # relative paths to related articles
estimated_time: int     # minutes to read/follow
difficulty_score: 1-5
author: string
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD  # update to 2026-03-10
version: string
language: zh-CN
status: published
```

### Code Block Standards

```
Language tags used:
  verilog    — Verilog HDL
  c          — C (STM32 HAL, bare metal)
  cpp        — C++ (Arduino/ESP-IDF)
  python     — Python (host tools, scripts)
  bash       — Shell commands
  yaml       — Configuration files
  toml       — Telegraf config
  tcl        — Vivado XDC constraints
  mermaid    — Mermaid diagrams
  flux       — InfluxDB Flux queries
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do.*

### Property 1: Length Invariant
*For any* enriched article, the total line count SHALL be ≥ 1500 lines after enrichment.
**Validates: Requirements 1.1**

### Property 2: Code Block Count
*For any* enriched article, the number of fenced code blocks SHALL be ≥ 5.
**Validates: Requirements 2.3**

### Property 3: Diagram Count
*For any* enriched article, the number of ASCII/Mermaid diagrams SHALL be ≥ 3.
**Validates: Requirements 3.1**

### Property 4: Internal Link Count
*For any* enriched article, the number of internal relative-path links SHALL be ≥ 3.
**Validates: Requirements 8.1**

### Property 5: Section Completeness
*For any* enriched article, all 11 canonical sections SHALL be present (some may be combined for brevity, but none omitted entirely).
**Validates: Requirements 4.2**

### Property 6: Front Matter Validity
*For any* enriched article, the YAML front matter SHALL parse without errors and contain all required fields.
**Validates: Requirements 1.5**

### Property 7: No Broken Links
*For any* internal link in any enriched article, the target file SHALL exist in the knowledge system.
**Validates: Requirements 8.4**

## Error Handling

- If an article already has a section that meets the depth requirement, it is expanded rather than replaced
- If a code example references a chip not covered in the article, a note is added explaining the chip and where to find its datasheet
- If a section would exceed reasonable length for its topic, it is split into subsections with clear headings
- Articles that reference each other are enriched in dependency order (prerequisites first)

## Testing Strategy

### Unit Tests (Manual Verification)
- Line count check: `wc -l <article>` ≥ 1500
- Code block count: count ` ``` ` occurrences / 2 ≥ 5
- Diagram check: search for ASCII box-drawing chars or `mermaid` blocks ≥ 3
- Link check: all `[text](path)` internal links resolve to existing files

### Property Tests (Automated)
A simple Python script can verify all properties across all 18 articles:

```python
# verify_articles.py
import os, re, glob

ARTICLES = [
    "knowledge/02-technologies/embedded/01-hardware-layer/02-hardware-design-fundamentals/advanced/03-fpga-basics.md",
    # ... all 18 paths
]

for path in ARTICLES:
    with open(path) as f:
        lines = f.readlines()
    content = "".join(lines)
    
    assert len(lines) >= 1500, f"{path}: only {len(lines)} lines"
    
    code_blocks = content.count("```") // 2
    assert code_blocks >= 5, f"{path}: only {code_blocks} code blocks"
    
    # Check for diagram indicators
    has_diagram = ("┌" in content or "mermaid" in content or 
                   "graph " in content or "sequenceDiagram" in content)
    assert has_diagram, f"{path}: no diagrams found"
    
    # Check internal links
    internal_links = re.findall(r'\[.*?\]\((\.\.?/[^)]+\.md)\)', content)
    assert len(internal_links) >= 3, f"{path}: only {len(internal_links)} internal links"

print("All articles pass verification!")
```

**Property-Based Testing Library**: pytest with hypothesis (Python)
**Minimum iterations**: 1 per article (deterministic checks, not random)
**Tag format**: `Feature: embedded-docs-enrichment, Property N: <property_text>`
