import os
import glob
import ctypes
import shutil
from typing import Callable, List, Dict, Tuple, Optional

# --- GÜVENLİK FİLTRESİ: KESİNLİKLE DOKUNULMAYACAK SİSTEM DİZİNLERİ ---
USER_PROFILE = os.environ.get("USERPROFILE", r"C:\Users\Default")
CRITICAL_PROTECTED_PATHS = [
    r"c:\windows\system32",
    r"c:\windows\syswow64",
    r"c:\windows\winsxs",
    r"c:\windows\system",
    r"c:\windows\boot",
    r"c:\windows\drivers",
    r"c:\windows\assembly",
    r"c:\program files",
    r"c:\program files (x86)",
    r"c:\recovery",
    r"c:\system volume information",
    r"c:\boot",
    os.path.join(USER_PROFILE, "Desktop").lower(),
    os.path.join(USER_PROFILE, "Documents").lower(),
    os.path.join(USER_PROFILE, "Downloads").lower(),
    os.path.join(USER_PROFILE, "Pictures").lower(),
    os.path.join(USER_PROFILE, "Videos").lower(),
    os.path.join(USER_PROFILE, "Music").lower(),
    os.path.join(USER_PROFILE, "Contacts").lower(),
    os.path.join(USER_PROFILE, "Favorites").lower(),
]


def is_path_safe(target_path: str) -> bool:
    """
    Hedef yolun güvenli bir temizlik hedefi olup olmadığını denetler.
    Windows sistem dosyalarını veya kullanıcının kişisel klasörlerini ASLA silmez.
    """
    if not target_path or not os.path.isabs(target_path):
        return False

    norm = os.path.abspath(target_path).lower().rstrip(r"\/")

    # Kök dizinler veya sürücü kökleri (C:\ vb.) asla silinemez
    if len(norm) <= 3 and norm.endswith(":"):
        return False
    if norm in ("c:", "c:\\", "c:/"):
        return False

    # Korunan sistem klasörleriyle çakışma kontrolü
    for protected in CRITICAL_PROTECTED_PATHS:
        if norm == protected or norm.startswith(protected + "\\"):
            return False

    return True


def get_disk_info(drive: str = "C:\\") -> Tuple[float, float, float, float]:
    """
    Sürücü kullanımını döner: (total_gb, used_gb, free_gb, percent_used)
    """
    try:
        total, used, free = shutil.disk_usage(drive)
        total_gb = total / (1024 ** 3)
        used_gb = used / (1024 ** 3)
        free_gb = free / (1024 ** 3)
        percent = (used / total) * 100 if total > 0 else 0
        return round(total_gb, 2), round(used_gb, 2), round(free_gb, 2), round(percent, 1)
    except Exception:
        return 0.0, 0.0, 0.0, 0.0


def calculate_folder_size(path: str) -> int:
    """Verilen klasördeki toplam dosya boyutunu bayt cinsinden hesaplar."""
    if not os.path.exists(path):
        return 0
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += calculate_folder_size(entry.path)
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        pass
    return total


# --- TEMİZLEME KATEGORİ TANIMLARI ---
def get_categories_definition() -> List[Dict]:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    win_dir = os.environ.get("WINDIR", r"C:\Windows")

    return [
        {
            "id": "temp_files",
            "name": "Geçici Sistem Dosyaları (Temp)",
            "description": "Windows ve programların bıraktığı kilitlenmemiş geçici çalışma dosyaları.",
            "default": True,
            "paths": [
                {"path": os.path.join(local_app_data, "Temp"), "clean_children_only": True},
                {"path": os.path.join(win_dir, "Temp"), "clean_children_only": True},
            ],
            "special": None
        },
        {
            "id": "android_base",
            "name": "Android & Emülatör Altyapısı",
            "description": "Android SDK, derleyici emülatör dosyaları, Gradle önbelleği ve emülatör kalıntıları.",
            "default": True,
            "paths": [
                {"path": os.path.join(local_app_data, "Android"), "clean_children_only": False},
                {"path": os.path.join(USER_PROFILE, ".android"), "clean_children_only": False},
                {"path": os.path.join(USER_PROFILE, ".gradle"), "clean_children_only": False},
                {"path": os.path.join(local_app_data, "Google", "AndroidStudio*"), "clean_children_only": False, "is_glob": True},
                {"path": os.path.join(app_data, "Google", "AndroidStudio*"), "clean_children_only": False, "is_glob": True},
                {"path": os.path.join(USER_PROFILE, ".MUMUVMM"), "clean_children_only": False},
                {"path": os.path.join(USER_PROFILE, "Nox_share"), "clean_children_only": False},
            ],
            "special": None
        },
        {
            "id": "dev_caches",
            "name": "Geliştirici & Paket Önbellekleri",
            "description": "Python pip, Node.js npm ve pnpm paket yöneticisi indirme önbellekleri.",
            "default": True,
            "paths": [
                {"path": os.path.join(local_app_data, "pip", "cache"), "clean_children_only": True},
                {"path": os.path.join(app_data, "npm-cache"), "clean_children_only": True},
                {"path": os.path.join(USER_PROFILE, ".pnpm-cache"), "clean_children_only": True},
                {"path": os.path.join(USER_PROFILE, ".cache"), "clean_children_only": True},
            ],
            "special": None
        },
        {
            "id": "crash_dumps",
            "name": "Çökme & Hata Raporları (Crash Dumps)",
            "description": "Kilitlenen programların bıraktığı hata döküm (.dmp) ve WER logları.",
            "default": True,
            "paths": [
                {"path": os.path.join(local_app_data, "CrashDumps"), "clean_children_only": True},
                {"path": os.path.join(local_app_data, "Microsoft", "Windows", "WER"), "clean_children_only": True},
            ],
            "special": None
        },
        {
            "id": "recycle_bin",
            "name": "Geri Dönüşüm Kutusu (Recycle Bin)",
            "description": "Masaüstü çöp kutusunda bekleyen ve diskte yer tutan silinmiş öğeler.",
            "default": True,
            "paths": [],
            "special": "recycle_bin"
        },
        {
            "id": "browser_cache",
            "name": "Tarayıcı Web Önbelleği (Sadece Cache)",
            "description": "Chrome ve Edge önbelleği. Şifreler, yer imleri ve geçmiş ASLA silinmez.",
            "default": False,
            "paths": [
                {"path": os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "Cache"), "clean_children_only": True},
                {"path": os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "Code Cache"), "clean_children_only": True},
                {"path": os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "Cache"), "clean_children_only": True},
                {"path": os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "Code Cache"), "clean_children_only": True},
            ],
            "special": None
        },
        {
            "id": "win_update_cache",
            "name": "Windows Güncelleme İndirme Önbelleği",
            "description": "Tamamlanmış Windows güncellemelerinden kalan eski indirme paketleri.",
            "default": False,
            "paths": [
                {"path": os.path.join(win_dir, "SoftwareDistribution", "Download"), "clean_children_only": True},
            ],
            "special": None
        }
    ]


class CleanerEngine:
    def __init__(self):
        self.categories = get_categories_definition()

    def scan_all(self, progress_callback: Optional[Callable[[str, float], None]] = None) -> Dict[str, int]:
        """
        Tüm kategorileri tarar ve her birinin kapladığı boyutu (bayt cinsinden) döner.
        """
        results = {}
        total_cats = len(self.categories)

        for index, cat in enumerate(self.categories):
            cat_id = cat["id"]
            cat_name = cat["name"]
            if progress_callback:
                progress_callback(f"Taranıyor: {cat_name}...", (index / total_cats))

            cat_size = 0
            if cat.get("special") == "recycle_bin":
                cat_size = self._get_recycle_bin_size()
            else:
                for item in cat.get("paths", []):
                    raw_path = item["path"]
                    if item.get("is_glob"):
                        for matched in glob.glob(raw_path):
                            if os.path.exists(matched) and is_path_safe(matched):
                                cat_size += calculate_folder_size(matched)
                    else:
                        if os.path.exists(raw_path) and is_path_safe(raw_path):
                            cat_size += calculate_folder_size(raw_path)

            results[cat_id] = cat_size

        if progress_callback:
            progress_callback("Tarama tamamlandı.", 1.0)

        return results

    def clean_selected(
        self,
        selected_cat_ids: List[str],
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Tuple[int, int]:
        """
        Seçili kategorileri temizler.
        Döner: (toplam_silinen_bayt, toplam_silinen_dosya_sayisi)
        """
        total_freed_bytes = 0
        total_deleted_files = 0
        selected_cats = [c for c in self.categories if c["id"] in selected_cat_ids]
        num_cats = len(selected_cats)

        if num_cats == 0:
            return 0, 0

        for index, cat in enumerate(selected_cats):
            cat_name = cat["name"]
            if log_callback:
                log_callback(f"[+] Başlatılıyor: {cat_name}")

            if cat.get("special") == "recycle_bin":
                freed, count = self._empty_recycle_bin(log_callback)
                total_freed_bytes += freed
                total_deleted_files += count
            else:
                for item in cat.get("paths", []):
                    raw_path = item["path"]
                    clean_children_only = item.get("clean_children_only", False)

                    if item.get("is_glob"):
                        for matched in glob.glob(raw_path):
                            if os.path.exists(matched) and is_path_safe(matched):
                                freed, count = self._clean_path(matched, clean_children_only, log_callback)
                                total_freed_bytes += freed
                                total_deleted_files += count
                    else:
                        if os.path.exists(raw_path) and is_path_safe(raw_path):
                            freed, count = self._clean_path(raw_path, clean_children_only, log_callback)
                            total_freed_bytes += freed
                            total_deleted_files += count

            if progress_callback:
                progress_callback((index + 1) / num_cats)

        if log_callback:
            log_callback(f"[✓] Temizlik tamamlandı! {total_deleted_files} dosya silindi.")

        return total_freed_bytes, total_deleted_files

    def _clean_path(
        self,
        target_path: str,
        children_only: bool,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[int, int]:
        """
        Güvenli bir şekilde hedef yolu temizler.
        Kilitli veya yetki gerektiren dosyaları çökmeksizin atlar.
        """
        if not is_path_safe(target_path):
            if log_callback:
                log_callback(f"[!] Güvenlik engeli: '{target_path}' korunan bir sistem alanıdır, atlandı.")
            return 0, 0

        freed_bytes = 0
        deleted_count = 0

        if not os.path.exists(target_path):
            return 0, 0

        if os.path.isfile(target_path):
            try:
                size = os.path.getsize(target_path)
                os.remove(target_path)
                freed_bytes += size
                deleted_count += 1
            except (PermissionError, OSError):
                pass
            return freed_bytes, deleted_count

        # Dizin temizliği
        if children_only:
            try:
                with os.scandir(target_path) as it:
                    for entry in it:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                size = entry.stat(follow_symlinks=False).st_size
                                os.remove(entry.path)
                                freed_bytes += size
                                deleted_count += 1
                            elif entry.is_dir(follow_symlinks=False):
                                sub_freed, sub_count = self._clean_path(entry.path, False, None)
                                freed_bytes += sub_freed
                                deleted_count += sub_count
                        except (PermissionError, OSError):
                            continue
            except (PermissionError, OSError):
                pass
        else:
            # Klasörün kendisini ve altını sil
            try:
                size = calculate_folder_size(target_path)
                shutil.rmtree(target_path, ignore_errors=True)
                if not os.path.exists(target_path):
                    freed_bytes += size
                    deleted_count += 1
                    if log_callback:
                        log_callback(f"[-] Kaldırıldı: {os.path.basename(target_path)}")
            except (PermissionError, OSError):
                pass

        return freed_bytes, deleted_count

    def _get_recycle_bin_size(self) -> int:
        """Windows API üzerinden çöp kutusu boyutunu döner."""
        try:
            class SHQUERYRBINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("i64Size", ctypes.c_longlong),
                    ("i64NumItems", ctypes.c_longlong),
                ]

            rbinfo = SHQUERYRBINFO()
            rbinfo.cbSize = ctypes.sizeof(SHQUERYRBINFO)
            res = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rbinfo))
            if res == 0:
                return int(rbinfo.i64Size)
        except Exception:
            pass
        return 0

    def _empty_recycle_bin(self, log_callback: Optional[Callable[[str], None]] = None) -> Tuple[int, int]:
        """Windows SHEmptyRecycleBinW çağrısıyla güvenli çöp kutusu boşaltma."""
        initial_size = self._get_recycle_bin_size()
        try:
            # SHERB_NOCONFIRMATION (0x00000001) | SHERB_NOPROGRESSUI (0x00000002) | SHERB_NOSOUND (0x00000004)
            flags = 7
            res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
            if res == 0:
                if log_callback:
                    log_callback("[✓] Geri Dönüşüm Kutusu başarıyla boşaltıldı.")
                return initial_size, 1
        except Exception as e:
            if log_callback:
                log_callback(f"[!] Çöp kutusu boşaltılırken hata: {e}")
        return 0, 0
