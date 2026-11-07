import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import init, Fore, Style

init(autoreset=True)

BASE_DIR = "neko_text_archive"
TARGET_TOTAL_LIMIT = 5000
MAX_WORKERS = 10

def fetch_nekosapi_v4_items(current_id_start):
    fetched_items = []
    try:
        # Sadece güvenli (safe) içerikler için rating=safe parametresi
        url = "https://api.nekosapi.com/v4/images/random?rating=safe&limit=20"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", data) if isinstance(data, dict) else data
            
            for idx, item in enumerate(items):
                img_url = item.get("image_file") or item.get("url")
                if not img_url:
                    continue
                
                # İçerideki etiketleri (tags) ve kategorileri alıyoruz
                tags = item.get("tags", [])
                tag_name = "general"
                if tags and isinstance(tags, list):
                    first_tag = tags[0]
                    if isinstance(first_tag, dict):
                        tag_name = first_tag.get("name", "general")
                    elif isinstance(first_tag, str):
                        tag_name = first_tag

                fetched_items.append({
                    "category": tag_name.lower().replace(" ", "_"),
                    "data": {
                        "id": current_id_start + idx,
                        "artist_name": "NekosAPI Artist",
                        "artist_href": "",
                        "source_url": "",
                        "image_url": img_url,
                        "source_api": "nekosapi.com"
                    }
                })
    except Exception:
        pass
    return fetched_items

def archive_nekosapi_only():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.MAGENTA + Style.BRIGHT + "     NEKOSAPI.COM EXCLUSIVE ARCHIVER (5000 LIMIT)     ")
    print(Fore.CYAN + Style.BRIGHT + "=" * 60 + "\n")

    # Mevcut kayıtları yükle
    total_saved = 0
    category_items_map = {}
    existing_urls_global = set()

    # Mevcut klasörleri tarayıp eski verileri koruyalım
    if os.path.exists(BASE_DIR):
        for cat in os.listdir(BASE_DIR):
            cat_dir = os.path.join(BASE_DIR, cat)
            if os.path.isdir(cat_dir):
                metadata_path = os.path.join(cat_dir, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            items = json.load(f)
                            category_items_map[cat] = items
                            total_saved += len(items)
                            for item in items:
                                if "image_url" in item:
                                    existing_urls_global.add(item["image_url"])
                    except Exception:
                        pass

    print(Fore.GREEN + f"[i] Mevcut arşivde toplam {total_saved} kayıt var. Hedef: {TARGET_TOTAL_LIMIT}\n")

    if total_saved >= TARGET_TOTAL_LIMIT:
        print(Fore.YELLOW + "[!] Zaten 5.000 sınırına ulaşıldı.")
        return

    pbar = tqdm(total=TARGET_TOTAL_LIMIT, initial=total_saved, desc=Fore.GREEN + "Toplam İlerleme", unit="veri")

    while total_saved < TARGET_TOTAL_LIMIT:
        progress_made = False

        v4_results = fetch_nekosapi_v4_items(total_saved + 1)
        for res in v4_results:
            if total_saved >= TARGET_TOTAL_LIMIT:
                break
            
            cat = res["category"]
            item_data = res["data"]
            
            if item_data["image_url"] in existing_urls_global:
                continue

            cat_dir = os.path.join(BASE_DIR, cat)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)

            metadata_path = os.path.join(cat_dir, "metadata.json")
            if cat not in category_items_map:
                category_items_map[cat] = []

            category_items_map[cat].append(item_data)
            existing_urls_global.add(item_data["image_url"])
            total_saved += 1
            progress_made = True
            pbar.update(1)

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(category_items_map[cat], f, ensure_ascii=False, indent=4)

        if not progress_made:
            tqdm.write(Fore.YELLOW + "\n[!] API kaynaklarındaki benzersiz veriler tükendi.")
            break

        time.sleep(0.5)

    pbar.close()
    print(Fore.GREEN + Style.BRIGHT + f"\n[✔] İşlem tamamlandı! Toplam {total_saved} veri '{BASE_DIR}' klasöründe toplandı.")

if __name__ == "__main__":
    archive_nekosapi_only()
