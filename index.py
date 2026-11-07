import os
import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Taranacak arşiv klasörleri (Yeni klasörleri buradaki listeye ekleyebilirsin)
ARCHIVE_DIRS = [
    "/storage/emulated/0/Projeler/API/Anime Kızı Web/sfw/neko_text_archive",
    "/storage/emulated/0/Projeler/API/Anime Kızı Web/sfw 2/Uygun İçerik./neko_text_archive",
    "/storage/emulated/0/Projeler/API/Anime Kızı Web/nsfw/+18 İçeriktir./neko_text_archive/",
    "/storage/emulated/0/Projeler/API/Anime Kızı Web/nsfw 2/+18 İçerik Girmeyiniz./neko_text_archive/",
    # Yeni klasörlerini buraya ekleyebilirsin:
    # "/storage/emulated/0/Projeler/API/Anime Kızı Web/yeni_klasor_3/neko_text_archive",
    # "/storage/emulated/0/Projeler/API/Anime Kızı Web/yeni_klasor_4/neko_text_archive",
]

def load_all_archives():
    all_items = []
    categories = set()
    
    for base_dir in ARCHIVE_DIRS:
        if not os.path.exists(base_dir):
            continue
        try:
            for cat_name in os.listdir(base_dir):
                cat_path = os.path.join(base_dir, cat_name)
                if os.path.isdir(cat_path):
                    metadata_file = os.path.join(cat_path, "metadata.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, "r", encoding="utf-8") as f:
                                items = json.load(f)
                                for item in items:
                                    item['category'] = cat_name
                                    all_items.append(item)
                                    categories.add(cat_name)
                        except Exception:
                            pass
        except Exception:
            pass
            
    return all_items, sorted(list(categories))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/categories")
def get_categories():
    _, categories = load_all_archives()
    return jsonify(categories)

@app.route("/api/items")
def get_items():
    category = request.args.get("category", "all")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    
    items, categories = load_all_archives()
    
    if category != "all":
        items = [i for i in items if i.get('category') == category]
        
    start = (page - 1) * limit
    end = start + limit
    paginated_items = items[start:end]
    
    return jsonify({
        "items": paginated_items,
        "total": len(items),
        "has_more": end < len(items)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
