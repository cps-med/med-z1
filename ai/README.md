# AI/ML Subsystem

AI and machine learning layer for med-z1, providing intelligent clinical insights and decision support.

## Overview

The AI subsystem delivers AI-assisted capabilities to help clinicians quickly understand patient stories, identify key risks, and detect gaps in care. This component is designed to augment (not replace) clinical judgment by surfacing relevant patterns and insights from longitudinal health records.

**Current Status:** Placeholder (Phase 4 implementation planned)

## Primary Use Cases

1. **Chart Overview Summarization**
   - Generate concise patient story summaries from longitudinal data
   - Highlight key clinical events and trends
   - Surface most relevant information for current encounter

2. **Drug-Drug Interaction (DDI) Risk Assessment**
   - Identify potential medication interactions across VA and non-VA prescriptions
   - Provide severity ratings and clinical guidance
   - Alert clinicians to emerging risks

3. **Patient Flag-Aware Risk Narratives**
   - Generate contextual risk assessments based on active patient flags
   - Synthesize risk indicators from multiple clinical domains
   - Provide actionable recommendations for care management

## Technology Stack

**LLM Integration:**
- OpenAI-compatible clients (GPT-4, Claude, or local models)
- Support for multiple LLM providers via unified interface

**NLP and Embeddings:**
- `transformers` - Hugging Face models for text processing
- `sentence-transformers` - Semantic embeddings for similarity search
- `langchain`/`langgraph` - Agent workflows and orchestration (optional)

**Vector Storage:**
- **Phase 4 (Initial):** Local vector stores (Chroma or FAISS)
- **Later Phases:** pgvector in PostgreSQL for production deployment

## Architecture Integration

**Data Sources:**
- Reads from Gold layer Parquet files (curated, query-friendly data)
- May access PostgreSQL serving database for real-time patient context
- No direct access to Bronze/Silver layers or raw CDW data

**API Integration:**
- Exposes endpoints via FastAPI (likely in `app/routes/ai.py`)
- Called from main med-z1 web application as needed
- Asynchronous processing for longer-running AI tasks

**Configuration:**
- Shares root-level `.env` and `config.py` for API keys and model settings
- Environment variables: `OPENAI_API_KEY`, `LLM_PROVIDER`, `EMBEDDING_MODEL`, etc.

## Future Directory Structure

```
ai/
  models/         # Model wrappers and LLM clients
  prompts/        # Prompt templates and chains
  embeddings/     # Embedding generation and vector store management
  agents/         # Agentic workflows (if using langchain/langgraph)
  utils/          # Shared utilities (caching, retry logic, etc.)
  tests/          # Unit and integration tests
  README.md       # This file
```

## Development Notes

**Privacy and Security:**
- All development uses ONLY synthetic, non-PHI/PII data
- Production deployment will require PHI-safe LLM endpoints (VA-approved models)
- Audit logging for all AI-generated content

**Performance Considerations:**
- AI operations may have 1-10 second latency (LLM API calls)
- Use asynchronous processing and caching where appropriate
- Display loading indicators in UI for AI-powered features

**Quality Assurance:**
- AI-generated content should be clearly labeled in UI
- Provide citations/sources for AI recommendations when possible
- Allow clinicians to provide feedback on AI suggestions (future)

## Getting Started

Phase 4 implementation planned for 3-6 weeks after Phases 0-3 complete. Until then, this subsystem serves as a placeholder for future AI/ML capabilities.

For full developer setup instructions, see `docs/guide/developer-setup-guide.md`.
