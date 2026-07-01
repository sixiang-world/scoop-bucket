# 🪣 scoop-bucket

自建 [Scoop](https://scoop.sh) 软件源，定期自动爬取维护社区软件。

## 📦 当前收录

| 软件 | 描述 | 版本 |
|------|------|------|
| [warp-cn](https://github.com/Heartcoolman/warp-cn) | Warp 客户端中文本地化 & 自定义改造 | [![warp-cn](https://img.shields.io/github/v/release/Heartcoolman/warp-cn?label=)](https://github.com/Heartcoolman/warp-cn/releases) |

## 🔧 使用方式

```powershell
# 添加本 bucket
scoop bucket add scoop-bucket https://github.com/sixiang-world/scoop-bucket

# 安装软件
scoop install scoop-bucket/warp-cn
```

或者直接安装：

```powershell
scoop install https://raw.githubusercontent.com/sixiang-world/scoop-bucket/main/bucket/warp-cn.json
```

## 🤖 自动更新机制

每个 manifest 都配置了：

- **`checkver`** — 通过 GitHub Release API 自动检测新版本（本地 `scoop update scoop-bucket` 时触发）
- **`autoupdate`** — 新版本下载 URL 自动生成
- **GitHub Actions** — 每 6 小时自动检查上游 Release，有新版时自动更新 manifest 并提交

## 🧩 贡献新软件源

想加入新软件？提 Issue 或 PR，需提供：

1. 项目主页（GitHub / 官网）
2. Windows 安装包或便携版的下载地址
3. 版本检测方式（Release tag / 网页）

## 📋 前置要求

- 安装 [Scoop](https://scoop.sh/)（Windows 包管理器）

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```
