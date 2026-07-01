# 🪣 scoop-bucket

自建 [Scoop](https://scoop.sh) 软件源，每 6 小时自动爬取上游 Release，保持 manifest 最新。

对标的参考实现: [Scoopforge/Extras-CN](https://github.com/Scoopforge/Extras-CN)

---

## 📦 收录清单

| 软件 | 描述 | 主程序 | 安装方式 |
|------|------|--------|----------|
| [warp-cn](https://github.com/Heartcoolman/warp-cn) | Warp 终端 · 中文本地化社区版 | `warp-oss.exe` | InnoSetup 提取 |

**warp-cn 安装目录结构**（scoop 通过 `innosetup: true` 提取安装包）:

```
~\scoop\apps\warp-cn\current\
├── bin\warp-oss.cmd        ← CLI 入口（由安装器创建，scoop 提取时不可用）
├── resources\               ← 内置资源
├── x64\OpenConsole.exe      ← ConPTY 后端
├── warp-oss.exe             ← 主程序（355MB）
├── conpty.dll / dxcompiler.dll / dxil.dll  ← 运行时依赖
├── msvcp140.dll / vcruntime140.dll / vcruntime140_1.dll
├── icon.ico / pwsh.ps1
└── unins000.exe / unins000.dat
```

---

## 🔧 使用方法

### 添加 bucket

```powershell
scoop bucket add scoop-bucket https://github.com/sixiang-world/scoop-bucket
```

### 安装软件

```powershell
# 安装 warp-cn
scoop install scoop-bucket/warp-cn

# 更新所有软件
scoop update scoop-bucket

# 仅更新 warp-cn
scoop update warp-cn
```

### 直接安装（不添加 bucket）

```powershell
scoop install https://raw.githubusercontent.com/sixiang-world/scoop-bucket/main/bucket/warp-cn.json
```

### 本地 checkver（需安装 Scoop）

```powershell
# 检查是否有新版本
.\bin\checkver.ps1 -Dir bucket

# 检查并自动更新 manifest
.\bin\checkver.ps1 -Dir bucket -Update
```

---

## 🤖 自动更新机制

| 层级 | 方式 | 频率 |
|------|------|------|
| **GitHub Actions** | `update-bucket.yml` — 矩阵化 Python 脚本，自动检测 Release → 下载计算 SHA256 → 提交 | 每 6 小时 |
| **Scoop checkver** | manifest 中配置 `checkver.github` + `hash.mode: download`，本地 `scoop update` 时生效 | 用户触发 |
| **手动触发** | GitHub → Actions → `Auto-Update Bucket` → Run workflow | 随时 |

### CI 流程

```
定时触发 / 手动触发
       │
       ▼
  Python 更新脚本
  ────────────────
  1. 调用 GitHub API 获取最新 Release
  2. 对比 manifest 当前版本
  3. 有新版本 → 下载安装包 → 计算 SHA256
  4. 更新 manifest（version + url + hash）
       │
       ▼
  git diff 检查是否有变更
       │
       ▼
  有变更 → git commit + push
```

---

## 🧩 新增软件源

参考步骤：

1. **创建 manifest** `bucket/<app>.json`

   必须包含 `checkver` 和 `autoupdate` 字段。参考格式:

   ```json
   {
       "version": "x.y.z",
       "description": "描述",
       "homepage": "https://github.com/user/repo",
       "license": "Proprietary",
       "architecture": {
           "64bit": {
               "url": "https://github.com/user/repo/releases/download/v$version/AppSetup.exe",
               "hash": "sha256hex"
           }
       },
       "innosetup": true,
       "bin": "app.exe",
       "shortcuts": [["app.exe", "App 名称"]],
       "checkver": { "github": "https://github.com/user/repo" },
       "autoupdate": {
           "architecture": {
               "64bit": {
                   "url": "https://github.com/user/repo/releases/download/v$version/AppSetup.exe",
                   "hash": { "mode": "download" }
               }
           }
       }
   }
   ```

2. **创建更新脚本** `scripts/update-<app>.py`

   可参考 `scripts/update-warp-cn.py` 编写，核心逻辑:
   - 调用 GitHub API 获取最新 Release 信息
   - 下载安装包 → 计算 SHA256
   - 更新 manifest JSON

3. **注册到 CI** — 在 `.github/workflows/update-bucket.yml` 的 `matrix.app` 中添加名称

---

## 📋 前置要求

- 安装 [Scoop](https://scoop.sh/)（Windows 包管理器）

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```
