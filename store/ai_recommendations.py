import re
from store.models import Product


def get_ai_product_recommendations(query=None, target_product_id=None, limit=6):
    """
    AI Recommendation Algorithm that parses user search intent (use case, budget,
    category, brand) or target product context, and computes weighted match scores
    with human-readable AI explanation strings.
    """
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related('brand', 'category')
        .prefetch_related('images', 'specifications__key', 'variants')
    )

    recommendations = []
    query_str = (query or '').strip().lower()

    # ── Helper ────────────────────────────────────────────────────────────────
    def _image_url(p):
        img = p.images.filter(is_primary=True).first() or p.images.first()
        return img.image.url if img else '/static/images/placeholder.png'

    def _pack(p, score, reasons):
        pct = min(99, max(68, int(score)))
        reason_str = " • ".join(list(dict.fromkeys(reasons))) if reasons else (
            f"Recommended based on {p.category.name} performance metrics."
        )
        return {
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'brand': p.brand.name,
            'category': p.category.name,
            'price': float(p.effective_price),
            'base_price': float(p.base_price),
            'has_discount': p.discount_price is not None,
            'image': _image_url(p),
            'match_percentage': pct,
            'ai_reason': reason_str,
            'stock_status': p.get_stock_status_display(),
        }

    # ── 1. Context / Complementary recommendations ────────────────────────────
    if target_product_id and not query_str:
        base = products.filter(id=target_product_id).first()
        if base:
            for p in products.exclude(id=base.id):
                score = 50
                reasons = []
                if p.category == base.category:
                    score += 20
                    reasons.append(f"Same {p.category.name} category alternative")
                elif p.category.parent and p.category.parent == base.category.parent:
                    score += 30
                    reasons.append(f"Great pairing within {p.category.parent.name}")
                if p.brand == base.brand:
                    score += 15
                    reasons.append(f"Matching {p.brand.name} ecosystem product")
                price_diff = abs(float(p.effective_price) - float(base.effective_price))
                if price_diff <= float(base.effective_price) * 0.4:
                    score += 15
                if p.is_featured:
                    score += 10
                recommendations.append(_pack(p, score, reasons))
            recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
            return recommendations[:limit]

    # ── 2. Default: return top featured picks ────────────────────────────────
    if not query_str:
        for p in products.filter(is_featured=True)[:limit]:
            recommendations.append(_pack(p, 95, ["Top Trending Featured Tech Choice"]))
        return recommendations

    # ── 3. Intent-based Query Recommendation Engine ──────────────────────────
    INTENT_KEYWORDS = {
        'gaming':       ['gaming', 'game', 'rtx', 'fps', 'gpu', 'graphic', 'curved', 'hz'],
        'portability':  ['laptop', 'portable', 'light', 'thin', 'travel', 'wireless', 'macbook'],
        'audio':        ['earbuds', 'headphone', 'audio', 'sound', 'anc', 'noise', 'airpods', 'music'],
        'wearable':     ['watch', 'smartwatch', 'fitness', 'health', 'heart', 'gps', 'cellular'],
        'performance':  ['pro', 'i9', 'ryzen', 'ddr5', 'nvme', 'speed', 'turbo', 'max'],
        'display':      ['oled', '4k', 'retina', 'nit', 'screen'],
    }

    INTENT_MESSAGES = {
        'gaming':       "Optimised for high-FPS gaming",
        'portability':  "Ultra-portable with extended battery",
        'audio':        "Pro active noise-cancellation audio",
        'wearable':     "Advanced health & fitness tracking",
        'performance':  "Blazing-fast compute performance",
        'display':      "Stunning OLED / high-refresh display",
    }

    # Extract budget ceiling (e.g. "under $1500", "below 300")
    budget_match = re.search(r'(?:under|below|less than|\$)\s*(\d+)', query_str)
    max_budget = float(budget_match.group(1)) if budget_match else None

    detected_intents = [
        intent for intent, kws in INTENT_KEYWORDS.items()
        if any(kw in query_str for kw in kws)
    ]

    for p in products:
        score = 0
        reasons = []

        p_text = f"{p.title} {p.description or ''} {p.brand.name} {p.category.name}".lower()
        specs_text = " ".join(
            f"{s.key.name} {s.value}" for s in p.specifications.all()
        ).lower()
        full_info = f"{p_text} {specs_text}"

        # Token overlap score (0-40 pts)
        tokens = [w for w in re.split(r'\W+', query_str) if len(w) > 2]
        hits = [t for t in tokens if t in full_info]
        if tokens:
            score += (len(hits) / len(tokens)) * 40

        # Brand / category exact match (25 pts each)
        if p.brand.name.lower() in query_str:
            score += 25
            reasons.append(f"Official {p.brand.name} product")
        if p.category.name.lower() in query_str:
            score += 25
            reasons.append(f"Exact match for {p.category.name}")

        # Intent bonus (15 pts per detected intent that matches product)
        for intent in detected_intents:
            kws = INTENT_KEYWORDS[intent]
            if any(kw in full_info for kw in kws):
                score += 15
                reasons.append(INTENT_MESSAGES[intent])

        # Budget constraint
        p_price = float(p.effective_price)
        if max_budget is not None:
            if p_price <= max_budget:
                score += 20
                reasons.append(f"Fits within budget under ${int(max_budget)}")
            else:
                score -= 35

        if score <= 10:
            continue

        recommendations.append(_pack(p, score, reasons))

    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    return recommendations[:limit]
