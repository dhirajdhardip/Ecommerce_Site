/**
 * TechVault E-Commerce - Async Cart Operations Module
 * Demonstrates robust CSRF token extraction & Fetch API headers for Django AJAX POST
 */

/**
 * Extracts Django CSRF Token from Cookies or DOM Meta Tag
 * @returns {string} CSRF Token string
 */
function getCsrfToken() {
    // 1. Try extracting from document.cookie
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    
    // 2. Fallback to DOM meta tag if cookie extraction fails
    if (!cookieValue) {
        const metaCsrf = document.querySelector('meta[name="csrf-token"]');
        if (metaCsrf) {
            cookieValue = metaCsrf.getAttribute('content');
        }
    }

    // 3. Fallback to hidden CSRF input field in forms
    if (!cookieValue) {
        const inputCsrf = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (inputCsrf) {
            cookieValue = inputCsrf.value;
        }
    }

    return cookieValue || '';
}

/**
 * Asynchronously adds a Product Variant to Cart via Django AJAX Endpoint
 * @param {number|string} variantId - Unique ID of the ProductVariant
 * @param {number} quantity - Desired quantity (default: 1)
 * @param {number|string|null} productId - Fallback Product ID
 * @param {HTMLElement|null} buttonElem - UI Button for loading indicator
 */
async function addToCart(variantId, quantity = 1, productId = null, buttonElem = null) {
    const csrfToken = getCsrfToken();

    if (!csrfToken) {
        console.error('CSRF Token missing! Cannot perform secure AJAX POST request.');
        showToast('Security token missing. Please refresh the page.', 'error');
        return;
    }

    // Optional UI loading state
    let originalButtonText = '';
    if (buttonElem) {
        buttonElem.disabled = true;
        originalButtonText = buttonElem.innerHTML;
        buttonElem.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg> Adding...
        `;
    }

    try {
        // Core Fetch API request appending X-CSRFToken header
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                variant_id: variantId,
                product_id: productId,
                quantity: parseInt(quantity, 10)
            })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            // Update UI Cart Badge Counters dynamically
            updateCartCounter(data.cart_summary.total_items);
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to add item to cart.', 'error');
        }

    } catch (error) {
        console.error('Add to Cart Error:', error);
        showToast('Network error occurred. Please check your connection.', 'error');
    } finally {
        if (buttonElem) {
            buttonElem.disabled = false;
            buttonElem.innerHTML = originalButtonText;
        }
    }
}

/**
 * Updates navbar cart item counter badges
 */
function updateCartCounter(totalItems) {
    const badges = document.querySelectorAll('.cart-count-badge');
    badges.forEach(badge => {
        badge.textContent = totalItems;
        badge.classList.remove('hidden');
        badge.classList.add('scale-125');
        setTimeout(() => badge.classList.remove('scale-125'), 300);
    });
}

/**
 * Modern Toast Notification UI Helper
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    const isSuccess = type === 'success';
    
    toast.className = `flex items-center w-full max-w-xs p-4 text-white rounded-lg shadow-xl transition-all duration-300 transform translate-y-2 ${
        isSuccess ? 'bg-emerald-600' : 'bg-rose-600'
    }`;
    
    toast.innerHTML = `
        <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg bg-white/20">
            ${isSuccess ? '✓' : '✕'}
        </div>
        <div class="ml-3 text-sm font-medium">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-[-10px]');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed bottom-5 right-5 z-50 flex flex-col space-y-3';
    document.body.appendChild(container);
    return container;
}
