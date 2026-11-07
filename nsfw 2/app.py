import os
import json
import time
import requests
from tqdm import tqdm
from colorama import init, Fore, Style

init(autoreset=True)

BASE_DIR = "neko_text_archive"
TARGET_TOTAL_LIMIT = 5000
API_URL = "https://api.waifu.best/images"

def fetch_waifu_api_page(page_number, current_id_start):
    fetched_items = []
    try:
        # Dokümantasyona göre SFW filtreleme (IsNsfw=False) ve sayfalama parametreleri
        params = {
            "IsNsfw": "true",
            "PageSize": 50,
            "Page": page_number
        }
        response = requests.get(API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            for idx, item in enumerate(items):
                img_url = item.get("url")
                if not img_url:
                    continue
                
                # Tag (etiket) bilgisini alıp klasör ismi yapalım
                tags = item.get("tags", [])
                tag_name = "general"
                if tags and isinstance(tags, list):
                    first_tag = tags[0]
                    if isinstance(first_tag, dict):
                        tag_name = first_tag.get("name", "general")
                    elif isinstance(first_tag, str):
                        tag_name = first_tag

                # Sanatçı bilgilerini alalım (ilk sanatçı)
                artists = item.get("artists", [])
                artist_name = "Bilinmiyor"
                artist_pixiv = ""
                artist_twitter = ""
                if artists and isinstance(artists, list):
                    first_artist = artists[0]
                    if isinstance(first_artist, dict):
                        artist_name = first_artist.get("name", "Bilinmiyor")
                        artist_pixiv = first_artist.get("pixiv", "")
                        artist_twitter = first_artist.get("twitter", "")

                fetched_items.append({
                    "category": tag_name.lower().replace(" ", "_"),
                    "data": {
                        "id": current_id_start + idx,
                        "image_id": item.get("id"),
                        "artist_name": artist_name,
                        "artist_pixiv": artist_pixiv,
                        "artist_twitter": artist_twitter,
                        "source_url": item.get("source", ""),
                        "image_url": img_url,
                        "source_api": "waifu.best"
                    }
                })
    except Exception as e:
        pass
    return fetched_items

def archive_waifu_api_exact():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.MAGENTA + Style.BRIGHT + "     WAIFU API OFFICIAL DOCS ARCHIVER (5000 LIMIT)     ")
    print(Fore.CYAN + Style.BRIGHT + "=" * 60 + "\n")

    # Mevcut kayıtları yükle
    total_saved = 0
    category_items_map = {}
    existing_urls_global = set()

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
    
    current_page = 1
    while total_saved < TARGET_TOTAL_LIMIT:
        progress_made = False

        page_results = fetch_waifu_api_page(current_page, total_saved + 1)
        if not page_results:
            tqdm.write(Fore.YELLOW + "\n[!] API sayfalarında başka veri kalmadı.")
            break

        for res in page_results:
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

        current_page += 1
        time.sleep(0.3)

        if not progress_made and current_page > 100:
            break

    pbar.close()
    print(Fore.GREEN + Style.BRIGHT + f"\n[✔] İşlem tamamlandı! Toplam {total_saved} veri '{BASE_DIR}' klasöründe toplandı.")

if __name__ == "__main__":
    archive_waifu_api_exact()
