/**
 * TechVault PC Builder Tool Engine
 * Manages component slot selections, wattage calculation, and bulk cart additions
 */

const pcBuildState = {
    cpu: null,
    motherboard: null,
    ram: null,
    storage: null,
    gpu: null,
    psu: null,
    case: null,
    cooler: null,
};

let currentSlotType = '';

/**
 * Opens Component Selector Modal for a given slot type (e.g. 'cpu', 'gpu')
 */
async function openComponentModal(componentType, componentName) {
    currentSlotType = componentType;
    const modal = document.getElementById('pc-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalList = document.getElementById('modal-product-list');

    if (modalTitle) modalTitle.textContent = `Select ${componentName}`;
    if (modalList) {
        modalList.innerHTML = `
            <div class="flex flex-col items-center justify-center py-12 text-slate-400">
                <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-cyan-400 mb-3"></div>
                <span>Loading compatible ${componentName}...</span>
            </div>
        `;
    }

    if (modal) modal.classList.remove('hidden');

    try {
        const response = await fetch(`/api/pc-builder/${componentType}/`);
        const data = await response.json();

        if (response.ok && data.status === 'success') {
            renderModalProducts(data.products);
        } else {
            modalList.innerHTML = `<div class="text-center text-rose-400 py-8">Failed to load components.</div>`;
        }
    } catch (err) {
        console.error('Modal Error:', err);
        if (modalList) modalList.innerHTML = `<div class="text-center text-rose-400 py-8">Network error.</div>`;
    }
}

function closeComponentModal() {
    const modal = document.getElementById('pc-modal');
    if (modal) modal.classList.add('hidden');
}

/**
 * Renders products inside component selector modal
 */
function renderModalProducts(products) {
    const modalList = document.getElementById('modal-product-list');
    if (!modalList) return;

    if (products.length === 0) {
        modalList.innerHTML = `
            <div class="text-center text-slate-500 py-8">
                No active components available for this slot. Please seed database or check stock status.
            </div>
        `;
        return;
    }

    modalList.innerHTML = products.map(p => `
        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex items-center justify-between gap-4 hover:border-cyan-500/40 transition-all">
            <div class="flex items-center space-x-4">
                <img src="${p.image}" alt="${p.title}" class="w-16 h-16 object-contain bg-slate-900 p-2 rounded-xl border border-slate-800">
                <div>
                    <span class="text-[10px] uppercase font-bold text-slate-400 block">${p.brand} | ${p.model_number}</span>
                    <h4 class="text-sm font-bold text-white mb-1">${p.title}</h4>
                    <span class="text-xs text-amber-400 font-semibold">${p.wattage > 0 ? `⚡ ${p.wattage}W Power` : 'Power: N/A'}</span>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <span class="text-base font-extrabold text-white">$${p.price.toFixed(2)}</span>
                <button onclick="selectComponent('${p.id}', '${p.variant_id}', '${escapeQuotes(p.title)}', ${p.price}, ${p.wattage}, '${p.image}')" 
                        class="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs px-4 py-2 rounded-xl transition-all">
                    Add
                </button>
            </div>
        </div>
    `).join('');
}

function escapeQuotes(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

/**
 * Selects a component for the active slot and updates UI totals
 */
function selectComponent(productId, variantId, title, price, wattage, image) {
    pcBuildState[currentSlotType] = {
        productId: productId,
        variantId: variantId,
        title: title,
        price: parseFloat(price),
        wattage: parseInt(wattage, 10) || 0,
        image: image
    };

    updateSlotUI(currentSlotType);
    calculateBuildTotals();
    closeComponentModal();
}

/**
 * Updates slot UI row displaying selected item
 */
function updateSlotUI(slotType) {
    const slotRow = document.getElementById(`slot-${slotType}`);
    if (!slotRow) return;

    const container = slotRow.querySelector('.selected-product-container');
    const comp = pcBuildState[slotType];

    if (comp) {
        container.innerHTML = `
            <div class="flex items-center space-x-3 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                <img src="${comp.image}" alt="${comp.title}" class="w-10 h-10 object-contain bg-slate-900 rounded-lg p-1">
                <div class="flex-1 text-left">
                    <h4 class="text-xs font-bold text-white truncate max-w-xs">${comp.title}</h4>
                    <div class="flex items-center space-x-2 text-[10px] text-slate-400">
                        <span class="text-cyan-400 font-semibold">$${comp.price.toFixed(2)}</span>
                        ${comp.wattage > 0 ? `<span>• ⚡ ${comp.wattage}W</span>` : ''}
                    </div>
                </div>
                <button onclick="removeComponent('${slotType}')" class="text-rose-400 hover:text-rose-300 text-xs px-2 font-bold">Remove</button>
            </div>
        `;
    } else {
        container.innerHTML = `<span class="text-xs text-slate-500 italic">No component selected.</span>`;
    }
}

function removeComponent(slotType) {
    pcBuildState[slotType] = null;
    updateSlotUI(slotType);
    calculateBuildTotals();
}

/**
 * Recalculates total wattage and total build price
 */
function calculateBuildTotals() {
    let totalWattage = 0;
    let totalPrice = 0;

    Object.values(pcBuildState).forEach(item => {
        if (item) {
            totalWattage += item.wattage;
            totalPrice += item.price;
        }
    });

    const wattageElem = document.getElementById('total-wattage');
    const priceElem = document.getElementById('total-price');

    if (wattageElem) wattageElem.textContent = `${totalWattage} W`;
    if (priceElem) priceElem.textContent = `$${totalPrice.toFixed(2)}`;
}

/**
 * Bulk adds all selected PC components to cart via Django CSRF Fetch POST
 */
async function addWholeBuildToCart() {
    const selectedItems = Object.values(pcBuildState).filter(item => item !== null);

    if (selectedItems.length === 0) {
        showToast('Please select at least one component to add to cart.', 'error');
        return;
    }

    const payload = selectedItems.map(item => ({
        variant_id: item.variantId,
        product_id: item.productId,
        quantity: 1
    }));

    const csrfToken = getCsrfToken();

    try {
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ items: payload })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            updateCartCounter(data.cart_summary.total_items);
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to add build to cart.', 'error');
        }
    } catch (err) {
        console.error('Bulk Add Error:', err);
        showToast('Network error while adding build to cart.', 'error');
    }
}
