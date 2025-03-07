<script>
  import { onMount, onDestroy } from 'svelte';
  import { io } from 'socket.io-client';
  
  // State variables
  let socket;
  let connected = false;
  let messages = [];
  let inputMessage = '';
  let randomUpdates = [];
  let connectionStatus = 'Disconnected';
  
  // Connection options - adjust URL as needed for your setup
  const SERVER_URL = 'http://localhost:5000';
  
  onMount(() => {
    // Initialize socket connection
    initializeSocket();
  });
  
  onDestroy(() => {
    // Clean up socket connection when component is destroyed
    if (socket) {
      socket.disconnect();
    }
  });
  
  function initializeSocket() {
    try {
      connectionStatus = 'Connecting...';
      
      // Initialize socket.io connection
      socket = io(SERVER_URL, {
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });
      
      // Connection event handlers
      socket.on('connect', () => {
        connected = true;
        connectionStatus = 'Connected';
        addMessage('System', 'Connected to server');
      });
      
      socket.on('disconnect', () => {
        connected = false;
        connectionStatus = 'Disconnected';
        addMessage('System', 'Disconnected from server');
      });
      
      socket.on('connect_error', (error) => {
        connectionStatus = 'Connection Error';
        addMessage('System', `Connection error: ${error.message}`);
      });
      
      socket.on('reconnect_attempt', (attemptNumber) => {
        connectionStatus = `Reconnecting (${attemptNumber})...`;
        addMessage('System', `Reconnection attempt: ${attemptNumber}`);
      });
      
      // Message handlers
      socket.on('server_message', (data) => {
        addMessage('Server', data.message);
      });
      
      // Random update handler
      socket.on('server_update', (data) => {
        randomUpdates = [...randomUpdates, data].slice(-5); // Keep last 5 updates
      });
    } catch (error) {
      connectionStatus = 'Error';
      addMessage('System', `Socket initialization error: ${error.message}`);
    }
  }
  
  function sendMessage() {
    if (inputMessage.trim() && connected) {
      socket.emit('client_message', { message: inputMessage });
      addMessage('You', inputMessage);
      inputMessage = '';
    }
  }
  
  function addMessage(sender, text) {
    const timestamp = new Date().toLocaleTimeString();
    messages = [...messages, { sender, text, timestamp }];
  }
  
  function reconnect() {
    if (socket) {
      socket.disconnect();
    }
    initializeSocket();
  }
</script>

<div class="container mx-auto p-4 max-w-3xl">
  <h1 class="text-2xl font-bold mb-4">SvelteKit - Flask WebSocket Test</h1>
  
  <!-- Connection status -->
  <div class="mb-4 p-2 rounded-md {connected ? 'bg-green-100' : 'bg-red-100'}">
    <p>Status: <span class="font-bold">{connectionStatus}</span></p>
    <button 
      class="mt-2 px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
      on:click={reconnect}
    >
      Reconnect
    </button>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <!-- Message area -->
    <div class="border rounded-md p-4">
      <h2 class="text-xl font-semibold mb-2">Messages</h2>
      <div class="h-64 overflow-y-auto border rounded-md p-2 mb-4 bg-gray-50">
        {#if messages.length === 0}
          <p class="text-gray-500 italic">No messages yet</p>
        {:else}
          {#each messages as message}
            <div class="mb-2 p-2 rounded-md {message.sender === 'You' ? 'bg-blue-100' : message.sender === 'Server' ? 'bg-green-100' : 'bg-gray-200'}">
              <div class="flex justify-between text-xs text-gray-500">
                <span class="font-bold">{message.sender}</span>
                <span>{message.timestamp}</span>
              </div>
              <p>{message.text}</p>
            </div>
          {/each}
        {/if}
      </div>
      
      <!-- Message input -->
      <div class="flex">
        <input
          type="text"
          bind:value={inputMessage}
          placeholder="Type a message..."
          class="flex-grow p-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-300"
          on:keydown={(e) => e.key === 'Enter' && sendMessage()}
          disabled={!connected}
        />
        <button
          class="px-4 py-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 disabled:bg-gray-300"
          on:click={sendMessage}
          disabled={!connected || !inputMessage.trim()}
        >
          Send
        </button>
      </div>
    </div>
    
    <!-- Server updates -->
    <div class="border rounded-md p-4">
      <h2 class="text-xl font-semibold mb-2">Server Updates</h2>
      <div class="h-64 overflow-y-auto border rounded-md p-2 bg-gray-50">
        {#if randomUpdates.length === 0}
          <p class="text-gray-500 italic">No updates received yet</p>
        {:else}
          {#each randomUpdates as update}
            <div class="mb-2 p-2 bg-yellow-100 rounded-md">
              <div class="text-xs text-gray-500">
                Timestamp: {new Date(update.timestamp * 1000).toLocaleTimeString()}
              </div>
              <p>Random value: <span class="font-bold">{update.value}</span></p>
            </div>
          {/each}
        {/if}
      </div>
    </div>
  </div>
</div>
