import os
import sys
import threading
import time
import customtkinter as ctk
from typing import Dict

# cleaner_core modülünü içe aktar
from cleaner_core import CleanerEngine, get_disk_info

# --- TEMA & RENK PALETİ ---
COLOR_BG = "#121316"           # Derin koyu arka plan
COLOR_SURFACE = "#1c1d22"      # Kart ve panel yüzeyi
COLOR_SURFACE_HOVER = "#24252b"
COLOR_CARD_BORDER = "#2b2d35"  # İnce sınır çizgisi
COLOR_ACCENT = "#10a37f"       # Zümrüt Yeşili (Primary)
COLOR_ACCENT_HOVER = "#158c6e" # Vurgu hover
COLOR_ACCENT_MUTED = "#0e4a3b"
COLOR_TEXT_PRIMARY = "#f4f4f5" # Ana metin
COLOR_TEXT_MUTED = "#9496a1"   # İkincil soluk metin
COLOR_DANGER = "#ef4444"       # Uyarı / Hata
COLOR_CONSOLE_BG = "#0d0e11"   # Konsol arka planı

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


def format_bytes(size_bytes: int) -> str:
    """Bayt miktarını insan tarafından okunabilir birime çevirir."""
    if size_bytes <= 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


class PureDiskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PureDisk — Akıllı & Güvenli Sistem Temizleyici")
        self.geometry("980x740")
        self.minsize(860, 640)
        self.configure(fg_color=COLOR_BG)

        self.engine = CleanerEngine()
        self.scan_results: Dict[str, int] = {}
        self.category_widgets: Dict[str, dict] = {}
        self.is_busy = False

        self._build_ui()
        self._refresh_disk_info()

        # Açılışta otomatik taramayı arka planda başlat
        self.after(500, self.start_scan)

    def _build_ui(self):
        # 1. ÜST BAŞLIK & HEADER
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 12))

        # Sol taraf: Logo & Başlık
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=16)

        app_badge = ctk.CTkLabel(
            title_box,
            text=" P ",
            fg_color=COLOR_ACCENT,
            text_color="#ffffff",
            font=ctk.CTkFont(size=18, weight="bold"),
            corner_radius=8,
            width=36,
            height=36
        )
        app_badge.pack(side="left", padx=(0, 14))

        titles_sub = ctk.CTkFrame(title_box, fg_color="transparent")
        titles_sub.pack(side="left")

        app_title = ctk.CTkLabel(
            titles_sub,
            text="PureDisk",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        app_title.pack(anchor="w")

        app_subtitle = ctk.CTkLabel(
            titles_sub,
            text="Güvenli Sistem & Disk Temizleyici  •  Windows Korumalı Mod",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        app_subtitle.pack(anchor="w")

        # Sağ taraf: Hızlı Aksiyon Butonları
        btn_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_box.pack(side="right", padx=20, pady=16)

        self.btn_scan = ctk.CTkButton(
            btn_box,
            text="🔍  Sistemi Tara",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#272830",
            hover_color=COLOR_SURFACE_HOVER,
            text_color=COLOR_TEXT_PRIMARY,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            corner_radius=8,
            height=38,
            command=self.start_scan
        )
        self.btn_scan.pack(side="left", padx=(0, 10))

        self.btn_clean = ctk.CTkButton(
            btn_box,
            text="⚡  Güvenli Temizle",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#ffffff",
            corner_radius=8,
            height=38,
            command=self.start_clean
        )
        self.btn_clean.pack(side="left")

        # 2. DİSK DURUM KARTI (C: Sürücüsü)
        self.disk_card = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        self.disk_card.pack(fill="x", padx=20, pady=(0, 12))

        disk_header = ctk.CTkFrame(self.disk_card, fg_color="transparent")
        disk_header.pack(fill="x", padx=20, pady=(14, 8))

        self.lbl_disk_name = ctk.CTkLabel(
            disk_header,
            text="💾  Yerel Disk (C:)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.lbl_disk_name.pack(side="left")

        self.lbl_disk_status = ctk.CTkLabel(
            disk_header,
            text="Hesaplanıyor...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.lbl_disk_status.pack(side="right")

        self.disk_progress = ctk.CTkProgressBar(
            self.disk_card,
            fg_color="#272830",
            progress_color=COLOR_ACCENT,
            height=8,
            corner_radius=4
        )
        self.disk_progress.pack(fill="x", padx=20, pady=(0, 14))

        # 3. KATEGORİ LİSTESİ & SEÇİM ALANI
        list_header = ctk.CTkFrame(self, fg_color="transparent")
        list_header.pack(fill="x", padx=24, pady=(4, 6))

        ctk.CTkLabel(
            list_header,
            text="Temizleme Kategorileri",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(side="left")

        # Tümünü Seç / Temizle Butonları
        toggle_box = ctk.CTkFrame(list_header, fg_color="transparent")
        toggle_box.pack(side="right")

        btn_select_all = ctk.CTkButton(
            toggle_box,
            text="Tümünü Seç",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=COLOR_SURFACE,
            text_color=COLOR_ACCENT,
            width=70,
            height=24,
            command=self._select_all
        )
        btn_select_all.pack(side="left", padx=4)

        btn_deselect_all = ctk.CTkButton(
            toggle_box,
            text="Kaldır",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=COLOR_SURFACE,
            text_color=COLOR_TEXT_MUTED,
            width=50,
            height=24,
            command=self._deselect_all
        )
        btn_deselect_all.pack(side="left")

        # Kaydırılabilir Kategori Paneli
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        self._populate_category_cards()

        # 4. ALT DURUM & İLERLEME ÇUBUĞU
        self.status_bar = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=10, border_width=1, border_color=COLOR_CARD_BORDER)
        self.status_bar.pack(fill="x", padx=20, pady=(0, 16))

        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="Hazır. Taramayı veya temizliği başlatabilirsiniz.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED
        )
        self.lbl_status.pack(side="left", padx=16, pady=10)

        self.clean_progress = ctk.CTkProgressBar(
            self.status_bar,
            fg_color="#272830",
            progress_color=COLOR_ACCENT,
            width=180,
            height=6,
            corner_radius=3
        )
        self.clean_progress.pack(side="right", padx=16, pady=10)
        self.clean_progress.set(0)

    def _populate_category_cards(self):
        for cat in self.engine.categories:
            cat_id = cat["id"]

            card = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=COLOR_SURFACE,
                corner_radius=10,
                border_width=1,
                border_color=COLOR_CARD_BORDER
            )
            card.pack(fill="x", pady=5)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)

            var = ctk.BooleanVar(value=cat.get("default", True))

            switch = ctk.CTkCheckBox(
                inner,
                text="",
                variable=var,
                width=24,
                checkbox_width=20,
                checkbox_height=20,
                border_width=2,
                corner_radius=5,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_HOVER,
                border_color="#3d404d"
            )
            switch.pack(side="left", padx=(0, 12))

            info_box = ctk.CTkFrame(inner, fg_color="transparent")
            info_box.pack(side="left", fill="both", expand=True)

            title_row = ctk.CTkFrame(info_box, fg_color="transparent")
            title_row.pack(fill="x")

            lbl_name = ctk.CTkLabel(
                title_row,
                text=cat["name"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLOR_TEXT_PRIMARY
            )
            lbl_name.pack(side="left")

            lbl_desc = ctk.CTkLabel(
                info_box,
                text=cat["description"],
                font=ctk.CTkFont(size=12),
                text_color=COLOR_TEXT_MUTED,
                anchor="w",
                justify="left"
            )
            lbl_desc.pack(fill="x", pady=(2, 0))

            lbl_size = ctk.CTkLabel(
                inner,
                text="Taranmadı",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLOR_TEXT_MUTED,
                fg_color="#24262e",
                corner_radius=6,
                width=80,
                height=28
            )
            lbl_size.pack(side="right", padx=(10, 0))

            self.category_widgets[cat_id] = {
                "var": var,
                "lbl_size": lbl_size,
                "card": card
            }

    def _select_all(self):
        for w in self.category_widgets.values():
            w["var"].set(True)

    def _deselect_all(self):
        for w in self.category_widgets.values():
            w["var"].set(False)

    def _refresh_disk_info(self):
        total_gb, used_gb, free_gb, percent = get_disk_info("C:\\")
        self.disk_progress.set(percent / 100)
        self.lbl_disk_status.configure(
            text=f"{free_gb:.1f} GB Boş  /  {total_gb:.1f} GB Toplam  (%{percent:.0f} Dolu)"
        )

    def start_scan(self):
        if self.is_busy:
            return
        self.is_busy = True
        self.btn_scan.configure(state="disabled")
        self.btn_clean.configure(state="disabled")
        self.lbl_status.configure(text="Sistem taranıyor, gereksiz dosyalar hesaplanıyor...")
        self.clean_progress.set(0)

        def worker():
            def on_progress(msg: str, frac: float):
                self.after(0, lambda: self.lbl_status.configure(text=msg))
                self.after(0, lambda: self.clean_progress.set(frac))

            results = self.engine.scan_all(progress_callback=on_progress)
            self.after(0, lambda: self._on_scan_completed(results))

        threading.Thread(target=worker, daemon=True).start()

    def _on_scan_completed(self, results: Dict[str, int]):
        self.scan_results = results
        total_cleanable = sum(results.values())

        for cat_id, size in results.items():
            if cat_id in self.category_widgets:
                w = self.category_widgets[cat_id]["lbl_size"]
                formatted = format_bytes(size)
                w.configure(text=formatted)
                if size > 0:
                    w.configure(text_color=COLOR_ACCENT, fg_color=COLOR_ACCENT_MUTED)
                else:
                    w.configure(text_color=COLOR_TEXT_MUTED, fg_color="#24262e")

        self.lbl_status.configure(
            text=f"Tarama bitti! Toplam temizlenebilir alan: {format_bytes(total_cleanable)}"
        )
        self.clean_progress.set(1.0)
        self.btn_scan.configure(state="normal")
        self.btn_clean.configure(state="normal")
        self.is_busy = False

    def start_clean(self):
        if self.is_busy:
            return

        selected_ids = [
            cat_id for cat_id, w in self.category_widgets.items() if w["var"].get()
        ]

        if not selected_ids:
            self.lbl_status.configure(text="Lütfen temizlemek için en az bir kategori seçin.")
            return

        self.is_busy = True
        self.btn_scan.configure(state="disabled")
        self.btn_clean.configure(state="disabled")
        self.clean_progress.set(0)

        def worker():
            def log_msg(msg: str):
                self.after(0, lambda: self.lbl_status.configure(text=msg))

            def on_progress(frac: float):
                self.after(0, lambda: self.clean_progress.set(frac))

            freed_bytes, count = self.engine.clean_selected(
                selected_ids,
                log_callback=log_msg,
                progress_callback=on_progress
            )
            self.after(0, lambda: self._on_clean_completed(freed_bytes, count))

        threading.Thread(target=worker, daemon=True).start()

    def _on_clean_completed(self, freed_bytes: int, count: int):
        self._refresh_disk_info()
        formatted = format_bytes(freed_bytes)

        self.lbl_status.configure(
            text=f"✓ Temizlik tamamlandı! {formatted} alan kazanıldı ({count} dosya temizlendi)."
        )
        self.clean_progress.set(1.0)
        self.btn_scan.configure(state="normal")
        self.btn_clean.configure(state="normal")
        self.is_busy = False

        # Sonuçları güncellemek için hızlı bir tarama tetikle
        self.after(1000, self.start_scan)


if __name__ == "__main__":
    app = PureDiskApp()
    app.mainloop()
