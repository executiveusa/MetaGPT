# Connection Window - Agent Observation Panel

A real-time observation panel where humans can watch AI agents (like Meta, Devika, Alex) talking to each other.

## Architecture

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

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Features

- **Real-time Agent Observation**: Watch agents collaborate in real-time
- **Split-Panel Interface**: See both sides of agent conversations
- **Timeline Stream**: Visual timeline of message flow
- **Agent Avatars**: Visual representation of each agent
- **Status Indicators**: See when agents are thinking, acting, or idle
- **Message Logging**: Full audit trail of all communications
- **Replay Mode**: Review past agent conversations

## Message Protocol

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

## Integration with MetaGPT

The Connection Window integrates with MetaGPT's Canonical Order system:

```python
from metagpt.roles import MetaAgent
from metagpt.utils.canonical_order import CanonicalOrder

# Create Meta Agent with tracking
meta = MetaAgent()

# All actions are automatically logged
meta.publish_team_message(
    content="Build the landing page for Archon X",
    send_to="Devika"
)

# Get session summary
summary = meta.get_session_summary()
```

## WebSocket Events

| Event | Description |
|-------|-------------|
| `agent:message` | New message from an agent |
| `agent:status` | Agent status change (thinking, acting, idle) |
| `session:start` | New observation session started |
| `session:end` | Observation session ended |
| `canonical_order` | New canonical order created |

## Configuration

```typescript
interface ConnectionWindowConfig {
  wsEndpoint: string;          // WebSocket endpoint
  agentAvatars: {              // Agent avatar URLs
    [agentName: string]: string;
  };
  theme: 'dark' | 'light';     // UI theme
  showTimeline: boolean;       // Show timeline stream
  enableReplay: boolean;       // Enable replay mode
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}
```

## Future: 3D Visualization

The Connection Window is the foundation for the 3D visualization layer:

1. **Phase 1** (Current): 2D split-panel observation
2. **Phase 2**: Animated avatars with expressions
3. **Phase 3**: 3D meeting room environment
4. **Phase 4**: AI-generated world locations
5. **Phase 5**: Cinematic replay clips

---

*Part of Archon X - AI-Native Operating System*
