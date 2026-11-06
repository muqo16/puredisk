# PureDisk 🧹

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)
[![UI: CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-10a37f.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Safe Mode](https://img.shields.io/badge/Safety-Protected%20Whitelist-success.svg)](#-g%C3%BCvenlik-mimarisi-fail-safe-protection)

> **PureDisk**, Windows sisteminizi yormadan, çekirdek sistem bileşenlerine ve kişisel dosyalarınıza **asla zarar vermeden** güvenli bir şekilde gigabaytlarca disk alanı açan modern masaüstü temizleme aracıdır.

---

## ✨ Özellikler (Key Features)

- 🛡️ **%100 Güvenli Mod (Fail-Safe Architecture):** Windows çekirdek dosyalarını (`System32`, `WinSxS`, `Boot`, `Program Files`) ve kullanıcı özel dizinlerini (`Masaüstü`, `Belgeler`, `İndirilenler` vb.) koruma altına alan katı beyaz/kara liste filtresi.
- 🎨 **Minimalist & Modern Tasarım:** Koyu antrasit yüzeyler, zümrüt yeşili aksiyon vurguları ve akıcı animasyonlarla yüksek kaliteli CustomTkinter arayüzü.
- 📊 **Canlı Disk Göstergesi:** C: sürücünüzün doluluk oranını, boş ve toplam alanını anlık olarak izler.
- 🔍 **Önizlemeli Analiz (Tara Modu):** Silme işlemi yapmadan önce her kategorinin diskte ne kadar yer kapladığını tespit eder ve rozetlerle gösterir.
- ⚡ **Çok Kanallı (Multithreaded) Performans:** Tarama ve temizlik işlemleri arka plan iş parçacığında çalışır; kullanıcı arayüzü asla donmaz veya takılmaz.
- 🗂️ **Kategori Tabanlı Kontrol:** Temizlenecek her alanı onay kutuları ile ayrı ayrı açıp kapatabilirsiniz.

---

## 🗂️ Desteklenen Temizlik Kategorileri

| Kategori | Açıklama | Güvenlik Düzeyi |
| :--- | :--- | :---: |
| **Geçici Sistem Dosyaları (Temp)** | Windows ve çalışan programların geride bıraktığı geçici çalışma ve kurulum dosyaları (`%LOCALAPPDATA%\Temp`, `C:\Windows\Temp`). | ✅ Çok Güvenli |
| **Android & Emülatör Altyapısı** | Birkaç GB ile onlarca GB arası yer tutabilen Android SDK, emülatör imajları, derleme araçları, Gradle önbelleği ve Nox/MuMu kalıntıları. | ✅ Güvenli (Geliştirici) |
| **Geliştirici Önbellekleri** | Python (`pip`), Node.js (`npm`, `pnpm`) indirme ve paket önbellek depoları. | ✅ Çok Güvenli |
| **Çökme & Hata Dökümleri (Crash Dumps)** | Kilitlenen uygulamaların oluşturduğu devasa `.dmp` dosyaları ve WER hata raporları. | ✅ Çok Güvenli |
| **Geri Dönüşüm Kutusu (Recycle Bin)** | Windows API (`SHEmptyRecycleBinW`) ile çöp kutusunu sessiz ve güvenli şekilde boşaltır. | ✅ Güvenli |
| **Tarayıcı Web Önbelleği (Sadece Cache)** | Chrome, Edge ve Brave'in web resim/stil önbelleği. *(Şifreler, yer imleri, açık sekmeler ve tarama geçmişi ASLA silinmez)* | ✅ Çok Güvenli |
| **Windows Update İndirme Önbelleği** | Yüklenmiş ve tamamlanmış eski Windows güncelleştirmelerinden kalan kurulum paketleri. | ✅ Güvenli |

---

## 🛡️ Güvenlik Mimarisi (Fail-Safe Protection)

Sistemin kararlılığını korumak için aşağıdaki koruma mekanizmaları devrededir:

1. **Katı Sistem Kara Listesi:** Temizlenecek hedef yolun `C:\Windows\System32`, `SysWOW64`, `Boot`, `Program Files` veya kullanıcının kişisel klasörleriyle kesişmesi durumunda işlem anında reddedilir.
2. **Kök Klasör Korunumu:** `Temp` gibi dizinlerin kendisi asla silinmez; yalnızca içerisindeki eski alt dosyalar temizlenir.
3. **Kilitli Dosya Toleransı:** Windows veya çalışan başka bir uygulamanın kilitlediği dosyalar zorlanmaz; sistem hatası üretilmeden sessizce atlanır.

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Windows 10 veya Windows 11
- Python 3.10 veya üzeri (Kaynak koddan çalıştırılacaksa)

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/muqo16/puredisk.git
cd puredisk
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatın
```bash
python main.py
```
*(Konsol penceresi görünmeden arka planda çalıştırmak için `pythonw main.py` veya `run.bat` kullanabilirsiniz)*

---

## 🔨 Bağımsız EXE Olarak Derleme (Build Standalone Executable)

Uygulamayı Python yüklü olmayan herhangi bir bilgisayarda çalıştırmak üzere tek bir `.exe` haline getirmek için:

```bash
pyinstaller --onefile --noconsole --name "PureDisk" main.py
```
Derleme tamamlandığında bağımsız çalıştırılabilir dosya `dist/PureDisk.exe` konumunda üretilecektir.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır. Dilediğiniz gibi kullanabilir, değiştirebilir ve geliştirebilirsiniz.
