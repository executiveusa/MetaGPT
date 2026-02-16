# Meta Agent Implementation Plan

## Executive Summary

This document outlines the implementation plan for the Meta Agent - the Chief Orchestrator of Archon X. The Meta Agent coordinates all agents in the ecosystem with full transparency, tracking every action in the Canonical Order system.

## Completed Components

### 1. Core Modules (metagpt/core/)

#### Heart Module (`heart.py`)
- **Purpose**: Core values engine that guides every decision
- **Components**:
  - `CoreValue` enum: Loyalty, Honor, Truth, Respect
  - `HigherConscience`: Ethical framework for humanity's good
  - `CollaborationRule`: Rules for agent collaboration
  - `Heart` class: Main engine with value checking
- **Key Functions**:
  - `check_values_alignment()`: Validates actions against core values
  - `get_heart()`: Singleton instance accessor

#### Soul Module (`soul.py`)
- **Purpose**: Behavior engine for decision-making patterns
- **Components**:
  - `BehaviorMode` enum: Orchestrate, Execute, Observe, Deliberate, Rest
  - `DecisionType` enum: Task assignment, coordination, conflict resolution, etc.
  - `BehaviorPattern`: Situation-response patterns
  - `DecisionFramework`: Structured decision-making
  - `Soul` class: Main behavior engine with learning capability
- **Key Functions**:
  - `get_behavior_pattern()`: Match situation to behavior
  - `make_decision()`: Use decision framework
  - `record_experience()`: Learn from outcomes

#### Memory Module (`memory.py`)
- **Purpose**: Persistent memory across sessions
- **Components**:
  - `MemoryType`: Episodic, Semantic, Procedural, Working, Mission
  - `MemoryEntry`: Individual memory with importance scoring
  - `PersistentMemory` class: Full memory system with persistence
- **Key Functions**:
  - `store()`: Save memories with importance
  - `search()`: Query memories by content
  - `recall()`: Retrieve specific memories
  - `consolidate()`: Clean up low-importance memories

### 2. Meta Agent Role (`metagpt/roles/meta_agent.py`)

- **Extends**: `RoleZero` from MetaGPT
- **Integrates**: Heart, Soul, Memory modules
- **Tools**:
  - `publish_team_message`: Send messages to agents
  - `create_canonical_order`: Track all actions
  - `get_session_summary`: Report progress
  - `remember_experience`: Store in memory
  - `check_values`: Validate actions

### 3. Canonical Order System (`metagpt/utils/canonical_order.py`)

- **Purpose**: Comprehensive audit trail of every agent action
- **Features**:
  - Session-based tracking
  - Parent-child order relationships
  - Automatic persistence to disk
  - Export to JSON/JSONL/Markdown

### 4. Beads Integration (`metagpt/utils/beads_integration.py`)

- **Purpose**: Connect Canonical Orders to Beads CLI for task management
- **Features**:
  - Create/update/claim issues
  - Sync with git
  - Map Canonical Orders to Beads issues

## Remaining Work

### Phase 1: Connection Window (Frontend)

The Connection Window is the real-time observation panel where humans watch AI agents collaborate.

#### Components to Build:

1. **WebSocket Server** (`connection-window/server/`)
   - FastAPI + WebSocket for real-time updates
   - Broadcast Canonical Order events
   - Subscribe to agent activities

2. **React Frontend** (`connection-window/src/`)
   - Agent activity feed
   - Canonical Order timeline
   - Agent status dashboard
   - Task progress visualization

3. **API Endpoints**:
   - `GET /api/agents` - List all agents
   - `GET /api/orders` - Get Canonical Orders
   - `WS /ws/orders` - Real-time order stream
   - `GET /api/session/summary` - Session stats

### Phase 2: Test Suite with Ralphy

Using the ralphy framework from `/tmp/ralphy`:

1. **Unit Tests**:
   - Heart module value checking
   - Soul behavior pattern matching
   - Memory storage and retrieval
   - Canonical Order creation

2. **Integration Tests**:
   - Meta Agent coordination
   - Multi-agent workflows
   - WebSocket event streaming

3. **End-to-End Tests**:
   - Full task orchestration
   - Connection Window visualization
   - Deployment verification

### Phase 3: Coolify Deployment

1. **Docker Configuration**:
   - Multi-stage Dockerfile
   - docker-compose.yml for services
   - Environment variable injection

2. **Coolify Setup**:
   - Use provided API tokens
   - Configure domain and SSL
   - Set up resource limits

3. **CI/CD Pipeline**:
   - GitHub Actions workflow
   - Automated testing
   - Deploy on merge to main

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARCHON X                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   HEART     │    │    SOUL     │    │   MEMORY    │         │
│  │ Core Values │    │  Behaviors  │    │ Persistent  │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                   ┌────────▼────────┐                          │
│                   │   META AGENT    │                          │
│                   │ Chief Orchestr. │                          │
│                   └────────┬────────┘                          │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         │                  │                  │                │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐        │
│  │ Canonical   │    │   Beads     │    │ Connection  │        │
│  │   Order     │    │ Integration │    │   Window    │        │
│  │  Tracking   │    │   (Tasks)   │    │ (Frontend)  │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Core Framework | MetaGPT (Python) |
| Heart/Soul/Memory | Python + Pydantic |
| Canonical Order | Python + JSONL |
| Connection Window | Next.js + React + TypeScript |
| Real-time | WebSocket + FastAPI |
| Task Management | Beads CLI |
| Testing | Ralphy + Pytest |
| Deployment | Docker + Coolify |
| Database | Supabase (PostgreSQL) |

## Next Steps

1. **Build Connection Window WebSocket Server**
   - Create FastAPI server with WebSocket support
   - Implement Canonical Order broadcasting
   - Add subscription management

2. **Build Connection Window Frontend**
   - Set up Next.js project
   - Create agent activity components
   - Implement real-time updates

3. **Create Test Suite**
   - Set up pytest with ralphy patterns
   - Write unit tests for core modules
   - Write integration tests for Meta Agent

4. **Deploy to Coolify**
   - Create Dockerfile
   - Configure Coolify application
   - Set up domain and SSL

## Success Criteria

- [ ] All core modules pass unit tests
- [ ] Meta Agent can coordinate multi-agent workflows
- [ ] Connection Window shows real-time agent activity
- [ ] Canonical Orders are persisted and queryable
- [ ] System deployed and accessible via public URL
- [ ] All secrets remain secure (never exposed)

---

*Generated by Meta Agent - Chief Orchestrator of Archon X*
*Last Updated: 2026-02-15*
