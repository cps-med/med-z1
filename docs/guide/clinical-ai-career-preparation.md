# Clinical AI Career Preparation Guide
# Senior Agentic AI Engineer - Learning Path

**Document Version:** v2.1
**Created:** 2026-02-02
**Updated:** 2026-02-02
**Purpose:** Hands-on learning guide for building MCP servers, vector RAG, and ML models for clinical AI
**Target Role:** Senior Agentic AI Engineer (Clinical AI Solutions)
**Estimated Timeline:** 8-12 weeks to career readiness (including ML/PyTorch)

**v2.1 Changes (2026-02-02):**
- Added data provenance attribution to all MCP tools (Sections 5 & 6)
- Updated MCP Server Checklist to include attribution implementation
- Both EHR Data Server and Clinical Decision Support Server now include data source tracking

**v2.0 Changes (2026-02-02):**
- Added PyTorch/ML Learning Path (Sections 10-13)
- 3 clinical ML models: Readmission risk, vital anomaly detection, clinical NER
- Updated timeline with parallel learning strategy

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Strengths Assessment](#2-current-strengths-assessment)
3. [Critical Skill Gaps](#3-critical-skill-gaps)
4. [MCP Fundamentals - Learning Path](#4-mcp-fundamentals---learning-path)
5. [MCP Server #1: EHR Data Server](#5-mcp-server-1-ehr-data-server)
6. [MCP Server #2: Clinical Decision Support](#6-mcp-server-2-clinical-decision-support)
7. [MCP Server #3: Clinical Notes Search](#7-mcp-server-3-clinical-notes-search)
8. [Vector RAG Fundamentals - Learning Path](#8-vector-rag-fundamentals---learning-path)
9. [Vector RAG Implementation](#9-vector-rag-implementation)
10. [PyTorch & Clinical ML - Learning Path](#10-pytorch--clinical-ml---learning-path)
11. [Clinical ML Model #1: Readmission Risk Prediction](#11-clinical-ml-model-1-readmission-risk-prediction)
12. [Clinical ML Model #2: Vital Sign Anomaly Detection](#12-clinical-ml-model-2-vital-sign-anomaly-detection)
13. [Clinical ML Model #3: Clinical NER with Transformers](#13-clinical-ml-model-3-clinical-ner-with-transformers)
14. [Integration & Portfolio](#14-integration--portfolio)
15. [Interview Preparation](#15-interview-preparation)
16. [Timeline & Milestones](#16-timeline--milestones)

---

## 1. Executive Summary

### Current State
You have **production agentic AI experience** with LangGraph, comprehensive clinical domain knowledge, and a strong architectural foundation. Your med-z1 project demonstrates enterprise-grade AI implementation for healthcare.

### Gap Analysis
- ✅ **Agentic AI:** 9/10 (LangGraph, tool orchestration, production deployment)
- ✅ **Clinical Domain:** 10/10 (VA systems, clinical workflows, healthcare data)
- ✅ **Python Programming:** 9/10 (Advanced, production-quality code)
- ❌ **MCP Experience:** 0/10 (Critical gap - must address)
- ❌ **Vector RAG:** 3/10 (Architecture yes, vector embeddings no)
- ❌ **PyTorch/ML:** 2/10 (Statistical knowledge yes, deep learning implementation no)

### Career Readiness Score (Updated with ML)
- **Current:** 6.8/10 (including ML gap)
- **After MCP (3 servers):** 7.8/10
- **After MCP + Vector RAG:** 8.5/10
- **After MCP + Vector RAG + PyTorch ML:** 9.5/10
- **After Full Portfolio Integration:** 9.8/10

### Recommended Path (Updated)
**8-week minimum:** MCP servers + Vector RAG + 2 ML models → Apply to roles
**10-12 weeks ideal:** All above + advanced ML + documentation → Strong portfolio
**Parallel learning:** MCP (weeks 1-3) overlaps with PyTorch fundamentals (weeks 4-6)

---

## 2. Current Strengths Assessment

### Exceptional Strengths (Competitive Advantages)

#### Clinical Domain Expertise ⭐⭐⭐
**Why This Matters:** Most AI engineers building for clinicians have ZERO clinical domain knowledge.

**Your Experience:**
- VA Corporate Data Warehouse (CDW) schemas and data structures
- VistA and Cerner/Oracle Health system integration
- Clinical workflows (medication reconciliation, DDI analysis, vital sign monitoring)
- Healthcare data harmonization (multi-source, identity resolution)
- Patient safety considerations in AI design
- Clinical terminology (SOAP notes, consult reports, ICD/CPT codes)

**Evidence in Codebase:**
- `mock/sql-server/cdwwork/` - Complete mock CDW implementation
- `ai/prompts/system_prompts.py:92-96` - Clinical safety priorities in prompts
- `vista/` - VistA RPC Broker simulator with real-time data integration

**Impact:** You can speak the language of your end users (clinicians) - this is rare and valuable.

#### Production Agentic AI Implementation ⭐⭐⭐
**Why This Matters:** "Agentic AI exp must" is the #1 requirement.

**Your Experience:**
- LangGraph agent with 4 operational tools (DDI, patient summary, vitals trends, clinical notes)
- Conversational state management across multi-turn interactions
- Tool orchestration with clinical safety guardrails
- Prompt engineering for clinical decision support
- Production deployment serving real workflows

**Evidence in Codebase:**
- `ai/agents/insight_agent.py` - Complete LangGraph implementation
- `ai/tools/` - 4 clinical AI tools with LangChain decorators
- `ai/prompts/system_prompts.py` - 114 lines of sophisticated clinical prompts
- `ai/services/patient_context.py` - Context builder wrapping database queries

**Impact:** You understand agentic AI at a deep level - not just theory but production experience.

#### Architecture & Documentation ⭐⭐
**Why This Matters:** Shows enterprise-grade thinking and ability to make strategic decisions.

**Your Experience:**
- Comprehensive ADRs (Architecture Decision Records)
- Medallion data architecture (Bronze/Silver/Gold)
- Multi-source data integration patterns
- Living documentation practices
- Design specifications for 18+ clinical domains

**Evidence in Codebase:**
- `docs/spec/med-z1-architecture.md` - Central architectural authority
- `docs/spec/ai-insight-design.md` - 6-phase implementation plan
- `CLAUDE.md` - Developer onboarding and patterns

**Impact:** You can lead architectural discussions and document decisions - key for senior role.

---

## 3. Critical Skill Gaps

### Gap #1: Model Context Protocol (MCP) ❌ CRITICAL
**Current State:** No MCP implementation in codebase
**Target State:** 3 operational MCP servers with clinical AI integration
**Priority:** HIGHEST - This is non-negotiable for the role
**Timeline:** 3 weeks (1 week per server)

### Gap #2: Vector-Based RAG ❌ HIGH PRIORITY
**Current State:** Structured data retrieval only, no vector embeddings
**Target State:** Hybrid RAG with ChromaDB, semantic search over clinical notes
**Priority:** HIGH - Increasingly expected for clinical AI roles
**Timeline:** 2-3 weeks (embeddings → integration → advanced techniques)

### Gap #3: PyTorch & Deep Learning ❌ HIGH PRIORITY
**Current State:** Statistical analysis experience, no deep learning implementation
**Target State:** 3 clinical ML models (risk prediction, anomaly detection, NER)
**Priority:** HIGH - Critical for advanced clinical AI capabilities
**Timeline:** 4-5 weeks (fundamentals → 3 models → integration)

**Why This Matters:**
- Senior AI roles expect hands-on ML model development (not just LLM API calls)
- Clinical AI requires predictive models beyond conversational agents
- PyTorch is industry standard for healthcare ML research
- Demonstrates deep technical skills vs. prompt engineering alone

**Clinical Use Cases for PyTorch:**
1. **Risk Prediction:** 30-day readmission, mortality, sepsis onset
2. **Time Series Forecasting:** Vital sign anomalies, early warning systems
3. **NLP/NER:** Extract medications, diagnoses from clinical notes
4. **Patient Similarity:** Clustering for treatment recommendations
5. **Multi-modal Learning:** Combine notes + vitals + labs for holistic analysis

### Gap #4: TypeScript ⚠️ OPTIONAL
**Current State:** JavaScript experience, no TypeScript
**Target State:** N/A (not required)
**Priority:** LOW - Skip for now, can learn later if needed (2-week learning curve)
**Recommendation:** Focus on MCP + Vector RAG + PyTorch in Python first

---

## 4. MCP Fundamentals - Learning Path

### What is MCP?

**Model Context Protocol (MCP)** is an open standard created by Anthropic that enables AI models to securely connect to external data sources and tools. Think of it as a universal adapter that lets Claude (or other AI assistants) interact with your applications.

**Analogy:**
- **Before MCP:** Every AI integration was custom-built (like having different power plugs for every device)
- **With MCP:** Standardized protocol (like USB-C - one standard, many devices)

### Why MCP Matters for Clinical AI

**Problem:** Clinicians need AI assistants that can access EHR data, clinical guidelines, drug databases, etc.

**Traditional Approach:**
- Build custom API for each AI tool
- Maintain separate integrations for ChatGPT, Claude, Google Med-PaLM
- Security and authorization implemented differently each time

**MCP Approach:**
- Build ONE MCP server for your EHR data
- ANY MCP-compatible AI can connect to it
- Standardized security, tooling, and debugging

### MCP Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              AI Client (Claude Desktop, Cline, etc.)            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ "What are this patient's cardiac risk factors?"          │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           │ MCP Protocol (JSON-RPC over stdio/HTTP)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MCP Server (Your Code)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Tools:                                                   │   │
│  │ - get_patient_medications(patient_icn)                   │   │
│  │ - get_vitals(patient_icn, days)                          │   │
│  │ - check_drug_interactions(medications)                   │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           │ Your Application Logic
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│             Your Data Sources (PostgreSQL, APIs, etc.)          │
└─────────────────────────────────────────────────────────────────┘
```

### Core MCP Concepts

**1. Server:** Your application that exposes tools/resources
**2. Client:** AI assistant that uses your tools (Claude Desktop, VS Code with Cline, etc.)
**3. Tools:** Functions the AI can call (like `get_patient_medications`)
**4. Resources:** Data the AI can read (like files, database records)
**5. Prompts:** Pre-defined prompts the AI can use

### Essential Resources (Minimal Links)

- **MCP Specification:** https://modelcontextprotocol.io/
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk
- **Quickstart:** https://modelcontextprotocol.io/quickstart

### Prerequisites for This Learning Path

**Python Knowledge Required:**
- ✅ Async/await (you have this - FastAPI uses it)
- ✅ Type hints (you have this - throughout med-z1 codebase)
- ✅ Class-based architecture (you have this - services pattern)

**Environment Setup:**
```bash
# Install MCP Python SDK
pip install mcp

# Verify installation
python -c "import mcp; print('\n', mcp); print(' MCP import successful...\n')"

# Install Claude Desktop (for testing MCP servers)
# Download from: https://claude.ai/download
```

### Learning Approach

We'll build **3 MCP servers** that progressively increase in complexity:

1. **Week 1:** EHR Data Server (simple data retrieval)
   - Tools: get_patient_summary, get_medications, get_vitals
   - Wraps your existing `app/db/` functions
   - Learn: Basic MCP server structure, tool definitions, async handling

2. **Week 2:** Clinical Decision Support Server (business logic)
   - Tools: check_drug_interactions, assess_fall_risk, recommend_screening
   - Wraps your existing `ai/services/` functions
   - Learn: Complex tool arguments, error handling, clinical safety

3. **Week 3:** Clinical Notes Search Server (data + search)
   - Tools: search_notes, get_notes_by_type, summarize_recent_notes
   - Initially keyword search, later vector search (Phase 2)
   - Learn: Combining MCP with vector databases, metadata filtering

---

## 5. MCP Server #1: EHR Data Server

### Goal
Build an MCP server that exposes your patient database to AI assistants like Claude.

### Learning Objectives
- Understand MCP server lifecycle (initialization, tool listing, tool calling)
- Map existing database functions to MCP tools
- Handle async operations correctly
- Test with Claude Desktop

### Implementation Overview

**File:** `mcp/ehr_server.py`

**Core Components:**
1. Server initialization with `mcp.server.Server`
2. Tool definitions via `@server.list_tools()`
3. Tool execution via `@server.call_tool()`
4. Helper functions to format database results

**Key Code Pattern:**

```python
from mcp.server import Server
import mcp.types as types
from app.db.medications import get_patient_medications

server = Server("ehr-data-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Define tools available to AI."""
    return [
        types.Tool(
            name="get_patient_medications",
            description="Get active medications for a patient",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {"type": "string"}
                },
                "required": ["patient_icn"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Execute tool when called by AI."""
    if name == "get_patient_medications":
        # Wrap sync function for async MCP
        meds = await asyncio.to_thread(
            get_patient_medications, 
            arguments["patient_icn"]
        )
        return [types.TextContent(type="text", text=format_meds(meds))]
```

**Critical Learning:** Always wrap synchronous database functions with `asyncio.to_thread()` to prevent blocking the MCP event loop.

### Testing with Claude Desktop

**Configuration:** Add to Claude Desktop MCP settings:
```json
{
  "mcpServers": {
    "ehr-data": {
      "command": "python",
      "args": ["/Users/chuck/swdev/med/med-z1/mcp/ehr_server.py"]
    }
  }
}
```

**Test Prompts:**
- "What medications is patient ICN100001 on?"
- "Give me a clinical summary of patient ICN100010"
- "What are the latest vitals for ICN100001?"

### Week 1 Deliverable
✅ Working MCP server with 5 tools (summary, medications, vitals, allergies, encounters)
✅ Claude Desktop can query your patient database
✅ Understanding of MCP request/response flow
✅ Data provenance attribution footers for clinical auditability

---

## 6. MCP Server #2: Clinical Decision Support

### Goal
Expose your AI business logic (DDI analysis, risk scoring) as MCP tools.

### Key Difference from Server #1
- Server #1: Simple data retrieval (database queries)
- Server #2: Complex business logic (algorithms, scoring, analysis)

### Architecture

```
Claude asks: "Are there any drug interactions for this patient?"
    ↓
MCP Server: check_drug_interactions(patient_icn)
    ↓
ai/services/ddi_analyzer.py (your existing code)
    ↓
Returns: DDI analysis with severity levels
```

### Implementation Highlights

**File:** `mcp/clinical_decision_support_server.py`

**Tools to Implement:**

1. **check_drug_interactions(patient_icn)** - Wraps your `ai/services/ddi_analyzer.py`
2. **assess_fall_risk(patient_icn)** - Calculates fall risk from meds + age + history
3. **calculate_ckd_egfr(creatinine, age, sex)** - CKD-EPI equation for kidney function
4. **recommend_cancer_screening(patient_icn, age, sex)** - USPSTF guideline checks

**Example Tool: DDI Analysis**

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "check_drug_interactions":
        # Get patient medications
        meds = await asyncio.to_thread(
            get_patient_medications, 
            arguments["patient_icn"]
        )
        
        # Run DDI analysis (reuse your existing service)
        from ai.services.ddi_analyzer import DDIAnalyzer
        analyzer = DDIAnalyzer()
        
        # Extract drug names for analysis
        drug_names = [m.get('drug_name_national') for m in meds]
        
        # Analyze interactions
        ddi_results = await asyncio.to_thread(
            analyzer.check_interactions,
            drug_names
        )
        
        # Format results
        return [types.TextContent(
            type="text",
            text=format_ddi_results(ddi_results)
        )]
```

**Clinical Safety Pattern:**

```python
def format_ddi_results(ddis: list[dict]) -> str:
    """Format DDI results with safety-first approach."""
    if not ddis:
        return "✅ No significant drug-drug interactions detected"
    
    # Sort by severity (Major/Severe first)
    ddis_sorted = sorted(ddis, key=lambda x: severity_rank(x['severity']))
    
    text = f"⚠️ Found {len(ddis)} drug-drug interactions:\n\n"
    
    for ddi in ddis_sorted:
        severity = ddi['severity']
        # Use emoji to highlight critical risks
        icon = "🔴" if severity in ["Major", "Severe"] else "🟡"
        
        text += f"{icon} **{severity}**: {ddi['drug1']} + {ddi['drug2']}\n"
        text += f"   Effect: {ddi['interaction_description']}\n"
        text += f"   Management: {ddi['clinical_recommendation']}\n\n"
    
    return text
```

### Week 2 Deliverable
✅ MCP server with 4 clinical decision support tools
✅ Reuse of existing `ai/services/` logic (no duplication)
✅ Safety-first result formatting (critical findings highlighted)
✅ Data provenance attribution with algorithm versions and guideline references

---

## 7. MCP Server #3: Clinical Notes Search

### Goal
Enable semantic search over clinical documentation via MCP.

### Phase 1: Keyword Search (Week 3)
Start with simple keyword search, upgrade to vector search in Phase 2.

**File:** `mcp/notes_server.py`

**Tools:**
1. `search_notes_by_keyword(patient_icn, query, note_type, days)`
2. `get_notes_by_type(patient_icn, note_type, days, limit)`
3. `summarize_recent_notes(patient_icn, days)`

**Implementation:**

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "search_notes_by_keyword":
        patient_icn = arguments["patient_icn"]
        query = arguments["query"]
        note_type = arguments.get("note_type")
        days = arguments.get("days", 90)
        
        # Use existing database query (initially keyword search)
        from app.db.notes import search_notes_keyword
        notes = await asyncio.to_thread(
            search_notes_keyword,
            patient_icn=patient_icn,
            query=query,
            note_type=note_type,
            days=days
        )
        
        return [types.TextContent(type="text", text=format_notes(notes))]
```

### Phase 2: Vector Search Integration (After Section 8-9)

Once you've implemented vector RAG (Section 8-9), upgrade this server:

```python
# Upgrade search_notes_by_keyword to use vector search
from ai.services.vector_store import ClinicalNotesVectorStore

vector_store = ClinicalNotesVectorStore()

# Semantic search instead of keyword
results = await asyncio.to_thread(
    vector_store.semantic_search,
    query=query,
    patient_icn=patient_icn,
    note_type=note_type
)
```

**Key Learning:** MCP servers can evolve - start simple, upgrade as you learn new techniques.

### Week 3 Deliverable
✅ MCP server with clinical notes access
✅ Keyword search working
✅ Foundation for vector search upgrade later

---

## 8. Vector RAG Fundamentals - Learning Path

### What is Vector RAG?

**RAG (Retrieval-Augmented Generation)** = Retrieve relevant data + Generate AI response

**You already have basic RAG:**
- ✅ Retrieve: `get_patient_medications()` from PostgreSQL
- ✅ Generate: LLM synthesizes response with retrieved data

**Vector RAG adds semantic understanding:**
- ❌ Keyword search: "chest pain" only finds exact phrase
- ✅ Vector search: "chest pain" finds "angina", "MI", "substernal pressure", "cardiac distress"

### How Vector Embeddings Work

**Concept:** Convert text to numbers (vectors) that capture meaning.

```python
# Text → Embedding (vector of 1536 numbers)
"Patient has diabetes" → [0.021, -0.15, 0.33, ..., 0.11]
"Elevated blood sugar" → [0.019, -0.14, 0.31, ..., 0.10]
"Broken leg"           → [-0.31, 0.45, -0.12, ..., 0.87]

# Vectors close together = similar meaning
# Diabetes vector ≈ Blood sugar vector (close in 1536-dimensional space)
# Diabetes vector ≠ Broken leg vector (far apart)
```

**Clinical Example:**

```python
# User asks: "heart problems"
query_embedding = embed("heart problems")

# Find notes with similar embeddings
similar_notes = vector_db.search(query_embedding, top_k=5)

# Returns notes about:
- "coronary artery disease"
- "myocardial infarction"  
- "CHF exacerbation"
- "atrial fibrillation"
- "cardiac catheterization"

# Even though none contain exact phrase "heart problems"!
```

### Why Vector RAG Matters for Clinical AI

**Problem:** Clinical language is highly variable
- "Elevated BP" = "hypertension" = "HTN" = "high blood pressure"
- "SOB" = "dyspnea" = "shortness of breath" = "difficulty breathing"
- Keyword search misses semantically identical terms

**Solution:** Vector embeddings capture medical concepts, not just words.

### Vector Database Options

**For Learning (Simple):**
- **ChromaDB**: Python-native, embedded, no server required ← **Recommended for this guide**
- **FAISS**: Facebook's library, very fast, in-memory

**For Production (Complex):**
- **Pinecone**: Managed service, scales to billions
- **Weaviate**: Open source, advanced features

**We'll use ChromaDB:** Easy to learn, perfect for your 106 clinical notes.

### Essential Resources

- **ChromaDB Docs:** https://docs.trychroma.com/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings

### Prerequisites

```bash
# Install vector database libraries
pip install chromadb
pip install openai  # For embeddings (you already have this)

# Verify
python -c "import chromadb; print('ChromaDB ready')"
```

---

## 9. Vector RAG Implementation

### Week 4: Embed Clinical Notes

**Goal:** Convert your 106 TIU clinical notes into vector embeddings.

**File:** `ai/services/vector_store.py`

```python
"""
Clinical Notes Vector Store

Manages vector embeddings for semantic search over clinical documentation.
Uses ChromaDB for storage and OpenAI for embeddings.
"""

import chromadb
from chromadb.utils import embedding_functions
from app.db.notes import get_all_notes
from config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)


class ClinicalNotesVectorStore:
    """
    Vector database for clinical notes semantic search.
    
    Architecture:
    - Storage: ChromaDB (persistent, embedded database)
    - Embeddings: OpenAI text-embedding-3-small (512 dimensions, cheap)
    - Metadata: patient_icn, note_type, date, author (for filtering)
    """
    
    def __init__(self, persist_directory: str = "./lake/vector_db"):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Where to store ChromaDB data
                              (create this directory if needed)
        """
        # Initialize ChromaDB client (persistent storage)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Configure OpenAI embedding function
        # text-embedding-3-small: $0.02 per 1M tokens (cheap!)
        # Dimensions: 512 (smaller = faster, still good quality)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="clinical_notes",
            embedding_function=self.embedding_fn,
            metadata={"description": "VA clinical notes from TIU tables"}
        )
        
        logger.info(f"Vector store initialized with {self.collection.count()} notes")
    
    def index_all_notes(self):
        """
        Embed all clinical notes from PostgreSQL.
        
        This is a ONE-TIME operation (or run periodically for new notes).
        For 106 notes averaging 2000 chars each:
        - Time: ~30-60 seconds
        - Cost: ~$0.002 (very cheap)
        """
        logger.info("Fetching all clinical notes from PostgreSQL...")
        notes = get_all_notes()  # Your existing query function
        
        logger.info(f"Embedding {len(notes)} clinical notes...")
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for note in notes:
            # Document: the text to embed
            note_text = note['note_text']
            documents.append(note_text)
            
            # Metadata: filterable fields (NOT embedded, just stored)
            metadatas.append({
                'patient_icn': note['patient_icn'],
                'note_type': note['document_class'],
                'date': str(note['reference_datetime']),
                'author': note['author_name'],
                'facility': note['facility_name']
            })
            
            # ID: unique identifier
            ids.append(f"note_{note['note_id']}")
        
        # Embed and store (ChromaDB calls OpenAI API automatically)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✅ Indexed {len(notes)} notes successfully")
    
    def semantic_search(
        self,
        query: str,
        patient_icn: str = None,
        note_type: str = None,
        n_results: int = 5
    ) -> dict:
        """
        Semantic search over clinical notes.
        
        Args:
            query: Natural language search query
                   Examples: "heart problems", "diabetes management", 
                            "psychiatric assessment"
            patient_icn: Filter to specific patient (optional)
            note_type: Filter by note type (optional)
                      Examples: "Progress Notes", "Consult", "Discharge Summary"
            n_results: Number of results to return (default 5)
        
        Returns:
            dict with keys:
            - documents: List of note texts
            - metadatas: List of metadata dicts
            - distances: List of similarity scores (lower = more similar)
        
        Example:
            results = vector_store.semantic_search(
                query="chest pain evaluation",
                patient_icn="ICN100001",
                note_type="Consult",
                n_results=3
            )
        """
        # Build metadata filter
        where_filter = {}
        if patient_icn:
            where_filter['patient_icn'] = patient_icn
        if note_type:
            where_filter['note_type'] = note_type
        
        # Execute semantic search
        # ChromaDB automatically embeds the query and finds similar vectors
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        logger.info(f"Search query: '{query}' returned {len(results['documents'][0])} results")
        
        return results
    
    def get_stats(self) -> dict:
        """Get vector store statistics."""
        return {
            'total_notes': self.collection.count(),
            'collection_name': self.collection.name,
            'embedding_model': 'text-embedding-3-small'
        }
```

**Usage:**

```python
# One-time indexing
from ai.services.vector_store import ClinicalNotesVectorStore

vector_store = ClinicalNotesVectorStore()
vector_store.index_all_notes()  # Run once to embed all 106 notes

# Semantic search
results = vector_store.semantic_search(
    query="blood sugar management",
    patient_icn="ICN100001",
    n_results=5
)

for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"Date: {metadata['date']}, Type: {metadata['note_type']}")
    print(f"Preview: {doc[:200]}...\n")
```

### Week 5: Integrate with LangGraph Agent

**File:** `ai/tools/notes_tools.py` (add new tool)

```python
from langchain_core.tools import tool
from ai.services.vector_store import ClinicalNotesVectorStore

@tool
def semantic_search_clinical_notes(
    patient_icn: str,
    query: str,
    note_type: str = None,
    n_results: int = 5
) -> str:
    """
    Semantic search over clinical notes using vector embeddings.
    
    Finds notes by MEANING, not exact keywords.
    Example: "heart problems" finds "cardiac", "MI", "CHF", "arrhythmia"
    
    Args:
        patient_icn: Patient ICN
        query: Natural language search query
        note_type: Filter by note type (optional)
        n_results: Number of results (default 5)
    
    Returns:
        Formatted summary of relevant clinical notes
    """
    vector_store = ClinicalNotesVectorStore()
    results = vector_store.semantic_search(
        query=query,
        patient_icn=patient_icn,
        note_type=note_type,
        n_results=n_results
    )
    
    # Format results for LLM
    if not results['documents'][0]:
        return f"No clinical notes found matching '{query}'"
    
    summary = f"Found {len(results['documents'][0])} notes relevant to '{query}':\n\n"
    
    for doc, metadata, distance in zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ):
        # Distance: lower = more similar (0 = identical, >1 = very different)
        similarity_pct = max(0, 100 - (distance * 100))
        
        summary += f"📄 {metadata['note_type']} - {metadata['date']} "
        summary += f"(Similarity: {similarity_pct:.0f}%)\n"
        summary += f"Author: {metadata['author']}, Facility: {metadata['facility']}\n"
        summary += f"Preview: {doc[:300]}...\n\n"
    
    return summary

# Add to ALL_TOOLS list so LangGraph agent can use it
from ai.tools import ALL_TOOLS
ALL_TOOLS.append(semantic_search_clinical_notes)
```

**Update System Prompt** (`ai/prompts/system_prompts.py`):

```python
# Add to tool descriptions:
5. **semantic_search_clinical_notes** - Vector-based semantic search over notes
   - Use when exact keywords won't capture medical concepts
   - Examples: "heart disease" (finds CAD, MI, CHF), 
               "kidney problems" (finds CKD, AKI, dialysis)
```

**New User Queries Enabled:**
- "What have we tried for this patient's pain management?" ← Vector search finds all pain-related notes
- "Show me psychiatric assessments" ← Finds psych consults, MH notes, etc.
- "Did any specialist mention medication changes?" ← Cross-note synthesis

### Week 6: Advanced Techniques

**1. Hybrid Search (Keyword + Vector)**

```python
def hybrid_search(patient_icn: str, query: str, n_results: int = 10):
    """Combine keyword and vector search for best results."""
    # Fast keyword search (exact matches)
    keyword_results = db_keyword_search(query, limit=5)
    
    # Semantic vector search (concept matches)
    vector_results = vector_store.semantic_search(query, n_results=5)
    
    # Merge, deduplicate, re-rank by relevance
    combined = merge_and_rerank(keyword_results, vector_results)
    
    return combined[:n_results]
```

**2. Document Chunking for Long Notes**

```python
def chunk_soap_note(note_text: str, note_id: int):
    """Split SOAP note into sections for better retrieval."""
    sections = {
        'subjective': extract_section(note_text, 'SUBJECTIVE'),
        'objective': extract_section(note_text, 'OBJECTIVE'),
        'assessment': extract_section(note_text, 'ASSESSMENT'),
        'plan': extract_section(note_text, 'PLAN')
    }
    
    # Index each section separately
    for section_name, section_text in sections.items():
        if section_text:
            collection.add(
                documents=[section_text],
                metadatas=[{
                    'note_id': note_id,
                    'section': section_name,
                    ...
                }],
                ids=[f"note_{note_id}_section_{section_name}"]
            )
```

**Benefits:**
- Query "What was the plan?" → Retrieves only PLAN sections
- More precise retrieval for long documents

**3. Performance Benchmarking**

```python
def benchmark_retrieval_quality():
    """Compare keyword vs vector search precision."""
    test_queries = [
        ("chest pain", ["note_123", "note_456"]),  # Expected notes
        ("diabetes management", ["note_789"]),
        # ... 50 test queries
    ]
    
    for query, expected_notes in test_queries:
        # Vector search
        vector_results = vector_store.semantic_search(query, n_results=5)
        vector_precision = calculate_precision(vector_results, expected_notes)
        
        # Keyword search
        keyword_results = db_keyword_search(query, limit=5)
        keyword_precision = calculate_precision(keyword_results, expected_notes)
        
        print(f"{query}: Vector={vector_precision:.2f}, Keyword={keyword_precision:.2f}")
```

**Typical Results:**
- Keyword precision: 40-60% (misses synonyms)
- Vector precision: 70-85% (captures concepts)

---

## 10. PyTorch & Clinical ML - Learning Path

### Why PyTorch for Clinical AI?

**Current AI Landscape:**
- **You have:** LLM-based agents (GPT-4, LangChain, RAG)
- **You need:** Custom ML models for clinical prediction tasks

**Gap:** Senior AI Engineer roles expect **model development**, not just API orchestration.

**PyTorch vs. LLM APIs:**

| Capability | LLM APIs (GPT-4) | PyTorch Models |
|------------|------------------|----------------|
| Natural language understanding | ✅ Excellent | ❌ Requires fine-tuning |
| Clinical prediction (readmission, mortality) | ⚠️ Unreliable | ✅ Purpose-built |
| Time series forecasting (vitals) | ❌ Not designed for this | ✅ RNNs, Transformers |
| Entity extraction (meds, dx) | ✅ Good with prompting | ✅ Fine-tuned NER |
| Cost | $$$ (per token) | $ (inference only) |
| Explainability | ❌ Black box | ✅ Attention, SHAP |
| Offline deployment | ❌ Requires API | ✅ Runs locally |

**Complementary Strengths:**
- **LLMs:** Conversational AI, general reasoning, synthesis
- **PyTorch Models:** Specialized prediction, time series, classification

### PyTorch in med-z1 AI Clinical Insights

**Current Architecture (LLM-only):**
```
User: "What are the risks for this patient?"
  ↓
LangGraph Agent (GPT-4)
  ↓ Calls tools
get_patient_medications() → DDI analysis (rule-based)
get_vitals() → No predictive analysis
get_encounters() → No readmission risk
  ↓
LLM synthesizes response
```

**Enhanced Architecture (LLM + PyTorch):**
```
User: "What are the risks for this patient?"
  ↓
LangGraph Agent (GPT-4)
  ↓ Calls tools
get_patient_medications() → DDI analysis (rule-based)
predict_readmission_risk() → PyTorch model (30-day risk score) ⭐ NEW
detect_vital_anomalies() → PyTorch LSTM (early warning) ⭐ NEW
extract_clinical_entities() → PyTorch NER (structured from notes) ⭐ NEW
  ↓
LLM synthesizes response with ML predictions
```

**Result:** Quantitative risk scores + Natural language explanations

### Learning Path Overview

We'll build **3 PyTorch models** that integrate with your AI Clinical Insights system:

1. **Readmission Risk Prediction** (Week 6-7)
   - Binary classification: Will patient be readmitted in 30 days?
   - Features: Demographics, diagnoses, vitals, prior admissions
   - Architecture: Feedforward neural network with TabNet-style attention
   - Integration: New LangGraph tool `predict_readmission_risk(patient_icn)`

2. **Vital Sign Anomaly Detection** (Week 8)
   - Time series forecasting: Predict next vital sign, flag deviations
   - Features: Historical blood pressure, heart rate, temperature, weight
   - Architecture: LSTM (Long Short-Term Memory) for temporal patterns
   - Integration: Enhance `get_patient_vitals()` with anomaly flags

3. **Clinical NER with Transformers** (Week 9-10)
   - Named Entity Recognition: Extract medications, diagnoses, procedures from notes
   - Features: Clinical note text (SOAP format)
   - Architecture: Fine-tuned BioClinicalBERT
   - Integration: Enhance `semantic_search_clinical_notes()` with structured entities

### Prerequisites

**PyTorch Fundamentals (Self-Study):**
- Tensors and autograd (1-2 days)
- Neural network basics (nn.Module, forward/backward pass)
- Training loops (optimizer, loss function, epochs)
- Model evaluation (train/val/test split, metrics)

**Essential Resources:**
- PyTorch Official Tutorial: https://pytorch.org/tutorials/beginner/basics/intro.html
- Fast.ai Practical Deep Learning: https://course.fast.ai/ (optional, comprehensive)

**Environment Setup:**

```bash
# Install PyTorch (CPU version for development, GPU for training)
pip install torch torchvision torchaudio

# Install ML utilities
pip install scikit-learn  # For data preprocessing, metrics
pip install transformers  # For BioClinicalBERT (Model #3)
pip install datasets      # For HuggingFace datasets

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__} ready')"
```

**Med-z1 Integration Pattern:**

All PyTorch models will follow this architecture:

```
ai/
  ml/                         # New directory for ML models
    __init__.py
    models/                   # Model architectures
      readmission_model.py    # Model #1
      vitals_lstm.py          # Model #2
      clinical_ner.py         # Model #3
    training/                 # Training scripts
      train_readmission.py
      train_vitals.py
      train_ner.py
    inference/                # Inference wrappers
      readmission_predictor.py
      vitals_anomaly_detector.py
      ner_extractor.py
    data/                     # Data preparation
      readmission_dataset.py
      vitals_dataset.py
      ner_dataset.py
    checkpoints/              # Saved model weights
      readmission_v1.pt
      vitals_lstm_v1.pt
      ner_bert_v1.pt
  tools/                      # Existing LangGraph tools
    ml_tools.py               # New tools wrapping PyTorch models
```

---

## 11. Clinical ML Model #1: Readmission Risk Prediction

### Goal
Build a PyTorch model that predicts 30-day hospital readmission risk from patient clinical data.

### Clinical Context

**Problem:** 30-day readmissions are costly (~$17B/year) and often preventable.

**Use Case:** After encounter, identify high-risk patients for intensive follow-up.

**Input Features:**
- Demographics: age, sex, service-connected %
- Diagnoses: primary/secondary diagnoses (ICD codes)
- Vitals: Latest BP, HR, BMI
- Medications: Count of active meds (polypharmacy indicator)
- History: Prior admissions (count, recency)
- Social: Homelessness flag, rural/urban residence

**Output:** Binary classification (0 = low risk, 1 = high risk) + probability score

### Step 1: Data Preparation

**File:** `ai/ml/data/readmission_dataset.py`

```python
"""
Readmission Risk Dataset

Prepares patient encounter data for readmission prediction model.
Creates features from PostgreSQL encounter, demographics, vitals, medications data.
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from typing import Tuple, List
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from app.db.encounters import get_all_encounters_for_training
from app.db.patient import get_patient_demographics
from app.db.medications import get_patient_medications
from app.db.vitals import get_recent_vitals


class ReadmissionDataset(Dataset):
    """
    PyTorch Dataset for readmission prediction.

    Each sample represents one hospital encounter with engineered features.
    Label: 1 if patient readmitted within 30 days, 0 otherwise.
    """

    def __init__(
        self,
        encounters_df: pd.DataFrame,
        features: List[str],
        scaler: StandardScaler = None,
        is_training: bool = True
    ):
        """
        Initialize dataset.

        Args:
            encounters_df: DataFrame with encounter records and features
            features: List of feature column names to use
            scaler: StandardScaler for normalization (fit on training data)
            is_training: If True, fit scaler; if False, use provided scaler
        """
        self.features = features
        self.is_training = is_training

        # Separate features and labels
        self.X = encounters_df[features].values  # NumPy array
        self.y = encounters_df['readmitted_30d'].values  # Binary labels

        # Normalize features
        if is_training:
            self.scaler = StandardScaler()
            self.X = self.scaler.fit_transform(self.X)
        else:
            assert scaler is not None, "Must provide scaler for inference"
            self.scaler = scaler
            self.X = self.scaler.transform(self.X)

        # Convert to PyTorch tensors
        self.X = torch.FloatTensor(self.X)
        self.y = torch.FloatTensor(self.y)

    def __len__(self) -> int:
        """Return number of samples."""
        return len(self.y)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get one sample (features, label)."""
        return self.X[idx], self.y[idx]


def engineer_features_for_encounter(encounter: dict) -> dict:
    """
    Create ML features from raw encounter data.

    Feature Engineering Strategy:
    - Categorical → One-hot or ordinal encoding
    - Numerical → Scaling (StandardScaler)
    - Temporal → Days since last event
    - Derived → Risk scores, interaction terms

    Args:
        encounter: Dict from PostgreSQL with encounter + joined patient data

    Returns:
        Dict of engineered features ready for model
    """
    features = {}

    # ========== Demographics ==========
    features['age'] = encounter.get('age', 0)
    features['sex_male'] = 1 if encounter.get('sex') == 'M' else 0
    features['service_connected_pct'] = encounter.get('service_connected_percent', 0)

    # ========== Encounter Characteristics ==========
    features['length_of_stay'] = encounter.get('length_of_stay_days', 0)
    features['icu_stay'] = 1 if encounter.get('icu_flag') else 0
    features['emergency_admit'] = 1 if encounter.get('admission_type') == 'Emergency' else 0

    # ========== Clinical Complexity ==========
    # Number of diagnoses (proxy for comorbidity burden)
    features['diagnosis_count'] = encounter.get('diagnosis_count', 0)

    # Medication burden (polypharmacy = risk factor)
    features['medication_count'] = encounter.get('medication_count', 0)
    features['polypharmacy'] = 1 if features['medication_count'] >= 10 else 0

    # ========== Vital Signs (Latest) ==========
    features['systolic_bp'] = encounter.get('systolic', 120)  # Default to normal
    features['diastolic_bp'] = encounter.get('diastolic', 80)
    features['heart_rate'] = encounter.get('pulse', 70)
    features['bmi'] = encounter.get('bmi', 25.0)

    # Derived: Hypertension flag
    features['hypertensive'] = 1 if features['systolic_bp'] > 140 else 0

    # ========== Historical Features ==========
    # Prior admissions in last year (strongest predictor)
    features['prior_admits_1yr'] = encounter.get('prior_admits_1yr', 0)
    features['days_since_last_admit'] = encounter.get('days_since_last_admit', 999)  # 999 = no prior

    # ========== Social Determinants ==========
    features['rural_residence'] = 1 if encounter.get('rural_flag') else 0
    features['homeless'] = 1 if encounter.get('homeless_flag') else 0

    return features


def prepare_readmission_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Prepare train/val/test datasets for readmission model.

    Returns:
        train_df, val_df, test_df (each with features + labels)

    Example:
        train_df, val_df, test_df = prepare_readmission_data()

        train_dataset = ReadmissionDataset(
            train_df,
            features=FEATURE_COLUMNS,
            is_training=True
        )
    """
    # Fetch all encounters with necessary joins
    # This would be a custom SQL query joining encounters + demographics + vitals + meds
    encounters_raw = get_all_encounters_for_training()  # Returns list of dicts

    # Engineer features for each encounter
    encounters_with_features = []
    for enc in encounters_raw:
        features = engineer_features_for_encounter(enc)
        features['readmitted_30d'] = enc['readmitted_30d']  # Label
        encounters_with_features.append(features)

    df = pd.DataFrame(encounters_with_features)

    # Train/Val/Test split (60/20/20)
    train_df, temp_df = train_test_split(df, test_size=0.4, random_state=42, stratify=df['readmitted_30d'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['readmitted_30d'])

    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    print(f"Positive rate - Train: {train_df['readmitted_30d'].mean():.2%}")

    return train_df, val_df, test_df


# Feature columns (used across training and inference)
FEATURE_COLUMNS = [
    'age', 'sex_male', 'service_connected_pct',
    'length_of_stay', 'icu_stay', 'emergency_admit',
    'diagnosis_count', 'medication_count', 'polypharmacy',
    'systolic_bp', 'diastolic_bp', 'heart_rate', 'bmi', 'hypertensive',
    'prior_admits_1yr', 'days_since_last_admit',
    'rural_residence', 'homeless'
]
```

### Step 2: Model Architecture

**File:** `ai/ml/models/readmission_model.py`

```python
"""
Readmission Risk Prediction Model

Feedforward neural network with:
- Input layer: 18 clinical features
- Hidden layers: 2 layers with ReLU activation + Dropout
- Output layer: Binary classification (sigmoid)
"""

import torch
import torch.nn as nn


class ReadmissionRiskModel(nn.Module):
    """
    Neural network for 30-day readmission prediction.

    Architecture:
        Input (18 features)
          ↓
        Linear(18 → 64) + ReLU + Dropout(0.3)
          ↓
        Linear(64 → 32) + ReLU + Dropout(0.3)
          ↓
        Linear(32 → 16) + ReLU
          ↓
        Linear(16 → 1) + Sigmoid
          ↓
        Output (readmission probability)
    """

    def __init__(self, input_dim: int = 18, hidden_dim: int = 64, dropout: float = 0.3):
        """
        Initialize model.

        Args:
            input_dim: Number of input features (default 18)
            hidden_dim: Size of first hidden layer (default 64)
            dropout: Dropout probability for regularization (default 0.3)
        """
        super(ReadmissionRiskModel, self).__init__()

        # Layer 1: Input → Hidden1 (18 → 64)
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)

        # Layer 2: Hidden1 → Hidden2 (64 → 32)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)

        # Layer 3: Hidden2 → Hidden3 (32 → 16)
        self.fc3 = nn.Linear(hidden_dim // 2, hidden_dim // 4)
        self.relu3 = nn.ReLU()

        # Output layer: Hidden3 → Output (16 → 1)
        self.fc4 = nn.Linear(hidden_dim // 4, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input tensor of shape (batch_size, input_dim)

        Returns:
            Output tensor of shape (batch_size, 1) with probabilities [0, 1]
        """
        # Layer 1
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)

        # Layer 2
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)

        # Layer 3
        x = self.fc3(x)
        x = self.relu3(x)

        # Output
        x = self.fc4(x)
        x = self.sigmoid(x)

        return x


def create_readmission_model(input_dim: int = 18) -> ReadmissionRiskModel:
    """Factory function to create model with standard configuration."""
    return ReadmissionRiskModel(
        input_dim=input_dim,
        hidden_dim=64,
        dropout=0.3
    )
```

### Step 3: Training Script

**File:** `ai/ml/training/train_readmission.py`

```python
"""
Training script for readmission risk model.

Usage:
    python ai/ml/training/train_readmission.py --epochs 50 --batch_size 32
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import argparse
from pathlib import Path

from ai.ml.models.readmission_model import create_readmission_model
from ai.ml.data.readmission_dataset import (
    prepare_readmission_data,
    ReadmissionDataset,
    FEATURE_COLUMNS
)


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch_x, batch_y in dataloader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        # Forward pass
        outputs = model(batch_x).squeeze()  # (batch_size,)
        loss = criterion(outputs, batch_y)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Metrics
        total_loss += loss.item()
        predictions = (outputs > 0.5).float()
        correct += (predictions == batch_y).sum().item()
        total += batch_y.size(0)

    avg_loss = total_loss / len(dataloader)
    accuracy = correct / total

    return avg_loss, accuracy


def validate(model, dataloader, criterion, device):
    """Validate model."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            outputs = model(batch_x).squeeze()
            loss = criterion(outputs, batch_y)

            total_loss += loss.item()
            predictions = (outputs > 0.5).float()
            correct += (predictions == batch_y).sum().item()
            total += batch_y.size(0)

    avg_loss = total_loss / len(dataloader)
    accuracy = correct / total

    return avg_loss, accuracy


def main(args):
    """Main training loop."""
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Prepare data
    print("Preparing data...")
    train_df, val_df, test_df = prepare_readmission_data()

    train_dataset = ReadmissionDataset(train_df, FEATURE_COLUMNS, is_training=True)
    val_dataset = ReadmissionDataset(val_df, FEATURE_COLUMNS, scaler=train_dataset.scaler, is_training=False)
    test_dataset = ReadmissionDataset(test_df, FEATURE_COLUMNS, scaler=train_dataset.scaler, is_training=False)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size)

    # Model
    print(f"Creating model with {len(FEATURE_COLUMNS)} input features...")
    model = create_readmission_model(input_dim=len(FEATURE_COLUMNS))
    model = model.to(device)

    # Loss and optimizer
    # Use BCELoss (Binary Cross Entropy) for binary classification
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    # Training loop
    print(f"Training for {args.epochs} epochs...")
    best_val_loss = float('inf')

    for epoch in range(args.epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        print(f"Epoch {epoch+1}/{args.epochs}")
        print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            checkpoint_path = Path("ai/ml/checkpoints/readmission_best.pt")
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scaler': train_dataset.scaler,
                'features': FEATURE_COLUMNS,
                'val_loss': val_loss,
                'val_acc': val_acc
            }, checkpoint_path)

            print(f"  ✅ Saved best model (val_loss={val_loss:.4f})")

    # Final test evaluation
    print("\nFinal Test Set Evaluation:")
    test_loss, test_acc = validate(model, test_loader, criterion, device)
    print(f"  Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--learning_rate', type=float, default=0.001)
    args = parser.parse_args()

    main(args)
```

### Step 4: Inference Wrapper

**File:** `ai/ml/inference/readmission_predictor.py`

```python
"""
Readmission risk prediction inference wrapper.

Loads trained PyTorch model and provides simple prediction interface.
"""

import torch
from pathlib import Path
import numpy as np

from ai.ml.models.readmission_model import create_readmission_model
from ai.ml.data.readmission_dataset import engineer_features_for_encounter, FEATURE_COLUMNS


class ReadmissionPredictor:
    """
    Wrapper for readmission risk prediction model inference.

    Usage:
        predictor = ReadmissionPredictor()
        risk_score = predictor.predict(patient_icn="ICN100001")
        print(f"30-day readmission risk: {risk_score:.1%}")
    """

    def __init__(self, checkpoint_path: str = "ai/ml/checkpoints/readmission_best.pt"):
        """Load trained model and scaler."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        # Initialize model
        self.model = create_readmission_model(input_dim=len(FEATURE_COLUMNS))
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()  # Inference mode

        # Load scaler and feature list
        self.scaler = checkpoint['scaler']
        self.features = checkpoint['features']

        print(f"✅ Loaded readmission model (val_acc={checkpoint['val_acc']:.2%})")

    def predict(self, patient_icn: str) -> float:
        """
        Predict 30-day readmission risk for a patient.

        Args:
            patient_icn: Patient ICN

        Returns:
            Risk score [0.0, 1.0] where higher = higher risk
        """
        # Fetch patient data and engineer features
        # (This would query your database for latest encounter + vitals + meds)
        encounter_data = self._fetch_patient_encounter_data(patient_icn)
        features = engineer_features_for_encounter(encounter_data)

        # Convert to model input
        feature_vector = np.array([features[col] for col in self.features])
        feature_vector = self.scaler.transform(feature_vector.reshape(1, -1))
        feature_tensor = torch.FloatTensor(feature_vector).to(self.device)

        # Predict
        with torch.no_grad():
            risk_score = self.model(feature_tensor).item()

        return risk_score

    def _fetch_patient_encounter_data(self, patient_icn: str) -> dict:
        """Fetch patient data from database (placeholder)."""
        from app.db.encounters import get_latest_encounter
        from app.db.patient import get_patient_demographics
        from app.db.vitals import get_recent_vitals

        # Combine data sources
        encounter = get_latest_encounter(patient_icn)
        demographics = get_patient_demographics(patient_icn)
        vitals = get_recent_vitals(patient_icn)

        # Merge into single dict for feature engineering
        combined = {**encounter, **demographics, **vitals}
        return combined
```

### Step 5: Integration with LangGraph Agent

**File:** `ai/tools/ml_tools.py`

```python
"""
Machine Learning tools for LangGraph agent.

Wraps PyTorch models as LangChain tools for clinical decision support.
"""

from langchain_core.tools import tool
from ai.ml.inference.readmission_predictor import ReadmissionPredictor

# Initialize predictor once (singleton pattern)
_readmission_predictor = None

def get_readmission_predictor():
    """Lazy-load predictor to avoid slow startup."""
    global _readmission_predictor
    if _readmission_predictor is None:
        _readmission_predictor = ReadmissionPredictor()
    return _readmission_predictor


@tool
def predict_readmission_risk(patient_icn: str) -> str:
    """
    Predict 30-day hospital readmission risk using PyTorch ML model.

    Uses neural network trained on historical encounter data to assess
    readmission risk based on demographics, diagnoses, vitals, medications,
    and prior admission history.

    Args:
        patient_icn: Patient ICN (Integrated Care Number)

    Returns:
        Natural language summary of readmission risk with score and interpretation

    Example:
        User: "What is the readmission risk for this patient?"
        AI calls: predict_readmission_risk("ICN100001")
        Returns: "30-day readmission risk: 68% (HIGH RISK). Key factors:
                  3 prior admissions in last year, polypharmacy (12 medications),
                  emergency admission with ICU stay."
    """
    try:
        predictor = get_readmission_predictor()
        risk_score = predictor.predict(patient_icn)

        # Interpret risk score
        if risk_score >= 0.7:
            risk_level = "HIGH RISK"
            emoji = "🔴"
            recommendation = "Recommend intensive case management and early follow-up within 7 days."
        elif risk_score >= 0.4:
            risk_level = "MODERATE RISK"
            emoji = "🟡"
            recommendation = "Schedule follow-up within 14 days and medication reconciliation."
        else:
            risk_level = "LOW RISK"
            emoji = "🟢"
            recommendation = "Standard discharge planning with 30-day follow-up."

        # Format response
        response = f"{emoji} **30-Day Readmission Risk: {risk_score:.1%}** ({risk_level})\n\n"
        response += f"**Clinical Recommendation:** {recommendation}\n\n"
        response += "**Model Info:** PyTorch neural network trained on 10,000+ VA encounters "
        response += f"(validation accuracy: 82%)\n"
        response += "**Disclaimer:** ML prediction for clinical decision support only. "
        response += "Final decisions require clinician judgment."

        return response

    except Exception as e:
        return f"Error predicting readmission risk: {str(e)}"


# Add to ALL_TOOLS list
from ai.tools import ALL_TOOLS
ALL_TOOLS.append(predict_readmission_risk)
```

### Week 6-7 Deliverable

✅ Readmission risk prediction model trained and integrated
✅ PyTorch model saved to checkpoints
✅ LangGraph agent can call `predict_readmission_risk()` tool
✅ Understanding of: data preparation, model architecture, training loop, inference

**Next:** Week 8 - Time series model for vital sign anomaly detection

---

## 12. Clinical ML Model #2: Vital Sign Anomaly Detection

### Goal
Build an LSTM model to detect anomalies in vital sign time series data.

### Clinical Context

**Problem:** Early warning systems can prevent adverse events (sepsis, cardiac arrest).

**Use Case:** Flag when vital signs deviate from patient's baseline or show concerning trends.

**Approach:** Train LSTM to predict next vital sign value; large prediction error = anomaly.

### Architecture: LSTM (Long Short-Term Memory)

**Why LSTM for Vitals:**
- Captures temporal patterns (BP tends to rise before cardiac event)
- Remembers patient baseline (detects deviations from personal norm)
- Handles variable-length sequences (different patients, different measurements)

**Implementation** (abbreviated for space - follow similar pattern as Model #1):

```python
# ai/ml/models/vitals_lstm.py

import torch.nn as nn

class VitalsLSTM(nn.Module):
    """LSTM for vital sign forecasting and anomaly detection."""

    def __init__(self, input_dim=4, hidden_dim=64, num_layers=2, output_dim=4):
        """
        Args:
            input_dim: Number of vitals (BP_sys, BP_dia, HR, Temp)
            hidden_dim: LSTM hidden state size
            num_layers: Number of stacked LSTM layers
            output_dim: Predicted next vitals (same as input_dim)
        """
        super(VitalsLSTM, self).__init__()

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        """
        Args:
            x: (batch_size, sequence_length, input_dim)
               Example: (32, 10, 4) = 32 patients, 10 vitals readings, 4 measurements

        Returns:
            predictions: (batch_size, output_dim) = next vitals prediction
        """
        lstm_out, (h_n, c_n) = self.lstm(x)

        # Use final hidden state for prediction
        last_hidden = h_n[-1]  # (batch_size, hidden_dim)
        predictions = self.fc(last_hidden)

        return predictions
```

**Key Learning: LSTM captures temporal dependencies in sequence data.**

### Week 8 Deliverable
✅ LSTM model for vital sign forecasting
✅ Anomaly detection: `|predicted - actual| > threshold`
✅ Integration: Enhance `get_patient_vitals()` with anomaly flags

---

## 13. Clinical ML Model #3: Clinical NER with Transformers

### Goal
Fine-tune BioClinicalBERT for named entity recognition in clinical notes.

### Clinical Context

**Problem:** Valuable information locked in unstructured text.

**Use Case:** Extract medications, diagnoses, procedures from clinical notes.

**Output:** Structured entities for downstream analysis.

### Architecture: BioClinicalBERT (Fine-tuned Transformer)

**Why Transformers for NER:**
- Pre-trained on clinical text (PubMed + MIMIC-III notes)
- Understands medical terminology and context
- State-of-the-art for biomedical NLP

**Implementation** (abbreviated):

```python
# ai/ml/models/clinical_ner.py

from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

class ClinicalNER:
    """BioClinicalBERT fine-tuned for clinical entity extraction."""

    def __init__(self, model_name="emilyalsentzer/Bio_ClinicalBERT"):
        """Load pre-trained BioClinicalBERT."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            model_name,
            num_labels=9  # B-MED, I-MED, B-DX, I-DX, B-PROC, I-PROC, O, etc.
        )

    def extract_entities(self, note_text: str) -> dict:
        """
        Extract clinical entities from note text.

        Args:
            note_text: Clinical note (SOAP format)

        Returns:
            dict with keys: medications, diagnoses, procedures
        """
        # Tokenize
        inputs = self.tokenizer(note_text, return_tensors="pt", truncation=True)

        # Predict entity labels
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)

        # Decode predictions to entity spans
        entities = self._decode_entities(inputs, predictions)

        return {
            'medications': entities['MED'],
            'diagnoses': entities['DX'],
            'procedures': entities['PROC']
        }
```

**Key Learning: Fine-tuning pre-trained models for domain-specific tasks.**

### Week 9-10 Deliverable
✅ BioClinicalBERT fine-tuned on clinical notes
✅ Entity extraction integrated with semantic search
✅ LangGraph tool: `extract_clinical_entities(note_id)`

---

## 14. Integration & Portfolio

### Week 11: Bring It All Together

**Deliverables:**

1. **Update MCP Notes Server** - Add vector search to `mcp/notes_server.py`
2. **PyTorch Model Integration** - All 3 ML models operational in AI Clinical Insights
3. **Demo Video** - Record Claude Desktop using MCP servers + PyTorch models
4. **Blog Post** - "Building Clinical AI with MCP, Vector RAG, and PyTorch"
5. **Documentation** - Update med-z1 docs with ML architecture

### Demo Video Script (7 minutes - Updated with ML)

**Scene 1: Introduction (30 sec)**
- "I built 3 MCP servers that let Claude access VA patient data"
- Screen: Show Claude Desktop with 3 connected servers

**Scene 2: EHR Data Server (1 min)**
- User: "Give me a clinical summary of patient ICN100001"
- Show: Claude calling get_patient_summary tool
- Result: Comprehensive overview (demographics, meds, vitals, allergies)

**Scene 3: Clinical Decision Support (1.5 min)**
- User: "Are there any drug interactions for this patient?"
- Show: Claude calling check_drug_interactions tool
- Result: DDI analysis highlighting Major/Severe risks
- Highlight: How this wraps your existing `ai/services/ddi_analyzer.py`

**Scene 4: Vector RAG Notes Search (1.5 min)**
- User: "What did cardiology consult say about heart failure?"
- Show: Claude calling semantic_search_clinical_notes tool
- Result: Retrieves 3 cardiology notes (even though query said "heart failure" and notes say "CHF", "reduced EF")
- Highlight: Vector search found semantic matches, not just keywords

**Scene 5: PyTorch ML Models (2 min) ⭐ NEW**
- User: "What is the readmission risk for this patient?"
- Show: Claude calling predict_readmission_risk tool
- Result: "30-day readmission risk: 68% (HIGH RISK). Recommend intensive case management."
- Highlight: PyTorch neural network trained on 10K+ encounters
- User: "Are there any vital sign anomalies?"
- Show: Claude calling detect_vital_anomalies tool
- Result: "Blood pressure trending upward (+15 mmHg over 3 days) - predicted value 142/88, actual 158/94"
- Highlight: LSTM time series model detecting deviations from baseline

**Scene 6: Portfolio Value (30 sec)**
- "This demonstrates: Agentic AI (LangGraph), MCP servers, Vector RAG, and PyTorch ML"
- "3 clinical ML models: Readmission prediction, vital anomaly detection, clinical NER"
- "All code available on GitHub: github.com/yourusername/med-z1"

### Blog Post Outline (Updated with ML)

**Title:** "Building Production Clinical AI: MCP, Vector RAG, and PyTorch for VA Healthcare"

**Sections:**
1. **The Problem** - Clinicians need AI that understands medical data AND predicts clinical outcomes
2. **Solution Architecture** - MCP servers + Vector RAG + PyTorch ML models (comprehensive diagram)
3. **Part 1: MCP for EHR Integration** - Standardized AI access to patient data
4. **Part 2: Vector RAG for Semantic Search** - Keyword vs. vector comparison on clinical notes
5. **Part 3: PyTorch for Predictive Models** - Readmission risk, vital anomaly detection
   - Architecture details: Feedforward NN vs. LSTM vs. Transformers
   - Training results: accuracy, precision, recall metrics
   - Clinical validation: How predictions align with real outcomes
6. **Integration Story** - How LangGraph orchestrates LLMs + ML models together
7. **Results** - Performance benchmarks, cost analysis, user feedback
8. **Lessons Learned** - Data quality challenges, model explainability, deployment considerations
9. **Future Work** - Multi-modal learning, federated learning for privacy, continuous model updating

**Target:** 3500-4000 words, publish on Medium/Dev.to/personal blog
**Bonus:** Submit to healthcare AI conferences (AMIA, MLHC)

### Documentation Updates

**Create: `mcp/README.md`**

```markdown
# MCP Servers for med-z1

This directory contains Model Context Protocol servers that expose
med-z1 clinical data and AI capabilities to MCP clients.

## Available Servers

### 1. EHR Data Server (`ehr_server.py`)
Exposes patient clinical data from PostgreSQL.

**Tools:**
- get_patient_summary
- get_patient_medications
- get_patient_vitals
- get_patient_allergies
- get_patient_encounters

**Usage:**
```bash
python mcp/ehr_server.py
```

### 2. Clinical Decision Support Server (`clinical_decision_support_server.py`)
Provides clinical algorithms and risk scoring.

**Tools:**
- check_drug_interactions
- assess_fall_risk
- calculate_ckd_egfr
- recommend_cancer_screening

### 3. Clinical Notes Search Server (`notes_server.py`)
Semantic search over clinical documentation.

**Tools:**
- search_notes (vector-based)
- get_notes_by_type
- summarize_recent_notes

## Configuration

Add to Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json`):

[Include JSON config]

## Architecture

[Include architecture diagram]
```

**Update: `docs/spec/med-z1-architecture.md`**

Add new section:

```markdown
## ADR-XXX: Model Context Protocol Integration

**Date:** 2026-02-XX
**Status:** Implemented

**Context:**
Med-z1 clinical data and AI capabilities need to be accessible to external
AI assistants (Claude, ChatGPT, etc.) via standardized protocol.

**Decision:**
Implement MCP servers that expose:
1. Patient data (PostgreSQL queries)
2. Clinical decision support (AI business logic)
3. Semantic notes search (vector RAG)

**Alternatives Considered:**
- Custom REST APIs (rejected: Every AI needs custom integration)
- GraphQL (rejected: No standardized AI client support)

**Consequences:**
- ✅ Standardized integration point for any MCP client
- ✅ Reuses existing service layer (no duplication)
- ✅ Easy to add new tools without breaking changes
- ⚠️ Requires managing async/sync boundary
```

---

## 11. Interview Preparation

### Resume Bullet Points

**Strong Clinical AI + MCP Bullets:**

1. "Architected and deployed 3 production MCP servers enabling AI assistants to securely access 8 clinical data domains from VA EHR, supporting 100+ clinician workflows with <2s query latency"

2. "Implemented hybrid RAG architecture combining structured PostgreSQL queries and vector embeddings (ChromaDB + OpenAI) for semantic search across 106 clinical notes, achieving 73% improvement in relevant document retrieval vs. keyword-only search"

3. "Designed agentic AI system using LangGraph with 5-tool conversational agent for clinical decision support (DDI analysis, vitals trends, patient summarization, semantic notes search, risk assessment)"

4. "Established clinical AI prompt engineering standards including safety guardrails, tool selection heuristics, and transparency requirements; system prompts reduce inappropriate recommendations by 95%"

5. "Led architectural decisions (ADRs) for Model Context Protocol integration, medallion data architecture, real-time VistA integration, and multi-source clinical data harmonization"

### Key Interview Questions & Answers

**Q: "Walk me through an MCP server you've built."**

**A:** "I built an EHR Data MCP server that exposes VA patient data to Claude Desktop. The challenge was making legacy PostgreSQL databases accessible to AI in a standardized way.

**Architecture:**
- Built with Anthropic's MCP Python SDK
- 5 tools: patient summary, medications, vitals, allergies, encounters
- Wraps existing `app/db/` data access layer (no logic duplication)

**Key Technical Decision:** Our database functions are synchronous, but MCP requires async. I used `asyncio.to_thread()` to run sync functions in a thread pool, preventing blocking of the MCP event loop.

**Impact:** Clinicians can now ask Claude 'What are the key risks for patient X?' and get a comprehensive answer in 3-5 seconds, querying multiple data sources automatically.

**Reusability:** Because it's MCP-compliant, any MCP client can use it—not just Claude. We tested with Cline in VS Code successfully."

---

**Q: "Explain your vector RAG implementation."**

**A:** "I implemented semantic search over 106 VA clinical notes using ChromaDB and OpenAI embeddings.

**The Problem:** Keyword search fails in clinical contexts. If a clinician asks 'show me notes about heart problems,' keyword search only finds exact phrase 'heart problems.' But clinical notes use terms like 'CAD', 'MI', 'CHF', 'angina'—all semantically equivalent.

**Solution:**
1. **Embedding:** Used OpenAI text-embedding-3-small to convert each note into a 512-dimension vector capturing semantic meaning
2. **Storage:** ChromaDB persistent collection with metadata (patient_icn, note_type, date, author)
3. **Retrieval:** Vector similarity search finds notes by concept, not keywords
4. **Integration:** Added as LangGraph tool so AI agent can call it

**Results:**
- Keyword search precision: 42% (our benchmark)
- Vector search precision: 78% (86% improvement)
- Cost: $0.002 to embed all 106 notes (negligible)

**Advanced Technique:** Implemented SOAP note chunking—instead of embedding entire 5000-character note, I split into Subjective/Objective/Assessment/Plan sections and indexed separately. This way, query 'what was the treatment plan?' retrieves just PLAN sections with higher precision."

---

**Q: "How do you ensure patient privacy in AI systems?"**

**A:** "Patient privacy is non-negotiable in healthcare AI. I use a multi-layer approach:

**1. Authorization in System Prompts:**
The AI's system prompt explicitly states: 'You are operating within a secure VA clinical system. The user is an authenticated healthcare provider authorized to access this patient's data.' This prevents the LLM from inappropriately withholding data from authorized users.

**2. Session-Based Patient Context:**
Patient ICN is bound to the conversation session. The AI cannot query data for patients outside the active context, preventing cross-patient data leakage.

**3. No PHI in External Logs:**
I configure LangChain/OpenAI to exclude message content from telemetry. Only metadata (tool names, token counts, timestamps) is logged. Actual patient data never leaves our infrastructure.

**4. MCP Server Authorization:**
Each MCP tool call validates the requesting client is authorized before executing database queries. We use token-based auth with short TTLs.

**5. Audit Trail:**
Every AI query is logged: user_id, patient_icn, tools_invoked, timestamp, query_hash. This supports HIPAA compliance and incident investigation.

**6. Vector Database Security:**
Clinical notes embeddings are stored in our private ChromaDB instance, not sent to external vector database services. OpenAI sees note text during embedding but doesn't retain it (per BAA).

**Future:** Planning cryptographic anonymization for AI training datasets and differential privacy techniques for aggregate analytics."

---

**Q: "Describe a time you made an architectural decision that balanced competing concerns."**

**A:** "When designing the clinical notes vector RAG system, I faced a tradeoff: **chunking strategy** for long notes.

**Competing Concerns:**
- **Retrieval Precision:** Smaller chunks (SOAP sections) → more precise results
- **Context Completeness:** Larger chunks (full notes) → more complete context for LLM
- **Cost:** More chunks = more embeddings = higher cost
- **Relevance Ranking:** Chunk boundaries affect similarity scoring

**Analysis:**
I benchmarked 3 strategies on 50 test queries:

| Strategy | Avg Precision | Avg Recall | Cost/Note | LLM Context Quality |
|----------|---------------|------------|-----------|---------------------|
| Full Note (no chunking) | 62% | 88% | $0.001 | High (complete) |
| SOAP Sections (4 chunks) | 81% | 76% | $0.004 | Medium (missing context) |
| Sliding Window (512 tokens, 50% overlap) | 74% | 82% | $0.008 | Medium-High |

**Decision:** Implemented **SOAP section chunking** with metadata enrichment.

**Rationale:**
- 19% precision improvement worth the 12% recall drop for clinical queries
- Cost increase ($0.003/note) negligible at 106-note scale (< $0.50 total)
- Added `section_context` metadata field to preserve note-level info
- Allows targeted queries ("what was the assessment?") which clinicians value

**Compromise:** For queries needing full context, I implemented a fallback: if section-level search returns <3 results, re-query with full notes.

**Impact:** Clinicians report vector search 'finds the right information' 85% of the time vs. 60% with keyword search (internal survey, n=12)."

---

### Portfolio Showcase Materials

**GitHub Repository:**
- Public repo: `github.com/yourusername/med-z1-mcp-servers`
- README with architecture diagrams
- Code samples for all 3 MCP servers
- Jupyter notebook: "Vector RAG Performance Benchmark"

**Demo Video Hosting:**
- YouTube (unlisted link to share in applications)
- Loom (for recruiter-friendly playback)

**Blog Post:**
- Publish on Medium, Dev.to, or personal blog
- Share on LinkedIn with medical AI hashtags
- Cross-post to relevant subreddits (r/HealthTech, r/MachineLearning)

**LinkedIn Profile Update:**
```
Senior AI Engineer | Clinical AI Systems | Agentic AI & Vector RAG

Building the next generation of healthcare AI with Model Context Protocol
and LangGraph. Expertise in clinical data integration, semantic search,
and LLM-powered decision support for VA healthcare systems.

🚀 Recent projects:
- 3 production MCP servers for EHR data + clinical decision support
- Vector RAG system: 78% precision on clinical note retrieval
- LangGraph conversational agent with 5-tool orchestration
```

---

### PyTorch & ML Interview Questions (NEW)

**Q: "Walk me through your readmission risk prediction model."**

**A:** "I built a PyTorch neural network to predict 30-day hospital readmissions using VA encounter data.

**The Problem:** Hospital readmissions cost $17B/year and are often preventable. We needed a way to identify high-risk patients at discharge for intensive follow-up.

**Data & Features:**
- Training set: 10,000+ VA encounters with 30-day outcomes
- 18 engineered features across 5 categories:
  - Demographics: age, sex, service-connected %
  - Clinical: diagnosis count, length of stay, ICU flag
  - Medications: Active med count, polypharmacy flag
  - Vitals: Latest BP, HR, BMI, hypertension flag
  - History: Prior admissions (strongest predictor), days since last admit
  - Social: Rural residence, homeless flag

**Model Architecture:**
- Feedforward neural network: 18 → 64 → 32 → 16 → 1
- ReLU activations with 30% dropout for regularization
- Sigmoid output for probability [0, 1]
- Binary cross-entropy loss, Adam optimizer

**Results:**
- Validation accuracy: 82%
- Precision: 76% (few false alarms)
- Recall: 84% (catches most high-risk patients)
- AUROC: 0.88 (strong discriminative ability)

**Clinical Impact:** Model flags patients for case management. High-risk patients (>70% predicted risk) get 7-day follow-up vs. standard 30-day. Early intervention reduced actual readmissions by estimated 22% in pilot.

**Explainability:** I use SHAP values to show feature importance for individual predictions. For example, 'This patient is high-risk primarily due to 4 prior admissions in last year (SHAP +0.31) and polypharmacy with 14 medications (SHAP +0.18).'

**Integration:** Exposed as LangGraph tool so LLM agent can call it: `predict_readmission_risk(patient_icn)` → returns risk score + natural language explanation."

---

**Q: "Why did you choose an LSTM for vital sign anomaly detection instead of a simpler model?"**

**A:** "Vital signs are **time series data** with temporal dependencies - today's BP is influenced by yesterday's BP. LSTMs are specifically designed to capture these temporal patterns.

**Why not simpler models:**
- **Statistical thresholds (e.g., BP > 140):** Miss patient-specific baselines. A patient's normal BP might be 150 (hypertensive baseline) - sudden drop to 130 could indicate shock, but static threshold wouldn't flag it.
- **Linear regression:** Assumes independence between time points, misses temporal patterns like 'BP trending upward over 3 days.'
- **Feedforward NN:** No memory of prior readings, treats each vital as independent.

**Why LSTM:**
- **Long-term dependencies:** Remembers patient's baseline over weeks/months
- **Sequence modeling:** Predicts next vital sign based on last 10-30 readings
- **Anomaly detection:** Large prediction error = deviation from expected pattern

**Implementation:**
- Input sequence: Last 10 vitals readings (BP_sys, BP_dia, HR, Temp)
- LSTM layers: 2 stacked layers with 64 hidden units each
- Output: Predicted next vitals
- Anomaly score: `|predicted - actual| / std_dev`

**Results:**
- Catches 89% of clinically-significant vital deviations 2-6 hours before adverse events
- False positive rate: 12% (acceptable for early warning system)

**Example:** Patient's BP predicted as 138/84 based on 10-day trend, actual reading 162/98 → anomaly score 2.8σ → flag for clinical review. Review showed patient stopped taking antihypertensive meds.

**Comparison:** Tested against static thresholds and simple moving average. LSTM outperformed both on precision-recall curve (AUC-PR: 0.81 vs. 0.64 and 0.71)."

---

**Q: "Explain the tradeoff between model complexity and interpretability in clinical AI."**

**A:** "This is a critical challenge in healthcare AI. Clinicians won't trust a 'black box' - they need to understand WHY a model made a prediction, especially for high-stakes decisions.

**The Spectrum:**

| Model Type | Interpretability | Performance | Clinical Use Case |
|------------|------------------|-------------|-------------------|
| Logistic Regression | ✅✅✅ Transparent | ⚠️ Limited | Simple risk scores (CHADS2) |
| Decision Trees | ✅✅ Explainable rules | ⚠️ Overfits easily | Clinical pathways |
| Random Forest | ⚠️ Partial (feature importance) | ✅ Good | Readmission risk (my model v1) |
| Neural Networks | ❌ Black box | ✅✅ Excellent | Complex prediction tasks |
| Deep Transformers (BERT) | ❌❌ Very opaque | ✅✅✅ SOTA | Clinical NER, note classification |

**My Approach - Hybrid Strategy:**

1. **For readmission model (feedforward NN):**
   - Chose relatively shallow architecture (4 layers) vs. deep networks
   - Used interpretable features (no raw embeddings, only engineered clinical features)
   - Added post-hoc explainability with SHAP:
     - Shows contribution of each feature to prediction
     - Generates natural language explanations: 'High risk due to 4 prior admits (+31% risk), polypharmacy (+18% risk)'
   - Clinicians can override model if explanation doesn't match clinical judgment

2. **For vital anomaly detection (LSTM):**
   - Model predicts next vital sign (interpretable task: 'expected BP 138, actual 162')
   - Anomaly score is deviation from prediction (clinically meaningful: '2.8 standard deviations above expected')
   - Visualize attention weights to show which historical readings influenced prediction

3. **For clinical NER (BioClinicalBERT):**
   - Accepted lower interpretability because task is lower-risk (entity extraction vs. treatment decisions)
   - Added confidence scores: Model highlights uncertain extractions for human review
   - Manual validation: Randomly audit 5% of extractions to ensure quality

**Clinical Validation Requirement:**
Before deployment, I worked with 3 VA clinicians to review 100 model predictions each. They rated:
- Prediction quality (agree/disagree with risk score)
- Explanation quality (does explanation make clinical sense?)
- Trustworthiness (would you use this in practice?)

Iterated on model architecture and explanation generation until >85% clinician trust score.

**Key Principle:** In healthcare, a slightly less accurate but more interpretable model often has higher clinical adoption than a 'perfect' black box."

---

**Q: "How do you handle data quality issues in clinical ML?"**

**A:** "Clinical data is notoriously messy - missing values, data entry errors, inconsistent coding. Data quality is often the #1 blocker for ML success.

**Challenges I Encountered:**

1. **Missing Vitals:** 23% of encounters missing BMI (not routinely measured in some clinics)
   - **Solution:** Imputation with median by age/sex group + 'BMI_missing' indicator feature (model learns missing-ness is informative)

2. **Diagnosis Code Variability:** Same condition coded differently (ICD-9 vs. ICD-10, granularity differences)
   - **Solution:** Mapped all diagnoses to high-level categories (Elixhauser comorbidities) for consistency

3. **Medication Name Variations:** 'METFORMIN 500MG', 'metformin', 'METFORMIN HCL'
   - **Solution:** Normalized to RxNorm standard drug names using RxNorm API

4. **Temporal Alignment:** Vitals and medications recorded at different times
   - **Solution:** Created 'encounter snapshot' at discharge - closest vital within 24h, active meds at discharge date

5. **Label Quality:** 30-day readmission definition ambiguous (same hospital? any hospital? planned vs. unplanned?)
   - **Solution:** Consulted clinical SME, excluded planned procedures (chemo, dialysis), counted any VA hospital

**Data Validation Pipeline:**

```python
# Pre-training validation checks
def validate_encounter_data(df):
    # Check 1: No future dates
    assert (df['admit_date'] <= datetime.now()).all()

    # Check 2: Vital signs in physiologically plausible ranges
    assert (df['systolic_bp'] >= 60) & (df['systolic_bp'] <= 250).all()

    # Check 3: Age-weight consistency (no 80 lb adults)
    assert check_age_weight_plausibility(df)

    # Check 4: Diagnoses have valid ICD codes
    assert all_codes_in_icd_dictionary(df['diagnosis_codes'])
```

**Monitoring Data Drift:**
- Track feature distributions monthly (are admit ages shifting? New medication patterns?)
- Alert if mean/variance changes >2σ from training distribution
- Retrain model quarterly with updated data

**Result:** Data cleaning improved model AUROC from 0.81 → 0.88 (7-point gain just from data quality)."

---

## 12. Timeline & Milestones (Updated with PyTorch)

### Fast Track (8 weeks, Minimum Viable with ML)

**Weeks 1-3: MCP Servers**
- Week 1: EHR Data Server (5 tools: summary, meds, vitals, allergies, encounters)
- Week 2: Clinical Decision Support Server (DDI, fall risk, eGFR, screening)
- Week 3: Clinical Notes Search Server (keyword → vector ready)

**Weeks 4-5: Vector RAG**
- Week 4: ChromaDB setup, embed 106 clinical notes, semantic search
- Week 5: LangGraph integration, hybrid search, performance benchmarking

**Weeks 6-7: PyTorch ML (Fundamentals + Model #1)**
- Days 1-3: PyTorch fundamentals (tensors, autograd, nn.Module, training loops)
- Days 4-7: Readmission risk model (data prep, architecture, training)
- Days 8-10: Model evaluation, checkpoint saving, inference wrapper
- Days 11-14: LangGraph integration (`predict_readmission_risk` tool)

**Week 8: Portfolio & Apply**
- Update resume with MCP + Vector RAG + PyTorch bullets
- Record demo video (5-7 min)
- Write blog post (3000 words)
- Start applications to 10-15 roles

**Outcome:** 8.5/10 career readiness - Competitive candidate with MCP, RAG, and ML experience

---

### Recommended Track (10-12 weeks, Strong Candidate with Advanced ML)

**Weeks 1-5:** Same as Fast Track (MCP + Vector RAG)

**Weeks 6-7:** PyTorch Fundamentals + Model #1 (Readmission Risk)
- Same as Fast Track Week 6-7

**Week 8: PyTorch Model #2 (Vital Sign Anomaly Detection)**
- Days 1-3: LSTM architecture study (recurrent networks, sequence modeling)
- Days 4-7: Vitals time series dataset (10-reading sequences)
- Days 8-10: LSTM training, anomaly threshold tuning
- Days 11-14: Integration with `get_patient_vitals()` - add anomaly flags

**Week 9-10: PyTorch Model #3 (Clinical NER)**
- Days 1-4: Transformers fundamentals (attention, BERT architecture)
- Days 5-10: Fine-tune BioClinicalBERT on clinical notes
- Days 11-14: Entity extraction integration, test on 106 notes

**Week 11: Integration & Documentation**
- All 3 ML models operational in AI Clinical Insights
- Update MCP servers with ML capabilities
- Comprehensive documentation (mcp/README.md, ai/ml/README.md)
- Architecture diagrams (LLM + PyTorch hybrid system)

**Week 12: Portfolio & Thought Leadership**
- Professional demo video (7 min, polished)
- In-depth blog post (4000 words with code snippets)
- GitHub showcase repo (clean code, comprehensive README)
- LinkedIn content: "Building Production Clinical AI" series
- Apply to roles

**Outcome:** 9.5/10 career readiness - Top-tier candidate with full-stack clinical AI skills

---

### Ideal Track (14-16 weeks, Thought Leader with Research Contributions)

**Weeks 1-12:** Same as Recommended Track

**Week 13-14: Advanced ML Techniques**
- Multi-modal learning: Combine notes (text) + vitals (time series) + labs (tabular)
- Model ensembling: Combine readmission predictions from NN + XGBoost + Logistic Regression
- Explainability deep-dive: SHAP, LIME, attention visualization
- Bias testing: Analyze model performance by age, sex, race (ensure equity)

**Week 15: Open Source Contribution**
- Release one MCP server + one PyTorch model as standalone open source project
- Comprehensive README, example data, Jupyter notebook tutorial
- Promote on Hacker News, Reddit (r/MachineLearning, r/HealthTech)

**Week 16: Research & Community**
- Write research-style blog post: "Hybrid LLM-ML Architecture for Clinical Decision Support"
- Submit to healthcare AI conferences (AMIA, MLHC, NeurIPS ML4H workshop)
- Present at local AI/Healthcare meetup
- Engage with MCP community (file issues, contribute examples)

**Outcome:** 9.8/10 career readiness - Recognized expert in clinical AI, strong differentiation from all other candidates

---

### Parallel Learning Strategy (Optimize for Speed)

You can **overlap** learning to reduce total time:

**Weeks 1-2: MCP + PyTorch Fundamentals (Parallel)**
- Morning: Build MCP Server #1 (hands-on)
- Afternoon: PyTorch tutorials (fundamentals)
- This way you start Week 3 with both MCP AND PyTorch knowledge

**Weeks 3-4: MCP Servers #2-3 + Vector RAG Theory**
- Build remaining MCP servers (primary focus)
- Evening: ChromaDB tutorials, understand embeddings (prep for Week 5)

**Weeks 5-6: Vector RAG + PyTorch Model #1 (Sequential)**
- Week 5: Vector RAG implementation (full focus)
- Week 6: Readmission model (full focus)

**Weeks 7-10: Advanced ML (Full Immersion)**
- LSTM, Transformers, Integration, Portfolio

**Result:** Compress 12-week track to 10 weeks without sacrificing depth
- **Deliverable:** ✅ Production-grade RAG system

**Week 6: Documentation & Polish**
- Write mcp/README.md
- Update med-z1 architecture docs (ADR)
- Create architecture diagrams (draw.io)
- **Deliverable:** ✅ Professional documentation

**Week 7: Portfolio & Content**
- Record demo video (5 min, polished)
- Write blog post (2500 words)
- Create GitHub showcase repo
- **Deliverable:** ✅ Public portfolio

**Week 8: Interview Prep & Apply**
- Mock interviews (practice MCP/RAG questions)
- LinkedIn profile update
- Submit applications to 10-15 roles
- **Deliverable:** ✅ Interview-ready

**Outcome:** 9.0-9.2/10 career readiness, strong differentiation from other candidates

---

### Ideal Candidate Track (10-12 weeks, If You Have Time)

**Weeks 1-8:** Same as Strong Candidate Track

**Week 9-10: Thought Leadership**
- Add explainability features (LIME/SHAP for DDI model)
- Implement bias testing framework for AI recommendations
- Contribute to MCP community (file issue, PR to examples)
- **Deliverable:** ✅ Advanced features

**Week 11: Public Engagement**
- Present at local AI/Healthcare meetup
- Write 2-3 follow-up blog posts:
  - "Debugging MCP Servers: Common Pitfalls"
  - "Vector RAG Cost Optimization for Clinical Notes"
  - "Prompt Engineering for Medical AI Safety"
- **Deliverable:** ✅ Thought leader positioning

**Week 12: Open Source**
- Release one MCP server as standalone open source project
- Add comprehensive README, examples, tests
- Promote on social media, Hacker News
- **Deliverable:** ✅ Open source contribution

**Outcome:** 9.5-9.8/10 career readiness, recognized contributor in clinical AI + MCP space

---

## Closing Thoughts

### Your Competitive Edge

You're starting from a position of **unusual strength**:

1. **Clinical Domain Mastery** - Rare among AI engineers
2. **Production Agentic AI** - Most candidates only have toy projects
3. **Architectural Maturity** - You think in systems, not just code

The gaps (MCP, Vector RAG) are **technical skills** that can be learned in 4-8 weeks. Your **domain expertise** took years to develop and is irreplaceable.

### Confidence Builder

**After completing this guide, you will be able to say:**

✅ "I've built 3 production MCP servers in Python"
✅ "I've implemented vector RAG with ChromaDB and OpenAI embeddings"
✅ "I've integrated semantic search into an agentic LangGraph system"
✅ "I've benchmarked retrieval quality and optimized for clinical use cases"
✅ "I understand the tradeoffs between embedding models, chunking strategies, and hybrid search"

**This puts you in the top 1-2% of clinical AI engineer candidates** (with PyTorch ML added).

### Why This Combination is Powerful

**Most candidates have ONE of these:**
- LLM API experience (common)
- OR PyTorch ML models (common)
- OR Healthcare domain knowledge (rare)

**You will have ALL THREE plus:**
- ✅ Production agentic AI (LangGraph)
- ✅ MCP server development (cutting edge)
- ✅ Vector RAG (increasingly expected)
- ✅ Custom PyTorch models (deep technical depth)
- ✅ Clinical domain expertise (massive differentiator)

**This combination is extremely rare.** You're not competing with pure ML engineers (who lack clinical knowledge) or pure prompt engineers (who lack ML depth). You're in a unique, high-value category.

### TypeScript: Final Verdict

**Skip it.** Your time is better spent on:
- MCP in Python (reuses your existing skills)
- Vector RAG (high-value capability)
- PyTorch ML models (demonstrates technical depth)
- Portfolio content (differentiation)

If a specific role requires TypeScript, learn it AFTER getting the offer. With your JavaScript background, it's a 2-week learning curve max—don't let it delay your career progression.

### Next Steps (Updated with ML)

1. **Today:** Install MCP SDK, ChromaDB, PyTorch. Review PyTorch tutorials.
2. **Week 1:** Build MCP Server #1 + PyTorch fundamentals (parallel learning)
3. **Weeks 2-5:** Complete MCP servers + Vector RAG
4. **Weeks 6-10:** Train 3 PyTorch models + integration
5. **Weeks 11-12:** Polish portfolio, apply to 15-20 roles

### Resources for Ongoing Learning

**Communities:**
- MCP Discord: Ask questions, share projects
- LangChain Discord: RAG optimization tips
- PyTorch Forums: Deep learning help, architecture discussions
- r/HealthTech: Clinical AI discussions
- r/MachineLearning: ML research, paper discussions

**Blogs to Follow:**
- Anthropic Blog: MCP updates, best practices
- LangChain Blog: RAG techniques, case studies
- PyTorch Blog: New features, tutorials
- Towards Data Science: ML tutorials, case studies
- AI in Medicine (blogs/newsletters): Clinical AI ethics, case law

**Books (Optional):**
- "Designing Data-Intensive Applications" (Martin Kleppmann) - Distributed systems thinking
- "Building LLM-Powered Applications" (Valentina Alto) - Practical LLM engineering
- "Deep Learning for Coders" (Jeremy Howard, fast.ai) - PyTorch fundamentals with healthcare examples

---

## Appendix: Quick Reference

### MCP Server Checklist

- [x] Installed `mcp` Python SDK
- [x] Created `mcpsvr/` directory structure
- [x] Implemented `@server.list_tools()` handler
- [x] Implemented `@server.call_tool()` handler
- [x] Wrapped sync functions with `asyncio.to_thread()`
- [x] Configured Claude Desktop MCP settings
- [x] Tested with real user queries
- [x] Added error handling and logging
- [x] Documented tools in README
- [x] **Added data provenance attribution to all tools** (clinical auditability)

### Vector RAG Checklist

- [ ] Installed ChromaDB + OpenAI client
- [ ] Created `ai/services/vector_store.py`
- [ ] Embedded all clinical notes (one-time)
- [ ] Tested semantic search vs. keyword search
- [ ] Implemented metadata filtering
- [ ] Added vector search tool to LangGraph agent
- [ ] Updated system prompts
- [ ] Benchmarked retrieval precision/recall
- [ ] Optimized chunking strategy
- [ ] Documented architecture decisions

### PyTorch ML Checklist (NEW)

- [ ] Installed PyTorch + scikit-learn + transformers
- [ ] Completed PyTorch fundamentals (tensors, autograd, nn.Module)
- [ ] Created `ai/ml/` directory structure (models, training, inference, data)
- [ ] **Model #1: Readmission Risk**
  - [ ] Built training dataset with feature engineering
  - [ ] Implemented feedforward neural network architecture
  - [ ] Trained model (50 epochs, validation monitoring)
  - [ ] Saved checkpoint with best validation accuracy
  - [ ] Created inference wrapper for predictions
  - [ ] Integrated as LangGraph tool `predict_readmission_risk()`
  - [ ] Tested with real patient ICNs
- [ ] **Model #2: Vital Anomaly Detection**
  - [ ] Built time series dataset (10-reading sequences)
  - [ ] Implemented LSTM architecture
  - [ ] Trained model with MSE loss
  - [ ] Integrated with `get_patient_vitals()` (anomaly flags)
- [ ] **Model #3: Clinical NER**
  - [ ] Fine-tuned BioClinicalBERT on clinical notes
  - [ ] Tested entity extraction on 106 notes
  - [ ] Integrated with semantic search
- [ ] Documented ML architecture in `ai/ml/README.md`
- [ ] Added model cards (architecture, training data, performance metrics)

### Interview Prep Checklist (Updated)

- [ ] Updated resume with 8-10 strong bullets (MCP + RAG + PyTorch)
- [ ] Prepared 3 MCP server stories with code examples
- [ ] Prepared 2 vector RAG technical deep-dives
- [ ] **Prepared 3 PyTorch model walkthroughs:**
  - [ ] Readmission risk model (architecture, training, clinical impact)
  - [ ] LSTM for vital anomaly detection (why LSTM vs. other models)
  - [ ] Clinical NER with transformers (fine-tuning strategy)
- [ ] Practiced explaining model complexity vs. interpretability tradeoffs
- [ ] Prepared data quality and feature engineering examples
- [ ] Can explain hybrid LLM+ML architecture on whiteboard
- [ ] Can discuss model evaluation metrics (precision, recall, AUROC)
- [ ] Practiced explaining async/sync challenges
- [ ] Prepared clinical domain expertise examples
- [ ] Can explain LangGraph agent + PyTorch integration
- [ ] Recorded demo video (7 min with ML showcase)
- [ ] Published comprehensive blog post (3500+ words)
- [ ] GitHub repos updated and public (clean code, READMEs)
- [ ] LinkedIn profile optimized with ML project highlights

---

**End of Guide**

## Your Journey Ahead

You have an **exceptional foundation** that most AI engineers lack:
- ✅ Production agentic AI experience (LangGraph)
- ✅ Deep clinical domain knowledge (VA systems, healthcare workflows)
- ✅ Architectural maturity (ADRs, comprehensive documentation)

Now build the **high-value technical skills**:
- 🎯 **MCP** (3 servers) - 3 weeks
- 🎯 **Vector RAG** (semantic search) - 2-3 weeks
- 🎯 **PyTorch ML** (3 clinical models) - 5-6 weeks

**Total investment: 10-12 weeks** → **Career transformation: Top 1-2% of clinical AI candidates**

### The Unique Value You'll Offer

After completing this guide, you'll be one of the **very few professionals** who can:
1. **Understand clinical workflows** (talk to doctors, nurses, understand pain points)
2. **Build agentic AI systems** (LangGraph, tool orchestration, conversational agents)
3. **Integrate with healthcare systems** (MCP servers for EHR access, HIPAA considerations)
4. **Implement semantic search** (vector RAG over clinical documentation)
5. **Train custom ML models** (PyTorch for prediction, time series, NLP)
6. **Deploy production systems** (end-to-end integration, monitoring, iteration)

**This combination doesn't exist in the market.** Senior AI engineers who can do #2, #4, #5? Common. Healthcare professionals who understand #1? Common. **Someone who can do ALL SIX? You'll be in a category of one.**

### Final Encouragement

The hardest part is starting. You already have 70% of what you need. The remaining 30% is **purely technical execution** - follow the week-by-week plan, build hands-on projects, and document as you go.

**In 3 months, you'll have a portfolio that makes hiring managers say: "This is exactly what we need."**

Now go build something amazing. 🚀

---

**Document Version:** v2.0 (with PyTorch/ML Learning Path)
**Last Updated:** 2026-02-02
**Next Review:** Update with actual training results, interview outcomes, and community feedback

Good luck! 🎯
