import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuthToken, clearSession } from '../services/auth';
import { Button } from './design-system/Button';
import { Heading } from './design-system/Heading';
import { Text } from './design-system/Text';
import { Spinner } from './design-system/Spinner';
import styles from './ChatInterface.module.css';

interface Message {
  id: string;
  role: 'USER' | 'ASSISTANT';
  content: string;
  created_at: string;
}

export const ChatInterface: React.FC = () => {
  const navigate = useNavigate();
  const token = getAuthToken();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  console.log('ChatInterface mounted, token:', token ? 'present' : 'missing');

  const handleLogout = () => {
    clearSession();
    navigate('/login');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Create a new thread on mount
    const createThread = async () => {
      if (!token) {
        console.error('No token available for thread creation');
        setError('Authentication required');
        return;
      }

      console.log('Creating thread with token:', token.substring(0, 20) + '...');

      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        console.log('API URL:', apiUrl);
        const response = await fetch(`${apiUrl}/chatkit/threads`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({}),
        });

        console.log('Thread creation response status:', response.status);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Thread created successfully:', data);
        setThreadId(data.thread_id);
      } catch (err: any) {
        setError('Failed to create conversation thread');
        console.error('Thread creation error:', err);
      }
    };
    createThread();
  }, [token]);

  const handleSend = async () => {
    if (!input.trim() || !threadId || loading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    // Add user message to UI
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      role: 'USER',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      // Send message and get streaming response
      const response = await fetch(`${import.meta.env.VITE_API_URL}/chatkit/threads/${threadId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ text: userMessage }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';
      let assistantMsgId = `temp-assistant-${Date.now()}`;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              if (!data || data === '[DONE]') continue;

              try {
                const parsed = JSON.parse(data);

                // Handle error responses
                if (parsed.error) {
                  setError(parsed.error);
                  setLoading(false);
                  return;
                }

                // Handle content responses
                if (parsed.content) {
                  assistantMessage += parsed.content;
                  // Update assistant message in real-time
                  setMessages((prev) => {
                    const filtered = prev.filter((m) => m.id !== assistantMsgId);
                    return [
                      ...filtered,
                      {
                        id: assistantMsgId,
                        role: 'ASSISTANT',
                        content: assistantMessage,
                        created_at: new Date().toISOString(),
                      },
                    ];
                  });
                }
              } catch (e) {
                // If JSON parsing fails, treat as plain text content
                console.warn('Failed to parse SSE data as JSON:', data);
                assistantMessage += data;
                setMessages((prev) => {
                  const filtered = prev.filter((m) => m.id !== assistantMsgId);
                  return [
                    ...filtered,
                    {
                      id: assistantMsgId,
                      role: 'ASSISTANT',
                      content: assistantMessage,
                      created_at: new Date().toISOString(),
                    },
                  ];
                });
              }
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error('Send message error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.chatInterface}>
      {/* Header */}
      <div className={styles.header}>
        <Heading level="h1" className={styles.title}>
          Agentic Todo
        </Heading>
        <Button variant="ghost" size="md" onClick={handleLogout}>
          Logout
        </Button>
      </div>

      {/* Messages */}
      <div className={styles.messages}>
        {messages.length === 0 && !loading && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>💬</div>
            <Heading level="h2" className={styles.emptyTitle}>
              Welcome to Agentic Todo!
            </Heading>
            <Text size="lg" className={styles.emptyDescription}>
              Chat with AI to manage your tasks effortlessly
            </Text>
            <div className={styles.suggestions}>
              <Text size="sm" className={styles.suggestionsTitle}>
                Try saying:
              </Text>
              <ul className={styles.suggestionsList}>
                <li>"Add a task to buy groceries"</li>
                <li>"Show me my tasks"</li>
                <li>"Mark my first task as complete"</li>
                <li>"What do I need to do today?"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.messageWrapper} ${
              msg.role === 'USER' ? styles.userMessage : styles.assistantMessage
            }`}
          >
            <div className={styles.messageContent}>
              <Text size="base" className={styles.messageText}>
                {msg.content}
              </Text>
              <Text size="xs" className={styles.messageTime}>
                {new Date(msg.created_at).toLocaleTimeString()}
              </Text>
            </div>
          </div>
        ))}

        {loading && (
          <div className={styles.loadingIndicator}>
            <Spinner size="sm" />
            <Text size="sm" className={styles.loadingText}>
              AI is thinking...
            </Text>
          </div>
        )}

        {error && (
          <div className={styles.errorMessage} role="alert">
            <span className={styles.errorIcon}>⚠</span>
            <Text size="sm" className={styles.errorText}>
              {error}
            </Text>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={styles.inputContainer}>
        <div className={styles.inputWrapper}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (e.g., 'Add a task to buy milk')"
            disabled={loading || !threadId}
            className={styles.input}
            aria-label="Chat message input"
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim() || !threadId}
            variant="primary"
            size="md"
            loading={loading}
            className={styles.sendButton}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
