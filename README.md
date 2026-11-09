# Fading Afternoon 无伤补丁 · God Mode 无敌修改器（日落西山）

给 Steam 游戏 **Fading Afternoon**（AppID `1687000`，也有人叫它「日落西山」）做的**玩家无伤 / 无敌补丁**。

效果一句话：**玩家怎么打都不掉血**；游戏里按 `K` 关掉，再按一下开回来；无敌时血条旁边会显示绿色 `GOD`。敌人不受影响，照样掉血。

> **一个 exe，双击就能用**：下载 → 双击 → 点「安装补丁」。
> 不联网、不用装任何东西、不用命令行。

---

## 搜索关键词 / Keywords

中文：Fading Afternoon 无伤 无敌 不掉血 修改器 补丁 上帝模式 内挂 金手指 血量锁定 角色无敌 日落西山 怎么开无敌 血量不减 一键安装 exe 教程

English: Fading Afternoon god mode, no damage mod, invincible player, trainer, cheat, health lock, Steam 1687000, yeo, offline installer

---

## 下载

[**Releases → `FadingAfternoon-GodMode.exe`**](https://github.com/luoxh8/fading-afternoon-godmode/releases/latest)（12 MB）

校验值（想确认没下坏的话）：

```
SHA256  91b66147d269991621009f0f68d8b0aa984c80dc0441ec7cd8c1924279e902d3
```

Windows 上比对：`certutil -hashfile FadingAfternoon-GodMode.exe SHA256`

---

## 怎么用（三步）

1. **双击 `FadingAfternoon-GodMode.exe`**
2. 它会自动找到你的游戏目录（找不到就点「浏览…」，选 Fading Afternoon 的安装目录——里面有 `data.win`）
3. 点 **「安装补丁」**，等几秒，看到「完成」就好了

再打开游戏就是无敌。想还原，点 **「还原原版」**。

界面上会显示当前状态：

- `已安装（进游戏就是无敌）` —— 已经是补丁版
- `原版，可以安装` —— 干净的，可以装
- `版本不匹配或文件异常` —— 见下面「版本对不上」

---

## 支持的版本

补丁是**按游戏版本做的**。

| 项目 | 值 |
| --- | --- |
| Steam AppID | 1687000 |
| 制作时的 buildid | `21324752` |
| 原版 `data.win` 大小 | 706,180,856 字节 |
| 原版 SHA256 | `5efe323a…c76e14ccc4` |
| 打完补丁后 SHA256 | `9c2155a4…3848d2c5a554a6` |

动手前会先算你 `data.win` 的 SHA256，**只有和上表完全一致才会改**。不一致就停手，一个字节不动。

---

## 版本对不上怎么办

游戏更新之后，你机器上的 `data.win` 会变成新版本，补丁就对不上了。程序会直接告诉你，并且不动你的文件。

去 Releases 看有没有对应你版本的新补丁；没有的话，把日志里那两行哈希贴到 issue，我按你的版本重做一份。

---

## 常见问题

**Q：为什么才 12 MB，游戏文件 700 多 MB？**
因为不发游戏文件。exe 里只有「原版 → 打完补丁」的差异（840 KB），用你自己机器上那份 `data.win` 现场还原出补丁版。

**Q：这算不算分发游戏内容？**
不算。里面没有游戏任何资源，只有一个差异包；没有你本机那份原版文件，这个差异解不出任何东西。

**Q：杀毒软件报警？**
exe 是 Python 打包的单文件程序，有些杀软对这类壳敏感（误报）。加白名单即可；介意的话可以自己按 `app/` 里的源码重新打包。

**Q：装完进游戏没反应 / 血量照掉？**
日志最后出现 `已替换 data.win。` 才算成功；显示别的就把日志截图发 issue。

**Q：为什么不能像别的 mod 那样把文件丢进目录就完事？**
这个游戏不支持外部 mod 加载，代码和资源都在一个文件里，只能改它本身。

**Q：会不会影响成就 / 存档？**
不碰存档结构，也不碰 Steam 统计，成就照拿。

**Q：要多少内存 / 磁盘？**
打补丁时峰值内存约 1.4 GB，磁盘要留 900 MB 临时空间（要写出新的 706 MB 文件），完事自动清掉。

**Q：GitHub 下载很慢 / 断在半路？**
Release 附件走 GitHub 的 CDN，国内直连经常断。挂代理最稳，或者换手机热点再试。

---

## 源码

`app/fa_godmode.py` 就是 exe 的全部源码（Python + tkinter，界面和打补丁逻辑都在里面），`app/payload/` 是打包进 exe 的差异包。第三方组件许可见 `THIRD-PARTY-NOTICES.md`。

---

## English

A **god mode / no-damage patch** for *Fading Afternoon* (Steam AppID 1687000). Press `K` in game to toggle; a green `GOD` appears next to the HP bar while active. Enemies are unaffected.

Download `FadingAfternoon-GodMode.exe`, run it, click **安装补丁 (Install)**. It locates your game, verifies the SHA256 of `data.win`, applies an 840 KB binary delta, and verifies the result — no extra tools, no .NET, no internet. **还原原版 (Restore)** puts the original file back, byte-identical.

The patch targets game build `21324752`; after a game update it refuses to touch your file rather than risk damage.

---

## 免责

单人游戏、自己机器上自娱用。本仓库只提供差异包与安装程序，**不分发游戏本体任何资源**。出问题先点「还原原版」，或用 Steam 验证文件完整性还原。
