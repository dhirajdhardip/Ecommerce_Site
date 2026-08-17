/**
 * TechOrbit E-Commerce - Dynamic Filter & Pagination Module
 * Star Tech White Background Image Showcase Style
 */

document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    if (!filterForm) return;

    // Parse URL parameters from window.location.search to initialize checkboxes
    const urlParams = new URLSearchParams(window.location.search);
    
    // Auto-check category checkboxes if present in URL
    const catParams = urlParams.getAll('categories');
    if (catParams.length > 0) {
        document.querySelectorAll('input[name="categories"]').forEach(cb => {
            if (catParams.includes(cb.value)) {
                cb.checked = true;
            }
        });
    }

    // Auto-check brand checkboxes if present in URL
    const brandParams = urlParams.getAll('brands');
    if (brandParams.length > 0) {
        document.querySelectorAll('input[name="brands"]').forEach(cb => {
            if (brandParams.includes(cb.value)) {
                cb.checked = true;
            }
        });
    }

    // Attach event listeners to filter inputs
    const inputs = filterForm.querySelectorAll('input[type="checkbox"], input[type="radio"], select');
    inputs.forEach(input => {
        input.addEventListener('change', () => applyFilters(1));
    });

    const priceMinInput = document.getElementById('price-min');
    const priceMaxInput = document.getElementById('price-max');
    if (priceMinInput && priceMaxInput) {
        priceMinInput.addEventListener('change', () => applyFilters(1));
        priceMaxInput.addEventListener('change', () => applyFilters(1));
    }

    // Initial load
    applyFilters(1);
});

/**
 * Asynchronously gathers filter inputs and fetches dynamic product JSON array
 */
async function applyFilters(page = 1) {
    const productGrid = document.getElementById('product-grid');
    const productCount = document.getElementById('product-count');

    if (productGrid) {
        productGrid.innerHTML = `
            <div class="col-span-full flex flex-col items-center justify-center py-16">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-400"></div>
                <p class="mt-4 text-slate-400 font-medium text-xs">Filtering TechOrbit inventory...</p>
            </div>
        `;
    }

    const params = new URLSearchParams();
    params.append('page', page);

    // Read initial URL search query parameter if present
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search') || urlParams.get('q');
    if (searchQuery) {
        params.append('search', searchQuery);
    }

    const sortSelect = document.getElementById('sort-by');
    if (sortSelect) {
        params.append('sort', sortSelect.value);
    }

    document.querySelectorAll('input[name="brands"]:checked').forEach(cb => {
        params.append('brands', cb.value);
    });

    document.querySelectorAll('input[name="categories"]:checked').forEach(cb => {
        params.append('categories', cb.value);
    });

    document.querySelectorAll('input[name="stock"]:checked').forEach(cb => {
        params.append('stock', cb.value);
    });

    const minPrice = document.getElementById('price-min')?.value;
    const maxPrice = document.getElementById('price-max')?.value;
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);

    document.querySelectorAll('input[name^="spec_"]:checked').forEach(cb => {
        params.append(cb.name, cb.value);
    });

    try {
        const response = await fetch(`/api/products/filter/?${params.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            if (productCount) {
                productCount.textContent = `${data.total_count} Products Found`;
            }
            renderProductGrid(data.products);
            renderPagination(data, page);
        } else {
            productGrid.innerHTML = `<div class="col-span-full text-center text-rose-400 py-10">Error loading products.</div>`;
        }

    } catch (err) {
        console.error('Filter Error:', err);
        if (productGrid) {
            productGrid.innerHTML = `<div class="col-span-full text-center text-slate-400 py-10">Connection error. Please try again.</div>`;
        }
    }
}

/**
 * Dynamically renders product cards matching Star Tech's exact White Background Image layout
 */
function renderProductGrid(products) {
    const grid = document.getElementById('product-grid');
    if (!grid) return;

    if (products.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full bg-[#0f172a] border border-slate-800 rounded-3xl p-12 text-center">
                <div class="text-5xl mb-4">🔍</div>
                <h3 class="text-xl font-bold text-white mb-2">No Matching Products Found</h3>
                <p class="text-slate-400 text-xs max-w-md mx-auto">Try clearing some of your filter selections or adjusting the price bounds.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = products.map(p => {
        const defaultVariant = p.variants.find(v => v.is_default) || p.variants[0];
        const variantId = defaultVariant ? defaultVariant.id : '';

        const saveAmount = p.save_amount ? p.save_amount.toFixed(2) : (p.discount_price ? (p.base_price - p.discount_price).toFixed(2) : null);
        const discountBadge = saveAmount ? `
            <span class="absolute top-3 left-0 bg-purple-700 text-white font-bold text-[10px] px-2.5 py-1 rounded-r-lg shadow-md z-10">
                Save: $${saveAmount} (-${p.discount_percentage}%)
            </span>
        ` : `
            <span class="absolute top-3 left-0 bg-indigo-800 text-white font-bold text-[10px] px-2.5 py-1 rounded-r-lg shadow-md z-10">
                Earn Point: 200
            </span>
        `;

        const specBadges = p.specifications.slice(0, 2).map(s => `
            <span class="inline-block bg-slate-100 text-slate-700 text-[10px] px-2 py-0.5 rounded font-mono border border-slate-200">
                ${s.key}: ${s.value}
            </span>
        `).join('');

        return `
            <div class="group bg-white border border-slate-200 rounded-3xl p-4 hover:border-emerald-500 hover:shadow-xl transition-all duration-300 flex flex-col justify-between relative overflow-hidden">
                <div>
                    <!-- Top Star Tech Save / Reward Badge -->
                    ${discountBadge}

                    <!-- Pure White Background Image Showcase Box -->
                    <a href="/product/${p.slug}/" class="product-img-box block relative w-full h-52 bg-slate-50 rounded-2xl p-4 flex items-center justify-center border border-slate-100 shadow-sm mb-4">
                        <img src="${p.primary_image}" alt="${p.title}" class="max-h-full object-contain">
                    </a>

                    <!-- Title -->
                    <h3 class="text-xs font-bold text-slate-900 group-hover:text-emerald-600 transition-colors line-clamp-2 mb-2 leading-snug">
                        <a href="/product/${p.slug}/">${p.title}</a>
                    </h3>

                    <!-- Specs Tags -->
                    <div class="flex flex-wrap gap-1 mb-4">
                        ${specBadges}
                    </div>
                </div>

                <!-- Footer Star Tech Style Red Pricing & Cart Button -->
                <div class="pt-3 border-t border-slate-100 flex items-center justify-between mt-2">
                    <div>
                        <div class="flex items-baseline space-x-2">
                            <span class="text-base font-extrabold text-rose-500">$${p.effective_price.toFixed(2)}</span>
                            ${p.discount_price ? `<span class="text-[11px] text-slate-500 line-through">$${p.base_price}</span>` : ''}
                        </div>
                    </div>
                    
                    <button onclick="addToCart('${variantId}', 1, '${p.id}', this)" 
                            class="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-black text-xs px-3.5 py-2 rounded-xl shadow-lg shadow-emerald-500/20 active:scale-95 transition-all flex items-center">
                        Add To Cart
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Renders pagination controls
 */
function renderPagination(data, currentPage) {
    const container = document.getElementById('pagination-container');
    if (!container || data.total_pages <= 1) {
        if (container) container.innerHTML = '';
        return;
    }

    let buttons = '';
    for (let i = 1; i <= data.total_pages; i++) {
        buttons += `
            <button onclick="applyFilters(${i})" 
                    class="px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                        i === currentPage
                        ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/30'
                        : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'
                    }">
                ${i}
            </button>
        `;
    }

    container.innerHTML = `
        <div class="flex items-center justify-center space-x-2 my-8">
            ${buttons}
        </div>
    `;
}
