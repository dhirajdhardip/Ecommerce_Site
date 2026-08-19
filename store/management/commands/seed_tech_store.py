from django.core.management.base import BaseCommand
from store.models import (
    Category, Brand, Product, SpecificationKey, ProductSpecification,
    VariantAttribute, VariantAttributeValue, ProductVariant, ProductImage
)
from cart.models import Coupon
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds database with realistic Star Tech tech hardware inventory, Product Images, EAV specs, and PC Builder components'

    def handle(self, *args, **options):
        self.stdout.write("Seeding TechOrbit tech retail database...")

        # 1. Base Categories with Component Mappings
        comp_cat, _ = Category.objects.get_or_create(slug='components', defaults={'name': 'Components', 'component_type': 'none'})
        cpu_cat, _ = Category.objects.get_or_create(slug='processors', defaults={'name': 'Processors', 'parent': comp_cat, 'component_type': 'cpu'})
        gpu_cat, _ = Category.objects.get_or_create(slug='graphics-cards', defaults={'name': 'Graphics Cards', 'parent': comp_cat, 'component_type': 'gpu'})
        mb_cat, _ = Category.objects.get_or_create(slug='motherboards', defaults={'name': 'Motherboards', 'parent': comp_cat, 'component_type': 'motherboard'})
        ram_cat, _ = Category.objects.get_or_create(slug='ram-memory', defaults={'name': 'RAM (Memory)', 'parent': comp_cat, 'component_type': 'ram'})
        ssd_cat, _ = Category.objects.get_or_create(slug='storage-ssd', defaults={'name': 'Storage (SSD)', 'parent': comp_cat, 'component_type': 'storage'})
        psu_cat, _ = Category.objects.get_or_create(slug='power-supplies', defaults={'name': 'Power Supplies', 'parent': comp_cat, 'component_type': 'psu'})
        case_cat, _ = Category.objects.get_or_create(slug='cases-enclosures', defaults={'name': 'Cases & Enclosures', 'parent': comp_cat, 'component_type': 'case'})
        laptop_cat, _ = Category.objects.get_or_create(slug='laptops', defaults={'name': 'Laptops', 'component_type': 'none'})
        smartphone_cat, _ = Category.objects.get_or_create(slug='smartphones', defaults={'name': 'Smartphones', 'component_type': 'none', 'icon_name': 'smartphone'})
        monitor_cat, _ = Category.objects.get_or_create(slug='monitors', defaults={'name': 'Monitors', 'component_type': 'none', 'icon_name': 'monitor'})
        mouse_cat, _ = Category.objects.get_or_create(slug='mice-accessories', defaults={'name': 'Mice & Accessories', 'component_type': 'none', 'icon_name': 'mouse'})
        smartwatch_cat, _ = Category.objects.get_or_create(slug='smartwatches', defaults={'name': 'Smartwatches', 'component_type': 'none', 'icon_name': 'clock'})
        earbuds_cat, _ = Category.objects.get_or_create(slug='earbuds', defaults={'name': 'Earbuds & Audio', 'component_type': 'none', 'icon_name': 'headphones'})

        for cat, ctype in [(cpu_cat, 'cpu'), (gpu_cat, 'gpu'), (mb_cat, 'motherboard'), (ram_cat, 'ram'), (ssd_cat, 'storage'), (psu_cat, 'psu'), (case_cat, 'case')]:
            cat.component_type = ctype
            cat.save()

        # 2. Brands
        intel, _ = Brand.objects.get_or_create(slug='intel', defaults={'name': 'Intel'})
        amd, _ = Brand.objects.get_or_create(slug='amd', defaults={'name': 'AMD'})
        nvidia, _ = Brand.objects.get_or_create(slug='nvidia', defaults={'name': 'NVIDIA'})
        asus, _ = Brand.objects.get_or_create(slug='asus', defaults={'name': 'ASUS'})
        msi, _ = Brand.objects.get_or_create(slug='msi', defaults={'name': 'MSI'})
        corsair, _ = Brand.objects.get_or_create(slug='corsair', defaults={'name': 'Corsair'})
        kingston, _ = Brand.objects.get_or_create(slug='kingston', defaults={'name': 'Kingston'})
        apple, _ = Brand.objects.get_or_create(slug='apple', defaults={'name': 'Apple'})
        dell, _ = Brand.objects.get_or_create(slug='dell', defaults={'name': 'Dell'})
        lenovo, _ = Brand.objects.get_or_create(slug='lenovo', defaults={'name': 'Lenovo'})
        samsung, _ = Brand.objects.get_or_create(slug='samsung', defaults={'name': 'Samsung'})
        logitech, _ = Brand.objects.get_or_create(slug='logitech', defaults={'name': 'Logitech'})

        # 3. Spec Keys
        socket_key, _ = SpecificationKey.objects.get_or_create(name='Socket', category=cpu_cat)
        cores_key, _ = SpecificationKey.objects.get_or_create(name='Cores', category=cpu_cat)
        clock_key, _ = SpecificationKey.objects.get_or_create(name='Boost Clock', category=cpu_cat)
        mem_key, _ = SpecificationKey.objects.get_or_create(name='Memory Type', category=cpu_cat)

        # Phone Spec Keys
        phone_disp_key, _ = SpecificationKey.objects.get_or_create(name='Display', category=smartphone_cat)
        phone_cpu_key, _ = SpecificationKey.objects.get_or_create(name='Processor', category=smartphone_cat)
        phone_cam_key, _ = SpecificationKey.objects.get_or_create(name='Camera', category=smartphone_cat)
        phone_bat_key, _ = SpecificationKey.objects.get_or_create(name='Battery', category=smartphone_cat)

        # Monitor Spec Keys
        mon_res_key, _ = SpecificationKey.objects.get_or_create(name='Resolution', category=monitor_cat)
        mon_hz_key, _ = SpecificationKey.objects.get_or_create(name='Refresh Rate', category=monitor_cat)
        mon_panel_key, _ = SpecificationKey.objects.get_or_create(name='Panel Type', category=monitor_cat)
        mon_resp_key, _ = SpecificationKey.objects.get_or_create(name='Response Time', category=monitor_cat)

        # Mouse Spec Keys
        mouse_sensor_key, _ = SpecificationKey.objects.get_or_create(name='Sensor', category=mouse_cat)
        mouse_dpi_key, _ = SpecificationKey.objects.get_or_create(name='Max DPI', category=mouse_cat)
        mouse_weight_key, _ = SpecificationKey.objects.get_or_create(name='Weight', category=mouse_cat)

        # Smartwatch Spec Keys
        sw_disp_key, _ = SpecificationKey.objects.get_or_create(name='Display & Size', category=smartwatch_cat)
        sw_chip_key, _ = SpecificationKey.objects.get_or_create(name='Processor / Chip', category=smartwatch_cat)
        sw_bat_key, _ = SpecificationKey.objects.get_or_create(name='Battery Life', category=smartwatch_cat)
        sw_water_key, _ = SpecificationKey.objects.get_or_create(name='Water Resistance', category=smartwatch_cat)

        # Earbuds Spec Keys
        eb_chip_key, _ = SpecificationKey.objects.get_or_create(name='Audio Chip', category=earbuds_cat)
        eb_anc_key, _ = SpecificationKey.objects.get_or_create(name='Noise Cancellation', category=earbuds_cat)
        eb_bat_key, _ = SpecificationKey.objects.get_or_create(name='Play Time', category=earbuds_cat)
        eb_conn_key, _ = SpecificationKey.objects.get_or_create(name='Connectivity', category=earbuds_cat)

        # 4. Products, White-Background Cutout Images & Specs
        # Product 1: Intel i9-14900K
        p1, _ = Product.objects.get_or_create(
            slug='intel-core-i9-14900k',
            defaults={
                'title': 'Intel Core i9-14900K Processor',
                'brand': intel,
                'category': cpu_cat,
                'model_number': 'BX8071514900K',
                'description': '24 Cores (8 P-cores + 16 E-cores) up to 6.0 GHz unlocked desktop processor.',
                'base_price': Decimal('589.99'),
                'discount_price': Decimal('549.99'),
                'wattage': 125,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img1, _ = ProductImage.objects.get_or_create(product=p1, image='products/cpu_white.png', defaults={'is_primary': True, 'alt_text': p1.title})
        img1.image = 'products/cpu_white.png'
        img1.save()

        ProductSpecification.objects.get_or_create(product=p1, key=socket_key, defaults={'value': 'LGA1700'})
        ProductSpecification.objects.get_or_create(product=p1, key=cores_key, defaults={'value': '24'})
        ProductSpecification.objects.get_or_create(product=p1, key=clock_key, defaults={'value': '6.0 GHz'})
        ProductSpecification.objects.get_or_create(product=p1, key=mem_key, defaults={'value': 'DDR5'})

        # Product 2: AMD Ryzen 7 7800X3D
        p2, _ = Product.objects.get_or_create(
            slug='amd-ryzen-7-7800x3d',
            defaults={
                'title': 'AMD Ryzen 7 7800X3D Gaming Processor',
                'brand': amd,
                'category': cpu_cat,
                'model_number': '100-100000910WOF',
                'description': 'The ultimate gaming processor featuring 3D V-Cache technology.',
                'base_price': Decimal('449.00'),
                'discount_price': Decimal('389.99'),
                'wattage': 120,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img2, _ = ProductImage.objects.get_or_create(product=p2, image='products/cpu_white.png', defaults={'is_primary': True, 'alt_text': p2.title})
        img2.image = 'products/cpu_white.png'
        img2.save()

        # Product 3: ASUS ROG Strix Z790 Motherboard
        p3, _ = Product.objects.get_or_create(
            slug='asus-rog-strix-z790-e-gaming-wifi-ii',
            defaults={
                'title': 'ASUS ROG Strix Z790-E Gaming WiFi II',
                'brand': asus,
                'category': mb_cat,
                'model_number': 'ROG STRIX Z790-E',
                'description': 'LGA 1700 ATX Motherboard with PCIe 5.0, WiFi 7, and 18+1 Power Stages.',
                'base_price': Decimal('499.99'),
                'discount_price': Decimal('459.99'),
                'wattage': 50,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img3, _ = ProductImage.objects.get_or_create(product=p3, image='products/motherboard_white.png', defaults={'is_primary': True, 'alt_text': p3.title})
        img3.image = 'products/motherboard_white.png'
        img3.save()

        # Product 4: ASUS ROG Strix RTX 4090 GPU
        p4, _ = Product.objects.get_or_create(
            slug='asus-rog-strix-rtx-4090-24gb',
            defaults={
                'title': 'ASUS ROG Strix GeForce RTX 4090 OC 24GB',
                'brand': asus,
                'category': gpu_cat,
                'model_number': 'ROG-STRIX-RTX4090-O24G-GAMING',
                'description': 'Flagship 24GB GDDR6X graphics card with DLSS 3 support.',
                'base_price': Decimal('1999.99'),
                'discount_price': Decimal('1899.99'),
                'wattage': 450,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img4, _ = ProductImage.objects.get_or_create(product=p4, image='products/gpu_white.png', defaults={'is_primary': True, 'alt_text': p4.title})
        img4.image = 'products/gpu_white.png'
        img4.save()

        # Product 5: Corsair Vengeance 32GB DDR5 RAM
        p5, _ = Product.objects.get_or_create(
            slug='corsair-vengeance-rgb-32gb-ddr5-6000mhz',
            defaults={
                'title': 'Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz',
                'brand': corsair,
                'category': ram_cat,
                'model_number': 'CMH32GX5M2B6000C30',
                'description': 'High performance DDR5 RAM with dynamic ten-zone RGB lighting.',
                'base_price': Decimal('139.99'),
                'discount_price': Decimal('124.99'),
                'wattage': 15,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img5, _ = ProductImage.objects.get_or_create(product=p5, image='products/ram_white.png', defaults={'is_primary': True, 'alt_text': p5.title})
        img5.image = 'products/ram_white.png'
        img5.save()

        # Product 6: Kingston FURY Renegade 2TB NVMe SSD
        p6, _ = Product.objects.get_or_create(
            slug='kingston-fury-renegade-2tb-nvme-ssd',
            defaults={
                'title': 'Kingston FURY Renegade 2TB M.2 PCIe 4.0 NVMe SSD',
                'brand': kingston,
                'category': ssd_cat,
                'model_number': 'SFYRD/2000G',
                'description': 'Ultra-fast 7,300MB/s Read speed PCIe 4.0 NVMe M.2 SSD.',
                'base_price': Decimal('179.99'),
                'discount_price': Decimal('159.99'),
                'wattage': 10,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img6, _ = ProductImage.objects.get_or_create(product=p6, image='products/ssd_white.png', defaults={'is_primary': True, 'alt_text': p6.title})
        img6.image = 'products/ssd_white.png'
        img6.save()

        # Product 7: Corsair RM1000x 1000W PSU
        p7, _ = Product.objects.get_or_create(
            slug='corsair-rm1000x-1000w-psu',
            defaults={
                'title': 'Corsair RM1000x 1000W 80 PLUS Gold Fully Modular Power Supply',
                'brand': corsair,
                'category': psu_cat,
                'model_number': 'CP-9020201-NA',
                'description': 'Low-noise 1000 Watt 80+ Gold certified power supply with Japanese capacitors.',
                'base_price': Decimal('189.99'),
                'discount_price': Decimal('169.99'),
                'wattage': 0,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img7, _ = ProductImage.objects.get_or_create(product=p7, image='products/psu_white.png', defaults={'is_primary': True, 'alt_text': p7.title})
        img7.image = 'products/psu_white.png'
        img7.save()

        # Product 8: MSI MAG FORGE 112R Case
        p8, _ = Product.objects.get_or_create(
            slug='msi-mag-forge-112r-case',
            defaults={
                'title': 'MSI MAG FORGE 112R ARGB Mid-Tower Gaming Case',
                'brand': msi,
                'category': case_cat,
                'model_number': 'MAG FORGE 112R',
                'description': 'Tempered glass mid-tower casing with 4 pre-installed ARGB fans.',
                'base_price': Decimal('89.99'),
                'discount_price': Decimal('79.99'),
                'wattage': 5,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img8, _ = ProductImage.objects.get_or_create(product=p8, image='products/case_white.png', defaults={'is_primary': True, 'alt_text': p8.title})
        img8.image = 'products/case_white.png'
        img8.save()

        # Product 9: Laptop Motherboard
        p9, _ = Product.objects.get_or_create(
            slug='laptop-gaming-motherboard-so-dimm-ram-slots',
            defaults={
                'title': 'High Performance Gaming Laptop Motherboard (Dual SO-DIMM RAM Slots)',
                'brand': asus,
                'category': mb_cat,
                'model_number': 'MB-LPT-Z690',
                'description': 'Ultra-thin laptop mainboard motherboard featuring soldered Intel i7 CPU, dual SO-DIMM DDR5 RAM expansion slots, copper heatpipes, and M.2 NVMe slot.',
                'base_price': Decimal('429.99'),
                'discount_price': Decimal('389.99'),
                'wattage': 45,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img9, _ = ProductImage.objects.get_or_create(product=p9, image='products/laptop_motherboard.png', defaults={'is_primary': True, 'alt_text': p9.title})
        img9.image = 'products/laptop_motherboard.png'
        img9.save()

        # Product 10: Laptop RAM SO-DIMM
        p10, _ = Product.objects.get_or_create(
            slug='corsair-virtus-32gb-ddr5-laptop-ram',
            defaults={
                'title': 'Corsair Virtus 32GB (2x16GB) DDR5 5600MHz SO-DIMM Laptop RAM',
                'brand': corsair,
                'category': ram_cat,
                'model_number': 'CMSX32GX5M2A5600C40',
                'description': 'Premium high-density DDR5 SO-DIMM RAM module designed for modern gaming laptops, ultrabooks, and portable workstations.',
                'base_price': Decimal('149.99'),
                'discount_price': Decimal('129.99'),
                'wattage': 10,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img10, _ = ProductImage.objects.get_or_create(product=p10, image='products/laptop_ram.png', defaults={'is_primary': True, 'alt_text': p10.title})
        img10.image = 'products/laptop_ram.png'
        img10.save()

        # Product 11: ASUS ROG Strix SCAR 18 Gaming Laptop
        p11, _ = Product.objects.get_or_create(
            slug='asus-rog-strix-scar-18-gaming-laptop',
            defaults={
                'title': 'ASUS ROG Strix SCAR 18 (2026) 18" 240Hz QHD Gaming Laptop',
                'brand': asus,
                'category': laptop_cat,
                'model_number': 'G834JYR-XS96',
                'description': 'Ultimate gaming laptop powered by Intel Core i9-14900HX, NVIDIA GeForce RTX 4090 16GB, 32GB DDR5 RAM, and 2TB PCIe 4.0 NVMe SSD.',
                'base_price': Decimal('3699.99'),
                'discount_price': Decimal('3499.99'),
                'wattage': 330,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img11, _ = ProductImage.objects.get_or_create(product=p11, image='products/laptop_asus_rog.png', defaults={'is_primary': True, 'alt_text': p11.title})
        img11.image = 'products/laptop_asus_rog.png'
        img11.save()

        # Product 12: Apple MacBook Pro 16 M3 Max
        p12, _ = Product.objects.get_or_create(
            slug='apple-macbook-pro-16-m3-max-space-black',
            defaults={
                'title': 'Apple MacBook Pro 16-inch M3 Max (36GB Unified Memory, 1TB SSD) - Space Black',
                'brand': apple,
                'category': laptop_cat,
                'model_number': 'MUW63LL/A',
                'description': 'Pro performance workstation featuring 16-core CPU, 40-core GPU, 16.2-inch Liquid Retina XDR Display, and 22-hour battery life.',
                'base_price': Decimal('3499.00'),
                'discount_price': Decimal('3299.99'),
                'wattage': 140,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img12, _ = ProductImage.objects.get_or_create(product=p12, image='products/laptop_macbook.png', defaults={'is_primary': True, 'alt_text': p12.title})
        img12.image = 'products/laptop_macbook.png'
        img12.save()

        # Product 13: Dell XPS 15 OLED Touch Laptop
        p13, _ = Product.objects.get_or_create(
            slug='dell-xps-15-9530-oled-touch-laptop',
            defaults={
                'title': 'Dell XPS 15 (9530) 15.6" 3.5K OLED Touch Laptop',
                'brand': dell,
                'category': laptop_cat,
                'model_number': 'XPS9530-9743SLV-PUS',
                'description': 'Premium thin & light ultrabook featuring Intel Core i9-13900H, NVIDIA GeForce RTX 4070 8GB, 32GB DDR5 RAM, and 1TB NVMe SSD.',
                'base_price': Decimal('2499.99'),
                'discount_price': Decimal('2249.99'),
                'wattage': 130,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img13, _ = ProductImage.objects.get_or_create(product=p13, image='products/laptop_dell_xps.png', defaults={'is_primary': True, 'alt_text': p13.title})
        img13.image = 'products/laptop_dell_xps.png'
        img13.save()

        # Product 14: Lenovo Legion Pro 7i Gaming Laptop
        p14, _ = Product.objects.get_or_create(
            slug='lenovo-legion-pro-7i-gen-9-gaming-laptop',
            defaults={
                'title': 'Lenovo Legion Pro 7i Gen 9 16" 240Hz WQXGA Gaming Laptop',
                'brand': lenovo,
                'category': laptop_cat,
                'model_number': '83DE0007US',
                'description': 'High refresh rate esports gaming laptop with Intel Core i9-14900HX, RTX 4080 12GB, 32GB DDR5 RAM, 1TB SSD, and Legion Coldfront Vapor Chamber cooling.',
                'base_price': Decimal('2799.99'),
                'discount_price': Decimal('2549.99'),
                'wattage': 330,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img14, _ = ProductImage.objects.get_or_create(product=p14, image='products/laptop_lenovo_legion.png', defaults={'is_primary': True, 'alt_text': p14.title})
        img14.image = 'products/laptop_lenovo_legion.png'
        img14.save()

        # Product 15: Samsung Galaxy S26 Ultra 5G AI Smartphone
        p15, _ = Product.objects.get_or_create(
            slug='samsung-galaxy-s26-ultra-5g',
            defaults={
                'title': 'Samsung Galaxy S26 Ultra 5G AI Flagship Smartphone (12GB RAM, 512GB Storage)',
                'brand': samsung,
                'category': smartphone_cat,
                'model_number': 'SM-S938B/DS',
                'description': 'Next-generation flagship smartphone powered by Snapdragon 8 Gen 5, 200MP Quad Camera with Galaxy AI, 6.8" Dynamic AMOLED 2X 120Hz display, titanium body, and built-in S Pen.',
                'base_price': Decimal('1399.99'),
                'discount_price': Decimal('1299.99'),
                'wattage': 0,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img15, _ = ProductImage.objects.get_or_create(product=p15, image='products/smartphone_s26.png', defaults={'is_primary': True, 'alt_text': p15.title})
        img15.image = 'products/smartphone_s26.png'
        img15.save()

        ProductSpecification.objects.get_or_create(product=p15, key=phone_disp_key, defaults={'value': '6.8" Dynamic AMOLED 2X 120Hz'})
        ProductSpecification.objects.get_or_create(product=p15, key=phone_cpu_key, defaults={'value': 'Snapdragon 8 Gen 5'})
        ProductSpecification.objects.get_or_create(product=p15, key=phone_cam_key, defaults={'value': '200MP + 50MP + 50MP + 10MP Quad'})
        ProductSpecification.objects.get_or_create(product=p15, key=phone_bat_key, defaults={'value': '5000 mAh (45W Fast Charge)'})

        # Product 16: Samsung Odyssey OLED G9 49" Gaming Monitor
        p16, _ = Product.objects.get_or_create(
            slug='samsung-odyssey-oled-g9-49-curved-gaming-monitor',
            defaults={
                'title': 'Samsung Odyssey OLED G9 49" DQHD 240Hz 0.03ms Curved Gaming Monitor',
                'brand': samsung,
                'category': monitor_cat,
                'model_number': 'LS49CG950SNXZA',
                'description': 'World premier 49" dual QHD OLED gaming monitor featuring 1800R curvature, 240Hz ultra refresh rate, 0.03ms response time, Neo Quantum Processor Pro, and DisplayHDR True Black 400.',
                'base_price': Decimal('1599.99'),
                'discount_price': Decimal('1399.99'),
                'wattage': 0,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img16, _ = ProductImage.objects.get_or_create(product=p16, image='products/monitor_gaming.png', defaults={'is_primary': True, 'alt_text': p16.title})
        img16.image = 'products/monitor_gaming.png'
        img16.save()

        ProductSpecification.objects.get_or_create(product=p16, key=mon_res_key, defaults={'value': 'Dual QHD (5120 x 1440)'})
        ProductSpecification.objects.get_or_create(product=p16, key=mon_hz_key, defaults={'value': '240 Hz'})
        ProductSpecification.objects.get_or_create(product=p16, key=mon_panel_key, defaults={'value': 'OLED 1800R Curved'})
        ProductSpecification.objects.get_or_create(product=p16, key=mon_resp_key, defaults={'value': '0.03ms (GtG)'})

        # Product 17: Logitech G PRO X SUPERLIGHT 2 Wireless Gaming Mouse
        p17, _ = Product.objects.get_or_create(
            slug='logitech-g-pro-x-superlight-2-wireless-gaming-mouse',
            defaults={
                'title': 'Logitech G PRO X SUPERLIGHT 2 Wireless Gaming Mouse - Black',
                'brand': logitech,
                'category': mouse_cat,
                'model_number': '910-006796',
                'description': 'Iconic 60g ultra-lightweight wireless esports gaming mouse with HERO 2 sensor up to 32,000 DPI, LIGHTFORCE hybrid optical-mechanical switches, zero-additive PTFE feet, and 95-hour battery life.',
                'base_price': Decimal('169.99'),
                'discount_price': Decimal('149.99'),
                'wattage': 0,
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img17, _ = ProductImage.objects.get_or_create(product=p17, image='products/mouse_gaming.png', defaults={'is_primary': True, 'alt_text': p17.title})
        img17.image = 'products/mouse_gaming.png'
        img17.save()

        ProductSpecification.objects.get_or_create(product=p17, key=mouse_sensor_key, defaults={'value': 'HERO 2'})
        ProductSpecification.objects.get_or_create(product=p17, key=mouse_dpi_key, defaults={'value': '32,000 DPI'})
        ProductSpecification.objects.get_or_create(product=p17, key=mouse_weight_key, defaults={'value': '60g Ultra Light'})

        # Product 18: Apple Watch Ultra 2
        p18, _ = Product.objects.get_or_create(
            slug='apple-watch-ultra-2-gps-cellular',
            defaults={
                'title': 'Apple Watch Ultra 2 GPS + Cellular (Titanium)',
                'brand': apple,
                'category': smartwatch_cat,
                'model_number': 'MREG3LL/A',
                'description': 'Rugged and capable titanium smartwatch with S9 SiP, double tap gesture, brightest Apple display (3000 nits), and up to 36 hours battery life.',
                'base_price': Decimal('799.99'),
                'discount_price': Decimal('749.99'),
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img18, _ = ProductImage.objects.get_or_create(product=p18, image='products/smartwatch_apple.png', defaults={'is_primary': True, 'alt_text': p18.title})
        img18.image = 'products/smartwatch_apple.png'
        img18.save()

        ProductSpecification.objects.get_or_create(product=p18, key=sw_disp_key, defaults={'value': '49mm Always-On Retina OLED (3000 nits)'})
        ProductSpecification.objects.get_or_create(product=p18, key=sw_chip_key, defaults={'value': 'Apple S9 SiP (64-bit dual core)'})
        ProductSpecification.objects.get_or_create(product=p18, key=sw_bat_key, defaults={'value': 'Up to 36 Hours (72 Hours Low Power)'})
        ProductSpecification.objects.get_or_create(product=p18, key=sw_water_key, defaults={'value': '100m Water Resistant (WR100)'})

        # Product 19: Apple AirPods Pro 2nd Gen
        p19, _ = Product.objects.get_or_create(
            slug='apple-airpods-pro-2nd-gen-usbc',
            defaults={
                'title': 'Apple AirPods Pro (2nd Gen) with MagSafe Case (USB-C)',
                'brand': apple,
                'category': earbuds_cat,
                'model_number': 'MTJV3AM/A',
                'description': 'Pro-level Active Noise Cancellation, Adaptive Audio, Transparency mode, Spatial Audio with dynamic head tracking, and USB-C MagSafe case.',
                'base_price': Decimal('249.99'),
                'discount_price': Decimal('199.99'),
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img19, _ = ProductImage.objects.get_or_create(product=p19, image='products/earbuds_airpods.png', defaults={'is_primary': True, 'alt_text': p19.title})
        img19.image = 'products/earbuds_airpods.png'
        img19.save()

        ProductSpecification.objects.get_or_create(product=p19, key=eb_chip_key, defaults={'value': 'Apple H2 Headphone Chip'})
        ProductSpecification.objects.get_or_create(product=p19, key=eb_anc_key, defaults={'value': '2x Active Noise Cancellation & Adaptive Audio'})
        ProductSpecification.objects.get_or_create(product=p19, key=eb_bat_key, defaults={'value': 'Up to 6 Hours (30 Hours with Case)'})
        ProductSpecification.objects.get_or_create(product=p19, key=eb_conn_key, defaults={'value': 'Bluetooth 5.3 & MagSafe USB-C Case'})

        # Product 20: Apple Watch Series 9
        p20, _ = Product.objects.get_or_create(
            slug='apple-watch-series-9-gps-45mm',
            defaults={
                'title': 'Apple Watch Series 9 GPS 45mm Aluminium Case',
                'brand': apple,
                'category': smartwatch_cat,
                'model_number': 'MR993LL/A',
                'description': 'Apple S9 SiP chip, magical double tap gesture control, brighter 2000 nits display, precision finding for iPhone, and advanced health tracking.',
                'base_price': Decimal('429.99'),
                'discount_price': Decimal('389.99'),
                'stock_status': 'in_stock',
                'is_featured': True
            }
        )
        img20, _ = ProductImage.objects.get_or_create(product=p20, image='products/smartwatch_apple.png', defaults={'is_primary': True, 'alt_text': p20.title})
        img20.image = 'products/smartwatch_apple.png'
        img20.save()

        ProductSpecification.objects.get_or_create(product=p20, key=sw_disp_key, defaults={'value': '45mm Always-On Retina Display (2000 nits)'})
        ProductSpecification.objects.get_or_create(product=p20, key=sw_chip_key, defaults={'value': 'Apple S9 SiP'})
        ProductSpecification.objects.get_or_create(product=p20, key=sw_bat_key, defaults={'value': '18 Hours Normal Use'})
        ProductSpecification.objects.get_or_create(product=p20, key=sw_water_key, defaults={'value': '50m Water Resistant'})

        # 5. Variants Setup
        var_attr, _ = VariantAttribute.objects.get_or_create(name='Packaging')
        v_opt1, _ = VariantAttributeValue.objects.get_or_create(attribute=var_attr, value='Standard Box')
        
        v1, _ = ProductVariant.objects.get_or_create(
            sku='I9-14900K-BOX',
            defaults={
                'product': p1,
                'title': 'Boxed Edition',
                'price': Decimal('549.99'),
                'stock_quantity': 35,
                'is_default': True
            }
        )
        v1.attribute_values.add(v_opt1)

        # 6. Seed Coupons
        Coupon.objects.get_or_create(
            code='WELCOME10',
            defaults={
                'discount_type': 'percentage',
                'discount_value': Decimal('10.00'),
                'min_order_amount': Decimal('100.00'),
                'active': True
            }
        )
        Coupon.objects.get_or_create(
            code='TECH50',
            defaults={
                'discount_type': 'fixed',
                'discount_value': Decimal('50.00'),
                'min_order_amount': Decimal('300.00'),
                'active': True
            }
        )

        self.stdout.write(self.style.SUCCESS("TechOrbit white-background product cutouts successfully seeded!"))
