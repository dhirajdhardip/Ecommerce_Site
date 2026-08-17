import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from store.models import Product, SpecificationKey

class CompareView(View):
    """
    Renders side-by-side product specification comparison table.
    """
    def get(self, request):
        compare_ids = request.session.get('compare_ids', [])
        products = Product.objects.filter(id__in=compare_ids, is_active=True).select_related('brand', 'category').prefetch_related('specifications__key', 'images')

        # Build union matrix of specification keys across compared products
        all_spec_keys = set()
        product_spec_map = {}

        for p in products:
            product_spec_map[p.id] = {}
            for spec in p.specifications.all():
                key_name = spec.key.name
                all_spec_keys.add(key_name)
                product_spec_map[p.id][key_name] = spec.value

        spec_keys_sorted = sorted(list(all_spec_keys))

        context = {
            'products': products,
            'spec_keys': spec_keys_sorted,
            'product_spec_map': product_spec_map,
        }
        return render(request, 'compare/compare.html', context)

class ToggleCompareApiView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = int(data.get('product_id'))

            compare_ids = request.session.get('compare_ids', [])

            if product_id in compare_ids:
                compare_ids.remove(product_id)
                added = False
                msg = "Product removed from comparison."
            else:
                if len(compare_ids) >= 4:
                    return JsonResponse({'status': 'error', 'message': 'Maximum 4 products can be compared simultaneously.'}, status=400)
                compare_ids.append(product_id)
                added = True
                msg = "Product added to comparison drawer!"

            request.session['compare_ids'] = compare_ids
            request.session.modified = True

            return JsonResponse({
                'status': 'success',
                'added': added,
                'message': msg,
                'compare_count': len(compare_ids)
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class ClearCompareApiView(View):
    def post(self, request):
        request.session['compare_ids'] = []
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Comparison list cleared.'})
