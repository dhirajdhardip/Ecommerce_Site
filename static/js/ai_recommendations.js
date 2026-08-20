/**
 * TechOrbit AI Tech Advisor — Frontend Controller
 * Powers the AI Product Recommendation widget on home page and product detail.
 */

// ── Quick-prompt chips ───────────────────────────────────────────────────────
const AI_PROMPTS = [
    { icon: '⚡', label: 'Best Gaming Setup under $2000', q: 'best gaming setup under $2000' },
    { icon: '🎧', label: 'Top Noise-Canceling Earbuds',  q: 'noise canceling earbuds airpods' },
    { icon: '💻', label: 'Ultralight Laptop for Work',   q: 'ultralight portable laptop' },
    { icon: '⌚', label: 'Apple Watch for Fitness',      q: 'apple watch smartwatch fitness gps' },
    { icon: '🖥️', label: 'Best 4K OLED Monitor',         q: 'best 4k oled monitor gaming' },
    { icon: '🚀', label: 'Fastest SSD Storage',          q: 'fastest nvme ssd storage' },
];

// ── State ─────────────────────────────────────────────────────────────────────
let aiDebounceTimer = null;

// ── Boot: render prompt chips ─────────────────────────────────────────────────
function initAiAdvisor() {
    const chipsContainer = document.getElementById('ai-prompt-chips');
    if (!chipsContainer) return;

    chipsContainer.innerHTML = AI_PROMPTS.map(p => `
        <button onclick="aiAskPrompt('${p.q}')"
                class="ai-chip flex items-center gap-2 bg-white/5 hover:bg-white/15 border border-white/15
                       hover:border-[#ef4a23] text-slate-200 hover:text-white text-xs font-semibold
                       px-4 py-2 rounded-full transition-all duration-200 backdrop-blur-sm whitespace-nowrap">
            <span>${p.icon}</span>
            <span>${p.label}</span>
        </button>
    `).join('');

    // Restore last query if any
    const input = document.getElementById('ai-advisor-input');
    if (input) {
        input.addEventListener('input', () => {
            clearTimeout(aiDebounceTimer);
            const q = input.value.trim();
            if (q.length > 3) {
                aiDebounceTimer = setTimeout(() => fetchAiRecommendations(q), 500);
            }
        });
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                clearTimeout(aiDebounceTimer);
                const q = input.value.trim();
                if (q) fetchAiRecommendations(q);
            }
        });
    }
}

function aiAskPrompt(query) {
    const input = document.getElementById('ai-advisor-input');
    if (input) input.value = query;
    fetchAiRecommendations(query);
}

// ── Fetch & render ─────────────────────────────────────────────────────────────
async function fetchAiRecommendations(query, containerId = 'ai-results-container', productId = null) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Show loader
    container.innerHTML = `
        <div class="col-span-full flex flex-col items-center justify-center py-16 text-center">
            <div class="w-12 h-12 rounded-full border-4 border-[#ef4a23]/20 border-t-[#ef4a23] animate-spin mb-4"></div>
            <p class="text-sm text-slate-400 font-medium">AI is analysing your request…</p>
        </div>
    `;

    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (productId) params.set('product_id', productId);

    try {
        const res = await fetch('/api/ai-recommendations/?' + params.toString());
        const data = await res.json();

        if (data.status !== 'success' || !data.results.length) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <p class="text-sm text-slate-400">No AI recommendations found. Try a different query.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.results.map(p => renderAiCard(p)).join('');

        // Show query summary
        const summary = document.getElementById('ai-results-summary');
        if (summary && query) {
            summary.textContent = `AI found ${data.results.length} products matching "${query}"`;
            summary.classList.remove('hidden');
        }

    } catch (err) {
        container.innerHTML = `
            <div class="col-span-full text-center py-12">
                <p class="text-sm text-red-400">Failed to load AI recommendations.</p>
            </div>
        `;
    }
}

// ── Card Renderer ─────────────────────────────────────────────────────────────
function renderAiCard(p) {
    const badgeColor = p.match_percentage >= 90 ? '#22c55e' :
                       p.match_percentage >= 80 ? '#ef4a23' : '#f59e0b';
    const discountBadge = p.has_discount ? `
        <span class="absolute top-2 left-2 bg-[#ef4a23] text-white text-[10px] font-black px-2 py-0.5 rounded-lg">
            DEAL
        </span>` : '';

    return `
        <div class="group bg-white border border-slate-200 rounded-2xl p-4 hover:border-[#ef4a23]
                    hover:shadow-xl transition-all duration-300 flex flex-col relative overflow-hidden">
            ${discountBadge}

            <!-- AI Match Badge -->
            <div class="absolute top-2 right-2 flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-black text-white"
                 style="background:${badgeColor}">
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
                </svg>
                ${p.match_percentage}% AI
            </div>

            <!-- Image -->
            <a href="/product/${p.slug}/"
               class="block h-40 bg-white rounded-xl flex items-center justify-center p-3 mb-3 border border-slate-100">
                <img src="${p.image}" alt="${p.title}" class="max-h-full object-contain">
            </a>

            <!-- Meta -->
            <span class="text-[10px] font-bold uppercase tracking-wider text-[#ef4a23] mb-1">${p.brand} · ${p.category}</span>
            <h3 class="text-xs font-bold text-slate-900 group-hover:text-[#ef4a23] line-clamp-2 mb-1 leading-snug">
                <a href="/product/${p.slug}/">${p.title}</a>
            </h3>

            <!-- AI Reason -->
            <p class="text-[10px] text-slate-500 italic mb-3 line-clamp-2">✦ ${p.ai_reason}</p>

            <!-- Price + Cart -->
            <div class="mt-auto flex items-center justify-between pt-2 border-t border-slate-100">
                <div>
                    <span class="text-sm font-black text-[#ef4a23]">$${p.price.toFixed(2)}</span>
                    ${p.has_discount ? `<span class="text-[10px] text-slate-400 line-through ml-1">$${p.base_price.toFixed(2)}</span>` : ''}
                </div>
                <button onclick="addToCart('', 1, '${p.id}', this)"
                        class="bg-[#ef4a23] hover:bg-[#d93b15] text-white text-[10px] font-black px-3 py-1.5
                               rounded-xl active:scale-95 transition-all flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                              d="M12 4v16m8-8H4"/>
                    </svg>
                    Add
                </button>
            </div>
        </div>
    `;
}

// ── Complementary loader (for product detail page) ───────────────────────────
function loadComplementaryRecommendations(productId) {
    fetchAiRecommendations(null, 'ai-complementary-container', productId);
}

// ── Auto-init on DOM ready ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initAiAdvisor();

    // Auto-load default featured recommendations on home page
    const defaultContainer = document.getElementById('ai-results-container');
    if (defaultContainer) {
        fetchAiRecommendations(null);
    }

    // Auto-load complementary recs on product detail page
    const compContainer = document.getElementById('ai-complementary-container');
    if (compContainer) {
        const pid = compContainer.dataset.productId;
        if (pid) loadComplementaryRecommendations(pid);
    }
});
