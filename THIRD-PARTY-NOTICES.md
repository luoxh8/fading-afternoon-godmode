# 第三方组件声明

`FadingAfternoon-GodMode.exe` 是把 `app/fa_godmode.py`（本仓库，MIT）连同下列第三方组件打包成的单文件程序。

## Python 运行时

- 组件：CPython 3.12
- 许可证：Python Software Foundation License 2.0
- 说明：PSF 许可允许再分发，前提是保留其版权与许可声明
- 全文：https://docs.python.org/3/license.html

## Tcl/Tk（图形界面）

- 组件：Tcl/Tk 8.6（tkinter 的底层实现）
- 许可证：BSD 风格许可
- 全文：https://www.tcl.tk/software/tcltk/license.html

## python-zstandard / Zstandard

- 组件：python-zstandard 0.25.0（内含 Zstandard 库）
- 许可证：BSD 3-Clause
- 用途：把「原版 → 补丁版」的差异解码回完整文件

```
BSD License

Copyright (c) Meta Platforms, Inc. and affiliates.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

 * Neither the name Facebook nor the names of its contributors may be used to
   endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## PyInstaller

- 组件：PyInstaller 6.x（打包工具，其 bootloader 会进入 exe）
- 许可证：GPL 2.0，附「bootloader 例外条款」（允许把打包产物按任意许可分发）
- 全文：https://pyinstaller.org/en/stable/license.html

---

以上组件均未修改源码，仅被打包进同一个可执行文件。本仓库自身的代码（`app/fa_godmode.py`）按根目录 `LICENSE` 的 MIT 条款授权。
