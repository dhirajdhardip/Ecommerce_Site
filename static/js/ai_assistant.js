/**
 * TechOrbit AI Shopping Assistant
 * A floating chat widget that provides AI-powered product recommendations.
 * Powered by the /api/ai-recommendations/ backend endpoint.
 */

// ── State ─────────────────────────────────────────────────────────────────────
let aiAssistantOpen = false;
let aiTypingTimer = null;
const MAX_HISTORY = 20;
let msgHistory = [];

// ── Quick suggestion chips ────────────────────────────────────────────────────
const QUICK_SUGGESTIONS = [
  { icon: '🎮', text: 'Best gaming laptop under $1500' },
  { icon: '🎧', text: 'Top noise-canceling earbuds' },
  { icon: '⌚', text: 'Apple Watch for fitness' },
  { icon: '💻', text: 'Ultralight laptop for work' },
  { icon: '🖥️', text: 'Best 4K gaming monitor' },
  { icon: '🚀', text: 'Fastest NVMe SSD' },
];

// ── Greeting messages ─────────────────────────────────────────────────────────
const GREETINGS = [
  "Hey! 👋 I'm TechOrbit's AI Shopping Assistant. Tell me what you're looking for — budget, use case, brand — and I'll find the perfect tech for you!",
  "Hi there! 🤖 I can help you find the best tech products. What are you shopping for today?",
  "Welcome to TechOrbit! 🚀 I'm your AI shopping guide. Ask me anything — best gaming setup, laptop recommendations, or anything tech-related!",
];

// ── Inject widget HTML into DOM ───────────────────────────────────────────────
function injectAssistantWidget() {
  const greeting = GREETINGS[Math.floor(Math.random() * GREETINGS.length)];

  const html = `
    <!-- AI Assistant Toggle Button -->
    <button id="ai-assistant-toggle"
            onclick="toggleAiAssistant()"
            aria-label="Open AI Shopping Assistant"
            class="fixed bottom-24 left-5 z-50 w-14 h-14 rounded-2xl shadow-2xl
                   flex items-center justify-center transition-all duration-300
                   hover:scale-110 active:scale-95"
            style="background: linear-gradient(135deg, #ef4a23 0%, #c73d18 100%);
                   box-shadow: 0 8px 30px rgba(239,74,35,0.45);">
      <span id="ai-btn-icon" class="text-white transition-all duration-300">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
        </svg>
      </span>
      <!-- Pulsing dot indicator -->
      <span class="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full border-2 border-white
                   animate-pulse"></span>
    </button>

    <!-- AI Assistant Panel -->
    <div id="ai-assistant-panel"
         class="fixed bottom-44 left-5 z-50 w-80 sm:w-96 rounded-3xl shadow-2xl
                flex flex-col overflow-hidden transition-all duration-400 origin-bottom-left"
         style="max-height: 520px; display: none; opacity: 0; transform: scale(0.85);
                background: #0b1623; border: 1px solid rgba(255,255,255,0.08);">

      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3.5 flex-shrink-0"
           style="background: linear-gradient(135deg, #ef4a23 0%, #c73d18 100%);">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" class="text-white">
              <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 010 2h-1v1a2 2 0 01-2 2H5a2 2 0 01-2-2v-1H2a1 1 0 010-2h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2zM9 11a5 5 0 000 10h6a5 5 0 000-10H9zm1 3a1 1 0 110 2 1 1 0 010-2zm4 0a1 1 0 110 2 1 1 0 010-2z"/>
            </svg>
          </div>
          <div>
            <p class="text-white font-black text-sm leading-tight">AI Shopping Assistant</p>
            <p class="text-white/70 text-[10px] font-medium">TechOrbit Intelligence · Always Online</p>
          </div>
        </div>
        <button onclick="toggleAiAssistant()"
                class="w-7 h-7 rounded-lg bg-white/20 hover:bg-white/30 text-white flex items-center
                       justify-center transition-all backdrop-blur-sm text-sm font-black">
          ✕
        </button>
      </div>

      <!-- Messages Area -->
      <div id="ai-chat-messages"
           class="flex-1 overflow-y-auto px-4 py-4 space-y-4"
           style="max-height: 300px; scrollbar-width: thin; scrollbar-color: #ef4a23 #0b1623;">

        <!-- Initial greeting message -->
        <div class="flex items-start gap-2.5 ai-msg-bot">
          <div class="w-7 h-7 rounded-lg bg-[#ef4a23] flex-shrink-0 flex items-center justify-center text-white text-[10px] font-black mt-0.5">AI</div>
          <div class="bg-white/8 border border-white/10 rounded-2xl rounded-tl-sm px-3.5 py-3 max-w-[85%]">
            <p class="text-slate-200 text-xs leading-relaxed">${greeting}</p>
          </div>
        </div>

        <!-- Quick suggestion chips -->
        <div id="ai-quick-chips" class="flex flex-wrap gap-2 pl-9">
          ${QUICK_SUGGESTIONS.map(s => `
            <button onclick="aiAssistantAsk('${s.text.replace(/'/g, "\\'")}')"
                    class="bg-white/5 hover:bg-[#ef4a23]/20 border border-white/10 hover:border-[#ef4a23]/50
                           text-slate-300 hover:text-white text-[10px] font-semibold px-2.5 py-1.5
                           rounded-xl transition-all duration-200 whitespace-nowrap">
              ${s.icon} ${s.text}
            </button>
          `).join('')}
        </div>
      </div>

      <!-- Input Area -->
      <div class="px-4 py-3 flex-shrink-0 border-t border-white/8">
        <div class="flex items-center gap-2 bg-white/6 border border-white/10 rounded-2xl px-3 py-2
                    focus-within:border-[#ef4a23]/60 transition-all">
          <input type="text"
                 id="ai-assistant-input"
                 placeholder="Ask me anything about tech…"
                 class="flex-1 bg-transparent text-white text-xs placeholder-slate-500
                        focus:outline-none font-medium"
                 onkeydown="if(event.key==='Enter') aiAssistantSubmit()">
          <button onclick="aiAssistantSubmit()"
                  id="ai-send-btn"
                  class="w-7 h-7 rounded-xl bg-[#ef4a23] hover:bg-[#d93b15] text-white flex items-center
                         justify-center transition-all active:scale-90 flex-shrink-0">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2 21l21-9L2 3v7l15 2-15 2z"/>
            </svg>
          </button>
        </div>
        <p class="text-center text-[9px] text-slate-600 mt-2 font-medium">
          Powered by TechOrbit Intelligence Engine
        </p>
      </div>
    </div>
  `;

  const wrapper = document.createElement('div');
  wrapper.innerHTML = html;
  document.body.appendChild(wrapper);
}

// ── Toggle panel open/close ───────────────────────────────────────────────────
function toggleAiAssistant() {
  const panel = document.getElementById('ai-assistant-panel');
  const icon  = document.getElementById('ai-btn-icon');

  aiAssistantOpen = !aiAssistantOpen;

  if (aiAssistantOpen) {
    panel.style.display  = 'flex';
    panel.style.flexDirection = 'column';
    requestAnimationFrame(() => {
      panel.style.transition = 'opacity 0.25s ease, transform 0.25s cubic-bezier(0.34,1.56,0.64,1)';
      panel.style.opacity   = '1';
      panel.style.transform = 'scale(1)';
    });
    icon.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2.5" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>`;
    // Focus input
    setTimeout(() => {
      const inp = document.getElementById('ai-assistant-input');
      if (inp) inp.focus();
    }, 250);
  } else {
    panel.style.opacity   = '0';
    panel.style.transform = 'scale(0.85)';
    setTimeout(() => { panel.style.display = 'none'; }, 250);
    icon.innerHTML = `<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>`;
  }
}

// ── Public: ask from quick chip ───────────────────────────────────────────────
function aiAssistantAsk(query) {
  const input = document.getElementById('ai-assistant-input');
  if (input) input.value = query;
  // Hide quick chips after first interaction
  const chips = document.getElementById('ai-quick-chips');
  if (chips) chips.style.display = 'none';
  aiAssistantSubmit();
}

// ── Submit handler ────────────────────────────────────────────────────────────
function aiAssistantSubmit() {
  const input = document.getElementById('ai-assistant-input');
  const query = (input?.value || '').trim();
  if (!query) return;

  input.value = '';

  // Hide quick chips
  const chips = document.getElementById('ai-quick-chips');
  if (chips) chips.style.display = 'none';

  appendUserMessage(query);
  showTypingIndicator();
  fetchAssistantResults(query);
}

// ── Append user message bubble ────────────────────────────────────────────────
function appendUserMessage(text) {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return;

  const div = document.createElement('div');
  div.className = 'flex items-end justify-end gap-2 ai-msg-user';
  div.innerHTML = `
    <div class="bg-[#ef4a23] rounded-2xl rounded-br-sm px-3.5 py-2.5 max-w-[80%]">
      <p class="text-white text-xs font-semibold leading-relaxed">${escapeHtml(text)}</p>
    </div>
    <div class="w-7 h-7 rounded-lg bg-slate-700 flex-shrink-0 flex items-center justify-center text-slate-300 text-[10px] font-black mb-0.5">
      You
    </div>
  `;
  container.appendChild(div);
  scrollToBottom(container);
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function showTypingIndicator() {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return;

  removeTypingIndicator();

  const div = document.createElement('div');
  div.id = 'ai-typing-indicator';
  div.className = 'flex items-start gap-2.5';
  div.innerHTML = `
    <div class="w-7 h-7 rounded-lg bg-[#ef4a23] flex-shrink-0 flex items-center justify-center text-white text-[10px] font-black mt-0.5">AI</div>
    <div class="bg-white/8 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
      <div class="flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 bg-[#ef4a23] rounded-full animate-bounce" style="animation-delay:0s"></span>
        <span class="w-1.5 h-1.5 bg-[#ef4a23] rounded-full animate-bounce" style="animation-delay:0.15s"></span>
        <span class="w-1.5 h-1.5 bg-[#ef4a23] rounded-full animate-bounce" style="animation-delay:0.3s"></span>
      </div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom(container);
}

function removeTypingIndicator() {
  const el = document.getElementById('ai-typing-indicator');
  if (el) el.remove();
}

// ── Fetch recommendations from API ───────────────────────────────────────────
async function fetchAssistantResults(query) {
  try {
    const res  = await fetch(`/api/ai-recommendations/?q=${encodeURIComponent(query)}&limit=4`);
    const data = await res.json();
    removeTypingIndicator();

    if (data.status !== 'success' || !data.results?.length) {
      appendBotMessage("😔 I couldn't find matching products for that. Try rephrasing — like \"gaming laptop under $1200\" or \"best earbuds\".");
      return;
    }

    // Smart conversational response
    const count = data.results.length;
    const topItem = data.results[0];
    const intros = [
      `Found ${count} great matches! 🎯 Top pick: <strong class="text-[#ef4a23]">${escapeHtml(topItem.title)}</strong>`,
      `Here are ${count} AI-curated picks for you! ✨ Check out the <strong class="text-[#ef4a23]">${escapeHtml(topItem.title)}</strong>`,
      `I found ${count} products that match! 🚀 The <strong class="text-[#ef4a23]">${escapeHtml(topItem.title)}</strong> looks like your best bet.`,
    ];
    const intro = intros[Math.floor(Math.random() * intros.length)];
    appendBotMessage(intro, false);

    // Render product cards
    appendProductCards(data.results);

    appendBotMessage(`Want more details? Click any product to open it. Or refine your search! 💬`, false);

  } catch (err) {
    removeTypingIndicator();
    appendBotMessage("⚡ Connection hiccup! Please try again in a moment.");
  }
}

// ── Append bot text message ───────────────────────────────────────────────────
function appendBotMessage(html, safe = true) {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return;

  const div = document.createElement('div');
  div.className = 'flex items-start gap-2.5 ai-msg-bot';
  div.innerHTML = `
    <div class="w-7 h-7 rounded-lg bg-[#ef4a23] flex-shrink-0 flex items-center justify-center text-white text-[10px] font-black mt-0.5">AI</div>
    <div class="bg-white/8 border border-white/10 rounded-2xl rounded-tl-sm px-3.5 py-3 max-w-[85%]">
      <p class="text-slate-200 text-xs leading-relaxed">${safe ? escapeHtml(html) : html}</p>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom(container);
}

// ── Render inline product cards ───────────────────────────────────────────────
function appendProductCards(products) {
  const container = document.getElementById('ai-chat-messages');
  if (!container) return;

  const wrapper = document.createElement('div');
  wrapper.className = 'pl-9 space-y-2';

  products.forEach(p => {
    const card = document.createElement('a');
    card.href = `/product/${p.slug}/`;
    card.className = 'flex items-center gap-3 bg-white/5 hover:bg-white/10 border border-white/8 ' +
                     'hover:border-[#ef4a23]/50 rounded-2xl p-2.5 transition-all duration-200 group block';
    card.innerHTML = `
      <!-- Product Image -->
      <div class="w-14 h-14 bg-white rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden border border-slate-200 shadow-sm">
        <img src="${p.image}" alt="${escapeHtml(p.title)}"
             class="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform duration-200">
      </div>
      <!-- Info -->
      <div class="flex-1 min-w-0">
        <p class="text-white text-[11px] font-bold leading-snug line-clamp-2 group-hover:text-[#ef4a23] transition-colors">
          ${escapeHtml(p.title)}
        </p>
        <div class="flex items-center justify-between mt-1">
          <span class="text-[#ef4a23] text-xs font-black">$${p.price.toFixed(2)}</span>
          <span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full border"
                style="${p.match_percentage >= 90
                  ? 'color:#22c55e;border-color:#22c55e33;background:#22c55e11'
                  : 'color:#f59e0b;border-color:#f59e0b33;background:#f59e0b11'}">
            ${p.match_percentage}% match
          </span>
        </div>
        <p class="text-slate-500 text-[9px] leading-snug mt-0.5 line-clamp-1 italic">✦ ${escapeHtml(p.ai_reason)}</p>
      </div>
      <!-- Arrow -->
      <div class="text-slate-600 group-hover:text-[#ef4a23] transition-colors flex-shrink-0">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </div>
    `;
    wrapper.appendChild(card);
  });

  container.appendChild(wrapper);
  scrollToBottom(container);
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function scrollToBottom(container) {
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  injectAssistantWidget();

  // Auto-open hint after 8 seconds on first visit
  const hasSeenHint = sessionStorage.getItem('aiAssistantHintSeen');
  if (!hasSeenHint) {
    setTimeout(() => {
      const btn = document.getElementById('ai-assistant-toggle');
      if (btn) {
        btn.style.animation = 'none';
        btn.classList.add('animate-bounce');
        setTimeout(() => btn.classList.remove('animate-bounce'), 2000);
      }
      sessionStorage.setItem('aiAssistantHintSeen', '1');
    }, 8000);
  }
});
