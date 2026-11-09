# -*- coding: utf-8 -*-
"""
Fading Afternoon 无伤补丁 —— 一键安装器（单文件 exe）

界面：选游戏目录 → 点“安装补丁”。全程本地，不联网。
内部：校验 data.win 的 SHA256 → 用内置差异包还原 → 再校验结果 → 替换。

也支持命令行（用于自测 / 批量）：
    FA-GodMode.exe --check    "D:\\path\\to\\Fading Afternoon"
    FA-GodMode.exe --install  "D:\\path\\to\\Fading Afternoon"
    FA-GodMode.exe --restore  "D:\\path\\to\\Fading Afternoon"
    FA-GodMode.exe --install  "<path>" --log "E:\\out.log"
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import threading
import traceback

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import zstandard as zstd

APP_NAME = "Fading Afternoon 无伤补丁"
APP_VERSION = "3.0.0"

STATE_OK_ORIGINAL = "original"
STATE_OK_PATCHED = "patched"
STATE_UNKNOWN = "unknown"


# ---------------------------------------------------------------- 资源与路径
def res_path(*parts):
    """PyInstaller 打包后资源在 _MEIPASS 里；源码运行时在脚本目录。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def load_manifest():
    with open(res_path("payload", "manifest.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def config_path():
    base = os.environ.get("APPDATA") or tempfile.gettempdir()
    d = os.path.join(base, "fa-godmode")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        return None
    return os.path.join(d, "config.json")


def load_config():
    p = config_path()
    if p and os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(cfg):
    p = config_path()
    if not p:
        return
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------- 找游戏目录
def steam_roots():
    roots = []
    try:
        import winreg
        for hive, key in (
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
        ):
            try:
                with winreg.OpenKey(hive, key) as k:
                    p = winreg.QueryValueEx(k, "SteamPath")[0]
                    if p:
                        roots.append(os.path.normpath(p))
                        break
            except OSError:
                continue
    except Exception:
        pass

    if not roots:
        roots.append(r"C:\Program Files (x86)\Steam")

    libs = []
    for r in roots:
        libs.append(r)
        vdf = os.path.join(r, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            try:
                with open(vdf, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                import re
                for m in re.finditer(r'"path"\s+"([^"]+)"', txt):
                    libs.append(os.path.normpath(m.group(1).replace("\\\\", "\\")))
            except Exception:
                pass
    out = []
    for x in libs:
        if x not in out:
            out.append(x)
    return out


def find_game_dir(hint=None):
    cands = []
    if hint:
        cands.append(hint)
    for r in steam_roots():
        cands.append(os.path.join(r, "steamapps", "common", "Fading Afternoon"))
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "data.win")):
            return os.path.abspath(c)
    return None


def is_valid_game_dir(path):
    return bool(path) and os.path.isfile(os.path.join(path, "data.win"))


# ---------------------------------------------------------------- 核心逻辑
def sha256_file(path, chunk=8 * 1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def detect_state(game_dir):
    win = os.path.join(game_dir, "data.win")
    if not os.path.isfile(win):
        return STATE_UNKNOWN, ""
    cur = sha256_file(win)
    m = load_manifest()
    if cur == m["patched"]["sha256"]:
        return STATE_OK_PATCHED, cur
    if cur == m["source"]["sha256"]:
        return STATE_OK_ORIGINAL, cur
    return STATE_UNKNOWN, cur


def apply_patch(game_dir, direction, log):
    """direction: 'install' 或 'restore'"""
    m = load_manifest()
    win = os.path.join(game_dir, "data.win")
    src_expect = m["source"]["sha256"] if direction == "install" else m["patched"]["sha256"]
    dst_expect = m["patched"]["sha256"] if direction == "install" else m["source"]["sha256"]
    patch_file = res_path("payload", "godmode.patch.zst" if direction == "install" else "original.patch.zst")

    log("正在校验 data.win（706 MB，约 3-10 秒）…")
    cur = sha256_file(win)
    log("  当前哈希 %s…" % cur[:16])

    if cur == dst_expect:
        log("不用动：这个文件已经是目标状态了。")
        return True, "already"
    if cur != src_expect:
        log("这个文件和补丁制作时的版本不一致，停手不动。")
        log("  你的文件 : %s" % cur)
        log("  补丁认的 : %s" % src_expect)
        return False, "version"

    log("正在生成新的 data.win …")
    t0 = time.time()
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=".data_", suffix=".new", dir=game_dir)
    os.close(tmp_fd)
    try:
        with open(win, "rb") as f:
            data = f.read()
        d = zstd.ZstdCompressionDict(data, dict_type=zstd.DICT_TYPE_RAWCONTENT)
        del data
        dctx = zstd.ZstdDecompressor(dict_data=d, max_window_size=2 ** 31)
        with open(patch_file, "rb") as pf, open(tmp_path, "wb") as of:
            with dctx.stream_reader(pf) as reader:
                while True:
                    chunk = reader.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    of.write(chunk)
        log("  完成，用时 %.1f 秒" % (time.time() - t0))

        log("正在校验结果 …")
        new_hash = sha256_file(tmp_path)
        if new_hash != dst_expect:
            os.unlink(tmp_path)
            log("结果校验不通过，已删除半成品，原文件没动。")
            return False, "verify"

        if direction == "install":
            bak = os.path.join(game_dir, "data.win.bak")
            if not os.path.exists(bak):
                try:
                    import shutil
                    shutil.copy2(win, bak)
                    log("  顺手备份了原版：data.win.bak（可删）")
                except Exception:
                    pass

        os.replace(tmp_path, win)
        log("已替换 data.win。")
        return True, "done"
    except Exception as e:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception:
            pass
        log("出错：%s" % e)
        return False, "error"


# ---------------------------------------------------------------- 命令行模式
def cli_main(argv):
    args = argv[1:]
    mode = None
    path = None
    logfile = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--check", "--install", "--restore"):
            mode = a.lstrip("-")
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                path = args[i + 1]
                i += 2
                continue
        elif a == "--log" and i + 1 < len(args):
            logfile = args[i + 1]
            i += 2
            continue
        i += 1

    lines = []

    def log(s):
        lines.append(str(s))
        try:
            print(s, flush=True)
        except Exception:
            pass

    if not mode:
        return 2

    gd = find_game_dir(path)
    if not gd:
        log("找不到游戏目录。")
        rc = 3
    else:
        log("游戏目录：%s" % gd)
        if mode == "check":
            st, h = detect_state(gd)
            log("状态：%s  (%s…)" % (st, h[:16]))
            rc = 0 if st != STATE_UNKNOWN else 2
        else:
            ok, why = apply_patch(gd, mode, log)
            log("结果：%s" % ("成功" if ok else "失败(%s)" % why))
            rc = 0 if ok else 1

    if logfile:
        try:
            with open(logfile, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception:
            pass
    return rc


# ---------------------------------------------------------------- GUI
class App:
    def __init__(self, root):
        self.root = root
        self.cfg = load_config()
        self.busy = False
        self.mode = None

        root.title("%s  v%s" % (APP_NAME, APP_VERSION))
        root.geometry("560x420")
        root.minsize(520, 400)
        try:
            root.iconbitmap(default="")
        except Exception:
            pass

        pad = {"padx": 12, "pady": 6}

        head = ttk.Label(
            root, text="玩家不掉血 · 按 K 切换 · 血条旁显示 GOD",
            font=("Microsoft YaHei UI", 10),
        )
        head.pack(anchor="w", **pad)

        box = ttk.LabelFrame(root, text="游戏目录")
        box.pack(fill="x", **pad)

        self.path_var = tk.StringVar(value=self.cfg.get("game_dir", ""))
        entry = ttk.Entry(box, textvariable=self.path_var)
        entry.pack(side="left", fill="x", expand=True, padx=(8, 6), pady=8)

        ttk.Button(box, text="浏览…", width=8, command=self.browse).pack(side="left", padx=2, pady=8)
        ttk.Button(box, text="自动查找", width=10, command=self.autofind).pack(side="left", padx=(2, 8), pady=8)

        ops = ttk.Frame(root)
        ops.pack(fill="x", **pad)
        self.btn_install = ttk.Button(ops, text="安装补丁", command=lambda: self.start("install"))
        self.btn_install.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=6)
        self.btn_restore = ttk.Button(ops, text="还原原版", command=lambda: self.start("restore"))
        self.btn_restore.pack(side="left", fill="x", expand=True, ipady=6)

        self.state_lbl = ttk.Label(root, text="", font=("Microsoft YaHei UI", 9))
        self.state_lbl.pack(anchor="w", padx=12)

        self.pb = ttk.Progressbar(root, mode="determinate", maximum=100, value=0)
        self.pb.pack(fill="x", padx=12, pady=6)

        logf = ttk.LabelFrame(root, text="日志")
        logf.pack(fill="both", expand=True, **pad)
        self.log = tk.Text(logf, height=9, wrap="word", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

        foot = ttk.Label(
            root,
            text="全程本地处理 · 不联网 · 校验不过不改文件",
            font=("Microsoft YaHei UI", 8), foreground="#666",
        )
        foot.pack(anchor="w", padx=12, pady=(0, 8))

        if not self.path_var.get():
            gd = find_game_dir()
            if gd:
                self.path_var.set(gd)
        self.refresh_state()

    # ---- helpers
    def w(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def browse(self):
        d = filedialog.askdirectory(title="选择 Fading Afternoon 的游戏目录（里面有 data.win）")
        if d:
            self.path_var.set(os.path.normpath(d))
            self.refresh_state()

    def autofind(self):
        gd = find_game_dir()
        if gd:
            self.path_var.set(gd)
            self.refresh_state()
        else:
            messagebox.showwarning("没找到", "自动查找没找到游戏目录。\n请点“浏览…”手动选一下：\nSteam 库里 Fading Afternoon 的安装目录，里面有个 data.win。")

    def current_dir(self):
        p = self.path_var.get().strip().strip('"')
        return p

    def refresh_state(self):
        gd = self.current_dir()
        if not is_valid_game_dir(gd):
            self.state_lbl.config(text="状态：目录无效（找不到 data.win）", foreground="#b00")
            return
        self.cfg["game_dir"] = gd
        save_config(self.cfg)
        self.state_lbl.config(text="状态：检查中…", foreground="#666")
        threading.Thread(target=self._check_worker, args=(gd,), daemon=True).start()

    def _check_worker(self, gd):
        try:
            st, h = detect_state(gd)
        except Exception as e:
            st, h = STATE_UNKNOWN, str(e)
        self.root.after(0, lambda: self._show_state(st, h))

    def _show_state(self, st, h):
        if st == STATE_OK_PATCHED:
            self.state_lbl.config(text="状态：已安装（进游戏就是无敌）", foreground="#0a7a35")
        elif st == STATE_OK_ORIGINAL:
            self.state_lbl.config(text="状态：原版，可以安装", foreground="#333")
        else:
            self.state_lbl.config(text="状态：版本不匹配或文件异常（%s…）" % (h[:12] or "?"), foreground="#b00")

    def start(self, mode):
        if self.busy:
            return
        gd = self.current_dir()
        if not is_valid_game_dir(gd):
            messagebox.showerror("目录不对", "这个目录里没有 data.win。\n请选 Fading Afternoon 的安装目录。")
            return
        if self._game_running():
            messagebox.showwarning("先关游戏", "游戏正在运行，关掉再操作。")
            return
        self.busy = True
        self.mode = mode
        self.btn_install.config(state="disabled")
        self.btn_restore.config(state="disabled")
        self.pb.config(mode="indeterminate")
        self.pb.start(12)
        self.w("—— %s ——" % ("安装补丁" if mode == "install" else "还原原版"))
        threading.Thread(target=self._worker, args=(mode, gd), daemon=True).start()

    def _game_running(self):
        try:
            import subprocess
            out = subprocess.run(
                ["tasklist", "/fi", "imagename eq fading afternoon.exe"],
                capture_output=True, text=True, timeout=10,
                creationflags=0x08000000,
            ).stdout.lower()
            return "fading afternoon" in out
        except Exception:
            return False

    def _worker(self, mode, gd):
        try:
            ok, why = apply_patch(gd, mode, lambda s: self.root.after(0, lambda m=s: self.w(m)))
            self.root.after(0, lambda: self._done(ok, why))
        except Exception:
            err = traceback.format_exc()
            self.root.after(0, lambda: (self.w(err), self._done(False, "error")))

    def _done(self, ok, why):
        self.busy = False
        self.pb.stop()
        self.pb.config(mode="determinate", value=(100 if ok else 0))
        self.btn_install.config(state="normal")
        self.btn_restore.config(state="normal")
        self.refresh_state()
        if ok:
            if why == "already":
                messagebox.showinfo("不用动", "这个文件已经是目标状态了。")
            elif self.mode == "install":
                messagebox.showinfo("完成", "装好了。\n\n进游戏按 K 切换无敌，血条旁显示 GOD。")
            else:
                messagebox.showinfo("完成", "已还原成原版。\n\n游戏回到你刚买的样子，可以正常玩了。")
        else:
            if why == "version":
                messagebox.showerror(
                    "版本不匹配",
                    "你的 data.win 和补丁制作时的版本不同。\n\n"
                    "游戏更新过的话，等新补丁；或去 GitHub 提 issue，附上日志里那两行哈希。\n\n"
                    "你的文件没有被改动。",
                )
            else:
                messagebox.showerror("失败", "出错了，详情看日志。\n你的原文件没有被改动。")


def main():
    if len(sys.argv) > 1:
        sys.exit(cli_main(sys.argv))

    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.25)
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
