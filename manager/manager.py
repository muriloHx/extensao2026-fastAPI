"""
Uvicorn Manager - Gerenciador estilo XAMPP para FastAPI/Uvicorn
Uso: python uvicorn_manager.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import webbrowser
import json
import hashlib
import psutil

# ─── Senha padrão: "admin" (SHA-256) ────────────────────────────────────────
DEFAULT_PASSWORD_HASH = hashlib.sha256(b"admin").hexdigest()
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uvicorn_manager_config.json")
PID_FILE = "uvicorn.pid"

DEFAULT_CONFIG = {
    "app_module": "api.main:app",
    "host": "127.0.0.1",
    "port": "8000",
    "reload": True,
    "workers": "1",
    "log_level": "info",
    "timeout_keep_alive": "5",
    "password_hash": DEFAULT_PASSWORD_HASH,
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            # garante que todos os campos existam
            for k, v in DEFAULT_CONFIG.items():
                data.setdefault(k, v)
            return data
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


class AuthDialog(tk.Toplevel):
    """Janela de autenticação antes de abrir as configurações."""

    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("Autenticação")
        self.resizable(False, False)
        self.grab_set()

        self.config(bg="#16213e")
        self.geometry("320x200")

        tk.Label(self, text="🔒  Área Restrita", bg="#16213e", fg="#e2e8f0",
                 font=("Consolas", 14, "bold")).pack(pady=(20, 5))
        tk.Label(self, text="Digite a senha para acessar as configurações.",
                 bg="#16213e", fg="#94a3b8", font=("Consolas", 9)).pack()

        self.pw_var = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.pw_var, show="●",
                         bg="#0f3460", fg="white", insertbackground="white",
                         font=("Consolas", 11), bd=0, relief="flat", width=24)
        entry.pack(pady=12, ipady=6)
        entry.bind("<Return>", lambda e: self.check())
        entry.focus_set()

        self.msg = tk.Label(self, text="", bg="#16213e", fg="#f87171",
                            font=("Consolas", 9))
        self.msg.pack()

        tk.Button(self, text="Entrar", command=self.check,
                  bg="#0ea5e9", fg="white", activebackground="#0284c7",
                  font=("Consolas", 10, "bold"), bd=0, relief="flat",
                  padx=20, pady=6, cursor="hand2").pack(pady=8)

    def check(self):
        cfg = load_config()
        hashed = hashlib.sha256(self.pw_var.get().encode()).hexdigest()
        if hashed == cfg.get("password_hash", DEFAULT_PASSWORD_HASH):
            self.destroy()
            self.on_success()
        else:
            self.msg.config(text="Senha incorreta.")
            self.pw_var.set("")


class SettingsWindow(tk.Toplevel):
    """Janela de configurações protegida por senha."""

    def __init__(self, parent, cfg: dict, on_save):
        super().__init__(parent)
        self.cfg = cfg
        self.on_save = on_save
        self.title("Configurações")
        self.resizable(False, False)
        self.grab_set()
        self.config(bg="#0f172a")
        self.geometry("460x520")

        # ── título ──────────────────────────────────────────────────────────
        tk.Label(self, text="⚙  Configurações do Servidor",
                 bg="#0f172a", fg="#e2e8f0",
                 font=("Consolas", 13, "bold")).pack(pady=(18, 4))
        tk.Label(self, text="Alterações entram em vigor no próximo Start/Restart.",
                 bg="#0f172a", fg="#64748b", font=("Consolas", 8)).pack()

        container = tk.Frame(self, bg="#0f172a")
        container.pack(padx=24, pady=12, fill="both", expand=True)

        def row(label, row_n):
            tk.Label(container, text=label, bg="#0f172a", fg="#94a3b8",
                     font=("Consolas", 9), anchor="w", width=22).grid(
                row=row_n, column=0, sticky="w", pady=5)

        def entry(var, row_n, width=28):
            e = tk.Entry(container, textvariable=var, bg="#1e293b", fg="white",
                         insertbackground="white", font=("Consolas", 10),
                         bd=0, relief="flat", width=width)
            e.grid(row=row_n, column=1, sticky="w", pady=5, ipady=4)
            return e

        # ── campos ──────────────────────────────────────────────────────────
        self.v_app    = tk.StringVar(value=cfg["app_module"])
        self.v_host   = tk.StringVar(value=cfg["host"])
        self.v_port   = tk.StringVar(value=cfg["port"])
        self.v_workers= tk.StringVar(value=cfg["workers"])
        self.v_log    = tk.StringVar(value=cfg["log_level"])
        self.v_timeout= tk.StringVar(value=cfg["timeout_keep_alive"])
        self.v_reload = tk.BooleanVar(value=cfg["reload"])

        row("Módulo da aplicação",  0); entry(self.v_app,     0)
        row("Host",                 1); entry(self.v_host,    1, 18)
        row("Porta",                2); entry(self.v_port,    2, 8)
        row("Workers",              3); entry(self.v_workers, 3, 6)
        row("Log Level",            4)
        log_combo = ttk.Combobox(container, textvariable=self.v_log, width=12,
                                 values=["debug","info","warning","error","critical"],
                                 state="readonly", font=("Consolas", 10))
        log_combo.grid(row=4, column=1, sticky="w", pady=5)
        row("Timeout Keep-Alive",   5); entry(self.v_timeout, 5, 6)
        row("Auto-reload",          6)
        tk.Checkbutton(container, variable=self.v_reload, bg="#0f172a",
                       activebackground="#0f172a", fg="#0ea5e9",
                       selectcolor="#1e293b").grid(row=6, column=1, sticky="w")

        # ── separador / troca de senha ───────────────────────────────────────
        sep = tk.Frame(self, bg="#1e293b", height=1)
        sep.pack(fill="x", padx=24, pady=4)

        pw_frame = tk.Frame(self, bg="#0f172a")
        pw_frame.pack(padx=24, fill="x")

        tk.Label(pw_frame, text="🔑  Alterar senha", bg="#0f172a", fg="#f59e0b",
                 font=("Consolas", 9, "bold")).pack(anchor="w")

        fields = tk.Frame(pw_frame, bg="#0f172a")
        fields.pack(fill="x", pady=4)

        self.v_pw_curr = tk.StringVar()
        self.v_pw_new  = tk.StringVar()
        self.v_pw_conf = tk.StringVar()
        self.pw_msg    = tk.StringVar()

        for label, var, col in [("Atual", self.v_pw_curr, 0),
                                 ("Nova",  self.v_pw_new,  1),
                                 ("Conf.", self.v_pw_conf, 2)]:
            tk.Label(fields, text=label, bg="#0f172a", fg="#94a3b8",
                     font=("Consolas", 8)).grid(row=0, column=col, padx=4)
            tk.Entry(fields, textvariable=var, show="●", bg="#1e293b",
                     fg="white", insertbackground="white",
                     font=("Consolas", 9), bd=0, relief="flat", width=12,
                     ).grid(row=1, column=col, padx=4, ipady=4)

        tk.Label(pw_frame, textvariable=self.pw_msg, bg="#0f172a",
                 fg="#f87171", font=("Consolas", 8)).pack(anchor="w")

        # ── botões ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg="#0f172a")
        btn_frame.pack(pady=12)

        tk.Button(btn_frame, text="Salvar", command=self.save,
                  bg="#22c55e", fg="white", activebackground="#16a34a",
                  font=("Consolas", 10, "bold"), bd=0, relief="flat",
                  padx=20, pady=6, cursor="hand2").pack(side="left", padx=6)

        tk.Button(btn_frame, text="Cancelar", command=self.destroy,
                  bg="#475569", fg="white", activebackground="#334155",
                  font=("Consolas", 10), bd=0, relief="flat",
                  padx=16, pady=6, cursor="hand2").pack(side="left", padx=6)

    def save(self):
        # troca de senha (opcional)
        curr = self.v_pw_curr.get()
        new  = self.v_pw_new.get()
        conf = self.v_pw_conf.get()

        new_hash = self.cfg["password_hash"]
        if curr or new or conf:
            if hashlib.sha256(curr.encode()).hexdigest() != self.cfg["password_hash"]:
                self.pw_msg.set("Senha atual incorreta.")
                return
            if new != conf:
                self.pw_msg.set("Nova senha e confirmação não coincidem.")
                return
            if len(new) < 4:
                self.pw_msg.set("Nova senha muito curta (mín. 4 chars).")
                return
            new_hash = hashlib.sha256(new.encode()).hexdigest()

        # validação básica
        try:
            int(self.v_port.get())
            int(self.v_workers.get())
            int(self.v_timeout.get())
        except ValueError:
            messagebox.showerror("Erro", "Porta, workers e timeout devem ser números inteiros.")
            return

        self.cfg.update({
            "app_module": self.v_app.get().strip(),
            "host":       self.v_host.get().strip(),
            "port":       self.v_port.get().strip(),
            "workers":    self.v_workers.get().strip(),
            "log_level":  self.v_log.get(),
            "timeout_keep_alive": self.v_timeout.get().strip(),
            "reload":     self.v_reload.get(),
            "password_hash": new_hash,
        })
        save_config(self.cfg)
        self.on_save(self.cfg)
        self.destroy()
        messagebox.showinfo("Salvo", "Configurações salvas com sucesso!")


class UvicornManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Uvicorn Manager")
        self.root.geometry("740x560")
        self.root.config(bg="#0f172a")
        self.root.resizable(False, False)

        self.cfg = load_config()
        self.process = None
        self._recovered_pid = None
        self._build_ui()
        self._recover_process()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # cabeçalho
        header = tk.Frame(self.root, bg="#0f3460", height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚡  Uvicorn Manager",
                 bg="#0f3460", fg="#e2e8f0",
                 font=("Consolas", 15, "bold")).pack(side="left", padx=20)
        tk.Label(header, text="FastAPI · Starlette · ASGI",
                 bg="#0f3460", fg="#64748b",
                 font=("Consolas", 9)).pack(side="left")

        # info do módulo
        info = tk.Frame(self.root, bg="#1e293b", pady=6)
        info.pack(fill="x", padx=0)
        tk.Label(info, text="Módulo:", bg="#1e293b", fg="#94a3b8",
                 font=("Consolas", 9)).pack(side="left", padx=(16, 4))
        self.lbl_module = tk.Label(info, text=self.cfg["app_module"],
                                   bg="#1e293b", fg="#38bdf8",
                                   font=("Consolas", 10, "bold"))
        self.lbl_module.pack(side="left")
        tk.Label(info, text="  │  Host:", bg="#1e293b", fg="#94a3b8",
                 font=("Consolas", 9)).pack(side="left", padx=(8, 4))
        self.lbl_host = tk.Label(info,
                                 text=f"{self.cfg['host']}:{self.cfg['port']}",
                                 bg="#1e293b", fg="#38bdf8",
                                 font=("Consolas", 10, "bold"))
        self.lbl_host.pack(side="left")
        tk.Label(info, text="  │  Workers:", bg="#1e293b", fg="#94a3b8",
                 font=("Consolas", 9)).pack(side="left", padx=(8, 4))
        self.lbl_workers = tk.Label(info, text=self.cfg["workers"],
                                    bg="#1e293b", fg="#38bdf8",
                                    font=("Consolas", 10, "bold"))
        self.lbl_workers.pack(side="left")

        # botões
        btn_area = tk.Frame(self.root, bg="#0f172a", pady=10)
        btn_area.pack(fill="x", padx=16)

        def btn(parent, text, cmd, color, ac, state ="normal"):
            return tk.Button(parent, text=text, command=cmd,
                             bg=color, fg="white", activebackground=ac,
                             activeforeground="white",
                             font=("Consolas", 10, "bold"), bd=0,
                             relief="flat", padx=14, pady=7,
                             cursor="hand2", state=state)

        self.btn_start   = btn(btn_area, "▶  Start",   self.start_server, "#16a34a","#15803d")
        self.btn_stop    = btn(btn_area, "■  Stop",    self.stop_server,  "#dc2626","#b91c1c", "disabled")
        self.btn_restart = btn(btn_area, "↺  Restart", self.restart_server,"#d97706","#b45309", "disabled")
        self.btn_browser = btn(btn_area, "🌐  Browser", self.open_browser, "#0284c7","#0369a1")
        self.btn_cfg     = btn(btn_area, "⚙  Config",  self.open_settings,"#7c3aed","#6d28d9")

        for b in (self.btn_start, self.btn_stop, self.btn_restart,
                  self.btn_browser, self.btn_cfg):
            b.pack(side="left", padx=4)

        # status bar
        status_bar = tk.Frame(self.root, bg="#1e293b", height=30)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)
        self.status_dot  = tk.Label(status_bar, text="●", fg="#ef4444",
                                    bg="#1e293b", font=("Consolas", 11))
        self.status_dot.pack(side="left", padx=(12, 4))
        self.status_text = tk.Label(status_bar, text="Servidor parado",
                                    fg="#94a3b8", bg="#1e293b",
                                    font=("Consolas", 9))
        self.status_text.pack(side="left")

        self.pid_label = tk.Label(status_bar, text="", fg="#64748b",
                                  bg="#1e293b", font=("Consolas", 8))
        self.pid_label.pack(side="right", padx=12)

        # log area
        log_frame = tk.Frame(self.root, bg="#0f172a")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(6, 0))

        log_header = tk.Frame(log_frame, bg="#0f172a")
        log_header.pack(fill="x")
        tk.Label(log_header, text="Logs", bg="#0f172a", fg="#64748b",
                 font=("Consolas", 8, "bold")).pack(side="left")
        tk.Button(log_header, text="limpar", command=self.clear_logs,
                  bg="#0f172a", fg="#475569", activebackground="#0f172a",
                  activeforeground="#94a3b8", font=("Consolas", 8),
                  bd=0, relief="flat", cursor="hand2").pack(side="right")

        self.log_area = scrolledtext.ScrolledText(
            log_frame, bg="#020617", fg="#94a3b8",
            font=("Consolas", 9), bd=0, relief="flat",
            state="disabled", selectbackground="#1e293b")
        self.log_area.pack(fill="both", expand=True, pady=(2, 8))

        # color tags
        self.log_area.tag_config("info",  foreground="#38bdf8")
        self.log_area.tag_config("ok",    foreground="#4ade80")
        self.log_area.tag_config("warn",  foreground="#fbbf24")
        self.log_area.tag_config("error", foreground="#f87171")

    # ── actions ─────────────────────────────────────────────────────────────

    def log(self, msg: str):
        tag = "info"
        ml = msg.lower()
        if any(x in ml for x in ("started", "running", "application startup")):
            tag = "ok"
        elif any(x in ml for x in ("warning", "warn")):
            tag = "warn"
        elif any(x in ml for x in ("error", "exception", "traceback", "critical")):
            tag = "error"

        self.log_area.config(state="normal")
        self.log_area.insert("end", msg + "\n", tag)
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def clear_logs(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", "end")
        self.log_area.config(state="disabled")

    def _set_status(self, running: bool, pid: int = None):
        if running:
            self.status_dot.config(fg="#4ade80")
            self.status_text.config(text="Servidor rodando", fg="#4ade80")
            self.pid_label.config(text=f"PID {pid}" if pid else "")
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.btn_restart.config(state="normal")
        else:
            self.status_dot.config(fg="#ef4444")
            self.status_text.config(text="Servidor parado", fg="#94a3b8")
            self.pid_label.config(text="")
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.btn_restart.config(state="disabled")

    def _build_cmd(self):
        c = self.cfg
        cmd = [
            "uvicorn", c["app_module"],
            "--host", c["host"],
            "--port", c["port"],
            "--workers", c["workers"],
            "--log-level", c["log_level"],
            "--timeout-keep-alive", c["timeout_keep_alive"],
        ]
        if c["reload"]:
            cmd.append("--reload")
        return cmd

    def start_server(self):
        cmd = self._build_cmd()
        self.log(f"[CMD] {' '.join(cmd)}")
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except FileNotFoundError:
            self.log("[ERRO] 'uvicorn' não encontrado. Verifique seu virtualenv/PATH.")
            return

        save_pid(self.process.pid)
        self._recovered_pid = None
        self._set_status(True, self.process.pid)
        threading.Thread(target=self._read_logs, daemon=True).start()

    def _read_logs(self):
        for line in self.process.stdout:
            self.root.after(0, self.log, line.rstrip())
        self.root.after(0, self._set_status, False)

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process = None
        elif self._recovered_pid:
            try:
                psutil.Process(self._recovered_pid).terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            self._recovered_pid = None
        clear_pid()
        self._set_status(False)
        self.log("[INFO] Servidor encerrado.")

    def restart_server(self):
        self.log("[INFO] Reiniciando servidor...")
        self.stop_server()
        self.root.after(600, self.start_server)

    def open_browser(self):
        webbrowser.open(f"http://{self.cfg['host']}:{self.cfg['port']}")

    def open_settings(self):
        def show_settings():
            SettingsWindow(self.root, self.cfg, self._on_config_saved)

        AuthDialog(self.root, show_settings)

    def _on_config_saved(self, new_cfg):
        self.cfg = new_cfg
        self.lbl_module.config(text=new_cfg["app_module"])
        self.lbl_host.config(text=f"{new_cfg['host']}:{new_cfg['port']}")
        self.lbl_workers.config(text=new_cfg["workers"])
        self.log("[INFO] Configurações atualizadas.")

    # ── PID tracking ────────────────────────────────────────────────────────

    def _recover_process(self):
        """Ao abrir o manager, verifica se já existe um processo rodando."""
        pid = get_existing_pid()
        if pid:
            self._recovered_pid = pid
            self.log(f"[INFO] Processo existente encontrado — PID {pid}.")
            self.log("[INFO] Use Stop para encerrá-lo ou Start para substituí-lo.")
            self.log("[WARNING] Os logs não serão exibidos com o processo recuperado")
            self._set_status(True, pid)
        else:
            self._recovered_pid = None

    def _on_close(self):
        """Pergunta o que fazer com o servidor ao fechar a janela."""
        is_running = self.process is not None or self._recovered_pid is not None
        if is_running:
            resposta = messagebox.askyesnocancel(
                "Fechar o manager",
                "O servidor ainda está rodando.\n\n"
                "Sim     → encerrar o servidor e fechar\n"
                "Não     → fechar o manager, manter o servidor\n"
                "Cancelar → voltar"
            )
            if resposta is True:
                self.stop_server()
                self.root.destroy()
            elif resposta is False:
                # mantém o servidor, garante que o PID está salvo
                pid = self.process.pid if self.process else self._recovered_pid
                save_pid(pid)
                self.root.destroy()
            # Cancelar → não faz nada
        else:
            clear_pid()
            self.root.destroy()


# ─── PID helpers ─────────────────────────────────────────────────────────────

def save_pid(pid: int):
    with open(PID_FILE, "w") as f:
        f.write(str(pid))

def clear_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def get_existing_pid() -> int | None:
    """Lê o PID salvo e verifica se o processo ainda está vivo."""
    if not os.path.exists(PID_FILE):
        return None
    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        proc = psutil.Process(pid)
        name = proc.name().lower()
        # confirma que ainda é um processo uvicorn/python (não foi reaproveitado pelo SO)
        if "uvicorn" in name or "python" in name:
            return pid
        clear_pid()
        return None
    except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
        clear_pid()
        return None


if __name__ == "__main__":
    root = tk.Tk()
    UvicornManager(root)
    root.mainloop()
