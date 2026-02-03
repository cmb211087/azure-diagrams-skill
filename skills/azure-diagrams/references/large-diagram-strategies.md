# Large Diagram Strategies

Guidance for managing complex Azure architecture diagrams with 50+ nodes.

## When to Split Diagrams

### Signs Your Diagram is Too Large

| Symptom | Threshold | Action |
|---------|-----------|--------|
| Render time | > 30 seconds | Split into views |
| Node overlap | Any overlapping | Increase spacing or split |
| Unreadable labels | Text too small to read | Reduce scope |
| File size | > 2MB (PNG) | Use SVG or split |
| Cognitive load | Can't understand at a glance | Simplify |

### Recommended Approach by Node Count

| Node Count | Strategy | Diagram Count |
|------------|----------|---------------|
| < 25 | Single diagram | 1 |
| 25-50 | Increase spacing, consider 2 views | 1-2 |
| 50-75 | Split into 3-4 views (network/app/data/security) | 3-4 |
| 75-100 | C4-style hierarchy + view splitting | 4-6 |
| > 100 | Full C4 hierarchy with detail diagrams | 6+ |

---

## Strategy 1: View-Based Splitting

Split your architecture into logical views, each focused on a specific concern.

### Network View

Focus: VNets, subnets, NSGs, firewalls, gateways, peering

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.network import (
    VirtualNetworks, Firewall, ApplicationGateway,
    VirtualNetworkGateways, Bastions, PrivateEndpoint
)

with Diagram("Architecture - Network View", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "1.2", "ranksep": "1.5"}):

    with Cluster("Hub VNet (10.0.0.0/16)"):
        firewall = Firewall("Azure Firewall")
        bastion = Bastions("Bastion")
        vpn = VirtualNetworkGateways("VPN Gateway")

    with Cluster("Spoke 1 - Web (10.1.0.0/16)"):
        with Cluster("Frontend Subnet"):
            appgw = ApplicationGateway("App Gateway")
        with Cluster("Backend Subnet"):
            pe1 = PrivateEndpoint("Private Endpoints")

    with Cluster("Spoke 2 - Data (10.2.0.0/16)"):
        with Cluster("Data Subnet"):
            pe2 = PrivateEndpoint("Private Endpoints")

    vpn >> firewall
    appgw >> Edge(label="Peering") >> firewall
    pe1 >> Edge(label="Peering") >> firewall
    pe2 >> Edge(label="Peering") >> firewall
```

### Application View

Focus: Compute resources, containers, functions, app services

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AKS, FunctionApps, AppServices, ContainerApps
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.azure.containers import ACR

with Diagram("Architecture - Application View", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "1.2", "ranksep": "1.5"}):

    apim = APIManagement("API Management")

    with Cluster("Container Platform"):
        acr = ACR("Container Registry")
        aks = AKS("AKS Cluster")

    with Cluster("Serverless"):
        func_orders = FunctionApps("Order Functions")
        func_notify = FunctionApps("Notification Functions")

    with Cluster("Web Apps"):
        web = AppServices("Frontend")
        api = AppServices("Backend API")

    bus = ServiceBus("Event Bus")

    apim >> [web, api, aks]
    acr >> aks
    [api, aks] >> bus >> [func_orders, func_notify]
```

### Data View

Focus: Databases, storage, data flows, caching

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.database import CosmosDb, SQL, CacheForRedis
from diagrams.azure.storage import BlobStorage, DataLakeStorage
from diagrams.azure.analytics import AzureSynapseAnalytics, AzureDatabricks

with Diagram("Architecture - Data View", show=False, direction="LR", outformat="svg",
             graph_attr={"nodesep": "1.2", "ranksep": "1.5"}):

    with Cluster("Operational Data"):
        cosmos = CosmosDb("Cosmos DB\n(Orders)")
        sql = SQL("Azure SQL\n(Products)")
        redis = CacheForRedis("Redis Cache")

    with Cluster("Analytical Data"):
        lake = DataLakeStorage("Data Lake")
        synapse = AzureSynapseAnalytics("Synapse")
        databricks = AzureDatabricks("Databricks")

    with Cluster("Storage"):
        blob = BlobStorage("Blob Storage")

    [cosmos, sql] >> Edge(label="CDC") >> lake
    lake >> databricks >> synapse
    blob >> lake
```

### Security View

Focus: Identity, Key Vault, Defender, Sentinel, compliance

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.identity import ActiveDirectory, ManagedIdentities, ConditionalAccess
from diagrams.azure.security import KeyVaults, Sentinel, Defender
from diagrams.azure.network import Firewall

with Diagram("Architecture - Security View", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "1.2", "ranksep": "1.5"}):

    with Cluster("Identity Layer"):
        aad = ActiveDirectory("Entra ID")
        ca = ConditionalAccess("Conditional Access")
        mi = ManagedIdentities("Managed Identities")

    with Cluster("Secrets Management"):
        kv = KeyVaults("Key Vault")

    with Cluster("Network Security"):
        firewall = Firewall("Azure Firewall")

    with Cluster("Security Operations"):
        sentinel = Sentinel("Sentinel")
        defender = Defender("Defender for Cloud")

    aad >> ca >> mi >> kv
    [firewall, kv] >> Edge(style="dotted") >> sentinel
    defender >> sentinel
```

---

## Strategy 2: Hierarchical Clustering (C4-Style)

Use the C4 model approach: Context, Container, Component levels.

### Level 1: System Context

High-level overview showing system boundaries and external actors.

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.general import Resource
from diagrams.onprem.client import Users, Client

with Diagram("E-Commerce Platform - System Context", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "2.0", "ranksep": "2.0"}):

    customers = Users("Customers")
    admins = Users("Admin Users")
    partners = Client("Partner Systems")

    with Cluster("E-Commerce Platform", graph_attr={"style": "rounded", "bgcolor": "#E8F4FD"}):
        platform = Resource("E-Commerce\nPlatform")

    payment = Client("Payment Gateway")
    shipping = Client("Shipping Provider")

    customers >> platform
    admins >> platform
    partners >> Edge(label="API") >> platform
    platform >> payment
    platform >> shipping
```

### Level 2: Container View

Shows major containers (applications, databases, message queues).

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AKS, FunctionApps
from diagrams.azure.database import CosmosDb, SQL
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.azure.storage import BlobStorage
from diagrams.onprem.client import Users

with Diagram("E-Commerce Platform - Container View", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "1.5", "ranksep": "1.5"}):

    users = Users("Customers")

    with Cluster("E-Commerce Platform"):
        apim = APIManagement("API Gateway")

        with Cluster("Applications"):
            web = AKS("Web Frontend")
            api = AKS("API Services")
            worker = FunctionApps("Background Jobs")

        with Cluster("Data Stores"):
            orders_db = CosmosDb("Orders DB")
            products_db = SQL("Products DB")
            files = BlobStorage("File Storage")

        bus = ServiceBus("Event Bus")

    users >> apim >> web >> api
    api >> [orders_db, products_db]
    api >> bus >> worker
    worker >> files
```

### Level 3: Component View (for specific container)

Detailed view of a single container's internal structure.

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import ContainerApps
from diagrams.azure.database import CosmosDb, CacheForRedis
from diagrams.azure.integration import ServiceBus

with Diagram("API Services - Component View", show=False, direction="LR", outformat="svg",
             graph_attr={"nodesep": "1.0", "ranksep": "1.2"}):

    with Cluster("API Services Container"):
        with Cluster("Order Domain"):
            order_api = ContainerApps("Order API")
            order_handler = ContainerApps("Order Handler")

        with Cluster("Product Domain"):
            product_api = ContainerApps("Product API")
            inventory = ContainerApps("Inventory Service")

        with Cluster("User Domain"):
            user_api = ContainerApps("User API")
            auth = ContainerApps("Auth Service")

    cosmos = CosmosDb("Orders")
    cache = CacheForRedis("Cache")
    bus = ServiceBus("Events")

    order_api >> order_handler >> cosmos
    order_handler >> bus
    product_api >> inventory >> cache
    [order_api, product_api] >> auth
```

---

## Strategy 3: Layout Tuning

For diagrams at the 50-75 node threshold, tuning layout parameters can help.

### Recommended Graph Attributes for Large Diagrams

```python
graph_attr = {
    # Increase node spacing
    "nodesep": "1.5",          # Default: 0.25 - horizontal spacing
    "ranksep": "2.0",          # Default: 0.5 - vertical spacing

    # Use spline edges (curves around nodes)
    "splines": "spline",       # Options: spline, ortho, curved, polyline

    # Merge edges where possible
    "concentrate": "true",      # Reduces edge crossing

    # Adjust DPI for readability
    "dpi": "150",              # Lower DPI = smaller file, still readable

    # Add padding
    "pad": "1.0",

    # Aspect ratio hints
    "ratio": "auto",           # Options: auto, fill, compress
}

with Diagram("Large Architecture", show=False, direction="TB", outformat="svg",
             graph_attr=graph_attr):
    # ... your diagram code
```

### Node Attributes for Clarity

```python
node_attr = {
    "fontsize": "10",          # Smaller font for dense diagrams
    "fontname": "Arial",       # Clean, readable font
    "labelloc": "t",           # Labels above icons
}

with Diagram("Large Architecture",
             graph_attr=graph_attr,
             node_attr=node_attr):
    # ...
```

### Cluster Styling for Visual Hierarchy

```python
# Outer clusters - more prominent
outer_cluster_style = {
    "margin": "40",
    "fontsize": "14",
    "fontname": "Arial Bold",
    "bgcolor": "#F0F8FF",
    "style": "rounded",
}

# Inner clusters - subtle
inner_cluster_style = {
    "margin": "20",
    "fontsize": "12",
    "fontname": "Arial",
    "bgcolor": "#FAFAFA",
}

with Cluster("Resource Group", graph_attr=outer_cluster_style):
    with Cluster("Subnet A", graph_attr=inner_cluster_style):
        # ...
```

---

## Strategy 4: Progressive Disclosure

Create a master index diagram linking to detailed diagrams.

### Master Index Diagram

```python
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.general import Resource

with Diagram("Architecture Index", show=False, direction="TB", outformat="svg",
             graph_attr={"nodesep": "2.0", "ranksep": "2.0"}):

    with Cluster("Network Layer\n(See: network-view.svg)"):
        network = Resource("Hub-Spoke\nTopology")

    with Cluster("Application Layer\n(See: app-view.svg)"):
        apps = Resource("Microservices\n& Serverless")

    with Cluster("Data Layer\n(See: data-view.svg)"):
        data = Resource("Databases &\nAnalytics")

    with Cluster("Security Layer\n(See: security-view.svg)"):
        security = Resource("Identity &\nCompliance")

    # Show cross-cutting concerns
    network >> apps >> data
    security >> Edge(style="dashed") >> [network, apps, data]
```

### Navigation Pattern

Include in documentation:

```markdown
## Architecture Diagrams

| Diagram | Focus | File |
|---------|-------|------|
| **Index** | Overview and navigation | `architecture-index.svg` |
| **Network** | VNets, firewalls, connectivity | `network-view.svg` |
| **Application** | Compute, containers, services | `app-view.svg` |
| **Data** | Databases, storage, analytics | `data-view.svg` |
| **Security** | Identity, secrets, compliance | `security-view.svg` |
```

---

## Strategy 5: Simplification Techniques

### Aggregation

Instead of showing every instance, show logical groups.

```python
# DON'T do this (too detailed):
vm1 = VM("web-vm-001")
vm2 = VM("web-vm-002")
vm3 = VM("web-vm-003")
# ... 20 more VMs

# DO this instead:
web_cluster = AKS("Web Tier\n(20 instances)")
```

### Abstraction

Move implementation details to legends or documentation.

```python
from diagrams import Diagram, Cluster
from diagrams.azure.compute import AKS
from diagrams.azure.database import CosmosDb

with Diagram("Simplified View", show=False, outformat="svg"):
    with Cluster("Application Platform*"):
        apps = AKS("Services")

    with Cluster("Data Platform*"):
        data = CosmosDb("Data Stores")

    apps >> data

# Add legend as text:
# * Application Platform includes: AKS (3 clusters),
#   Functions (5 apps), Container Apps (2 envs)
# * Data Platform includes: Cosmos DB, SQL, Redis,
#   Storage Accounts, Data Lake
```

### Representative Patterns

Show one example that represents many similar components.

```python
with Cluster("Microservices (12 services)"):
    # Show 3 representative services
    order = ContainerApps("Order Service")
    product = ContainerApps("Product Service")
    user = ContainerApps("User Service")

    # Text note: "Plus 9 additional domain services"
```

---

## Anti-Patterns to Avoid

### 1. The "Everything" Diagram

**Problem:** Single diagram with 100+ nodes showing every resource.

**Solution:** Split into views or use C4 hierarchy.

### 2. Spaghetti Connections

**Problem:** Every node connects to every other node.

**Solution:**
- Use clusters to group related components
- Show only primary data flows
- Use edge styles to differentiate (solid = data, dashed = config)

### 3. Inconsistent Granularity

**Problem:** Mixing high-level concepts with low-level details.

**Solution:** Maintain consistent abstraction level within each diagram.

### 4. Missing Context

**Problem:** Detailed diagrams without an index or overview.

**Solution:** Always create a context diagram that links to details.

---

## Quick Reference: When to Use Each Strategy

| Situation | Best Strategy |
|-----------|---------------|
| Architecture review | View-based (network/app/data/security) |
| Stakeholder presentation | C4 Level 1-2 (Context + Container) |
| Developer documentation | C4 Level 2-3 (Container + Component) |
| Security audit | Security View + Network View |
| Performance analysis | Application View + Data View |
| Migration planning | Progressive Disclosure with phases |
| Troubleshooting | Component-level detail diagrams |

---

## Templates

### View-Based Split Template

```
project/
├── diagrams/
│   ├── architecture-overview.svg    # C4 Level 1
│   ├── network-view.svg             # Network focus
│   ├── application-view.svg         # Compute focus
│   ├── data-view.svg                # Storage focus
│   └── security-view.svg            # Security focus
└── docs/
    └── architecture.md              # Links all diagrams
```

### C4 Hierarchy Template

```
project/
├── diagrams/
│   ├── 01-system-context.svg        # Level 1
│   ├── 02-container-view.svg        # Level 2
│   ├── 03-api-components.svg        # Level 3 - API detail
│   ├── 03-web-components.svg        # Level 3 - Web detail
│   └── 03-data-components.svg       # Level 3 - Data detail
└── docs/
    └── architecture.md
```
