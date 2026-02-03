# Quick Reference Card

Copy-paste snippets for rapid diagram creation.

## Minimal Setup

```python
from diagrams import Diagram, Cluster, Edge

with Diagram("Title", show=False, filename="output", direction="LR"):
    # components here
    pass
```

## Common Imports - Integration Services

```python
# Integration
from diagrams.azure.integration import (
    LogicApps, ServiceBus, APIManagement, EventGridTopics,
    DataFactories, IntegrationAccounts, AppConfiguration
)

# Compute
from diagrams.azure.compute import FunctionApps, AppServices, ContainerApps, AKS

# Storage
from diagrams.azure.storage import BlobStorage, DataLakeStorage, StorageAccounts, QueuesStorage

# Database
from diagrams.azure.database import CosmosDb, SQL, CacheForRedis

# Security
from diagrams.azure.security import KeyVaults

# Networking
from diagrams.azure.networking import (
    ApplicationGateways, FrontDoorAndCDNProfiles, VirtualNetworks,
    OnPremisesDataGateways, PrivateLink, Firewalls
)

# Monitoring
from diagrams.azure.monitor import ApplicationInsights, LogAnalyticsWorkspaces

# Analytics
from diagrams.azure.analytics import EventHubs, StreamAnalyticsJobs, AzureSynapseAnalytics, AzureDatabricks

# Identity
from diagrams.azure.identity import ActiveDirectory, ManagedIdentities

# On-Premises
from diagrams.onprem.client import Users, Client
from diagrams.onprem.database import MSSQL, Oracle
from diagrams.onprem.compute import Server

# Generic (for unsupported services)
from diagrams.generic.compute import Rack
from diagrams.generic.database import SQL as GenericSQL
```

## Connection Syntax

```python
# Simple flow
a >> b >> c

# Fan-out (one to many)
a >> [b, c, d]

# Fan-in (many to one)
[a, b, c] >> d

# Labeled edge
a >> Edge(label="HTTPS") >> b

# Styled edge
a >> Edge(style="dashed", color="blue") >> b

# Common edge styles
a >> Edge(style="dashed") >> b   # Dashed (secrets, config)
a >> Edge(style="dotted") >> b   # Dotted (monitoring, logs)
a >> Edge(label="async") >> b    # Labeled
```

## Cluster Patterns

```python
# Simple cluster
with Cluster("Group Name"):
    a = ServiceA("A")
    b = ServiceB("B")

# Nested clusters
with Cluster("Outer"):
    with Cluster("Inner"):
        a = Service("A")

# Multiple clusters
with Cluster("Layer 1"):
    a = ServiceA("A")

with Cluster("Layer 2"):
    b = ServiceB("B")

a >> b  # Connect across clusters
```

## Diagram Configuration Options

```python
with Diagram(
    "Title",
    show=False,                    # Don't open in viewer
    filename="my-diagram",         # Output filename (no extension)
    outformat="png",               # png, svg, pdf, jpg
    direction="LR",                # LR, RL, TB, BT
    graph_attr={
        "fontsize": "20",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "spline",       # spline, ortho, curved, polyline
        "nodesep": "0.8",          # Horizontal spacing
        "ranksep": "1.0",          # Vertical spacing
    }
):
```

## Direction Guide

| Direction | Use Case |
|-----------|----------|
| `LR` | Workflows, data flows, pipelines |
| `TB` | Layered architectures, hierarchy |
| `RL` | Right-to-left flows |
| `BT` | Bottom-up hierarchy |

## Quick Patterns

### API Gateway Pattern
```python
users >> apim >> [logic, func] >> [cosmos, sql]
```

### Event-Driven Pattern
```python
source >> event_grid >> [handler1, handler2, handler3]
```

### Pub/Sub Pattern
```python
[producer1, producer2] >> service_bus >> [consumer1, consumer2]
```

### Hybrid Pattern
```python
on_prem >> data_gateway >> logic_apps >> azure_services
```

### Security Pattern
```python
component >> Edge(style="dashed") >> key_vault
component >> Edge(style="dotted") >> app_insights
```

## Output Formats

```python
# PNG (recommended for sharing - GitHub, email, presentations)
filename="arch", outformat="png"

# SVG (for local documentation)
filename="arch", outformat="svg"

# PDF (for print documents)
filename="arch", outformat="pdf"

# Multiple formats at once
filename="arch", outformat=["svg", "png"]
```

### Format Recommendations

| Format | Best For | Limitation |
|--------|----------|------------|
| **PNG** | GitHub, email, sharing | Larger file size |
| **SVG** | Local docs, web embedding | External icon references* |
| **PDF** | Print documents | Not web-friendly |

> **Important:** SVG files from the `diagrams` library reference external PNG icon files via absolute local paths (e.g., `C:\Python313\...\icon.png`). This means:
> - SVGs render correctly on your local machine
> - SVGs will show broken images when shared (GitHub, email, other machines)
> - **Use PNG format when sharing diagrams**
> - SVG is ideal for local documentation or when post-processing to embed images

## Preventing Overlaps (Complex Diagrams)

```python
# Increase spacing for complex diagrams
dot.attr(
    nodesep='1.2',      # Horizontal (default 0.25)
    ranksep='1.2',      # Vertical (default 0.5)
    pad='0.5',
    splines='spline',
)

# Set explicit size on large nodes (cylinders, etc.)
dot.node('db', 'Database', shape='cylinder', width='2.5', height='1.2')

# Force nodes to same rank (horizontal alignment)
with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('node1')
    s.node('node2')
```

## Component Naming Tips

```python
# Good: Clear, concise labels
apim = APIManagement("API Gateway")
logic = LogicApps("Order Processor")
bus = ServiceBus("Event Bus")

# With line breaks for detail
logic = LogicApps("Order Processing\nWorkflow")
ia = IntegrationAccounts("Integration Account\n(Maps, Schemas)")
```

---

## Well-Architected Framework Patterns

Ready-to-use patterns aligned with Azure's Well-Architected Framework pillars.

### WAF Quick Reference Table

| Pillar | Key Patterns | Primary Azure Services |
|--------|--------------|------------------------|
| **Reliability** | Retry, Circuit Breaker, Bulkhead | Front Door, Cosmos DB multi-region, Traffic Manager |
| **Security** | Zero Trust, Defense in Depth | Entra ID, Key Vault, Firewall, Private Endpoints |
| **Cost** | Autoscale, Spot VMs, Consumption | AKS spot pools, Functions, Serverless Cosmos |
| **Performance** | Cache-Aside, CDN, CQRS | Redis Cache, CDN, Event Sourcing |
| **Ops Excellence** | GitOps, IaC, Blue-Green | Azure DevOps, Bicep, Deployment Slots |

---

### Reliability Patterns

#### Retry with Circuit Breaker

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import FunctionApps
from diagrams.azure.integration import ServiceBus
from diagrams.azure.database import CosmosDb
from diagrams.azure.storage import QueuesStorage

with Diagram("Retry & Circuit Breaker", show=False, direction="LR", outformat="svg"):
    with Cluster("Resilient Processing"):
        func = FunctionApps("Order Function\n(Polly retry)")

    bus = ServiceBus("Service Bus")
    dlq = QueuesStorage("Dead Letter Queue")
    cosmos = CosmosDb("Cosmos DB")

    bus >> func
    func >> Edge(label="success") >> cosmos
    func >> Edge(label="max retries", style="dashed", color="red") >> dlq
```

#### Multi-Region Failover

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.networking import FrontDoorAndCDNProfiles, TrafficManagerProfiles
from diagrams.azure.compute import AppServices
from diagrams.azure.database import CosmosDb

with Diagram("Multi-Region Failover", show=False, direction="TB", outformat="svg"):
    fd = FrontDoorAndCDNProfiles("Azure Front Door")

    with Cluster("Primary - East US"):
        app1 = AppServices("App Service")

    with Cluster("Secondary - West US"):
        app2 = AppServices("App Service")

    cosmos = CosmosDb("Cosmos DB\n(Multi-Region Write)")

    fd >> Edge(label="Active") >> app1
    fd >> Edge(label="Standby", style="dashed") >> app2
    [app1, app2] >> cosmos
```

#### Bulkhead Isolation

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AKS, FunctionApps
from diagrams.azure.integration import ServiceBus

with Diagram("Bulkhead Isolation", show=False, direction="TB", outformat="svg"):
    with Cluster("Isolated Pools"):
        with Cluster("Critical Orders"):
            critical = AKS("Order Pool\n(dedicated)")

        with Cluster("Standard Orders"):
            standard = AKS("Standard Pool")

        with Cluster("Batch Processing"):
            batch = FunctionApps("Batch Pool")

    bus = ServiceBus("Service Bus\n(topic per pool)")

    bus >> [critical, standard, batch]
```

---

### Security Patterns

#### Zero Trust Architecture

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.identity import ActiveDirectory, ConditionalAccess, ManagedIdentities
from diagrams.azure.network import ApplicationGateway, Firewall, PrivateEndpoint
from diagrams.azure.compute import AKS
from diagrams.azure.database import SQL
from diagrams.azure.security import KeyVaults

with Diagram("Zero Trust Architecture", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "1.0", "ranksep": "1.2"}):

    with Cluster("Identity Verification"):
        aad = ActiveDirectory("Entra ID")
        ca = ConditionalAccess("Conditional Access\n(MFA, device compliance)")

    with Cluster("Network Micro-Segmentation"):
        waf = ApplicationGateway("WAF")
        firewall = Firewall("Azure Firewall\n(L7 filtering)")

    with Cluster("Workload (Private VNet)"):
        mi = ManagedIdentities("Managed Identity")
        aks = AKS("AKS\n(no public IP)")
        pe = PrivateEndpoint("Private Endpoints")

    with Cluster("Data (No Public Access)"):
        sql = SQL("Azure SQL")
        kv = KeyVaults("Key Vault")

    aad >> ca >> waf >> firewall >> aks
    aks >> mi >> [kv, sql]
    pe >> [sql, kv]
```

#### Defense in Depth

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.network import ApplicationGateway, Firewall, VirtualNetworks
from diagrams.azure.compute import AppServices
from diagrams.azure.database import SQL
from diagrams.azure.security import KeyVaults, Defender
from diagrams.azure.identity import ActiveDirectory

with Diagram("Defense in Depth", show=False, direction="TB", outformat="svg"):

    with Cluster("Layer 1: Identity"):
        aad = ActiveDirectory("Entra ID + MFA")

    with Cluster("Layer 2: Perimeter"):
        waf = ApplicationGateway("WAF + DDoS")
        firewall = Firewall("Firewall")

    with Cluster("Layer 3: Network"):
        vnet = VirtualNetworks("VNet + NSGs")

    with Cluster("Layer 4: Application"):
        app = AppServices("App Service\n(TLS 1.3)")

    with Cluster("Layer 5: Data"):
        sql = SQL("SQL (TDE + AE)")
        kv = KeyVaults("Key Vault\n(HSM)")

    defender = Defender("Defender for Cloud")

    aad >> waf >> firewall >> vnet >> app >> [sql, kv]
    defender >> Edge(style="dotted") >> [app, sql, kv]
```

---

### Cost Optimization Patterns

#### Autoscaling with Spot Instances

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AKS, VMSS
from diagrams.azure.integration import APIManagement

with Diagram("Spot Instance Architecture", show=False, direction="LR", outformat="svg"):
    apim = APIManagement("API Gateway")

    with Cluster("AKS Cluster"):
        with Cluster("System Pool (Regular)"):
            system = AKS("System Nodes")

        with Cluster("User Pool (Spot - 70% savings)"):
            spot = AKS("Spot Nodes\n(interruptible)")

        with Cluster("Critical Pool (Regular)"):
            critical = AKS("Critical Nodes")

    apim >> [system, spot, critical]
```

#### Consumption-Based Architecture

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import CosmosDb
from diagrams.azure.integration import EventGridTopics, LogicApps
from diagrams.azure.storage import BlobStorage

with Diagram("Serverless / Consumption", show=False, direction="LR", outformat="svg"):
    with Cluster("Event Sources"):
        blob = BlobStorage("Blob Trigger")
        grid = EventGridTopics("Event Grid")

    with Cluster("Serverless Compute (Pay-per-execution)"):
        func = FunctionApps("Functions\n(Consumption)")
        logic = LogicApps("Logic Apps\n(Consumption)")

    cosmos = CosmosDb("Cosmos DB\n(Serverless)")

    [blob, grid] >> func >> cosmos
    grid >> logic >> cosmos
```

---

### Performance Patterns

#### Cache-Aside Pattern

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices
from diagrams.azure.database import CacheForRedis, SQL

with Diagram("Cache-Aside Pattern", show=False, direction="LR", outformat="svg"):
    app = AppServices("Application")

    with Cluster("Data Layer"):
        cache = CacheForRedis("Redis Cache\n(hot data)")
        db = SQL("SQL Database\n(source of truth)")

    app >> Edge(label="1. Check cache") >> cache
    app >> Edge(label="2. Cache miss", style="dashed") >> db
    db >> Edge(label="3. Populate cache", style="dashed") >> cache
```

#### CDN with Edge Caching

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.networking import FrontDoorAndCDNProfiles
from diagrams.azure.compute import AppServices
from diagrams.azure.storage import BlobStorage
from diagrams.onprem.client import Users

with Diagram("CDN Edge Caching", show=False, direction="LR", outformat="svg"):
    users = Users("Global Users")

    cdn = FrontDoorAndCDNProfiles("Azure CDN\n(edge caching)")

    with Cluster("Origin"):
        app = AppServices("API")
        blob = BlobStorage("Static Assets")

    users >> cdn >> [app, blob]
```

#### CQRS with Event Sourcing

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import FunctionApps
from diagrams.azure.integration import ServiceBus, EventGridTopics
from diagrams.azure.database import CosmosDb, SQL

with Diagram("CQRS Pattern", show=False, direction="LR", outformat="svg"):
    with Cluster("Command Side"):
        cmd_api = FunctionApps("Command API")
        event_store = CosmosDb("Event Store")

    bus = ServiceBus("Event Bus")

    with Cluster("Query Side"):
        query_api = FunctionApps("Query API")
        read_db = SQL("Read Model\n(optimized)")

    cmd_api >> event_store >> bus >> query_api
    bus >> read_db
    query_api >> read_db
```

---

### Operational Excellence Patterns

#### GitOps Deployment

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.devops import Repos, Pipelines
from diagrams.azure.compute import AKS, ACR

with Diagram("GitOps Deployment", show=False, direction="LR", outformat="svg"):
    with Cluster("Source Control"):
        repo = Repos("Git Repository")

    with Cluster("CI/CD"):
        pipeline = Pipelines("Azure Pipelines")

    with Cluster("Registry"):
        acr = ACR("Container Registry")

    with Cluster("Kubernetes"):
        with Cluster("Flux/ArgoCD"):
            aks = AKS("AKS Cluster")

    repo >> pipeline >> acr >> aks
    repo >> Edge(label="GitOps sync", style="dashed") >> aks
```

#### Observability Stack

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AKS
from diagrams.azure.monitor import ApplicationInsights, LogAnalyticsWorkspaces
from diagrams.azure.security import Sentinel

with Diagram("Observability Stack", show=False, direction="TB", outformat="svg"):
    with Cluster("Applications"):
        aks = AKS("AKS + Services")

    with Cluster("Observability Platform"):
        insights = ApplicationInsights("App Insights\n(APM)")
        logs = LogAnalyticsWorkspaces("Log Analytics\n(Logs)")
        sentinel = Sentinel("Sentinel\n(SIEM)")

    aks >> Edge(label="traces") >> insights
    aks >> Edge(label="logs") >> logs
    [insights, logs] >> sentinel
```

#### Blue-Green Deployment

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.networking import FrontDoorAndCDNProfiles
from diagrams.azure.compute import AppServices

with Diagram("Blue-Green Deployment", show=False, direction="TB", outformat="svg"):
    fd = FrontDoorAndCDNProfiles("Traffic Manager")

    with Cluster("Production Slots"):
        with Cluster("Blue (Current)"):
            blue = AppServices("v1.0")

        with Cluster("Green (New)"):
            green = AppServices("v1.1")

    fd >> Edge(label="100%") >> blue
    fd >> Edge(label="0%", style="dashed") >> green
```
