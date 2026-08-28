class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectTimeout = null;
    this.shouldReconnect = false;
    this._onMessage = null;
    this._onOpen = null;
    this._onClose = null;
  }

  connect(onMessage, onOpen, onClose) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this._onMessage = onMessage;
    this._onOpen = onOpen;
    this._onClose = onClose;
    this.shouldReconnect = true;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}/ws/simulation`;

    try {
      this.ws = new WebSocket(url);
    } catch (e) {
      console.warn('WebSocket connection failed:', e);
      return;
    }

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      if (onOpen) onOpen();
      if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (onMessage) onMessage(data);
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      if (onClose) onClose();
      // Only auto-reconnect if explicitly requested
      if (this.shouldReconnect) {
        this.reconnectTimeout = setTimeout(() => {
          this.connect(this._onMessage, this._onOpen, this._onClose);
        }, 5000);
      }
    };

    this.ws.onerror = (err) => {
      // Don't spam console, just log once
      console.warn('WebSocket connection unavailable');
      this.shouldReconnect = false; // Stop reconnecting on error
    };
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    this.shouldReconnect = false;
    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export default new WebSocketService();
