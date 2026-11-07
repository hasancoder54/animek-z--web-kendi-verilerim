Projen için GitHub'a doğrudan ekleyebileceğin, gereksinimleri, yerel çalışma mantığını ve internet bağlantısı gereksinimini net bir şekilde açıklayan profesyonel bir `README.md` içeriği:

```markdown
# 🌸 Anime Arşiv Yerel Web Galerisi (Flask)

Yerel depolama alanınızda bulunan JSON tabanlı anime görsel arşivlerini tarayarak kategorize eden, modern, performans odaklı ve kullanıcı dostu bir Flask web galerisi.

---

## 🚀 Özellikler

* **Dinamik Kategori Filtreleme:** Arşivinizdeki tüm kategorileri otomatik algılar ve açılır menü üzerinden filtreleme yapmanızı sağlar.
* **Performans Optimizasyonu (Lazy Loading & Intersection Observer):** Özellikle hareketli GIF'lerde cihazın kasanmasını önlemek için yalnızca ekranda görünen görseller yüklenir ve oynatılır; ekrandan çıkanlar durdurularak RAM ve işlemci rahatlatılır.
* **Sayfalandırma / Devamını Yükle:** Veriler 10'arlı gruplar halinde yüklenir, alt sınıra gelindiğinde "Devamını Yükle" butonu ile akıcı bir gezinti sunar.
* **Gelişmiş Modal Görüntüleyici:** Görsele tıklayarak tam ekran önizleme yapabilir; klavye ok tuşları (`←` / `→`) ile sonraki/önceki görsellere hızlıca geçebilirsiniz.
* **Manuel İndirme Desteği:** Otomatik indirme yapmaz, modal içinde yer alan "İndir" butonu ile istediğiniz görseli manuel indirebilirsiniz.

---

## ⚠️ Önemli Notlar (Çalışma Ortamı)

1. **Yerel Ortam (Localhost):** Bu uygulama tamamen kendi cihazınızda (örneğin Pydroid 3, Termux veya yerel Python ortamınızda) yerel bir sunucu olarak çalışır. Dış dünyaya açık bir web hosting üzerinde çalıştırılmak üzere tasarlanmamıştır.
2. **İnternet Gereksinimi:** Sunucu ve JSON dosyaları tamamen çevrimdışı (offline) çalışır; ancak **görseller harici CDN linklerinden çekildiği için** görsellerin görüntülenebilmesi ve indirilebilmesi için aktif bir internet bağlantısı gereklidir.

---

## 📦 Gereksinimler

Uygulamanın çalışabilmesi için sisteminizde aşağıdakiler bulunmalıdır:

* Python 3.x
* Flask kütüphanesi

Gerekli kütüphaneyi kurmak için terminalde şu komutu çalıştırın:
```bash
pip install flask

```

---

## 🛠️ Kurulum ve Yapılandırma

1. Projeyi bilgisayarınıza/cihazınıza indirin. Klasör yapısının şu şekilde olduğundan emin olun:
```text
Anime Kızı Web/
├── index.py
└── templates/
    └── index.html

```


2. `index.py` dosyasını açın ve kendi cihazınızdaki arşiv klasör yollarını `ARCHIVE_DIRS` listesine ekleyin:
```python
ARCHIVE_DIRS = [
    "/storage/emulated/0/Projeler/API/Anime Kızı Web/sfw/neko_text_archive",
    "/storage/emulated/0/Projeler/API/Anime Kızı Web/sfw 2/Uygun İçerik./neko_text_archive",
    # Kendi yeni klasör yollarınızı buraya ekleyebilirsiniz:
]

```


3. Uygulamayı başlatın:
```bash
python index.py

```


4. Tarayıcınızı açın ve şu adrese gidin:
```text
[http://127.0.0.1:5000](http://127.0.0.1:5000)

```



---

## 📝 Lisans

Bu proje kişisel kullanım ve arşiv amaçlı geliştirilmiştir.

```

```
