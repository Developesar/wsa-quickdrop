from __future__ import annotations

import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from . import APP_NAME, APP_VERSION, DEFAULT_WSA_HOST, DEFAULT_WSA_PORT
from .adb import AdbDiscovery
from .android_folders import (
    ROOT_LABEL,
    AndroidFolder,
    build_child_folder_path,
    folder_sort_key,
    selected_folder_from_config,
)
from .config import AppConfig
from .routes import human_file_size
from .sendto import install_sendto
from .transfer import TransferOptions, TransferService
from .windows_drop import enable_file_drop


PERSIAN_OCR_PACKAGES = ["ir.persiandots.ocr.dev", "ir.persiandots.ocr"]


TEXT = {
    "en": {
        "tagline": "Send files to Windows Subsystem for Android",
        "connect": "Connect",
        "refresh": "Refresh folders",
        "create_folder": "Create folder",
        "drop": "Drop files here",
        "browse": "Browse files",
        "send": "Send",
        "clear": "Clear",
        "settings": "Settings",
        "help": "Help",
        "open_logs": "Open logs",
        "copy_log": "Copy log",
        "install_sendto": "Install SendTo",
        "connected": "Connected",
        "not_connected": "Not connected",
        "adb_missing": "ADB missing",
        "wsa_not_running": "WSA not running",
        "multiple_devices": "Multiple devices",
        "folder": "Destination folder",
        "advanced_path": "Android path",
    },
    "fa": {
        "tagline": "ارسال فایل به Windows Subsystem for Android",
        "connect": "اتصال به WSA",
        "refresh": "به‌روزرسانی پوشه‌ها",
        "create_folder": "ساخت پوشه",
        "drop": "فایل‌ها را اینجا رها کنید",
        "browse": "انتخاب فایل",
        "send": "ارسال فایل",
        "clear": "پاک کردن",
        "settings": "تنظیمات",
        "help": "راهنما",
        "open_logs": "گزارش‌ها",
        "copy_log": "کپی گزارش",
        "install_sendto": "نصب میانبر راست‌کلیک",
        "connected": "متصل",
        "not_connected": "متصل نیست",
        "adb_missing": "ADB پیدا نشد",
        "wsa_not_running": "WSA اجرا نیست",
        "multiple_devices": "چند دستگاه",
        "folder": "پوشه مقصد",
        "advanced_path": "مسیر اندروید",
    },
}


class QuickDropApp:
    def __init__(
        self,
        root: tk.Tk,
        config: AppConfig,
        initial_files: list[str] | None = None,
        from_sendto: bool = False,
    ) -> None:
        self.root = root
        self.config = config
        self.service = TransferService(config=config)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.files: list[Path] = []
        self.tree_items: dict[str, str] = {}
        self.folder_items: dict[str, str] = {}
        self.folder_by_item: dict[str, AndroidFolder] = {}
        self.selected_folder = selected_folder_from_config(
            config.lastSelectedAndroidFolder,
            config.lastSelectedFriendlyFolder,
            config.lastDestination,
        )

        self.language = tk.StringVar(value=config.language or "en")
        self.theme = tk.StringVar(value=config.theme or "system")
        self.auto_scan = tk.BooleanVar(value=config.autoMediaScan)
        self.open_after_send = tk.BooleanVar(value=config.openAfterSend or config.closeAfterSend)
        self.send_immediately = tk.BooleanVar(value=config.sendImmediatelyFromSendTo)
        self.show_advanced = tk.BooleanVar(value=config.showAdvancedPaths)
        self.adb_path = tk.StringVar(value=config.adbPath)
        self.endpoint = tk.StringVar(value=f"{config.wsaHost or DEFAULT_WSA_HOST}:{config.wsaPort or DEFAULT_WSA_PORT}")

        self._build()
        self._apply_theme()
        self._set_icon()
        self._populate_folders([self.selected_folder])
        self._refresh_queue()
        self._poll_events()
        if initial_files:
            self.add_files(initial_files)
        drop_enabled = enable_file_drop(self.root, self.add_files)
        self.log("Explorer drag and drop is enabled." if drop_enabled else "Use Browse files if drag and drop is unavailable.")
        self.refresh_adb_status()
        if from_sendto:
            self.log("Files opened from SendTo. Choose a folder, then click Send.")
            self.root.after(350, self.connect)
            if self.config.sendImmediatelyFromSendTo:
                self.root.after(1800, self.send)

    def text(self, key: str) -> str:
        return TEXT.get(self.language.get(), TEXT["en"]).get(key, TEXT["en"][key])

    def _build(self) -> None:
        self.root.title(APP_NAME)
        self.root.geometry(self.config.windowGeometry or "1080x720")
        self.root.minsize(920, 620)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Subtle.TLabel", font=("Segoe UI", 10))
        self.style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=(14, 8))

        header = ttk.Frame(self.root, padding=(16, 14, 16, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)
        self.icon_label = ttk.Label(header)
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        ttk.Label(header, text=APP_NAME, style="Header.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(header, text=self.text("tagline"), style="Subtle.TLabel").grid(row=1, column=1, sticky="w")
        self.status_badge = tk.Label(header, text=self.text("not_connected"), padx=14, pady=6, font=("Segoe UI", 10, "bold"))
        self.status_badge.grid(row=0, column=2, rowspan=2, padx=8)
        ttk.Button(header, text=self.text("connect"), command=self.connect, style="Big.TButton").grid(row=0, column=3, rowspan=2)

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 10))

        left = ttk.Frame(main, padding=(0, 0, 10, 0))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        main.add(left, weight=1)

        ttk.Label(left, text=ROOT_LABEL, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.folder_tree = ttk.Treeview(left, show="tree", selectmode="browse", height=18)
        self.folder_tree.grid(row=1, column=0, sticky="nsew")
        self.folder_tree.bind("<<TreeviewSelect>>", self._on_folder_selected)
        folder_scroll = ttk.Scrollbar(left, orient="vertical", command=self.folder_tree.yview)
        folder_scroll.grid(row=1, column=1, sticky="ns")
        self.folder_tree.configure(yscrollcommand=folder_scroll.set)
        folder_buttons = ttk.Frame(left)
        folder_buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)
        folder_buttons.columnconfigure(0, weight=1)
        folder_buttons.columnconfigure(1, weight=1)
        ttk.Button(folder_buttons, text=self.text("refresh"), command=self.refresh_folders).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(folder_buttons, text=self.text("create_folder"), command=self.create_folder).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.selected_label = ttk.Label(left, text="", style="Subtle.TLabel", wraplength=270)
        self.selected_label.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        self.advanced_label = ttk.Label(left, text="", style="Subtle.TLabel", wraplength=270)
        self.advanced_label.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(3, 0))

        right = ttk.Frame(main, padding=(10, 0, 0, 0))
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)
        main.add(right, weight=3)

        self.drop_zone = tk.Frame(right, bd=0, highlightthickness=2, highlightbackground="#4f8cff", bg="#eef5ff")
        self.drop_zone.grid(row=0, column=0, sticky="ew")
        self.drop_zone.columnconfigure(0, weight=1)
        self.drop_label = tk.Label(
            self.drop_zone,
            text=self.text("drop"),
            font=("Segoe UI", 18, "bold"),
            bg="#eef5ff",
            fg="#18324f",
            pady=30,
        )
        self.drop_label.grid(row=0, column=0, sticky="ew")
        ttk.Button(right, text=self.text("browse"), command=self.browse_files).grid(row=1, column=0, sticky="w", pady=10)

        queue_frame = ttk.Frame(right)
        queue_frame.grid(row=2, column=0, sticky="nsew")
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        columns = ("name", "size", "destination", "status")
        self.queue = ttk.Treeview(queue_frame, columns=columns, show="headings", height=12)
        for column, heading, width in (
            ("name", "File", 260),
            ("size", "Size", 90),
            ("destination", "Destination", 280),
            ("status", "Status", 120),
        ):
            self.queue.heading(column, text=heading)
            self.queue.column(column, width=width, anchor="w")
        self.queue.grid(row=0, column=0, sticky="nsew")
        queue_scroll = ttk.Scrollbar(queue_frame, orient="vertical", command=self.queue.yview)
        queue_scroll.grid(row=0, column=1, sticky="ns")
        self.queue.configure(yscrollcommand=queue_scroll.set)

        send_row = ttk.Frame(right)
        send_row.grid(row=3, column=0, sticky="ew", pady=10)
        send_row.columnconfigure(0, weight=1)
        send_row.columnconfigure(1, weight=1)
        ttk.Button(send_row, text=self.text("send"), command=self.send, style="Big.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(send_row, text=self.text("clear"), command=self.clear, style="Big.TButton").grid(row=0, column=1, sticky="ew", padx=(6, 0))

        bottom = ttk.Frame(self.root, padding=(14, 0, 14, 12))
        bottom.grid(row=2, column=0, sticky="nsew")
        bottom.columnconfigure(0, weight=1)
        self.log_text = tk.Text(bottom, height=5, wrap="word", font=("Consolas", 9), bd=0)
        self.log_text.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        buttons = ttk.Frame(bottom)
        buttons.grid(row=1, column=0, sticky="ew")
        for index in range(6):
            buttons.columnconfigure(index, weight=1)
        ttk.Button(buttons, text=self.text("install_sendto"), command=self.install_sendto).grid(row=0, column=0, sticky="ew", padx=3)
        ttk.Button(buttons, text=self.text("settings"), command=self.open_settings).grid(row=0, column=1, sticky="ew", padx=3)
        ttk.Button(buttons, text=self.text("help"), command=self.open_help).grid(row=0, column=2, sticky="ew", padx=3)
        ttk.Button(buttons, text=self.text("open_logs"), command=self.open_log_folder).grid(row=0, column=3, sticky="ew", padx=3)
        ttk.Button(buttons, text=self.text("copy_log"), command=self.copy_log).grid(row=0, column=4, sticky="ew", padx=3)
        ttk.Button(buttons, text="Open WSA Settings", command=self.open_wsa_settings).grid(row=0, column=5, sticky="ew", padx=3)

    def _set_icon(self) -> None:
        icon_dir = self.app_root() / "assets" / "icon"
        ico = icon_dir / "wsa-quickdrop.ico"
        png = icon_dir / "wsa-quickdrop.png"
        try:
            if ico.exists():
                self.root.iconbitmap(str(ico))
        except tk.TclError:
            pass
        try:
            if png.exists():
                self.icon_image = tk.PhotoImage(file=str(png))
                self.root.iconphoto(True, self.icon_image)
                small = self.icon_image.subsample(max(1, self.icon_image.width() // 48), max(1, self.icon_image.height() // 48))
                self.header_icon = small
                self.icon_label.configure(image=self.header_icon)
        except tk.TclError:
            self.icon_label.configure(text="WSA", font=("Segoe UI", 16, "bold"))

    def _apply_theme(self) -> None:
        dark = self.theme.get() == "dark"
        bg = "#111827" if dark else "#f6f8fb"
        panel = "#1f2937" if dark else "#ffffff"
        text = "#e5e7eb" if dark else "#162033"
        self.root.configure(bg=bg)
        self.drop_zone.configure(bg="#172554" if dark else "#eef5ff", highlightbackground="#73a5ff")
        self.drop_label.configure(bg="#172554" if dark else "#eef5ff", fg="#e5f0ff" if dark else "#18324f")
        self.log_text.configure(bg="#0b1220" if dark else "#ffffff", fg=text, insertbackground=text)
        self.style.configure(".", background=bg, foreground=text, fieldbackground=panel)
        self.style.configure("Treeview", rowheight=28, fieldbackground=panel, background=panel, foreground=text)
        self.style.map("Treeview", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])

    def refresh_adb_status(self) -> None:
        path = AdbDiscovery().find_adb(self.adb_path.get())
        if path:
            self.adb_path.set(str(path))
            self._set_status(self.text("not_connected"), "neutral")
        else:
            self._set_status(self.text("adb_missing"), "error")

    def _set_status(self, text: str, kind: str) -> None:
        colors = {
            "ok": ("#dcfce7", "#166534"),
            "warn": ("#fef3c7", "#92400e"),
            "error": ("#fee2e2", "#991b1b"),
            "neutral": ("#e5e7eb", "#374151"),
        }
        bg, fg = colors.get(kind, colors["neutral"])
        self.status_badge.configure(text=text, bg=bg, fg=fg)

    def _populate_folders(self, folders: list[AndroidFolder]) -> None:
        if all(folder.android_path != self.selected_folder.android_path for folder in folders):
            folders = [*folders, self.selected_folder]
        self.folder_tree.delete(*self.folder_tree.get_children())
        self.folder_items.clear()
        self.folder_by_item.clear()
        root_id = self.folder_tree.insert("", "end", text=ROOT_LABEL, open=True)
        self.folder_items[ROOT_LABEL] = root_id
        for folder in sorted(folders, key=folder_sort_key):
            self._insert_folder(root_id, folder)
        self._select_folder(self.selected_folder.android_path)
        self._update_selected_label()

    def _insert_folder(self, root_id: str, folder: AndroidFolder) -> None:
        parent = root_id
        current = ""
        parts = folder.friendly_path.split("/")
        for index, part in enumerate(parts):
            current = part if not current else f"{current}/{part}"
            item = self.folder_items.get(current)
            if item is None:
                android_path = "/sdcard/" + current
                item = self.folder_tree.insert(parent, "end", text=part, open=index == 0)
                self.folder_items[current] = item
                self.folder_by_item[item] = AndroidFolder(current, android_path, depth=index + 1)
            parent = item
        self.folder_by_item[parent] = folder

    def _select_folder(self, android_path: str) -> None:
        for item, folder in self.folder_by_item.items():
            if folder.android_path == android_path:
                self.folder_tree.selection_set(item)
                self.folder_tree.see(item)
                self.selected_folder = folder
                return

    def _on_folder_selected(self, _event=None) -> None:
        selection = self.folder_tree.selection()
        if not selection:
            return
        folder = self.folder_by_item.get(selection[0])
        if not folder:
            return
        self.selected_folder = folder
        self._update_selected_label()
        self._refresh_queue()
        self.save_config()

    def _update_selected_label(self) -> None:
        self.selected_label.configure(text=f"{self.text('folder')}: {ROOT_LABEL} > {self.selected_folder.friendly_path}")
        if self.show_advanced.get():
            self.advanced_label.configure(text=f"{self.text('advanced_path')}: {self.selected_folder.android_path}")
        else:
            self.advanced_label.configure(text="")

    def refresh_folders(self) -> None:
        self.save_config()
        self.log("Refreshing Android folders.")
        threading.Thread(target=self._refresh_folders_worker, daemon=True).start()

    def _refresh_folders_worker(self) -> None:
        folders, messages = self.service.list_folders(self.options())
        self.events.put(("folders", (folders, messages)))

    def create_folder(self) -> None:
        name = simpledialog.askstring(APP_NAME, "Folder name", parent=self.root)
        if name is None:
            return
        self.log(f"Creating folder under {self.selected_folder.friendly_path}.")
        threading.Thread(target=self._create_folder_worker, args=(name,), daemon=True).start()

    def _create_folder_worker(self, name: str) -> None:
        folder, messages = self.service.create_folder(self.selected_folder.android_path, name, self.options())
        self.events.put(("created_folder", (folder, messages)))

    def add_files(self, files: list[str]) -> None:
        count = 0
        for raw in files:
            path = Path(raw)
            if path.is_file() and path not in self.files:
                self.files.append(path)
                count += 1
        self._refresh_queue()
        if count:
            self.log(f"Queued {count} file(s) for {self.selected_folder.friendly_path}.")

    def browse_files(self) -> None:
        selected = filedialog.askopenfilenames(title="Select files for WSA QuickDrop")
        if selected:
            self.add_files(list(selected))

    def _refresh_queue(self) -> None:
        self.queue.delete(*self.queue.get_children())
        self.tree_items.clear()
        for path in self.files:
            try:
                size = human_file_size(path.stat().st_size)
            except OSError:
                size = "?"
            item_id = self.queue.insert("", "end", values=(path.name, size, self.selected_folder.friendly_path, "queued"))
            self.tree_items[str(path)] = item_id

    def options(self) -> TransferOptions:
        host = DEFAULT_WSA_HOST
        port = DEFAULT_WSA_PORT
        if ":" in self.endpoint.get():
            host_text, port_text = self.endpoint.get().rsplit(":", 1)
            host = host_text or DEFAULT_WSA_HOST
            try:
                port = int(port_text)
            except ValueError:
                port = DEFAULT_WSA_PORT
        return TransferOptions(
            android_folder=self.selected_folder.android_path,
            adb_path=self.adb_path.get(),
            host=host,
            port=port,
            scan=self.auto_scan.get(),
            verbose=True,
        )

    def save_config(self) -> None:
        options = self.options()
        self.config.adbPath = self.adb_path.get()
        self.config.lastSelectedAndroidFolder = self.selected_folder.android_path
        self.config.lastSelectedFriendlyFolder = self.selected_folder.friendly_path
        self.config.autoMediaScan = self.auto_scan.get()
        self.config.openAfterSend = self.open_after_send.get()
        self.config.closeAfterSend = self.open_after_send.get()
        self.config.sendImmediatelyFromSendTo = self.send_immediately.get()
        self.config.showAdvancedPaths = self.show_advanced.get()
        self.config.theme = self.theme.get()
        self.config.language = self.language.get()
        self.config.windowGeometry = self.root.geometry()
        self.config.wsaHost = options.host
        self.config.wsaPort = options.port
        self.config.save()

    def send(self) -> None:
        if not self.files:
            messagebox.showinfo(APP_NAME, "Choose one or more files first.")
            return
        self.save_config()
        files = [str(path) for path in self.files]
        self.log(f"Sending {len(files)} file(s) to {ROOT_LABEL} > {self.selected_folder.friendly_path}.")
        threading.Thread(target=self._send_worker, args=(files, self.options()), daemon=True).start()

    def _send_worker(self, files: list[str], options: TransferOptions) -> None:
        summary = self.service.send_files(files, options, callback=lambda item: self.events.put(("item", item)))
        self.events.put(("summary", summary))

    def connect(self) -> None:
        self.save_config()
        self.log("Connecting to WSA.")
        threading.Thread(target=self._connect_worker, daemon=True).start()

    def _connect_worker(self) -> None:
        client, device, messages = self.service.ensure_connection(self.options())
        self.events.put(("connect", (client, device, messages)))
        if device and device.state == "device":
            folders, folder_messages = self.service.list_folders(self.options())
            self.events.put(("folders", (folders, folder_messages)))

    def _poll_events(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "item":
                    self._update_item(payload)
                elif kind == "summary":
                    self._handle_summary(payload)
                elif kind == "connect":
                    _client, device, messages = payload
                    self._handle_connect(device, messages)
                elif kind == "folders":
                    folders, messages = payload
                    self._populate_folders(folders)
                    for message in messages:
                        self.log(message)
                elif kind == "created_folder":
                    folder, messages = payload
                    for message in messages:
                        self.log(message)
                    if folder:
                        self.selected_folder = folder
                        self.refresh_folders()
        except queue.Empty:
            pass
        self.root.after(120, self._poll_events)

    def _handle_connect(self, device, messages: list[str]) -> None:
        for message in messages:
            self.log(message)
        if not self.adb_path.get():
            self._set_status(self.text("adb_missing"), "error")
        elif device is None:
            self._set_status(self.text("wsa_not_running"), "warn")
        elif device.state == "device":
            self._set_status(self.text("connected"), "ok")
        elif device.state in {"offline", "unauthorized"}:
            self._set_status(device.state, "warn")
        else:
            self._set_status(self.text("not_connected"), "warn")

    def _update_item(self, item) -> None:
        tree_id = self.tree_items.get(str(Path(item.local_path)))
        if tree_id:
            values = list(self.queue.item(tree_id, "values"))
            values[2] = self.selected_folder.friendly_path
            values[3] = item.status
            self.queue.item(tree_id, values=values)
        message = item.message
        if item.status == "scanned":
            message += f" If it is not visible immediately, open {ROOT_LABEL} > {self.selected_folder.friendly_path}."
        self.log(f"{item.status}: {Path(item.local_path).name} {message}")

    def _handle_summary(self, summary) -> None:
        for message in summary.messages:
            self.log(message)
        if summary.ok:
            self.log("All files sent.")
            if self.open_after_send.get():
                self.open_log_folder()
        else:
            self.log("Some files failed. See messages above.")

    def clear(self) -> None:
        self.files.clear()
        self._refresh_queue()
        self.log("Queue cleared.")

    def install_sendto(self) -> None:
        try:
            path = install_sendto()
            self.log(f"Installed SendTo launcher: {path}")
            messagebox.showinfo(APP_NAME, f"Installed:\n{path}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def open_settings(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("WSA QuickDrop Settings")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.columnconfigure(1, weight=1)
        pad = {"padx": 10, "pady": 6}
        ttk.Label(dialog, text="ADB path").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(dialog, textvariable=self.adb_path, width=54).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(dialog, text="Browse", command=self.browse_adb).grid(row=0, column=2, **pad)
        ttk.Label(dialog, text="WSA endpoint").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(dialog, textvariable=self.endpoint).grid(row=1, column=1, columnspan=2, sticky="ew", **pad)
        ttk.Label(dialog, text="Language").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(dialog, textvariable=self.language, values=["en", "fa"], state="readonly").grid(row=2, column=1, sticky="w", **pad)
        ttk.Label(dialog, text="Theme").grid(row=3, column=0, sticky="w", **pad)
        ttk.Combobox(dialog, textvariable=self.theme, values=["system", "light", "dark"], state="readonly").grid(row=3, column=1, sticky="w", **pad)
        ttk.Checkbutton(dialog, text="Auto media scan", variable=self.auto_scan).grid(row=4, column=0, columnspan=3, sticky="w", **pad)
        ttk.Checkbutton(dialog, text="Open log folder after send", variable=self.open_after_send).grid(row=5, column=0, columnspan=3, sticky="w", **pad)
        ttk.Checkbutton(dialog, text="Send immediately when opened from SendTo", variable=self.send_immediately).grid(
            row=6, column=0, columnspan=3, sticky="w", **pad
        )
        ttk.Checkbutton(dialog, text="Show advanced Android path", variable=self.show_advanced, command=self._update_selected_label).grid(
            row=7, column=0, columnspan=3, sticky="w", **pad
        )

        def save_and_close() -> None:
            self.save_config()
            self._apply_theme()
            self._update_selected_label()
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save_and_close).grid(row=8, column=1, sticky="e", **pad)

    def browse_adb(self) -> None:
        selected = filedialog.askopenfilename(title="Select adb.exe", filetypes=[("ADB", "adb.exe"), ("Executable", "*.exe")])
        if selected:
            self.adb_path.set(selected)
            self.save_config()
            self.refresh_adb_status()

    def open_help(self) -> None:
        doc = self.app_root() / "docs" / ("USER_GUIDE_FA.md" if self.language.get() == "fa" else "USER_GUIDE_EN.md")
        os.startfile(doc)

    def open_log_folder(self) -> None:
        os.startfile(self.service.logger.base_dir)

    def open_wsa_settings(self) -> None:
        for uri in ("wsa-settings:", "ms-wsa-settings:"):
            try:
                os.startfile(uri)
                self.log(f"Opened {uri}")
                return
            except OSError:
                continue
        messagebox.showinfo(APP_NAME, "Open Windows Subsystem for Android settings and enable Developer Mode.")

    def copy_log(self) -> None:
        text = self.log_text.get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log("Copied log text.")

    def copy_persian_ocr_instructions(self) -> None:
        text = f"Open Persian OCR Offline > Select Image > {ROOT_LABEL} > {self.selected_folder.friendly_path}"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log("Copied Persian OCR Offline test instructions.")

    def log(self, message: str) -> None:
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    @staticmethod
    def app_root() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parents[2]


def run_gui(config: AppConfig | None = None, initial_files: list[str] | None = None, from_sendto: bool = False) -> None:
    root = tk.Tk()
    app = QuickDropApp(root, config or AppConfig.load(), initial_files=initial_files, from_sendto=from_sendto)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_config(), root.destroy()))
    root.mainloop()
