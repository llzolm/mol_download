# MOL文件批量下载工具 - 云端部署版本

基于PubChem数据库的MOL文件批量下载工具，支持Excel文件批量上传。

## 目录结构

```
├── mol_downloader_server_cloud.py  # Flask后端服务器（云端版）
├── requirements.txt               # Python依赖
├── Procfile                       # Railway部署配置
├── static/
│   └── index.html                 # 前端页面
├── .gitignore                     # Git忽略配置
└── README.md                      # 本文件
```

## 部署步骤（Railway）

### 1. 创建GitHub仓库

1. 访问 [GitHub](https://github.com) 并登录
2. 点击右上角 **"+"** → **"New repository"**
3. 仓库名称输入 `mol-downloader`
4. 选择 **Public**（或Private）
5. 点击 **Create repository**

### 2. 上传代码

在仓库页面，点击 **"uploading an existing file"**，将以下文件拖入：
- `mol_downloader_server_cloud.py`
- `requirements.txt`
- `Procfile`
- `static/index.html`
- `.gitignore`

点击 **Commit changes**。

### 3. 部署到Railway

1. 访问 [Railway](https://railway.app) 并登录（可用GitHub账号）
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 选择刚才创建的仓库 `mol-downloader`
5. Railway会自动检测Procfile并部署

### 4. 获取访问地址

部署完成后，Railway会提供一个URL，格式如：
```
https://mol-downloader-production.up.railway.app
```

这就是你的云端访问地址，发送给任何人即可使用，无需安装Python！

## 使用方法

1. 打开部署好的网站链接
2. 上传包含化合物名称的Excel文件（.xlsx, .xls, .csv）
3. 选择化合物名称列
4. 点击"开始下载"
5. 下载完成后点击"下载ZIP"保存文件

## 费用说明

- Railway免费套餐：每月500小时运行时间
- 个人使用完全足够
- 如果需要24小时运行，可考虑付费套餐

## 备选平台

如果Railway不可用，可选择：
- **Render**: https://render.com （免费套餐可用）
- **PythonAnywhere**: https://pythonanywhere.com
- **Heroku**: https://heroku.com （免费套餐已取消）
