/**
 * Connection Window - Type Definitions
 * 
 * Types for the real-time agent observation panel
 */

// ============================================================================
// AGENT TYPES
// ============================================================================

export type AgentStatus = 'idle' | 'thinking' | 'acting' | 'communicating' | 'error';

export interface Agent {
  id: string;
  name: string;
  role: string;
  profile: string;
  avatarUrl?: string;
  status: AgentStatus;
  lastSeen?: string;
  metadata?: Record<string, unknown>;
}

// ============================================================================
// MESSAGE TYPES
// ============================================================================

export type MessageType = 'text' | 'code' | 'file' | 'command' | 'system';

export interface MessageContent {
  type: MessageType;
  body: string;
  attachments?: Attachment[];
  codeLanguage?: string;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  url?: string;
  size?: number;
}

export interface AgentMessage {
  id: string;
  timestamp: string;
  fromAgent: Agent;
  toAgent: Agent | null;
  content: MessageContent;
  context?: MessageContext;
  canonicalOrderId?: string;
  isBroadcast?: boolean;
}

export interface MessageContext {
  task?: string;
  project?: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  parentMessageId?: string;
}

// ============================================================================
// CANONICAL ORDER TYPES
// ============================================================================

export type ActionType = 'think' | 'act' | 'communicate' | 'observe' | 'create' | 'deploy';

export interface CanonicalOrder {
  orderId: string;
  timestamp: string;
  world: string;
  agent: {
    name: string;
    role: string;
    profile: string;
  };
  action: {
    type: ActionType;
    description: string;
    input: Record<string, unknown>;
    output: Record<string, unknown>;
  };
  context: {
    taskId?: string;
    project?: string;
    collaborators?: string[];
    environment?: string;
  };
  trace: {
    parentOrderId?: string;
    sequenceNumber: number;
    sessionId: string;
  };
  metadata: {
    modelUsed?: string;
    tokensConsumed?: number;
    durationMs?: number;
    success: boolean;
    error?: string;
  };
}

// ============================================================================
// SESSION TYPES
// ============================================================================

export interface SessionSummary {
  sessionId: string;
  sessionStart: string;
  durationSeconds: number;
  totalOrders: number;
  agentsInvolved: string[];
  agentCounts: Record<string, number>;
  actionTypes: string[];
  actionCounts: Record<string, number>;
  successRate: number;
}

export interface ObservationSession {
  id: string;
  startedAt: string;
  endedAt?: string;
  agents: Agent[];
  messages: AgentMessage[];
  canonicalOrders: CanonicalOrder[];
  summary?: SessionSummary;
}

// ============================================================================
// WEBSOCKET EVENT TYPES
// ============================================================================

export type WebSocketEventType = 
  | 'agent:message'
  | 'agent:status'
  | 'session:start'
  | 'session:end'
  | 'canonical_order'
  | 'error';

export interface WebSocketEvent<T = unknown> {
  type: WebSocketEventType;
  timestamp: string;
  data: T;
}

export interface AgentStatusEvent {
  agent: Agent;
  previousStatus: AgentStatus;
}

export interface AgentMessageEvent {
  message: AgentMessage;
}

export interface CanonicalOrderEvent {
  order: CanonicalOrder;
}

// ============================================================================
// UI TYPES
// ============================================================================

export interface ConnectionWindowConfig {
  wsEndpoint: string;
  agentAvatars: Record<string, string>;
  theme: 'dark' | 'light';
  showTimeline: boolean;
  enableReplay: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  type: 'message' | 'status' | 'action';
  agentName: string;
  description: string;
  icon?: string;
}

// ============================================================================
// REPLAY TYPES
// ============================================================================

export interface ReplayState {
  isPlaying: boolean;
  speed: 0.5 | 1 | 1.5 | 2;
  currentIndex: number;
  totalEvents: number;
  progress: number;
}

export interface ReplayEvent {
  id: string;
  timestamp: string;
  type: 'message' | 'status_change' | 'action_start' | 'action_end';
  data: AgentMessage | AgentStatusEvent | CanonicalOrder;
}
