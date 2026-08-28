import { useState, useEffect, useCallback } from 'react';
import wsService from '../services/websocket';

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    wsService.connect(
      (msg) => {
        setLastMessage(msg);
        setMessages((prev) => [...prev, msg].slice(-100)); // Keep last 100
      },
      () => setConnected(true),
      () => setConnected(false)
    );

    return () => wsService.disconnect();
  }, []);

  const send = useCallback((data) => {
    wsService.send(data);
  }, []);

  return { connected, lastMessage, messages, send };
}
