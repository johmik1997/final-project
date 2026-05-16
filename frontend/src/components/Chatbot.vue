<script setup>
import { ref, nextTick } from 'vue';
import { sendOpenAIChat } from '@/service/OpenAIService';

const isOpen = ref(false);
const inputText = ref('');
const messages = ref([
  { id: 1, text: 'Hello! How can I help you today?', sender: 'bot' }
]);
const messagesContainer = ref(null);
const isTyping = ref(false);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    scrollToBottom();
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const buildHistory = () => {
  return messages.value.map((message) => ({
    role: message.sender === 'user' ? 'user' : 'assistant',
    content: message.text,
  }));
};

const sendMessage = async () => {
  if (!inputText.value.trim()) return;

  const userText = inputText.value.trim();

  messages.value.push({
    id: Date.now(),
    text: userText,
    sender: 'user',
  });

  inputText.value = '';
  scrollToBottom();

  isTyping.value = true;

  try {
    const botResponse = await sendOpenAIChat(userText, buildHistory());
    messages.value.push({
      id: Date.now() + 1,
      text: botResponse,
      sender: 'bot',
    });
  } catch (err) {
    messages.value.push({
      id: Date.now() + 1,
      text:
        err?.message ||
        'Sorry, I could not connect to the AI service. Please try again later.',
      sender: 'bot',
    });
  } finally {
    isTyping.value = false;
    scrollToBottom();
  }
};
</script>

<template>
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none">
    
    <!-- Chat Window -->
    <Transition name="chat-window">
      <div 
        v-if="isOpen" 
        class="w-[350px] max-w-[calc(100vw-3rem)] bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden mb-4 flex flex-col pointer-events-auto"
        style="height: 500px; max-height: calc(100vh - 8rem);"
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-amber-500 to-red-500 p-4 flex items-center justify-between text-white shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm shadow-inner">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-lg leading-tight">Virtual Assistant</h3>
              <p class="text-xs text-white/80 font-medium">Online</p>
            </div>
          </div>
          <button 
            @click="toggleChat" 
            class="text-white/80 hover:text-white hover:bg-white/10 p-2 rounded-full transition-colors"
            aria-label="Close chat"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <!-- Messages Area -->
        <div 
          ref="messagesContainer"
          class="flex-1 p-4 overflow-y-auto bg-slate-50 dark:bg-slate-900 flex flex-col gap-3"
        >
          <div 
            v-for="msg in messages" 
            :key="msg.id"
            class="flex w-full"
            :class="msg.sender === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div 
              class="max-w-[80%] rounded-2xl px-4 py-2.5 shadow-sm text-sm"
              :class="[
                msg.sender === 'user' 
                  ? 'bg-amber-500 text-white rounded-tr-sm' 
                  : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-100 dark:border-slate-700 rounded-tl-sm'
              ]"
            >
              {{ msg.text }}
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="flex w-full justify-start mt-2">
            <div class="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="p-3 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 shrink-0">
          <form @submit.prevent="sendMessage" class="flex gap-2">
            <input 
              v-model="inputText"
              type="text" 
              placeholder="Type your message..." 
              class="flex-1 bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200 rounded-full px-4 py-2.5 text-sm outline-none border border-transparent focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all placeholder-slate-400 dark:placeholder-slate-500"
            />
            <button 
              type="submit" 
              :disabled="!inputText.trim() || isTyping"
              class="w-10 h-10 rounded-full bg-amber-500 text-white flex items-center justify-center shrink-0 hover:bg-amber-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed dark:focus:ring-offset-slate-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transform rotate-90" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </Transition>

    <!-- Floating Action Button -->
    <button 
      @click="toggleChat"
      class="w-14 h-14 bg-gradient-to-br from-amber-500 to-red-500 rounded-full shadow-lg shadow-amber-500/30 flex items-center justify-center text-white hover:scale-105 active:scale-95 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 pointer-events-auto group dark:focus:ring-offset-slate-900"
      aria-label="Toggle chat"
    >
      <Transition name="fab-icon" mode="out-in">
        <svg v-if="!isOpen" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </Transition>
    </button>
  </div>
</template>

<style scoped>
/* Chat Window Transitions */
.chat-window-enter-active,
.chat-window-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom right;
}

.chat-window-enter-from,
.chat-window-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

.chat-window-enter-to,
.chat-window-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* FAB Icon Transitions */
.fab-icon-enter-active,
.fab-icon-leave-active {
  transition: all 0.2s ease;
}

.fab-icon-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

.fab-icon-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}

/* Custom Scrollbar for messages */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}
</style>
