import os
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import init, Fore, Style

init(autoreset=True)

# Gönderdiğin tam kategori ve format sözlüğü
ENDPOINTS = {
    "lurk": "gif", "shoot": "gif", "sleep": "gif", "clap": "gif", "shrug": "gif",
    "stare": "gif", "wave": "gif", "poke": "gif", "confused": "gif", "smile": "gif",
    "peck": "gif", "wink": "gif", "sip": "gif", "blush": "gif", "smug": "gif",
    "tickle": "gif", "yeet": "gif", "think": "gif", "highfive": "gif", "feed": "gif",
    "wag": "gif", "bite": "gif", "teehee": "gif", "shocked": "gif", "bleh": "gif",
    "bored": "gif", "nom": "gif", "nya": "gif", "yawn": "gif", "facepalm": "gif",
    "cuddle": "gif", "kick": "gif", "happy": "gif", "carry": "gif", "hug": "gif",
    "kabedon": "gif", "baka": "gif", "bonk": "gif", "pat": "gif", "angry": "gif",
    "spin": "gif", "shake": "gif", "run": "gif", "nod": "gif", "nope": "gif",
    "kiss": "gif", "dance": "gif", "punch": "gif", "handshake": "gif", "slap": "gif",
    "cry": "gif", "lappillow": "gif", "pout": "gif", "blowkiss": "gif", "handhold": "gif",
    "salute": "gif", "thumbsup": "gif", "laugh": "gif", "tableflip": "gif",
    "neko": "png", "waifu": "png", "husbando": "png", "kitsune": "png"
}

API_BASE_URL = "https://nekos.best/api/v2/"
BASE_DIR = "neko_text_archive"
TARGET_TOTAL_LIMIT = 5000  # Maksimum toplam sınır
MAX_WORKERS = 10

def fetch_single_metadata(item, current_id):
    img_url = item.get("url")
    if not img_url:
        return None

    return {
        "id": current_id,
        "artist_name": item.get("artist_name", "Bilinmiyor"),
        "artist_href": item.get("artist_href", ""),
        "source_url": item.get("source_url", ""),
        "image_url": img_url
    }

def archive_text_data():
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    print(Fore.CYAN + Style.BRIGHT + "=" * 60)
    print(Fore.MAGENTA + Style.BRIGHT + "     ULTIMATE NEKO & EMOTE ARCHIVER (JSON ONLY)     ")
    print(Fore.CYAN + Style.BRIGHT + "=" * 60 + "\n")

    # Mevcut toplam kayıt sayısını hesapla (silmeme kuralı için başlangıç)
    total_saved = 0
    category_items_map = {}
    existing_urls_global = set()

    for category in ENDPOINTS.keys():
        cat_dir = os.path.join(BASE_DIR, category)
        metadata_path = os.path.join(cat_dir, "metadata.json")
        category_items_map[category] = []
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    category_items_map[category] = items
                    total_saved += len(items)
                    for item in items:
                        if "image_url" in item:
                            existing_urls_global.add(item["image_url"])
            except Exception:
                pass

    print(Fore.GREEN + f"[i] Mevcut arşivde halihazırda {total_saved} kayıt bulundu. Kaldığı yerden devam ediliyor...\n")

    if total_saved >= TARGET_TOTAL_LIMIT:
        print(Fore.YELLOW + "[!] Zaten 5.000 sınırına ulaşıldı.")
        return

    pbar = tqdm(total=TARGET_TOTAL_LIMIT, initial=total_saved, desc=Fore.GREEN + "Toplam İlerleme", unit="veri")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while total_saved < TARGET_TOTAL_LIMIT:
            progress_made = False

            for category in ENDPOINTS.keys():
                if total_saved >= TARGET_TOTAL_LIMIT:
                    break

                cat_dir = os.path.join(BASE_DIR, category)
                if not os.path.exists(cat_dir):
                    os.makedirs(cat_dir)

                metadata_path = os.path.join(cat_dir, "metadata.json")
                category_items = category_items_map[category]

                try:
                    url = f"{API_BASE_URL}{category}?amount=20"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        results = response.json().get("results", [])
                        if not results:
                            continue

                        # Küresel olarak daha önce kaydedilmemişleri filtrele
                        valid_results = [item for item in results if item.get("url") and item.get("url") not in existing_urls_global]
                        
                        if not valid_results:
                            continue

                        futures = [
                            executor.submit(fetch_single_metadata, item, len(category_items) + i + 1)
                            for i, item in enumerate(valid_results)
                        ]

                        batch_added = 0
                        for future in as_completed(futures):
                            result = future.result()
                            if result and result["image_url"] not in existing_urls_global:
                                category_items.append(result)
                                existing_urls_global.add(result["image_url"])
                                total_saved += 1
                                batch_added += 1
                                progress_made = True
                                pbar.update(1)

                                if total_saved >= TARGET_TOTAL_LIMIT:
                                    break

                        if batch_added > 0:
                            tqdm.write(
                                Fore.YELLOW + f"[KATEGORI: {category.upper()}] " +
                                Fore.WHITE + f"+{batch_added} yeni kayıt. " +
                                Fore.CYAN + f"(Bu klasör toplam: {len(category_items)}) | " +
                                Fore.GREEN + f"Genel Toplam: {total_saved}/{TARGET_TOTAL_LIMIT}"
                            )

                        with open(metadata_path, "w", encoding="utf-8") as f:
                            json.dump(category_items, f, ensure_ascii=False, indent=4)

                    else:
                        time.sleep(1)

                except Exception as e:
                    time.sleep(1)

            if not progress_made:
                tqdm.write(Fore.YELLOW + "\n[!] API havuzundaki tüm benzersiz veriler tükendi.")
                break

    pbar.close()
    print(Fore.GREEN + Style.BRIGHT + f"\n[✔] İşlem tamamlandı! Toplam {total_saved} veri '{BASE_DIR}' içinde korundu ve güncellendi.")

if __name__ == "__main__":
    archive_text_data()
