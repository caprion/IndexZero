"""Generate a 500-row synthetic Indian e-commerce product title CSV.

Produces data/flipkart_titles_500.csv with realistic Flipkart-style titles
that stress-test tokenizers: model numbers, units glued to digits, hyphens,
slashes, apostrophes, parenthetical specs, mixed capitalization, and
long compound titles with pipe separators.

Uses ONLY Python stdlib.  Deterministic via random.seed(42).

Usage:
    python scripts/generate_corpus.py
"""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------
# Brand pools
# ---------------------------------------------------------------------------

PHONE_BRANDS = ["Redmi", "Samsung", "OnePlus", "realme", "iQOO", "Motorola", "POCO", "Vivo"]
LAPTOP_BRANDS = ["HP", "Lenovo", "Asus", "Dell", "Acer", "MSI"]
AUDIO_BRANDS = ["boAt", "Noise", "JBL", "Sony", "Mivi", "Realme"]
CHARGER_BRANDS = ["Ambrane", "Portronics", "Mi", "Anker", "Belkin", "boAt"]
FASHION_BRANDS = ["Allen Solly", "Peter England", "Biba", "W", "Libas", "Anouk", "Roadster", "HRX"]
SHOE_BRANDS = ["Puma", "Adidas", "Nike", "Sparx", "Campus", "Bata", "Skechers"]
KITCHEN_BRANDS = ["Prestige", "Hawkins", "Pigeon", "Milton", "Cello", "Borosil", "Bajaj"]
BEAUTY_BRANDS = ["L'Oreal", "Mamaearth", "mCaffeine", "Nivea", "Lakme", "Biotique", "Cetaphil"]
GROCERY_BRANDS = ["Tata", "Fortune", "Saffola", "Aashirvaad", "Haldiram's", "MDH", "Everest"]
BABY_BRANDS = ["Pampers", "Huggies", "Cerelac", "Chicco", "LuvLap", "MeeMee", "Fisher-Price"]
SPORTS_BRANDS = ["Puma", "Adidas", "Nike", "Nivia", "Boldfit", "MuscleBlaze", "Decathlon"]
BOOK_PUBLISHERS = ["Arihant", "S. Chand", "Pearson", "McGraw Hill", "Penguin", "Drishti"]

# ---------------------------------------------------------------------------
# Spec helpers
# ---------------------------------------------------------------------------

COLORS = [
    "Black", "Blue", "White", "Silver", "Red", "Green", "Grey",
    "Midnight Blue", "Smoky Teal", "Coral Pink", "Lavender",
    "Phantom Black", "Starlight", "Rose Gold", "Maroon",
]
SIZES = ["S", "M", "L", "XL", "XXL", "Free Size"]
PHONE_MODELS_REDMI = [
    "Note 13 Pro+ 5G", "Note 13 5G", "Note 12 Pro 5G",
    "12C", "13C 5G", "A3",
]
PHONE_MODELS_SAMSUNG = [
    "Galaxy M34 5G", "Galaxy M14 5G", "Galaxy S24 Ultra",
    "Galaxy A15 5G", "Galaxy F15 5G", "Galaxy A05s",
]
PHONE_MODELS_ONEPLUS = ["Nord CE 3 Lite 5G", "Nord 3 5G", "12R 5G", "11R 5G"]
PHONE_MODELS_REALME = ["Narzo N53", "C55", "11 Pro+ 5G", "GT Neo 5 SE"]
PHONE_MODELS_IQOO = ["Z7 Pro 5G", "Neo 7 Pro 5G", "Z9x 5G", "11 5G"]
PHONE_MODELS_OTHER = ["Edge 40 Neo 5G", "POCO M6 Pro 5G", "V29e 5G"]

RAM_STORAGE = ["4GB/64GB", "6GB/128GB", "8GB/128GB", "8GB/256GB", "12GB/256GB"]

LAPTOP_SERIES = {
    "HP": ["15s", "14s", "Pavilion x360", "Victus"],
    "Lenovo": ["IdeaPad Slim 3", "IdeaPad 1", "V15", "LOQ"],
    "Asus": ["Vivobook 15", "TUF Gaming F15", "Zenbook 14"],
    "Dell": ["Inspiron 15", "Vostro 3420", "Latitude 3440"],
    "Acer": ["Aspire 3", "Aspire Lite", "Nitro V"],
    "MSI": ["Modern 14", "GF63 Thin", "Katana 15"],
}
PROCESSORS = [
    "Intel Core i3-1215U", "Intel Core i5-1235U", "Intel Core i5-12450H",
    "Intel Core i7-12650H", "AMD Ryzen 5 5500U", "AMD Ryzen 7 5800H",
    "Apple M2", "Snapdragon 7c Gen 2",
]
LAPTOP_RAM = ["8GB", "16GB", "32GB"]
LAPTOP_SSD = ["256GB SSD", "512GB SSD", "1TB SSD"]

EARBUDS_MODELS = {
    "boAt": ["Airdopes 141", "Airdopes 161", "Rockerz 255 Pro+", "Airdopes 131"],
    "Noise": ["Buds VS104", "ColorFit Pro 4", "Air Buds Pro 3"],
    "JBL": ["Tune 230NC TWS", "Wave Beam", "Tune 130NC TWS"],
    "Sony": ["WF-C500", "WH-1000XM5", "WF-1000XM5"],
    "Mivi": ["DuoPods A25", "Commando X9", "Rock X1"],
    "Realme": ["Buds T300", "Buds Air 5 Pro", "Buds T110"],
}

SMARTWATCH_MODELS = {
    "boAt": ["Wave Lite", "Storm Call 2", "Xtend Plus"],
    "Noise": ["ColorFit Pro 5", "Pulse 2 Max", "Twist Go"],
    "Samsung": ["Galaxy Watch 6", "Galaxy Fit 3"],
}

KURTI_STYLES = [
    "Anarkali Kurti", "A-Line Kurti with Palazzo Set", "Straight Kurti with Dupatta Set",
    "Printed Cotton Kurti", "Rayon Flared Kurti", "Embroidered Kurti Pant Set",
]

SAREE_TYPES = [
    "Banarasi Silk Saree", "Kanjivaram Art Silk Saree", "Cotton Blend Saree",
    "Georgette Saree with Blouse Piece", "Chiffon Printed Saree",
    "Linen Blend Saree with Running Blouse",
]

BOOK_TITLES_COMPETITIVE = [
    "Quantitative Aptitude for Competitive Examinations",
    "NCERT Exemplar Problems-Solutions Mathematics Class 12",
    "Word Power Made Easy (New Revised & Expanded Edition)",
    "Objective General English by SP Bakshi (2024-25)",
    "Fast Track Objective Arithmetic",
    "14000+ Objective Questions - General Studies",
    "A Modern Approach to Verbal & Non-Verbal Reasoning",
    "Lucent's General Knowledge (2024 Edition)",
]

BOOK_TITLES_FICTION = [
    "The Kite Runner (Paperback)",
    "Atomic Habits by James Clear",
    "Ikigai: The Japanese Secret to a Long and Happy Life",
    "Rich Dad Poor Dad - 25th Anniversary Edition",
    "The Psychology of Money by Morgan Housel",
    "Sapiens: A Brief History of Humankind",
    "The Alchemist (Paulo Coelho) 25th Anniversary Edition",
    "It Ends with Us by Colleen Hoover",
]


def pick(lst: list) -> str:
    return random.choice(lst)


def pick_color() -> str:
    return pick(COLORS)


# ---------------------------------------------------------------------------
# Title generators per sub-category
# ---------------------------------------------------------------------------

def _phone_title() -> str:
    brand = pick(PHONE_BRANDS)
    if brand == "Redmi":
        model = pick(PHONE_MODELS_REDMI)
    elif brand == "Samsung":
        model = pick(PHONE_MODELS_SAMSUNG)
    elif brand == "OnePlus":
        model = pick(PHONE_MODELS_ONEPLUS)
    elif brand == "realme":
        model = pick(PHONE_MODELS_REALME)
    elif brand == "iQOO":
        model = pick(PHONE_MODELS_IQOO)
    else:
        model = pick(PHONE_MODELS_OTHER)

    ram_stor = pick(RAM_STORAGE)
    color = pick_color()

    patterns = [
        f"{brand} {model} ({color}, {ram_stor})",
        f"{brand} {model} ({color}, {ram_stor}) | 50MP Triple Cam | 5000mAh",
        f"{brand} {model} {ram_stor} - {color}",
        f"{brand} {model} ({color}) {ram_stor} Storage | 120Hz AMOLED",
    ]
    return pick(patterns)


def _laptop_title() -> str:
    brand = pick(LAPTOP_BRANDS)
    series = pick(LAPTOP_SERIES[brand])
    proc = pick(PROCESSORS)
    ram = pick(LAPTOP_RAM)
    ssd = pick(LAPTOP_SSD)
    display = pick(["15.6 inch", "14 inch", "13.3 inch"])

    patterns = [
        f"{brand} {series} {proc} {display} FHD Laptop ({ram}/{ssd})",
        f"{brand} {series} ({proc}, {ram}, {ssd}) Thin & Light Laptop",
        f"{brand} {series} {display} Laptop | {proc} | {ram} RAM | {ssd} | Windows 11",
    ]
    return pick(patterns)


def _earbuds_title() -> str:
    brand = pick(list(EARBUDS_MODELS.keys()))
    model = pick(EARBUDS_MODELS[brand])
    color = pick_color()

    patterns = [
        f"{brand} {model} Bluetooth Headset ({color})",
        f"{brand} {model} with Mic | 42H Playtime | IPX5 Water-Resistant ({color})",
        f"{brand} {model} TWS Earbuds with Active Noise Cancellation",
        f"{brand} {model} in-Ear Wireless Earbuds, {pick(['13mm', '10mm', '6mm'])} Drivers",
    ]
    return pick(patterns)


def _charger_title() -> str:
    brand = pick(CHARGER_BRANDS)
    watts = pick(["18W", "20W", "25W", "33W", "45W", "65W", "67W"])
    cable_type = pick(["USB-C", "Type-C", "Micro-USB", "Type-C/Lightning"])

    patterns = [
        f"{brand} {watts} Fast Charger with {cable_type} Cable (Pack of 1)",
        f"{brand} {watts} USB-C PD Charger Adapter | BIS Certified",
        f"{brand} Dual Port {watts} Charger + {cable_type} 1m Cable Combo",
    ]
    return pick(patterns)


def _powerbank_title() -> str:
    brand = pick(["Mi", "Ambrane", "boAt", "Portronics", "Realme", "Samsung"])
    capacity = pick(["10000mAh", "20000mAh", "26800mAh"])
    watts = pick(["20W", "22.5W", "33W"])

    patterns = [
        f"{brand} {capacity} Power Bank with {watts} Fast Charging (Black)",
        f"{brand} Pocket Power {capacity} Li-Polymer | Dual USB-C | {watts} PD",
    ]
    return pick(patterns)


def _cable_title() -> str:
    brand = pick(["Ambrane", "Portronics", "boAt", "Belkin", "AmazonBasics", "Mi"])
    cable = pick(["USB-C to USB-C", "Type-C to Lightning", "Micro-USB", "USB-C"])
    length = pick(["1m", "1.5m", "2m", "3m"])

    patterns = [
        f"{brand} {cable} {length} Braided Cable | 3A Fast Charging",
        f"{brand} {cable} Cable {length} - 480Mbps Data Transfer | PVC (Black)",
    ]
    return pick(patterns)


def _smartwatch_title() -> str:
    brand = pick(list(SMARTWATCH_MODELS.keys()))
    model = pick(SMARTWATCH_MODELS[brand])
    color = pick_color()

    patterns = [
        f"{brand} {model} Smartwatch with 1.85 inch HD Display ({color})",
        f"{brand} {model} | BT Calling | 100+ Sports Modes | SpO2 ({color})",
        f"{brand} {model} Smart Watch with Heart Rate Monitor & IP68",
    ]
    return pick(patterns)


def _kurti_title() -> str:
    brand = pick(["Biba", "W", "Libas", "Anouk", "Ishin", "Janasya", "AKS"])
    style = pick(KURTI_STYLES)
    color = pick(["Maroon", "Navy Blue", "Mustard", "Teal", "Pink", "Green", "Red"])
    size = pick(SIZES)

    patterns = [
        f"{brand} Women's {style} - {color} (Size {size})",
        f"{brand} {style} for Women | Pure Cotton | {color}",
        f"{brand} Women Ethnic {style} ({color}, {size})",
    ]
    return pick(patterns)


def _saree_title() -> str:
    brand = pick(["Mimosa", "Saara", "Ishin", "Satrani", "Anni Designer", "SIRIL"])
    saree_type = pick(SAREE_TYPES)
    color = pick(["Red", "Gold", "Blue", "Green", "Pink", "Magenta", "Cream"])

    patterns = [
        f"{brand} {saree_type} ({color})",
        f"{brand} Women's {saree_type} with Unstitched Blouse | {color}",
        f"{brand} {saree_type} - Festive Wear ({color}) #1 Best Seller",
    ]
    return pick(patterns)


def _tshirt_title() -> str:
    brand = pick(["Allen Solly", "Peter England", "Roadster", "HRX", "Puma", "US Polo"])
    fit = pick(["Regular Fit", "Slim Fit", "Oversized"])
    sleeve = pick(["half-sleeve", "full-sleeve", "sleeveless"])
    style = pick(["Polo T-Shirt", "Round Neck T-Shirt", "Printed T-Shirt", "Striped T-Shirt"])
    color = pick_color()

    patterns = [
        f"{brand} Men's {fit} {sleeve} {style} ({color})",
        f"{brand} Men {style} - {fit} | 100% Cotton | {color} (Size {pick(SIZES)})",
    ]
    return pick(patterns)


def _jeans_title() -> str:
    brand = pick(["Levi's", "Wrangler", "Pepe Jeans", "Spykar", "Flying Machine", "Roadster"])
    fit = pick(["Slim Fit", "Skinny Fit", "Regular Fit", "Tapered Fit"])
    wash = pick(["Light Wash", "Dark Wash", "Mid-Rise", "High-Rise"])

    patterns = [
        f"{brand} Men's {fit} Stretchable Jeans - {wash} (Size {pick(['28', '30', '32', '34', '36'])})",
        f"{brand} Men {fit} {wash} Denim Jeans | Cotton Blend",
    ]
    return pick(patterns)


def _shoes_title() -> str:
    brand = pick(SHOE_BRANDS)
    shoe_type = pick(["Running Shoes", "Sneakers", "Casual Shoes", "Walking Shoes", "Sports Shoes"])
    color = pick_color()

    patterns = [
        f"{brand} Men's {shoe_type} - {color} (UK {pick(['6', '7', '8', '9', '10'])})",
        f"{brand} Unisex-Adult {shoe_type} | Lace-Up | Lightweight ({color})",
        f"{brand} Women's {shoe_type} ({color}, UK {pick(['4', '5', '6', '7'])})",
    ]
    return pick(patterns)


def _dupatta_set_title() -> str:
    brand = pick(["Biba", "Libas", "Anouk", "Ishin", "Janasya"])
    color = pick(["Maroon", "Navy", "Teal", "Mustard", "Peach"])

    patterns = [
        f"{brand} Women's Straight Kurta with Palazzo & Dupatta Set ({color})",
        f"{brand} Cotton Blend Kurta Dupatta Set - Printed ({color}, Size {pick(SIZES)})",
    ]
    return pick(patterns)


def _cookware_title() -> str:
    brand = pick(KITCHEN_BRANDS)
    item = pick(["Tawa", "Kadhai", "Fry Pan", "Dosa Tawa", "Roti Tawa", "Wok"])
    size = pick(["24cm", "26cm", "28cm", "30cm", "24cm/28cm"])
    coating = pick(["non-stick", "granite-coated", "hard-anodised"])

    patterns = [
        f"{brand} {coating} {item} {size} with Induction Base",
        f"{brand} Omega Deluxe {coating} {item} ({size}) | Sturdy Handle",
        f"{brand} {item} - {coating.title()}, {size}, 3mm Thick Base",
    ]
    return pick(patterns)


def _bottle_title() -> str:
    brand = pick(["Milton", "Cello", "Borosil", "Solimo", "Fridge Buddy"])
    material = pick(["Thermosteel", "Stainless Steel", "Glass", "Tritan Plastic"])
    capacity = pick(["500ml", "750ml", "1L", "1.5L", "2L"])
    color = pick_color()

    patterns = [
        f"{brand} {material} Water Bottle {capacity} ({color})",
        f"{brand} {material} Flask {capacity} - Hot & Cold 24H | BPA Free",
        f"{brand} Flip-Lid {material} Bottle ({capacity}) Pack of 3",
    ]
    return pick(patterns)


def _container_title() -> str:
    brand = pick(["Milton", "Cello", "Signoraware", "Borosil", "Amazon Brand - Solimo"])
    material = pick(["Plastic", "Glass", "Stainless Steel"])
    sizes = pick(["300ml/500ml/1000ml", "500ml + 750ml + 1L", "250ml/500ml"])

    patterns = [
        f"{brand} {material} Storage Container Set ({sizes}) - Pack of 3",
        f"{brand} Airtight {material} Container Combo | {sizes} | BPA Free",
        f"{brand} {material} Jar Set with Lid - {sizes} (Pack of 5)",
    ]
    return pick(patterns)


def _pressure_cooker_title() -> str:
    brand = pick(["Prestige", "Hawkins", "Pigeon", "Butterfly"])
    capacity = pick(["2L", "3L", "5L", "7.5L"])
    material = pick(["Aluminium", "Stainless Steel", "Hard Anodised"])

    patterns = [
        f"{brand} Popular {material} Pressure Cooker {capacity} | ISI Certified",
        f"{brand} Contura {material} Outer Lid Pressure Cooker ({capacity})",
        f"{brand} {capacity} {material} Pressure Cooker - Induction Base | 10-Year Warranty",
    ]
    return pick(patterns)


def _mixer_grinder_title() -> str:
    brand = pick(["Bajaj", "Philips", "Prestige", "Preethi", "Butterfly", "Maharaja Whiteline"])
    watts = pick(["500W", "600W", "750W", "1000W"])
    jars = pick(["3", "4"])

    patterns = [
        f"{brand} {watts} Mixer Grinder with {jars} Jars (White/Blue)",
        f"{brand} {watts} Mixer Grinder | Stainless Steel Blades | {jars} Jars | 2-Year Warranty",
        f"{brand} Rex {watts} {jars}-Jar Mixer Grinder - #1 Best Seller",
    ]
    return pick(patterns)


def _running_shoes_title() -> str:
    brand = pick(SPORTS_BRANDS)
    color = pick_color()
    uk_size = pick(["UK 7", "UK 8", "UK 9", "UK 10"])

    patterns = [
        f"{brand} Men's Ultraboost Running Shoes ({color}, {uk_size})",
        f"{brand} Revolution 6 Running Shoe | Breathable Mesh | {color}",
        f"{brand} Flexagon Energy 4 Men's Training Shoes - {color} ({uk_size})",
    ]
    return pick(patterns)


def _gym_equipment_title() -> str:
    brand = pick(["Boldfit", "Strauss", "Kore", "Lifelong", "Decathlon"])
    item = pick([
        "Adjustable Dumbbell Set 20kg",
        "Push-Up Board 9-in-1 Body Building",
        "Resistance Bands Set (Pack of 5)",
        "Pull-Up Bar Door Frame Mount",
        "Ab Roller Wheel with Knee Pad",
        "Skipping Rope with Counter",
        "Hand Gripper 3-in-1 Set",
    ])

    return f"{brand} {item}"


def _yoga_mat_title() -> str:
    brand = pick(["Boldfit", "Strauss", "Amazon Basics", "Adidas", "Decathlon"])
    thickness = pick(["4mm", "6mm", "8mm", "10mm"])
    color = pick(["Purple", "Blue", "Green", "Grey", "Black", "Pink"])

    patterns = [
        f"{brand} Yoga Mat {thickness} Anti-Skid | EVA Material ({color})",
        f"{brand} TPE Yoga Mat {thickness} with Carry Strap - Eco Friendly ({color})",
    ]
    return pick(patterns)


def _protein_title() -> str:
    brand = pick(["MuscleBlaze", "Optimum Nutrition", "MyProtein", "Amway Nutrilite"])
    flavor = pick(["Rich Chocolate", "Vanilla Ice Cream", "Double Chocolate", "Cafe Mocha", "Unflavoured"])
    weight = pick(["1kg", "2kg", "4kg", "500g"])

    patterns = [
        f"{brand} Whey Protein {weight} - {flavor} | 25g Protein/Serving",
        f"{brand} Raw Whey Isolate {weight} ({flavor}) | No Added Sugar",
        f"{brand} Biozyme Performance Whey {weight} - {flavor}",
    ]
    return pick(patterns)


def _supplement_title() -> str:
    brand = pick(["HealthKart", "Himalaya", "MuscleBlaze", "Boldfit", "GNC", "WOW Life Science"])
    item = pick([
        "Multivitamin for Men (Pack of 60 Tablets)",
        "Omega 3 Fish Oil 1000mg - 60 Capsules",
        "Ashwagandha 500mg Capsules (Pack of 90)",
        "Biotin 10000mcg for Hair Growth - 60 Tablets",
        "Vitamin D3 + K2 Supplement 120 Capsules",
        "Apple Cider Vinegar Effervescent Tablets (Pack of 15)",
    ])

    return f"{brand} {item}"


def _book_competitive_title() -> str:
    pub = pick(BOOK_PUBLISHERS)
    title = pick(BOOK_TITLES_COMPETITIVE)
    return f"{title} | {pub}"


def _book_fiction_title() -> str:
    title = pick(BOOK_TITLES_FICTION)
    return title


def _book_textbook_title() -> str:
    pub = pick(["NCERT", "S. Chand", "Pearson", "Laxmi Publications", "Cengage"])
    subject = pick([
        "Mathematics Class 12",
        "Physics Part-I Class 11",
        "Chemistry Concepts for JEE Main & Advanced",
        "Data Structures & Algorithms in C++",
        "Engineering Drawing (1st Year)",
        "Organic Chemistry (Morrison & Boyd)",
    ])

    patterns = [
        f"{pub} {subject} (Latest Edition 2024-25)",
        f"{pub} {subject} | CBSE Syllabus | With MCQs",
    ]
    return pick(patterns)


def _face_cream_title() -> str:
    brand = pick(BEAUTY_BRANDS)
    ml = pick(["25ml", "50ml", "100ml"])
    concern = pick([
        "anti-wrinkle night cream",
        "Vitamin C face cream",
        "moisturising day cream with SPF 30",
        "hydrating gel cream",
        "anti-aging cream with Retinol",
    ])
    return f"{brand} {concern} ({ml})"


def _shampoo_title() -> str:
    brand = pick(BEAUTY_BRANDS)
    ml = pick(["100ml", "200ml", "340ml", "650ml"])
    variant = pick([
        "anti-hair fall shampoo",
        "anti-dandruff shampoo",
        "colour protect shampoo",
        "onion hair fall shampoo",
        "tea tree oil shampoo",
    ])

    patterns = [
        f"{brand} {variant} {ml}",
        f"{brand} {variant} ({ml}) | SLS-Free | Paraben-Free",
    ]
    return pick(patterns)


def _perfume_title() -> str:
    brand = pick(["Bella Vita", "Denver", "Wild Stone", "Fogg", "Set Wet", "Engage"])
    ml = pick(["50ml", "100ml", "120ml"])
    variant = pick(["CEO", "Intense", "Date Night", "Luxury Oud", "Night Rider", "Fresh Aqua"])

    patterns = [
        f"{brand} {variant} Eau de Parfum - {ml} | For Men",
        f"{brand} {variant} Perfume for Women's ({ml})",
        f"{brand} {variant} Body Spray {ml} (Pack of 2)",
    ]
    return pick(patterns)


def _sunscreen_title() -> str:
    brand = pick(BEAUTY_BRANDS)
    spf = pick(["SPF 30", "SPF 50", "SPF 50+"])
    ml = pick(["50ml", "80ml", "120ml"])

    patterns = [
        f"{brand} UV Protect Sunscreen Lotion {spf} PA+++ ({ml})",
        f"{brand} Ultra-Light Aqua Gel Sunscreen {spf} | {ml} | Water-Resistant",
    ]
    return pick(patterns)


def _oil_title() -> str:
    brand = pick(GROCERY_BRANDS[:4])
    oil = pick([
        "Refined Sunflower Oil 1L Pouch",
        "Kachi Ghani Mustard Oil 1L Bottle",
        "Cold Pressed Coconut Oil 500ml",
        "Rice Bran Oil 1L | Heart-Healthy",
        "Extra Virgin Olive Oil 500ml",
        "Refined Soyabean Oil 5L Can",
    ])
    return f"{brand} {oil}"


def _spice_title() -> str:
    brand = pick(["MDH", "Everest", "Tata Sampann", "Catch", "Eastern", "Badshah"])
    spice = pick([
        "Garam Masala 100g",
        "Turmeric Powder 200g",
        "Red Chilli Powder 500g",
        "Kitchen King Masala 100g",
        "Biryani Masala 50g",
        "Sambhar Masala 100g | South Indian Special",
        "Meat Masala 100g",
        "Pav Bhaji Masala 100g",
    ])
    return f"{brand} {spice}"


def _cleaning_title() -> str:
    brand = pick(["Lizol", "Harpic", "Vim", "Dettol", "Domex", "Scotch-Brite"])
    item = pick([
        "Disinfectant Surface Cleaner 975ml | Citrus",
        "Toilet Cleaner 500ml (Pack of 2)",
        "Dishwash Liquid Gel 750ml - Lemon",
        "Floor Cleaner 1L | Pine Fresh",
        "Scrub Pad (Pack of 3) - 3M Non-Scratch",
        "Antibacterial Handwash 200ml (Buy 2 Get 1 Free)",
    ])
    return f"{brand} {item}"


def _toy_title() -> str:
    brand = pick(BABY_BRANDS[-2:] + ["Funskool", "Toyshine", "R for Rabbit", "Lego"])
    toy = pick([
        "Building Blocks Set 100+ Pieces | Ages 3-8",
        "Remote Control Car 1:18 Scale - Rechargeable",
        "Baby's First Rattle Set (Pack of 5)",
        "Magnetic Drawing Board for Kids | Erasable",
        "Kitchen Play Set 30+ Accessories | BPA Free",
        "Musical Learning Toy for Toddlers 12M+",
    ])
    return f"{brand} {toy}"


def _diaper_title() -> str:
    brand = pick(["Pampers", "Huggies", "MamyPoko", "Himalaya"])
    size = pick(["New Born (NB)", "Small (S)", "Medium (M)", "Large (L)", "XL"])
    count = pick(["36", "54", "72", "84", "114"])

    patterns = [
        f"{brand} Premium Pants Diapers - {size} | {count} Count",
        f"{brand} All-Round Protection Diaper Pants ({size}, {count} Pieces)",
    ]
    return pick(patterns)


def _baby_food_title() -> str:
    brand = pick(["Cerelac", "Nestum", "Slurrp Farm", "Early Foods"])
    variant = pick([
        "Wheat Rice Mixed Fruit Stage 3",
        "Ragi Dal Veg Stage 2 (8-24 Months)",
        "Multigrain Cereal 300g",
        "Organic Millet Porridge Mix 200g",
        "Rice & Mixed Vegetables Stage 2",
    ])
    return f"{brand} Baby Cereal {variant}"


def _school_supplies_title() -> str:
    brand = pick(["Classmate", "Doms", "Faber-Castell", "Cello", "Camlin"])
    item = pick([
        "Long Notebook 172 Pages (Pack of 6)",
        "Geometry Box Set - Compass + Divider + Protractor",
        "Oil Pastels 25 Shades",
        "Wax Crayons 24 Colors | Non-Toxic",
        "Mechanical Pencil 0.5mm (Pack of 5)",
        "Ball Pen Pack of 20 - Blue Ink",
        "Whiteboard Markers Assorted (Pack of 10)",
    ])
    return f"{brand} {item}"


# ---------------------------------------------------------------------------
# Category -> generator map with counts
# ---------------------------------------------------------------------------

CategorySpec = tuple[str, list[tuple[Callable[[], str], int]]]

CATEGORIES: list[CategorySpec] = [
    ("Electronics", [
        (_phone_title, 28),
        (_laptop_title, 20),
        (_earbuds_title, 18),
        (_charger_title, 10),
        (_powerbank_title, 8),
        (_cable_title, 8),
        (_smartwatch_title, 8),
    ]),  # total = 100
    ("Fashion", [
        (_kurti_title, 16),
        (_saree_title, 14),
        (_tshirt_title, 14),
        (_jeans_title, 12),
        (_shoes_title, 14),
        (_dupatta_set_title, 10),
    ]),  # total = 80
    ("Home & Kitchen", [
        (_cookware_title, 20),
        (_bottle_title, 16),
        (_container_title, 14),
        (_pressure_cooker_title, 16),
        (_mixer_grinder_title, 14),
    ]),  # total = 80
    ("Sports & Fitness", [
        (_running_shoes_title, 16),
        (_gym_equipment_title, 16),
        (_yoga_mat_title, 10),
        (_protein_title, 10),
        (_supplement_title, 8),
    ]),  # total = 60
    ("Books & Education", [
        (_book_competitive_title, 18),
        (_book_fiction_title, 16),
        (_book_textbook_title, 16),
    ]),  # total = 50
    ("Beauty & Personal Care", [
        (_face_cream_title, 12),
        (_shampoo_title, 12),
        (_perfume_title, 14),
        (_sunscreen_title, 12),
    ]),  # total = 50
    ("Grocery & Household", [
        (_oil_title, 14),
        (_spice_title, 14),
        (_cleaning_title, 12),
    ]),  # total = 40
    ("Baby & Kids", [
        (_toy_title, 12),
        (_diaper_title, 10),
        (_baby_food_title, 8),
        (_school_supplies_title, 10),
    ]),  # total = 40
]


def generate_title(category: str, generators: list[tuple[Callable[[], str], int]]) -> str:
    """Pick a weighted-random generator for the category and produce a title."""
    # Flatten into a weighted list
    pool: list[Callable[[], str]] = []
    for gen_fn, count in generators:
        pool.extend([gen_fn] * count)
    chosen = pick(pool)
    return chosen()


def main() -> None:
    random.seed(42)

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    out_path = project_root / "data" / "flipkart_titles_500.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build all rows: distribute exact counts per sub-category
    rows: list[tuple[str, str, str]] = []
    for category, generators in CATEGORIES:
        for gen_fn, count in generators:
            for _ in range(count):
                title = gen_fn()
                rows.append(("", title, category))

    # Shuffle so categories are interleaved (more realistic)
    random.shuffle(rows)

    # Assign product IDs after shuffle
    final_rows: list[tuple[str, str, str]] = []
    for i, (_, title, category) in enumerate(rows, start=1):
        product_id = f"fk-{i:03d}"
        final_rows.append((product_id, title, category))

    # Write CSV
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "title", "category"])
        writer.writerows(final_rows)

    # Summary
    print(f"Generated {len(final_rows)} product titles -> {out_path}")
    print()

    # Category distribution
    cat_counts: dict[str, int] = {}
    for _, _, cat in final_rows:
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print("Category distribution:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:<28s} {cnt:>4d}")
    print(f"  {'TOTAL':<28s} {sum(cat_counts.values()):>4d}")

    # Quick sanity checks
    ids = [r[0] for r in final_rows]
    titles = [r[1] for r in final_rows]
    assert len(set(ids)) == 500, "Duplicate product IDs found"
    assert all(t.strip() for t in titles), "Empty title found"
    print()
    print("Sanity checks passed: 500 unique IDs, no empty titles.")


if __name__ == "__main__":
    main()
