#!/usr/bin/env python3
"""
Azure Architecture Diagram Generator
Interactive script for quickly generating professional diagrams.

Usage:
    python generate_diagram.py --name "Customer Integration" --pattern api-led --output customer-arch
    python generate_diagram.py --interactive
"""

import argparse
import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Full whitelist of allowed imports for diagram generation
ALLOWED_IMPORTS = {
    # =============================================
    # DIAGRAMS LIBRARY (core + all submodules)
    # =============================================
    "diagrams",

    # Azure services (all categories)
    "diagrams.azure",
    "diagrams.azure.aimachinelearning",
    "diagrams.azure.analytics",
    "diagrams.azure.azurestack",
    "diagrams.azure.blockchain",
    "diagrams.azure.compute",
    "diagrams.azure.containers",
    "diagrams.azure.database",
    "diagrams.azure.databases",
    "diagrams.azure.devops",
    "diagrams.azure.general",
    "diagrams.azure.identity",
    "diagrams.azure.integration",
    "diagrams.azure.intune",
    "diagrams.azure.iot",
    "diagrams.azure.managementgovernance",
    "diagrams.azure.migration",
    "diagrams.azure.mixedreality",
    "diagrams.azure.ml",
    "diagrams.azure.monitor",
    "diagrams.azure.network",
    "diagrams.azure.networking",
    "diagrams.azure.security",
    "diagrams.azure.storage",
    "diagrams.azure.web",

    # On-premises components
    "diagrams.onprem",
    "diagrams.onprem.client",
    "diagrams.onprem.compute",
    "diagrams.onprem.database",
    "diagrams.onprem.network",

    # Generic components
    "diagrams.generic",
    "diagrams.generic.blank",
    "diagrams.generic.compute",
    "diagrams.generic.database",
    "diagrams.generic.storage",

    # Programming/flowchart shapes
    "diagrams.programming",
    "diagrams.programming.flowchart",

    # SaaS integrations (Teams, SAP, Salesforce, etc.)
    "diagrams.saas",
    "diagrams.saas.chat",
    "diagrams.saas.erp",
    "diagrams.saas.cdn",

    # Custom icons
    "diagrams.custom",

    # =============================================
    # DIRECT GRAPHVIZ (process flows, ERDs)
    # =============================================
    "graphviz",

    # =============================================
    # MATPLOTLIB (Gantt charts, timelines)
    # =============================================
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.patches",
    "matplotlib.dates",

    # =============================================
    # NUMPY (timeline calculations)
    # =============================================
    "numpy",

    # =============================================
    # SVG LIBRARIES (wireframes)
    # =============================================
    "svgwrite",
    "cairosvg",  # SVG to PNG conversion

    # =============================================
    # SAFE STDLIB (data/time handling)
    # =============================================
    "datetime",
    "collections",
    "pathlib",   # Path handling for output files
}

# Blocked dangerous builtins
BLOCKED_BUILTINS = {
    "exec", "eval", "compile", "open", "__import__",
    "globals", "locals", "vars", "dir",
    "getattr", "setattr", "delattr", "hasattr",
    "breakpoint", "input", "help",
}

# Blocked dangerous attribute access patterns
BLOCKED_ATTRIBUTES = {
    "__class__", "__bases__", "__subclasses__", "__globals__",
    "__code__", "__builtins__", "__import__", "__loader__",
    "__spec__", "__dict__", "__mro__", "__init_subclass__",
}

# Explicitly blocked imports (even if partial match)
BLOCKED_IMPORTS = {
    "os", "sys", "subprocess", "socket", "urllib", "requests",
    "http", "pickle", "shelve", "ctypes", "importlib",
    "shutil", "glob", "fnmatch", "io", "builtins",
    "code", "codeop", "marshal", "types",
}

# Allowed output directories
ALLOWED_OUTPUT_DIRS = {
    ".",
    "/mnt/user-data/outputs",
    "/tmp",
    "~/outputs",
}

# Execution timeout in seconds
EXECUTION_TIMEOUT = 60


# =============================================================================
# SECURITY VALIDATION
# =============================================================================

class CodeValidationError(Exception):
    """Raised when code fails security validation."""
    pass


class CodeValidator(ast.NodeVisitor):
    """AST-based code validator that checks for security violations."""

    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        """Check import statements."""
        for alias in node.names:
            module_name = alias.name
            if not self._is_allowed_import(module_name):
                self.errors.append(f"Blocked import: '{module_name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Check from ... import statements."""
        if node.module:
            if not self._is_allowed_import(node.module):
                self.errors.append(f"Blocked import: '{node.module}'")
        self.generic_visit(node)

    def visit_Call(self, node):
        """Check function calls for blocked builtins."""
        if isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_BUILTINS:
                self.errors.append(f"Blocked builtin call: '{node.func.id}()'")
        elif isinstance(node.func, ast.Attribute):
            # Check for dangerous method calls
            if node.func.attr in BLOCKED_BUILTINS:
                self.errors.append(f"Blocked builtin call: '{node.func.attr}()'")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Check attribute access for dangerous patterns."""
        if node.attr in BLOCKED_ATTRIBUTES:
            self.errors.append(f"Blocked attribute access: '{node.attr}'")
        self.generic_visit(node)

    def visit_Name(self, node):
        """Check for direct access to blocked names."""
        if node.id in BLOCKED_BUILTINS:
            # Only flag if used as a call (handled in visit_Call)
            pass
        self.generic_visit(node)

    def _is_allowed_import(self, module_name):
        """Check if a module import is allowed."""
        # Check if it's explicitly blocked
        base_module = module_name.split('.')[0]
        if base_module in BLOCKED_IMPORTS:
            return False

        # Check if it matches allowed imports
        if module_name in ALLOWED_IMPORTS:
            return True

        # Check if it's a submodule of an allowed import
        for allowed in ALLOWED_IMPORTS:
            if module_name.startswith(allowed + "."):
                return True

        return False

    def validate(self, code):
        """Validate code and return list of errors."""
        self.errors = []
        try:
            tree = ast.parse(code)
            self.visit(tree)
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
        return self.errors


def validate_code(code):
    """
    Validate code for security issues.

    Args:
        code: Python code string to validate

    Returns:
        tuple: (is_valid, errors)
    """
    validator = CodeValidator()
    errors = validator.validate(code)
    return len(errors) == 0, errors


def sanitize_name(name):
    """
    Sanitize diagram name to prevent injection.
    Only allows alphanumeric characters, spaces, hyphens, and basic punctuation.

    Args:
        name: User-provided diagram name

    Returns:
        Sanitized name string
    """
    # Allow only safe characters
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.,!?()\'"]', '', name)
    # Limit length
    return sanitized[:200]


def sanitize_output(output):
    """
    Sanitize output filename to prevent path traversal.

    Args:
        output: User-provided output filename

    Returns:
        Sanitized filename string
    """
    # Remove any path separators and dangerous characters
    sanitized = re.sub(r'[/\\:*?"<>|]', '', output)
    # Remove any path traversal attempts
    sanitized = sanitized.replace('..', '')
    # Limit length
    return sanitized[:100]


def validate_output_path(output_path):
    """
    Validate that output path is in an allowed directory.

    Args:
        output_path: Path to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    path = Path(output_path).resolve()

    # Check against allowed directories
    for allowed in ALLOWED_OUTPUT_DIRS:
        allowed_path = Path(allowed).expanduser().resolve()
        try:
            path.relative_to(allowed_path)
            return True, None
        except ValueError:
            continue

    # Also allow current working directory
    try:
        path.relative_to(Path.cwd())
        return True, None
    except ValueError:
        pass

    return False, f"Output path not allowed. Allowed directories: {', '.join(ALLOWED_OUTPUT_DIRS)}"


def execute_diagram_code(code, timeout=EXECUTION_TIMEOUT):
    """
    Execute validated diagram code in an isolated subprocess.

    Args:
        code: Validated Python code to execute
        timeout: Maximum execution time in seconds

    Returns:
        tuple: (success, output_or_error)
    """
    # First validate the code
    is_valid, errors = validate_code(code)
    if not is_valid:
        return False, f"Code validation failed:\n" + "\n".join(f"  - {e}" for e in errors)

    # Write code to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        # Execute in subprocess with minimal environment
        env = {
            'PATH': subprocess.os.environ.get('PATH', ''),
            'PYTHONPATH': subprocess.os.environ.get('PYTHONPATH', ''),
            'HOME': subprocess.os.environ.get('HOME', ''),
            'TEMP': subprocess.os.environ.get('TEMP', ''),
            'TMP': subprocess.os.environ.get('TMP', ''),
            'USERPROFILE': subprocess.os.environ.get('USERPROFILE', ''),
        }

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=Path.cwd()
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Execution error:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return False, f"Execution timed out after {timeout} seconds"
    except Exception as e:
        return False, f"Execution failed: {str(e)}"
    finally:
        # Clean up temporary file
        try:
            Path(temp_path).unlink()
        except:
            pass


# =============================================================================
# PATTERN TEMPLATES
# =============================================================================

# Pattern templates - easily extensible
PATTERNS = {
    "api-led": {
        "description": "API-Led Connectivity (3-tier: Experience, Process, System)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import APIManagement, LogicApps, ServiceBus
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import CosmosDb, SQL
from diagrams.azure.storage import BlobStorage
from diagrams.azure.security import KeyVaults
from diagrams.onprem.client import Users

with Diagram("{name}", show=False, filename="{output}", direction="LR", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):
    users = Users("API Consumers")

    with Cluster("Experience Layer"):
        apim = APIManagement("API Management")

    with Cluster("Process Layer"):
        logic = LogicApps("Orchestration")
        func = FunctionApps("Transformation")

    with Cluster("System Layer"):
        bus = ServiceBus("Service Bus")

    with Cluster("Data Layer"):
        cosmos = CosmosDb("Cosmos DB")
        sql = SQL("Azure SQL")
        blob = BlobStorage("Blob Storage")

    kv = KeyVaults("Key Vault")

    users >> apim >> logic >> bus >> func
    func >> [cosmos, sql, blob]
    logic >> Edge(style="dashed") >> kv
'''
    },

    "hybrid": {
        "description": "Hybrid Integration (On-premises to Azure)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import LogicApps, ServiceBus, DataFactories
from diagrams.azure.networking import OnPremisesDataGateways
from diagrams.azure.storage import DataLakeStorage, BlobStorage
from diagrams.azure.database import CosmosDb
from diagrams.azure.security import KeyVaults
from diagrams.onprem.database import MSSQL
from diagrams.onprem.compute import Server

with Diagram("{name}", show=False, filename="{output}", direction="LR", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    with Cluster("On-Premises"):
        erp = Server("ERP System")
        sql = MSSQL("SQL Server")
        files = Server("File Server")

    gateway = OnPremisesDataGateways("Data Gateway")

    with Cluster("Azure Integration"):
        logic = LogicApps("Logic Apps")
        adf = DataFactories("Data Factory")
        bus = ServiceBus("Service Bus")

    with Cluster("Azure Data"):
        cosmos = CosmosDb("Cosmos DB")
        lake = DataLakeStorage("Data Lake")
        blob = BlobStorage("Blob Storage")

    kv = KeyVaults("Key Vault")

    [erp, sql] >> gateway >> logic >> bus
    files >> gateway >> adf >> lake
    logic >> cosmos
    adf >> blob
    logic >> Edge(style="dashed") >> kv
'''
    },

    "event-driven": {
        "description": "Event-Driven Architecture (Pub/Sub with multiple handlers)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import ServiceBus, EventGridTopics, LogicApps
from diagrams.azure.compute import FunctionApps, AppServices
from diagrams.azure.database import CosmosDb
from diagrams.azure.storage import BlobStorage
from diagrams.azure.monitor import ApplicationInsights

with Diagram("{name}", show=False, filename="{output}", direction="TB", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    with Cluster("Event Producers"):
        app1 = AppServices("Order Service")
        app2 = AppServices("Inventory Service")

    with Cluster("Event Routing"):
        bus = ServiceBus("Service Bus Topics")
        grid = EventGridTopics("Event Grid")

    with Cluster("Event Handlers"):
        func1 = FunctionApps("Notifier")
        func2 = FunctionApps("Analytics")
        logic = LogicApps("Fulfillment")
        func3 = FunctionApps("Audit")

    with Cluster("Data"):
        cosmos = CosmosDb("Event Store")
        blob = BlobStorage("Archive")

    insights = ApplicationInsights("Monitoring")

    [app1, app2] >> bus >> [func1, func2, logic]
    app1 >> grid >> func3
    [func1, logic] >> cosmos
    func3 >> blob
    func2 >> Edge(style="dotted") >> insights
'''
    },

    "microservices": {
        "description": "Microservices with Service Bus (Domain-driven design)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.azure.compute import ContainerApps, FunctionApps
from diagrams.azure.database import CosmosDb, SQL, CacheForRedis
from diagrams.azure.monitor import ApplicationInsights

with Diagram("{name}", show=False, filename="{output}", direction="TB", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    apim = APIManagement("API Gateway")

    with Cluster("Microservices"):
        with Cluster("Order Domain"):
            order_svc = ContainerApps("Order Service")
            order_db = CosmosDb("Orders")

        with Cluster("Product Domain"):
            product_svc = ContainerApps("Product Service")
            product_db = SQL("Products")

        with Cluster("Notification Domain"):
            notif_svc = FunctionApps("Notification Service")

    bus = ServiceBus("Event Bus")
    cache = CacheForRedis("Cache")
    insights = ApplicationInsights("App Insights")

    apim >> [order_svc, product_svc]
    order_svc >> order_db
    product_svc >> product_db
    order_svc >> bus >> [product_svc, notif_svc]
    [order_svc, product_svc] >> cache
    [order_svc, product_svc, notif_svc] >> Edge(style="dotted") >> insights
'''
    },

    "b2b-edi": {
        "description": "B2B/EDI Integration (Trading partners with Integration Accounts)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import APIManagement, LogicApps, IntegrationAccounts, ServiceBus
from diagrams.azure.storage import BlobStorage
from diagrams.azure.security import KeyVaults
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server

with Diagram("{name}", show=False, filename="{output}", direction="LR", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    with Cluster("Trading Partners"):
        partner1 = Client("Supplier A")
        partner2 = Client("Supplier B")
        partner3 = Client("Customer")

    apim = APIManagement("AS2/SFTP Gateway")

    with Cluster("B2B Processing"):
        ia = IntegrationAccounts("Integration Account\\n(Maps, Schemas, Certs)")
        logic = LogicApps("EDI Processing")
        bus = ServiceBus("Message Queue")

    with Cluster("Backend"):
        erp = Server("ERP System")
        archive = BlobStorage("EDI Archive")

    kv = KeyVaults("Certificates & Keys")

    [partner1, partner2, partner3] >> apim >> logic
    logic - Edge(style="dashed") - ia
    logic >> bus >> erp
    logic >> archive
    ia >> Edge(style="dashed") >> kv
'''
    },

    "data-pipeline": {
        "description": "Data Pipeline (ETL/ELT with Data Factory and Synapse)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import DataFactories
from diagrams.azure.analytics import AzureDatabricks, AzureSynapseAnalytics
from diagrams.azure.storage import DataLakeStorage, BlobStorage
from diagrams.azure.database import SQL
from diagrams.onprem.database import MSSQL, Oracle

with Diagram("{name}", show=False, filename="{output}", direction="LR", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    with Cluster("Data Sources"):
        sql_src = MSSQL("On-Prem SQL")
        oracle = Oracle("Oracle")
        blob_src = BlobStorage("File Drops")

    with Cluster("Ingestion"):
        adf = DataFactories("Data Factory")

    with Cluster("Data Lake"):
        raw = DataLakeStorage("Raw Zone")
        curated = DataLakeStorage("Curated Zone")

    with Cluster("Transform"):
        databricks = AzureDatabricks("Databricks")

    with Cluster("Serve"):
        synapse = AzureSynapseAnalytics("Synapse Analytics")
        sql_dw = SQL("Azure SQL DW")

    [sql_src, oracle, blob_src] >> adf >> raw
    raw >> databricks >> curated
    curated >> [synapse, sql_dw]
'''
    },

    "secure-private": {
        "description": "Secure Architecture (Private Endpoints and VNet Integration)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import APIManagement, LogicApps, ServiceBus
from diagrams.azure.compute import FunctionApps
from diagrams.azure.networking import ApplicationGateways, VirtualNetworks
from diagrams.azure.database import SQL, CosmosDb
from diagrams.azure.storage import BlobStorage
from diagrams.azure.security import KeyVaults
from diagrams.onprem.client import Users

with Diagram("{name}", show=False, filename="{output}", direction="TB", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    users = Users("Users")
    appgw = ApplicationGateways("App Gateway + WAF")

    with Cluster("Virtual Network"):
        with Cluster("Integration Subnet"):
            apim = APIManagement("APIM (Internal)")
            logic = LogicApps("Logic Apps")
            func = FunctionApps("Functions")

        with Cluster("Data Subnet (Private Endpoints)"):
            sql = SQL("Azure SQL")
            cosmos = CosmosDb("Cosmos DB")
            blob = BlobStorage("Storage")
            bus = ServiceBus("Service Bus")
            kv = KeyVaults("Key Vault")

    users >> appgw >> apim >> [logic, func]
    logic >> bus
    logic >> [sql, cosmos, blob]
    func >> [sql, cosmos]
    logic >> Edge(style="dashed") >> kv
    func >> Edge(style="dashed") >> kv
'''
    },

    "multi-region": {
        "description": "Multi-Region HA (Geo-redundant with Front Door)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import APIManagement, LogicApps, ServiceBus
from diagrams.azure.networking import FrontDoorAndCDNProfiles
from diagrams.azure.database import CosmosDb, SQL

with Diagram("{name}", show=False, filename="{output}", direction="TB", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    frontdoor = FrontDoorAndCDNProfiles("Azure Front Door")

    with Cluster("UK South (Primary)"):
        apim1 = APIManagement("APIM")
        logic1 = LogicApps("Logic Apps")
        bus1 = ServiceBus("Service Bus")
        sql1 = SQL("SQL Primary")

    with Cluster("UK West (DR)"):
        apim2 = APIManagement("APIM")
        logic2 = LogicApps("Logic Apps")
        bus2 = ServiceBus("Service Bus")
        sql2 = SQL("SQL Secondary")

    cosmos = CosmosDb("Cosmos DB\\n(Multi-Region)")

    frontdoor >> [apim1, apim2]
    apim1 >> logic1 >> bus1
    apim2 >> logic2 >> bus2
    logic1 >> cosmos
    logic2 >> cosmos
    sql1 - Edge(style="dashed", label="Geo-Rep") - sql2
'''
    },

    "iot-streaming": {
        "description": "IoT & Streaming (Real-time data ingestion and processing)",
        "template": '''
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.iot import IotHub, IotEdge
from diagrams.azure.analytics import EventHubs, StreamAnalyticsJobs
from diagrams.azure.compute import FunctionApps
from diagrams.azure.database import CosmosDb
from diagrams.azure.storage import DataLakeStorage
from diagrams.azure.ml import MachineLearningServiceWorkspaces

with Diagram("{name}", show=False, filename="{output}", direction="LR", outformat="svg",
             graph_attr={{"fontsize": "20", "bgcolor": "white", "pad": "0.5"}}):

    with Cluster("Edge"):
        edge = IotEdge("IoT Edge")

    with Cluster("Ingestion"):
        iot = IotHub("IoT Hub")
        eh = EventHubs("Event Hubs")

    with Cluster("Processing"):
        asa = StreamAnalyticsJobs("Stream Analytics")
        func = FunctionApps("Alerting")

    with Cluster("Storage"):
        cosmos = CosmosDb("Hot Store")
        lake = DataLakeStorage("Cold Store")

    ml = MachineLearningServiceWorkspaces("ML Workspace")

    edge >> iot >> asa
    asa >> [cosmos, lake, func]
    eh >> asa
    lake >> ml
'''
    },
}


# =============================================================================
# DIAGRAM GENERATION
# =============================================================================

def generate_diagram(name: str, pattern: str, output: str):
    """Generate a diagram from a pattern template."""
    if pattern not in PATTERNS:
        print(f"Error: Unknown pattern '{pattern}'")
        print(f"Available patterns: {', '.join(PATTERNS.keys())}")
        sys.exit(1)

    # Sanitize inputs
    safe_name = sanitize_name(name)
    safe_output = sanitize_output(output)

    # Validate output path
    is_valid, error = validate_output_path(safe_output)
    if not is_valid:
        print(f"Error: {error}")
        sys.exit(1)

    template = PATTERNS[pattern]["template"]
    code = template.format(name=safe_name, output=safe_output)

    # Execute with security validation
    success, result = execute_diagram_code(code)

    if success:
        print(f"Generated: {safe_output}.svg")
    else:
        print(f"Error generating diagram:\n{result}")
        sys.exit(1)


def interactive_mode():
    """Interactive diagram generation."""
    print("\n Azure Architecture Diagram Generator")
    print("=" * 50)

    # Show available patterns
    print("\nAvailable patterns:")
    for i, (key, val) in enumerate(PATTERNS.items(), 1):
        print(f"  {i}. {key}: {val['description']}")

    # Get pattern selection
    print()
    choice = input("Select pattern (number or name): ").strip()

    # Handle numeric or name input
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(PATTERNS):
            pattern = list(PATTERNS.keys())[idx]
        else:
            print("Invalid selection")
            sys.exit(1)
    else:
        pattern = choice.lower().replace(" ", "-")

    if pattern not in PATTERNS:
        print(f"Unknown pattern: {pattern}")
        sys.exit(1)

    # Get diagram name
    name = input("Diagram title [Azure Architecture]: ").strip()
    if not name:
        name = "Azure Architecture"

    # Get output filename
    output = input("Output filename [architecture]: ").strip()
    if not output:
        output = "architecture"

    # Remove extension if provided
    output = output.replace(".svg", "").replace(".png", "")

    print(f"\nGenerating {pattern} diagram: '{name}'...")
    generate_diagram(name, pattern, output)


def list_patterns():
    """List all available patterns."""
    print("\n Available Architecture Patterns")
    print("=" * 50)
    for key, val in PATTERNS.items():
        print(f"\n  {key}")
        print(f"    {val['description']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Azure architecture diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive
  %(prog)s --list
  %(prog)s --name "Customer Portal" --pattern api-led --output customer-portal
  %(prog)s -n "Data Platform" -p data-pipeline -o data-arch
        """
    )

    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Interactive mode")
    parser.add_argument("-l", "--list", action="store_true",
                        help="List available patterns")
    parser.add_argument("-n", "--name", type=str,
                        help="Diagram title")
    parser.add_argument("-p", "--pattern", type=str,
                        help="Pattern name (e.g., api-led, hybrid, event-driven)")
    parser.add_argument("-o", "--output", type=str, default="architecture",
                        help="Output filename (without extension)")

    args = parser.parse_args()

    if args.list:
        list_patterns()
    elif args.interactive:
        interactive_mode()
    elif args.name and args.pattern:
        generate_diagram(args.name, args.pattern, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
