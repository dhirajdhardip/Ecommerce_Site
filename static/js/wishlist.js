/**
 * TechVault Wishlist & Comparison AJAX Module
 */

/**
 * Toggles product wishlist state via AJAX
 */
async function toggleWishlist(productId, buttonElem = null) {
    const csrfToken = getCsrfToken();

    try {
        const response = await fetch('/wishlist/api/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ product_id: productId })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            showToast(data.message, data.added ? 'success' : 'info');
            if (buttonElem) {
                if (data.added) {
                    buttonElem.classList.add('text-rose-500');
                } else {
                    buttonElem.classList.remove('text-rose-500');
                }
            }
        } else {
            showToast(data.message || 'Wishlist update failed.', 'error');
        }
    } catch (err) {
        console.error('Wishlist Error:', err);
        showToast('Network error while updating Wishlist.', 'error');
    }
}

/**
 * Toggles product compare list state via AJAX
 */
async function toggleCompare(productId) {
    const csrfToken = getCsrfToken();

    try {
        const response = await fetch('/compare/api/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ product_id: productId })
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            showToast(data.message, 'success');
            const badge = document.getElementById('compare-count-badge');
            if (badge) {
                badge.textContent = data.compare_count;
            }
        } else {
            showToast(data.message || 'Could not add to comparison.', 'error');
        }
    } catch (err) {
        console.error('Compare Error:', err);
        showToast('Network error while updating Comparison.', 'error');
    }
}
