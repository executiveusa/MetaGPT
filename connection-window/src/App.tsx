import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// Types
interface CanonicalOrder {
  canonical_order: {
    order_id: string;
    timestamp: string;
    world: string;
    agent: {
      name: string;
      role: string;
      profile: string;
    };
    action: {
      type: string;
      description: string;
      input: Record<string, unknown>;
      output: Record<string, unknown>;
    };
    context: {
      task_id: string | null;
      project: string | null;
      collaborators: string[];
      environment: string | null;
    };
    trace: {
      parent_order_id: string | null;
      sequence_number: number;
      session_id: string;
    };
    metadata: {
      model_used: string;
      tokens_consumed: number;
      duration_ms: number;
      success: boolean;
      error: string | null;
    };
  };
}

interface AgentStatus {
  name: string;
  role: string;
  status: 'idle' | 'thinking' | 'acting' | 'communicating';
  current_task: string | null;
  last_activity: string | null;
  orders_count: number;
}

interface SessionSummary {
  session_id: string;
  session_start: string;
  duration_seconds: number;
  total_orders: number;
  agents_involved: string[];
  agent_counts: Record<string, number>;
  action_types: string[];
  action_counts: Record<string, number>;
  success_rate: number;
}

interface WebSocketMessage {
  type: 'order_created' | 'agent_status' | 'session_summary' | 'heartbeat';
  data: CanonicalOrder | AgentStatus | SessionSummary | { status: string };
  timestamp: string;
}

// API Configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

// Components
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle': return '#6b7280';
      case 'thinking': return '#3b82f6';
      case 'acting': return '#10b981';
      case 'communicating': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  return (
    <span 
      className="status-badge"
      style={{ backgroundColor: getStatusColor(status) }}
    >
      {status}
    </span>
  );
};

const ActionTypeIcon: React.FC<{ type: string }> = ({ type }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'think': return '🧠';
      case 'act': return '⚡';
      case 'communicate': return '💬';
      case 'observe': return '👁️';
      case 'create': return '✨';
      case 'deploy': return '🚀';
      default: return '📋';
    }
  };

  return <span className="action-icon">{getIcon(type)}</span>;
};

const OrderCard: React.FC<{ order: CanonicalOrder }> = ({ order }) => {
  const o = order.canonical_order;
  const time = new Date(o.timestamp).toLocaleTimeString();

  return (
    <div className="order-card">
      <div className="order-header">
        <ActionTypeIcon type={o.action.type} />
        <span className="order-type">{o.action.type}</span>
        <span className="order-time">{time}</span>
      </div>
      <div className="order-agent">
        <strong>{o.agent.name}</strong>
        <span className="agent-role">{o.agent.role}</span>
      </div>
      <div className="order-description">
        {o.action.description}
      </div>
      {o.context.project && (
        <div className="order-project">
          📁 {o.context.project}
        </div>
      )}
      <div className="order-id">
        ID: {o.order_id.slice(0, 8)}...
      </div>
    </div>
  );
};

const AgentCard: React.FC<{ agent: AgentStatus }> = ({ agent }) => {
  return (
    <div className="agent-card">
      <div className="agent-header">
        <div className="agent-avatar">
          {agent.name.charAt(0).toUpperCase()}
        </div>
        <div className="agent-info">
          <h3>{agent.name}</h3>
          <p className="agent-role-text">{agent.role}</p>
        </div>
        <StatusBadge status={agent.status} />
      </div>
      {agent.current_task && (
        <div className="agent-task">
          📌 {agent.current_task}
        </div>
      )}
      <div className="agent-stats">
        <span>📊 {agent.orders_count} orders</span>
        {agent.last_activity && (
          <span>
            🕐 {new Date(agent.last_activity).toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};

const SessionStats: React.FC<{ summary: SessionSummary | null }> = ({ summary }) => {
  if (!summary) return null;

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="session-stats">
      <h2>Session Overview</h2>
      <div className="stats-grid">
        <div className="stat-item">
          <span className="stat-value">{summary.total_orders}</span>
          <span className="stat-label">Total Orders</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{summary.agents_involved.length}</span>
          <span className="stat-label">Active Agents</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{formatDuration(summary.duration_seconds)}</span>
          <span className="stat-label">Duration</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{(summary.success_rate * 100).toFixed(0)}%</span>
          <span className="stat-label">Success Rate</span>
        </div>
      </div>
      <div className="action-breakdown">
        <h3>Action Types</h3>
        <div className="action-bars">
          {Object.entries(summary.action_counts).map(([action, count]) => (
            <div key={action} className="action-bar-item">
              <span className="action-name">{action}</span>
              <div className="action-bar">
                <div 
                  className="action-bar-fill"
                  style={{ 
                    width: `${(count / summary.total_orders) * 100}%` 
                  }}
                />
              </div>
              <span className="action-count">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const ConnectionStatus: React.FC<{ connected: boolean }> = ({ connected }) => {
  return (
    <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
      <span className="status-dot"></span>
      {connected ? 'Connected' : 'Disconnected'}
    </div>
  );
};

// Main App
const App: React.FC = () => {
  const [orders, setOrders] = useState<CanonicalOrder[]>([]);
  const [agents, setAgents] = useState<Record<string, AgentStatus>>({});
  const [sessionSummary, setSessionSummary] = useState<SessionSummary | null>(null);
  const [connected, setConnected] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'orders' | 'agents' | 'stats'>('orders');

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        switch (message.type) {
          case 'order_created':
            setOrders(prev => [message.data as CanonicalOrder, ...prev].slice(0, 100));
            break;
          case 'agent_status':
            const agentData = message.data as AgentStatus;
            setAgents(prev => ({ ...prev, [agentData.name]: agentData }));
            break;
          case 'session_summary':
            setSessionSummary(message.data as SessionSummary);
            break;
          case 'heartbeat':
            // Heartbeat received, connection is alive
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    // Send heartbeat every 30 seconds
    const heartbeatInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);

    return () => {
      clearInterval(heartbeatInterval);
      ws.close();
    };
  }, []);

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ordersRes, agentsRes, sessionRes] = await Promise.all([
          fetch(`${API_URL}/api/orders?limit=50`),
          fetch(`${API_URL}/api/agents`),
          fetch(`${API_URL}/api/session`),
        ]);

        if (ordersRes.ok) {
          const ordersData = await ordersRes.json();
          setOrders(ordersData.orders);
        }

        if (agentsRes.ok) {
          const agentsData = await agentsRes.json();
          const agentsMap: Record<string, AgentStatus> = {};
          agentsData.agents.forEach((agent: AgentStatus) => {
            agentsMap[agent.name] = agent;
          });
          setAgents(agentsMap);
        }

        if (sessionRes.ok) {
          const sessionData = await sessionRes.json();
          setSessionSummary(sessionData);
        }
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>🔮 Connection Window</h1>
          <p className="subtitle">Archon X - Real-time Agent Observation</p>
        </div>
        <ConnectionStatus connected={connected} />
      </header>

      <nav className="tabs">
        <button 
          className={`tab ${selectedTab === 'orders' ? 'active' : ''}`}
          onClick={() => setSelectedTab('orders')}
        >
          📋 Orders ({orders.length})
        </button>
        <button 
          className={`tab ${selectedTab === 'agents' ? 'active' : ''}`}
          onClick={() => setSelectedTab('agents')}
        >
          🤖 Agents ({Object.keys(agents).length})
        </button>
        <button 
          className={`tab ${selectedTab === 'stats' ? 'active' : ''}`}
          onClick={() => setSelectedTab('stats')}
        >
          📊 Statistics
        </button>
      </nav>

      <main className="main-content">
        {selectedTab === 'orders' && (
          <div className="orders-feed">
            <h2>Canonical Order Feed</h2>
            <div className="orders-list">
              {orders.length === 0 ? (
                <div className="empty-state">
                  <p>No orders yet. Waiting for agent activity...</p>
                </div>
              ) : (
                orders.map(order => (
                  <OrderCard key={order.canonical_order.order_id} order={order} />
                ))
              )}
            </div>
          </div>
        )}

        {selectedTab === 'agents' && (
          <div className="agents-grid">
            <h2>Active Agents</h2>
            {Object.keys(agents).length === 0 ? (
              <div className="empty-state">
                <p>No agents connected yet.</p>
              </div>
            ) : (
              Object.values(agents).map(agent => (
                <AgentCard key={agent.name} agent={agent} />
              ))
            )}
          </div>
        )}

        {selectedTab === 'stats' && (
          <SessionStats summary={sessionSummary} />
        )}
      </main>

      <footer className="footer">
        <p>
          Session: {sessionSummary?.session_id.slice(0, 8) || '...'} | 
          Started: {sessionSummary ? new Date(sessionSummary.session_start).toLocaleString() : '...'}
        </p>
      </footer>
    </div>
  );
};

export default App;
