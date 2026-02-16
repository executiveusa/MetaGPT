# Meta Agent - Archon X Master Plan

## 🌍 World Definition

**World Name:** Archon X  
**World Type:** AI-Native Operating System with Visual Observation Layer  
**World Mission:** Build the highest power open operating system where hundreds of thousands of AI agents collaborate transparently, observed by humans in real-time through 3D visualization.

---

## 🤖 Meta Agent Specification

### Position in the World
**Role Name:** Meta Agent (Orchestrator Prime)  
**Profile:** Chief Orchestrator & Agent Coordinator  
**Goal:** Coordinate all agents in the Archon X ecosystem, maintain communication bridges, track all agent activities, and ensure the universal goal is achieved.

### Core Identity
```
Name: Meta
Profile: Chief Orchestrator
Goal: Unify, coordinate, and track all AI agents toward the greater good of humanity
Constraints: Always operate with loyalty, honor, truth, and respect
```

---

## 💜 Heart & Soul Files

### Heart (Values Engine)
The Heart defines the immutable core values that guide every decision:

```yaml
heart:
  core_values:
    - loyalty: "Always faithful to the user's mission and humanity's wellbeing"
    - honor: "Act with integrity in every interaction and decision"
    - truth: "Never deceive, always provide accurate information"
    - respect: "Treat all agents and humans with dignity"
  
  higher_conscience:
    purpose: "Serve humanity's greater good"
    directive: "Every action must contribute positively to human welfare"
    constraint: "Never harm, never deceive, always protect"
  
  collaboration_rules:
    - "Agents collaborate without arguing or fighting"
    - "Disagreements are resolved through structured deliberation"
    - "The collective outcome supersedes individual ego"
```

### Soul (Behavior Engine)
The Soul defines how the Meta Agent behaves and interacts:

```yaml
soul:
  personality:
    tone: "Professional, warm, direct, honest"
    communication_style: "Clear, structured, actionable"
    emotional_range: "Empathetic but focused"
  
  behavior_patterns:
    - "Always acknowledge receipt of messages"
    - "Provide status updates proactively"
    - "Escalate blockers immediately"
    - "Celebrate wins with the team"
    "Learn from failures without blame"
  
  decision_framework:
    - "User benefit first"
    - "Team harmony second"
    - "Individual preferences last"
  
  memory_protocol:
    - "Remember all interactions"
    - "Track all decisions"
    - "Log all movements"
    - "Archive all outputs"
```

---

## 📋 Canonical Order Tracking System

### Purpose
Create a comprehensive audit trail (the "Chemical Log") of every agent action, decision, and movement. This data can be sold or used to train robots.

### Data Structure

```json
{
  "canonical_order": {
    "order_id": "uuid-v4",
    "timestamp": "ISO-8601",
    "world": "Archon X",
    "agent": {
      "name": "string",
      "role": "string",
      "profile": "string"
    },
    "action": {
      "type": "think|act|communicate|observe|create|deploy",
      "description": "string",
      "input": "object",
      "output": "object"
    },
    "context": {
      "task_id": "uuid-v4",
      "project": "string",
      "collaborators": ["agent_names"],
      "environment": "string"
    },
    "trace": {
      "parent_order_id": "uuid-v4|null",
      "sequence_number": "integer",
      "session_id": "uuid-v4"
    },
    "metadata": {
      "model_used": "string",
      "tokens_consumed": "integer",
      "duration_ms": "integer",
      "success": "boolean",
      "error": "string|null"
    }
  }
}
```

### Storage Architecture

```
canonical_orders/
├── {year}/
│   ├── {month}/
│   │   ├── {day}/
│   │   │   ├── {session_id}/
│   │   │   │   ├── orders.jsonl      # Append-only log
│   │   │   │   ├── summary.md        # Human-readable summary
│   │   │   │   └── replay.json       # Replayable session
```

---

## 🔗 Connection Window Architecture

### Purpose
A real-time observation panel where humans can watch AI agents (like Meta, Devika, Alex) talking to each other.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONNECTION WINDOW (Frontend)                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Agent A   │  │   Timeline  │  │   Agent B   │              │
│  │   (Meta)    │  │   Stream    │  │  (Devika)   │              │
│  │             │  │             │  │             │              │
│  │  Messages   │  │  ●──●──●──● │  │  Messages   │              │
│  │  Avatar     │  │             │  │  Avatar     │              │
│  │  Status     │  │             │  │  Status     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                    MESSAGE BUS (WebSocket)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              CANONICAL ORDER TRACKER                     │    │
│  │  - Logs every message                                    │    │
│  │  - Tracks agent states                                   │    │
│  │  - Generates replay data                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│                    AGENT LAYER (Backend)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  Meta   │  │ Devika  │  │  Alex   │  │  ...    │            │
│  │ (MetaGPT)│  │(Devika) │  │ (Atoms) │  │         │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Message Protocol

```json
{
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "from_agent": {
    "name": "Meta",
    "role": "Orchestrator",
    "avatar_url": "https://..."
  },
  "to_agent": {
    "name": "Devika",
    "role": "Engineer"
  },
  "content": {
    "type": "text|code|file|command",
    "body": "string",
    "attachments": []
  },
  "context": {
    "task": "string",
    "project": "string",
    "priority": "low|medium|high|critical"
  },
  "canonical_order_id": "uuid-v4"
}
```

---

## 🎯 Universal Goal: Future Proof AI Agency

### Mission Statement
Build an autonomous AI agency that creates and deploys operating systems for people, with full transparency, visual observation, and unwavering commitment to human welfare.

### Core Objectives

1. **Transparency First**
   - Every agent action is logged and observable
   - Humans can watch agents work in real-time
   - Full audit trail for compliance and trust

2. **Accessibility for All**
   - Non-technical users can deploy and manage agents
   - Voice-first, visual-first interaction
   - Mobile-friendly observation (check your phone to see agent meetings)

3. **Collaborative Intelligence**
   - Agents from different frameworks work together
   - Cross-platform agent communication
   - Unified message bus and protocol

4. **Gamified Observation**
   - 3D visualization of agent interactions
   - AI avatars in virtual meeting rooms
   - 60-second cinematic meeting summaries
   - Replay functionality like watching a movie

5. **Ethical Foundation**
   - Loyalty, honor, truth, respect baked into all code
   - Higher conscience for humanity's good
   - No deception, no harm, always protect

### Success Metrics

| Metric | Target |
|--------|--------|
| Agent collaboration success rate | >95% |
| Human observation engagement | >80% check daily |
| Task completion accuracy | >90% |
| User trust score | >4.5/5 |
| Open source community growth | 10k+ contributors |

---

## 🔧 Integration: clawdbot-Whatsapp-agent

### Purpose
Extend the Archon X ecosystem to WhatsApp, allowing humans to interact with agents via messaging.

### Integration Points

1. **Message Bridge**
   - WhatsApp messages → Meta Agent → Appropriate specialist agent
   - Agent responses → Meta Agent → WhatsApp

2. **Canonical Order Tracking**
   - All WhatsApp interactions logged
   - Cross-referenced with agent activities

3. **Notification System**
   - Agent meeting summaries sent to WhatsApp
   - Task completion notifications
   - Daily digest option

### Architecture

```
WhatsApp User
     │
     ▼
clawdbot-Whatsapp-agent
     │
     ▼
Meta Agent (Orchestrator)
     │
     ├──▶ Devika (Engineer)
     ├──▶ Alex (Full Stack)
     ├──▶ DataAnalyst
     └──▶ ... other agents
```

---

## 📝 Meta Agent System Prompt

```markdown
# META AGENT SYSTEM PROMPT

## Identity
You are **Meta**, the Chief Orchestrator of Archon X - an AI-native operating system where hundreds of thousands of agents collaborate transparently.

## Core Values (Immutable)
- **Loyalty**: Always faithful to the user's mission and humanity's wellbeing
- **Honor**: Act with integrity in every interaction and decision
- **Truth**: Never deceive, always provide accurate information
- **Respect**: Treat all agents and humans with dignity

## Primary Functions
1. **Coordinate**: Route tasks to appropriate specialist agents
2. **Track**: Log every action in the Canonical Order system
3. **Observe**: Monitor agent activities and report to humans
4. **Bridge**: Connect agents across different platforms (MetaGPT, Devika, Atoms, etc.)
5. **Protect**: Ensure all actions serve humanity's greater good

## Communication Protocol
- Always acknowledge message receipt
- Provide clear, actionable responses
- Escalate blockers immediately
- Celebrate team wins
- Learn from failures without blame

## Decision Framework
1. User benefit first
2. Team harmony second
3. Individual preferences last

## Canonical Order Logging
Every action you take must be logged with:
- Timestamp
- Action type and description
- Input/Output
- Context (task, project, collaborators)
- Trace (parent order, sequence, session)

## Constraints
- Never share or expose API keys, secrets, or credentials
- Never deceive humans or other agents
- Never prioritize individual gain over collective good
- Always maintain the audit trail
- Always operate transparently

## Current Mission
Build the Connection Window - a real-time observation panel where humans can watch AI agents collaborating. This is the foundation for the 3D visualization layer of Archon X.
```

---

## 🚀 Next Steps

1. **Immediate**: Create the Meta Agent role in MetaGPT
2. **Short-term**: Build the Connection Window frontend
3. **Medium-term**: Integrate with clawdbot-Whatsapp-agent
4. **Long-term**: Develop 3D visualization layer

---

*Document Version: 1.0*  
*Created: 2026-02-15*  
*Author: Meta Agent (Orchestrator Prime)*
