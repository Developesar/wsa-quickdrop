from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import APP_NAME, APP_VERSION, DEFAULT_WSA_HOST, DEFAULT_WSA_PORT
from .adb import AdbDiscovery
from .config import AppConfig
from .routes import DestinationMode, human_file_size, route_for_file
from .sendto import install_sendto, uninstall_sendto
from .transfer import TransferOptions, TransferService
from .windows_drop import enable_file_drop


PERSIAN_OCR_PACKAGES = ["ir.persiandots.ocr.dev", "ir.persiandots.ocr"]


TEXT = {
    "en": {
        "drop": "Drop files here",
        "browse": "Browse Files",
        "send": "Send to WSA",
        "clear": "Clear",
        "connect": "Connect",
        "retry": "Retry",
        "install_sendto": "Install SendTo",
        "uninstall_sendto": "Uninstall SendTo",
        "copy_adb": "Copy ADB command",
        "open_help": "Open Help",
        "open_logs": "Open Log Folder",
        "copy_log": "Copy Log",
        "browse_adb": "Browse adb.exe",
        "custom_path": "Custom Android path",
        "open_wsa": "Open WSA Settings",
    },
    "fa": {
        "drop": "فایل‌ها را اینجا رها کنید",
        "browse": "انتخاب فایل",
        "send": "ارسال به WSA",
        "clear": "پاک کردن",
        "connect": "اتصال",
        "retry": "تلاش دوباره",
        "install_sendto": "نصب SendTo",
        "uninstall_sendto": "حذف SendTo",
        "copy_adb": "کپی دستور ADB",
        "open_help": "راهنما",
        "open_logs": "پوشه گزارش‌ها",
        "copy_log": "کپی گزارش",
        "browse_adb": "انتخاب adb.exe",
        "custom_path": "مسیر سفارشی اندروید",
        "open_wsa": "تنظیمات WSA",
    },
}


class QuickDropApp:
    def __init__(self, root: tk.Tk, config: AppConfig) -> None:
        self.root = root
        self.config = config
        self.service = TransferService(config=config)
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.files: list[Path] = []
        self.tree_items: dict[str, str] = {}

        self.language = tk.StringVar(value=config.language or "en")
        self.theme = tk.StringVar(value=config.theme or "system")
        self.target = tk.StringVar(value=config.defaultRouteMode or "auto")
        self.custom_path = tk.StringVar(value=config.lastDestination or "/sdcard/Download/WSAQuickDrop")
        self.auto_scan = tk.BooleanVar(value=config.autoMediaScan)
        self.append_timestamp = tk.BooleanVar(value=config.appendTimestampOnCollision)
        self.close_after_send = tk.BooleanVar(value=config.closeAfterSend)
        self.adb_path = tk.StringVar(value=config.adbPath)
        self.endpoint = tk.StringVar(value=f"{config.wsaHost or DEFAULT_WSA_HOST}:{config.wsaPort or DEFAULT_WSA_PORT}")

        self._build()
        self._apply_theme()
        self._refresh_routes()
        self._poll_events()
        drop_enabled = enable_file_drop(self.root, self.add_files)
        if drop_enabled:
            self.log("Explorer drag and drop is enabled.")
        else:
            self.log("Drag and drop is unavailable in this environment. Use Browse Files.")
        self.refresh_adb_status()

    def text(self, key: str) -> str:
        return TEXT.get(self.language.get(), TEXT["en"]).get(key, TEXT["en"][key])

    def _build(self) -> None:
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("980x700")
        self.root.minsize(860, 620)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        pad = {"padx": 12, "pady": 8}

        connection = ttk.LabelFrame(self.root, text="Connection Status")
        connection.grid(row=0, column=0, sticky="ew", **pad)
        for index in range(8):
            connection.columnconfigure(index, weight=1 if index in {1, 3, 5} else 0)
        ttk.Label(connection, text="ADB").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.adb_status = ttk.Label(connection, text="checking")
        self.adb_status.grid(row=0, column=1, sticky="w")
        ttk.Label(connection, text="WSA").grid(row=0, column=2, sticky="w")
        self.wsa_status = ttk.Label(connection, text="unknown")
        self.wsa_status.grid(row=0, column=3, sticky="w")
        ttk.Label(connection, text="Endpoint").grid(row=0, column=4, sticky="w")
        ttk.Entry(connection, textvariable=self.endpoint, width=22).grid(row=0, column=5, sticky="ew", padx=4)
        ttk.Button(connection, text=self.text("connect"), command=self.connect).grid(row=0, column=6, padx=4)
        ttk.Button(connection, text=self.text("retry"), command=self.refresh_adb_status).grid(row=0, column=7, padx=4)
        ttk.Button(connection, text=self.text("browse_adb"), command=self.browse_adb).grid(row=1, column=0, padx=8, pady=6)
        ttk.Entry(connection, textvariable=self.adb_path).grid(row=1, column=1, columnspan=6, sticky="ew", padx=4)
        ttk.Button(connection, text=self.text("open_wsa"), command=self.open_wsa_settings).grid(row=1, column=7, padx=4)

        top = ttk.Frame(self.root)
        top.grid(row=1, column=0, sticky="ew", **pad)
        top.columnconfigure(0, weight=2)
        top.columnconfigure(1, weight=1)

        drop = ttk.LabelFrame(top, text="Drop Zone")
        drop.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        drop.columnconfigure(0, weight=1)
        self.drop_label = ttk.Label(drop, text=self.text("drop"), anchor="center", font=("Segoe UI", 18))
        self.drop_label.grid(row=0, column=0, sticky="ew", padx=14, pady=22)
        ttk.Button(drop, text=self.text("browse"), command=self.browse_files).grid(row=1, column=0, pady=(0, 14))

        options = ttk.LabelFrame(top, text="Destination Mode")
        options.grid(row=0, column=1, sticky="nsew")
        options.columnconfigure(1, weight=1)
        ttk.Label(options, text="Target").grid(row=0, column=0, sticky="w", padx=8, pady=5)
        self.target_combo = ttk.Combobox(
            options,
            textvariable=self.target,
            values=[mode.value for mode in DestinationMode],
            state="readonly",
            width=14,
        )
        self.target_combo.grid(row=0, column=1, sticky="ew", padx=8, pady=5)
        self.target_combo.bind("<<ComboboxSelected>>", lambda _event: self._refresh_routes())
        ttk.Label(options, text=self.text("custom_path")).grid(row=1, column=0, sticky="w", padx=8, pady=5)
        self.custom_entry = ttk.Entry(options, textvariable=self.custom_path)
        self.custom_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=5)
        self.custom_path.trace_add("write", lambda *_: self._refresh_routes())
        ttk.Checkbutton(options, text="auto media scan", variable=self.auto_scan).grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=3)
        ttk.Checkbutton(options, text="append timestamp on collision", variable=self.append_timestamp, command=self._refresh_routes).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=8, pady=3
        )
        ttk.Checkbutton(options, text="close after successful send", variable=self.close_after_send).grid(
            row=4, column=0, columnspan=2, sticky="w", padx=8, pady=3
        )
        ttk.Label(options, text="language").grid(row=5, column=0, sticky="w", padx=8, pady=5)
        language = ttk.Combobox(options, textvariable=self.language, values=["en", "fa"], state="readonly", width=8)
        language.grid(row=5, column=1, sticky="w", padx=8, pady=5)
        language.bind("<<ComboboxSelected>>", lambda _event: self._refresh_language())
        ttk.Label(options, text="theme").grid(row=6, column=0, sticky="w", padx=8, pady=5)
        theme = ttk.Combobox(options, textvariable=self.theme, values=["system", "light", "dark"], state="readonly", width=8)
        theme.grid(row=6, column=1, sticky="w", padx=8, pady=5)
        theme.bind("<<ComboboxSelected>>", lambda _event: self._apply_theme())

        middle = ttk.LabelFrame(self.root, text="File Queue")
        middle.grid(row=2, column=0, sticky="nsew", **pad)
        middle.rowconfigure(0, weight=1)
        middle.columnconfigure(0, weight=1)
        columns = ("name", "type", "size", "destination", "status")
        self.tree = ttk.Treeview(middle, columns=columns, show="headings", height=10)
        headings = ["file name", "type", "size", "Android destination", "status"]
        widths = [220, 80, 90, 360, 120]
        for column, heading, width in zip(columns, headings, widths):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(middle, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        actions = ttk.LabelFrame(self.root, text="Actions")
        actions.grid(row=3, column=0, sticky="ew", **pad)
        for index in range(10):
            actions.columnconfigure(index, weight=1)
        ttk.Button(actions, text=self.text("send"), command=self.send).grid(row=0, column=0, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text=self.text("clear"), command=self.clear).grid(row=0, column=1, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text=self.text("install_sendto"), command=self.install_sendto).grid(row=0, column=2, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text=self.text("uninstall_sendto"), command=self.uninstall_sendto).grid(row=0, column=3, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text=self.text("copy_adb"), command=self.copy_adb_command).grid(row=0, column=4, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text=self.text("open_help"), command=self.open_help).grid(row=0, column=5, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text=self.text("open_logs"), command=self.open_log_folder).grid(row=0, column=6, padx=4, pady=6, sticky="ew")
        ttk.Button(actions, text="Copy OCR instructions", command=self.copy_persian_ocr_instructions).grid(
            row=0, column=7, padx=4, pady=6, sticky="ew"
        )
        ttk.Button(actions, text="Check OCR package", command=self.check_persian_ocr).grid(row=0, column=8, padx=4, pady=6, sticky="ew")

        log_frame = ttk.LabelFrame(self.root, text="Log Panel")
        log_frame.grid(row=4, column=0, sticky="nsew", **pad)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=8, wrap="word", font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)
        ttk.Button(log_frame, text=self.text("copy_log"), command=self.copy_log).grid(row=1, column=0, sticky="e", padx=4, pady=4)

    def _refresh_language(self) -> None:
        self.config.language = self.language.get()
        self.drop_label.configure(text=self.text("drop"))
        self.log(f"Language set to {self.language.get()}. Restart for full relabeling.")

    def _apply_theme(self) -> None:
        mode = self.theme.get()
        if mode == "dark":
            self.root.configure(bg="#202124")
            self.log_text.configure(bg="#111827", fg="#e5e7eb", insertbackground="#e5e7eb")
        else:
            self.root.configure(bg="#f3f4f6")
            self.log_text.configure(bg="#ffffff", fg="#111827", insertbackground="#111827")

    def add_files(self, files: list[str]) -> None:
        for raw in files:
            path = Path(raw)
            if path.is_file() and path not in self.files:
                self.files.append(path)
        self._refresh_routes()
        self.log(f"Queued {len(files)} file(s).")

    def browse_files(self) -> None:
        selected = filedialog.askopenfilenames(title="Select files for WSA QuickDrop")
        if selected:
            self.add_files(list(selected))

    def browse_adb(self) -> None:
        selected = filedialog.askopenfilename(title="Select adb.exe", filetypes=[("ADB", "adb.exe"), ("Executable", "*.exe")])
        if selected:
            self.adb_path.set(selected)
            self.config.adbPath = selected
            self.config.save()
            self.refresh_adb_status()

    def _refresh_routes(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree_items.clear()
        for path in self.files:
            try:
                route = route_for_file(path, self.target.get(), self.custom_path.get(), self.append_timestamp.get())
                destination = route.remote_path
                category = route.category
            except Exception as exc:
                destination = str(exc)
                category = "?"
            try:
                size = human_file_size(path.stat().st_size)
            except OSError:
                size = "?"
            item_id = self.tree.insert("", "end", values=(path.name, category, size, destination, "queued"))
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
            target=self.target.get(),
            custom_path=self.custom_path.get(),
            adb_path=self.adb_path.get(),
            host=host,
            port=port,
            scan=self.auto_scan.get(),
            append_timestamp=self.append_timestamp.get(),
            verbose=True,
        )

    def save_config(self) -> None:
        options = self.options()
        self.config.adbPath = self.adb_path.get()
        self.config.defaultRouteMode = self.target.get()
        self.config.lastDestination = self.custom_path.get()
        self.config.autoMediaScan = self.auto_scan.get()
        self.config.appendTimestampOnCollision = self.append_timestamp.get()
        self.config.closeAfterSend = self.close_after_send.get()
        self.config.theme = self.theme.get()
        self.config.language = self.language.get()
        self.config.wsaHost = options.host
        self.config.wsaPort = options.port
        self.config.save()

    def send(self) -> None:
        if not self.files:
            messagebox.showinfo(APP_NAME, "Choose one or more files first.")
            return
        self.save_config()
        options = self.options()
        files = [str(path) for path in self.files]
        self.log("Starting transfer.")
        thread = threading.Thread(target=self._send_worker, args=(files, options), daemon=True)
        thread.start()

    def _send_worker(self, files: list[str], options: TransferOptions) -> None:
        summary = self.service.send_files(files, options, callback=lambda item: self.events.put(("item", item)))
        self.events.put(("summary", summary))

    def connect(self) -> None:
        self.save_config()
        thread = threading.Thread(target=self._connect_worker, daemon=True)
        thread.start()

    def _connect_worker(self) -> None:
        client, device, messages = self.service.ensure_connection(self.options())
        self.events.put(("connect", (client, device, messages)))

    def refresh_adb_status(self) -> None:
        path = AdbDiscovery().find_adb(self.adb_path.get())
        if path:
            self.adb_status.configure(text=str(path))
            self.adb_path.set(str(path))
        else:
            self.adb_status.configure(text="adb.exe not found")
        self.wsa_status.configure(text="not checked")

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
                    self.wsa_status.configure(text=device.state if device else "not connected")
                    for message in messages:
                        self.log(message)
        except queue.Empty:
            pass
        self.root.after(120, self._poll_events)

    def _update_item(self, item) -> None:
        tree_id = self.tree_items.get(str(Path(item.local_path)))
        if tree_id:
            values = list(self.tree.item(tree_id, "values"))
            values[1] = item.category or values[1]
            values[3] = item.remote_path or item.remote_dir or values[3]
            values[4] = item.status
            self.tree.item(tree_id, values=values)
        self.log(f"{item.status}: {Path(item.local_path).name} {item.message}")

    def _handle_summary(self, summary) -> None:
        for message in summary.messages:
            self.log(message)
        if summary.ok:
            self.log("All files sent.")
            if self.close_after_send.get():
                self.root.after(700, self.root.destroy)
        else:
            self.log("Some files failed. See messages above.")

    def clear(self) -> None:
        self.files.clear()
        self._refresh_routes()
        self.log("Queue cleared.")

    def install_sendto(self) -> None:
        try:
            path = install_sendto()
            self.log(f"Installed SendTo launcher: {path}")
            messagebox.showinfo(APP_NAME, f"Installed:\n{path}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def uninstall_sendto(self) -> None:
        removed = uninstall_sendto()
        self.log("Removed SendTo launcher." if removed else "SendTo launcher was not installed.")

    def copy_adb_command(self) -> None:
        command = f'adb connect {self.endpoint.get() or "127.0.0.1:58526"}'
        self.root.clipboard_clear()
        self.root.clipboard_append(command)
        self.log(f"Copied: {command}")

    def copy_persian_ocr_instructions(self) -> None:
        text = "Open Persian OCR Offline > Select Image/PDF > Pixel 5 > Pictures or Download > WSAQuickDrop"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log("Copied Persian OCR Offline test instructions.")

    def check_persian_ocr(self) -> None:
        self.save_config()
        thread = threading.Thread(target=self._check_ocr_worker, daemon=True)
        thread.start()

    def _check_ocr_worker(self) -> None:
        found, message = self.service.check_package_installed(PERSIAN_OCR_PACKAGES, self.options())
        self.events.put(("connect", (None, None, [f"Persian OCR Offline installed: {'yes' if found else 'no'} ({message})"])))

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
        messagebox.showinfo(
            APP_NAME,
            "Open Windows Subsystem for Android settings, enable Developer Mode, "
            "confirm the ADB port, then click Retry.",
        )

    def copy_log(self) -> None:
        text = self.log_text.get("1.0", "end").strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log("Copied log text.")

    def log(self, message: str) -> None:
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    @staticmethod
    def app_root() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent
        return Path(__file__).resolve().parents[2]


def run_gui(config: AppConfig | None = None) -> None:
    root = tk.Tk()
    app = QuickDropApp(root, config or AppConfig.load())
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_config(), root.destroy()))
    root.mainloop()
