# Azure Diagrams Skill

A comprehensive technical diagramming toolkit for **solutions architects**, **presales engineers**, and **developers**. Generate professional diagrams for proposals, documentation, and architecture reviews.

## What You Can Create

| Diagram Type | Use Case |
|--------------|----------|
| **Azure Architecture** | Solution designs, infrastructure docs |
| **Business Process Flows** | Workflows, approvals, swimlanes |
| **Entity Relationship (ERD)** | Database schemas, data models |
| **Timeline / Gantt** | Project roadmaps, migration plans |
| **UI Wireframes** | Dashboard mockups, screen layouts |
| **Sequence Diagrams** | Auth flows, API interactions |
| **Network Topology** | Hub-spoke, VNets, hybrid cloud |

## Installation

For detailed installation instructions across different platforms (Claude Code CLI, GitHub Copilot, Cursor, etc.), see the [main repository README](https://github.com/cmb211087/azure-diagrams-skill#installation).

### Prerequisites

```bash
pip install diagrams matplotlib
apt-get install graphviz  # or: brew install graphviz (macOS) / choco install graphviz (Windows)
```

## Contents

```
azure-diagrams/
├── SKILL.md                              # Main skill instructions
├── references/
│   ├── azure-components.md               # 700+ Azure components + Nov 2025 icons
│   ├── common-patterns.md                # Architecture patterns (SVG default)
│   ├── business-process-flows.md         # Workflow & swimlane patterns
│   ├── entity-relationship-diagrams.md   # ERD patterns
│   ├── timeline-gantt-diagrams.md        # Timeline patterns
│   ├── ui-wireframe-diagrams.md          # Wireframe patterns
│   ├── iac-to-diagram.md                 # Generate from Bicep/Terraform
│   ├── large-diagram-strategies.md       # Handling 50+ node diagrams
│   ├── preventing-overlaps.md            # Layout troubleshooting
│   └── quick-reference.md                # Snippets + WAF patterns
└── scripts/
    ├── generate_diagram.py               # Secure interactive generator
    └── verify_installation.py            # Check prerequisites
```

## Output Format

**SVG is recommended** for all diagrams:
- Scalable without quality loss
- 50-80% smaller file size than PNG
- Web-ready, embeds in HTML/Markdown
- Text content is searchable

```python
with Diagram("Title", outformat="svg", ...):
```

## Example Prompts

**Architecture Diagram:**
```
Create an e-commerce platform architecture with:
- Front Door for global load balancing
- AKS for microservices
- Cosmos DB for product catalog
- Redis for session cache
- Service Bus for order processing
```

**Business Process Flow:**
```
Create a swimlane diagram for employee onboarding with lanes for:
- HR, IT, Manager, and New Employee
Show the process from offer acceptance to first day completion
```

**ERD Diagram:**
```
Generate an entity relationship diagram for an order management system with:
- Customers, Orders, OrderItems, Products, Categories
- Show primary keys, foreign keys, and cardinality
```

**Well-Architected Pattern:**
```
Create a Zero Trust security architecture showing:
- Entra ID with Conditional Access
- Network micro-segmentation with Firewall
- Private Endpoints for data services
- Key Vault with Managed Identity access
```

**Large Architecture (Split Views):**
```
Create a network view diagram for our 80-resource Azure environment,
focusing only on VNets, subnets, NSGs, and connectivity
```

## Compatibility

| Tool | Status |
|------|--------|
| Claude Code CLI | Supported |
| GitHub Copilot | Supported |
| Cursor | Supported |
| VS Code Copilot | Supported |

Built on the [Agent Skills](https://agentskills.io) open standard.

## License

MIT License - free to use, modify, and distribute.

## Credits

- [diagrams](https://diagrams.mingrammer.com/) - Diagram as Code library
- [Graphviz](https://graphviz.org/) - Graph visualization
- [Agent Skills](https://agentskills.io) - Open standard for AI skills
