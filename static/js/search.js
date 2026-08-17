/**
 * TechVault Live Autocomplete Search Module
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInputs = document.querySelectorAll('input[name="search"]');

    searchInputs.forEach(input => {
        const form = input.closest('form');
        if (!form) return;

        // Create autocomplete dropdown container
        const dropdown = document.createElement('div');
        dropdown.className = 'absolute left-0 right-0 top-full mt-2 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden z-50 hidden custom-scrollbar max-h-96';
        form.parentNode.appendChild(dropdown);

        let debounceTimer;

        input.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();

            if (query.length < 2) {
                dropdown.innerHTML = '';
                dropdown.classList.add('hidden');
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`/api/search/live/?q=${encodeURIComponent(query)}`);
                    const data = await response.json();

                    if (response.ok && data.status === 'success') {
                        renderSearchResults(dropdown, data.results, query);
                    }
                } catch (err) {
                    console.error('Live Search Error:', err);
                }
            }, 250);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!form.parentNode.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });
    });
});

function renderSearchResults(container, results, query) {
    if (results.length === 0) {
        container.innerHTML = `
            <div class="p-4 text-xs text-slate-400 text-center">
                No tech products found matching "<strong class="text-white">${query}</strong>"
            </div>
        `;
        container.classList.remove('hidden');
        return;
    }

    container.innerHTML = results.map(p => `
        <a href="/product/${p.slug}/" class="flex items-center space-x-3 p-3 hover:bg-slate-800/80 border-b border-slate-800/50 transition-colors group">
            <img src="${p.image}" alt="${p.title}" class="w-10 h-10 object-contain bg-slate-950 p-1 rounded-lg border border-slate-800 flex-shrink-0">
            <div class="flex-1 min-w-0">
                <span class="text-[10px] text-cyan-400 font-bold uppercase block truncate">${p.brand} | ${p.category}</span>
                <h4 class="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors truncate">${p.title}</h4>
            </div>
            <span class="text-xs font-extrabold text-white flex-shrink-0">$${p.price.toFixed(2)}</span>
        </a>
    `).join('') + `
        <a href="/catalog/?search=${encodeURIComponent(query)}" class="block p-3 text-center text-xs font-bold text-cyan-400 bg-slate-950 hover:bg-slate-900 transition-colors">
            View All Matching Products →
        </a>
    `;

    container.classList.remove('hidden');
}
