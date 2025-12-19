# ---------------------------------------------------------------------
# vista/app/main.py
# ---------------------------------------------------------------------
# VistA RPC Broker Simulator - FastAPI Application
# Main entry point for the Vista RPC Broker HTTP service
# ---------------------------------------------------------------------

import logging
import asyncio
import random
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from vista.app.services import DataLoader, RPCRegistry, RPCExecutionError
from vista.app.handlers import PatientInquiryHandler, LatestVitalsHandler

# Add project root to Python path for config import
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from config import VISTA_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="VistA RPC Broker Simulator",
    description="HTTP-based VistA Remote Procedure Call (RPC) simulation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


def load_sites_config() -> Dict[str, Dict[str, str]]:
    """
    Load site configurations from sites.json.

    Returns:
        Dictionary mapping sta3n to site metadata (name, description)

    Raises:
        FileNotFoundError: If sites.json is not found
        json.JSONDecodeError: If sites.json contains invalid JSON

    Example:
        {
            "200": {"name": "ALEXANDRIA", "sta3n": "200", "description": "..."},
            "500": {"name": "ANCHORAGE", "sta3n": "500", "description": "..."},
            ...
        }
    """
    config_path = Path(__file__).parent / "config" / "sites.json"

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Convert list to dictionary keyed by sta3n
        sites = {}
        for site in config.get("sites", []):
            sta3n = site["sta3n"]
            sites[sta3n] = {
                "name": site["name"],
                "sta3n": sta3n,
                "description": site.get("description", "")
            }

        logger.info(f"Loaded {len(sites)} sites from {config_path}")
        return sites

    except FileNotFoundError:
        logger.error(f"Sites configuration not found at {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in sites configuration: {e}")
        raise
    except KeyError as e:
        logger.error(f"Missing required field in sites configuration: {e}")
        raise


# Load site configurations from JSON file
SITES = load_sites_config()

# Global registry per site
# Each site gets its own DataLoader and RPCRegistry
site_registries: Dict[str, Dict[str, Any]] = {}


# Request/Response Models
class RPCRequest(BaseModel):
    """RPC request model"""
    name: str = Field(..., description="RPC name (e.g., 'ORWPT PTINQ')")
    params: List[Any] = Field(default_factory=list, description="RPC parameters")


class RPCResponse(BaseModel):
    """RPC response model"""
    success: bool = Field(..., description="Whether RPC execution succeeded")
    response: Optional[str] = Field(None, description="VistA-formatted response string")
    error: Optional[str] = Field(None, description="Error message if failed")
    site: str = Field(..., description="Site station number")
    rpc: str = Field(..., description="RPC name executed")


class SiteInfo(BaseModel):
    """Site information model"""
    sta3n: str = Field(..., description="Station number")
    name: str = Field(..., description="Site name")
    rpcs_registered: int = Field(..., description="Number of registered RPCs")
    patients_registered: int = Field(..., description="Number of registered patients")


def initialize_site(sta3n: str) -> Dict[str, Any]:
    """
    Initialize a VistA site with DataLoader and RPCRegistry.

    Args:
        sta3n: Station number

    Returns:
        Dictionary containing data_loader and registry
    """
    logger.info(f"Initializing site {sta3n}...")

    # Create DataLoader for this site
    data_loader = DataLoader(site_sta3n=sta3n)

    # Create RPC Registry
    registry = RPCRegistry()

    # Register RPC handlers
    # TODO: In Phase 3-5, register additional handlers here
    registry.register(PatientInquiryHandler())
    registry.register(LatestVitalsHandler())

    logger.info(
        f"Site {sta3n} initialized: "
        f"{registry.count()} RPCs, "
        f"{len(data_loader.get_registered_patients())} patients"
    )

    return {
        "data_loader": data_loader,
        "registry": registry,
        "sta3n": sta3n,
        "name": SITES[sta3n]["name"]
    }


@app.on_event("startup")
async def startup_event():
    """Initialize all sites on application startup"""
    logger.info("Starting VistA RPC Broker Simulator...")

    for sta3n in SITES.keys():
        try:
            site_registries[sta3n] = initialize_site(sta3n)
        except Exception as e:
            logger.error(f"Failed to initialize site {sta3n}: {e}")
            raise

    logger.info(f"VistA RPC Broker ready: {len(site_registries)} sites initialized")


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "service": "VistA RPC Broker Simulator",
        "version": "1.0.0",
        "status": "running",
        "sites": len(site_registries),
        "endpoints": {
            "rpc_execute": "POST /rpc/execute?site={sta3n}",
            "sites": "GET /sites",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "sites_initialized": len(site_registries),
        "sites": list(site_registries.keys())
    }


@app.get("/sites", response_model=List[SiteInfo])
async def list_sites():
    """
    List all available VistA sites.

    Returns:
        List of site information including registered RPCs and patients
    """
    sites = []
    for sta3n, site_data in site_registries.items():
        sites.append(SiteInfo(
            sta3n=sta3n,
            name=site_data["name"],
            rpcs_registered=site_data["registry"].count(),
            patients_registered=len(site_data["data_loader"].get_registered_patients())
        ))

    return sites


@app.post("/rpc/execute", response_model=RPCResponse)
async def execute_rpc(
    request: RPCRequest,
    site: str = Query(..., description="Site station number (e.g., '200', '500', '630')")
):
    """
    Execute a VistA RPC at a specific site.

    Args:
        request: RPC request containing name and parameters
        site: Site station number (query parameter)

    Returns:
        RPCResponse with VistA-formatted response or error

    Example:
        POST /rpc/execute?site=200
        {
            "name": "ORWPT PTINQ",
            "params": ["ICN100001"]
        }

        Response:
        {
            "success": true,
            "response": "DOOREE,ADAM^666-12-6789^2800102^M^VETERAN",
            "error": null,
            "site": "200",
            "rpc": "ORWPT PTINQ"
        }
    """
    # Validate site
    if site not in site_registries:
        raise HTTPException(
            status_code=404,
            detail=f"Site {site} not found. Available sites: {list(site_registries.keys())}"
        )

    site_data = site_registries[site]
    registry = site_data["registry"]
    data_loader = site_data["data_loader"]

    # Build context for RPC execution
    context = {
        "data_loader": data_loader,
        "site_sta3n": site,
        "request_id": f"{site}:{request.name}"
    }

    try:
        # Simulate network/processing latency (mimics real VistA RPC calls)
        if VISTA_CONFIG.get("rpc_latency_enabled", True):
            latency_min = VISTA_CONFIG.get("rpc_latency_min", 1.0)
            latency_max = VISTA_CONFIG.get("rpc_latency_max", 3.0)
            delay = random.uniform(latency_min, latency_max)
            logger.debug(f"Simulating {delay:.2f}s latency for {site}:{request.name}")
            await asyncio.sleep(delay)

        # Execute RPC via registry
        response = registry.dispatch(
            rpc_name=request.name,
            params=request.params,
            context=context
        )

        logger.info(f"RPC executed successfully: {site}:{request.name}")

        return RPCResponse(
            success=True,
            response=response,
            error=None,
            site=site,
            rpc=request.name
        )

    except RPCExecutionError as e:
        logger.error(f"RPC execution error: {site}:{request.name} - {e.message}")

        return RPCResponse(
            success=False,
            response=None,
            error=e.message,
            site=site,
            rpc=request.name
        )

    except Exception as e:
        logger.error(f"Unexpected error executing RPC: {site}:{request.name} - {e}", exc_info=True)

        return RPCResponse(
            success=False,
            response=None,
            error=f"Internal server error: {str(e)}",
            site=site,
            rpc=request.name
        )


# Development server entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
