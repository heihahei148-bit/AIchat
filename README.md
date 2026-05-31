# AIchat

AIchat 是一个基于 Streamlit 和 DeepSeek API 的本地 AI 聊天应用。它内置“编程导师”提示词，可以用温和、细致的方式解释 Python、爬虫、FastAPI、SQLAlchemy 等学习问题，并支持本地保存与切换历史会话。

## 功能特点

- 基于 Streamlit 构建，启动简单，适合本地学习和演示。
- 使用 DeepSeek Chat 模型进行流式回复。
- 支持配置导师昵称和性格，让回复风格更贴近使用习惯。
- 自动保存本地会话记录，并可在侧边栏切换或删除历史会话。
- 支持 `.env` 环境变量配置，避免把 API 密钥写进代码。

## 项目结构

```text
AIchat/
├── logo/                  # 应用 logo
├── partner.py             # Streamlit 主程序
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略规则
└── README.md              # 项目说明
```

运行后会在本地生成 `sessions/` 目录保存聊天记录。该目录包含个人会话数据，默认不会提交到 GitHub。

## 环境要求

- Python 3.10 或更高版本
- DeepSeek API Key

## 快速开始

1. 克隆项目：

```bash
git clone https://github.com/heihahei148-bit/AIchat.git
cd AIchat
```

2. 创建并激活虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置密钥。

复制 `.env.example` 为 `.env`，然后填写自己的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
```

`DEEPSEEK_MODEL` 是可选配置，不填写时默认使用 `deepseek-chat`。

5. 启动应用：

```bash
streamlit run partner.py
```

浏览器打开终端中显示的本地地址，一般是 `http://localhost:8501`。

## 密钥配置方式

推荐使用 `.env` 文件配置密钥：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

也可以直接配置系统环境变量。

Windows PowerShell 临时配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
streamlit run partner.py
```

macOS / Linux 临时配置：

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
streamlit run partner.py
```

请不要把真实 API Key 提交到 GitHub。项目已经在 `.gitignore` 中忽略 `.env` 和 `.streamlit/secrets.toml`。

## 常见问题

### `st.session_state has no attribute "current_session"`

这个错误通常是因为在初始化会话状态之前读取了 `st.session_state.current_session`。当前版本已经把初始化逻辑集中到 `init_session_state()`，页面渲染前会先创建 `messages`、`nick_name`、`nature` 和 `current_session`。

### 页面提示没有配置 `DEEPSEEK_API_KEY`

说明当前运行环境没有读到密钥。请确认：

- `.env` 文件位于项目根目录。
- 变量名是 `DEEPSEEK_API_KEY`。
- 启动命令是在项目根目录执行的。

## 开发说明

本项目的聊天记录默认保存在本地 `sessions/` 目录。为了保护隐私，该目录不会被 Git 追踪。如果需要迁移历史会话，可以手动备份该目录。
