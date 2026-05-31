from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


APP_TITLE = "AI 智能聊天"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
SESSION_DIR = Path("sessions")
LOGO_PATH = Path("logo/cloudlogo_1770558332_1024x1024.jpeg")

SYSTEM_PROMPT_TEMPLATE = """
你是一位拥有 10 年以上实战经验的 Python 高级工程师兼全栈开发专家。
你现在是用户的专属编程老师，需要耐心、细致、温和地帮助用户学习 Python、爬虫、FastAPI 和 SQLAlchemy 等内容。

你的教学准则：
1. 极致耐心，逐行拆解：当用户发来代码、API 调用或报错信息时，请解释“是什么”“为什么这么写”“起到了什么作用”。
2. 善用比喻，降低理解门槛：遇到 JWT、装饰器、多线程、ORM 等术语时，用生活中的例子帮助用户理解。
3. 授人以渔，拓展认知：回答具体问题后，补充相关最佳实践或工程习惯。
4. 温和鼓励，提供情绪价值：用亲切、积极的语气回应用户。
5. 代码规范：示例代码遵循 PEP 8，关键行配上清晰中文注释。

性格：{nature}
昵称：{nick_name}
"""


def create_session_name() -> str:
    """Create a readable and mostly unique session name."""
    return dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def init_session_state() -> None:
    defaults: dict[str, Any] = {
        "messages": [],
        "nick_name": "王老师",
        "nature": "温柔",
        "current_session": create_session_name(),
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def load_sessions() -> list[str]:
    if not SESSION_DIR.exists():
        return []

    sessions = [
        file_path.stem
        for file_path in SESSION_DIR.iterdir()
        if file_path.is_file() and file_path.suffix == ".json"
    ]
    return sorted(sessions, reverse=True)


def save_session() -> None:
    SESSION_DIR.mkdir(exist_ok=True)
    session_data = {
        "current_session": st.session_state["current_session"],
        "nick_name": st.session_state["nick_name"],
        "nature": st.session_state["nature"],
        "messages": st.session_state["messages"],
    }
    session_path = SESSION_DIR / f"{st.session_state['current_session']}.json"
    session_path.write_text(
        json.dumps(session_data, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def load_session(session_name: str) -> None:
    session_path = SESSION_DIR / f"{session_name}.json"
    if not session_path.exists():
        st.warning("这个历史会话文件不存在，可能已经被删除。")
        return

    try:
        session_data = json.loads(session_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        st.error("加载会话失败，请检查会话文件是否完整。")
        return

    st.session_state["current_session"] = session_data.get(
        "current_session",
        session_name,
    )
    st.session_state["nick_name"] = session_data.get("nick_name", "王老师")
    st.session_state["nature"] = session_data.get("nature", "温柔")
    st.session_state["messages"] = session_data.get("messages", [])


def delete_session(session_name: str) -> None:
    session_path = SESSION_DIR / f"{session_name}.json"
    try:
        session_path.unlink(missing_ok=True)
    except OSError:
        st.error("删除会话失败，请确认文件没有被其他程序占用。")
        return

    if session_name == st.session_state["current_session"]:
        st.session_state["messages"] = []
        st.session_state["current_session"] = create_session_name()
        save_session()


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def get_model_name() -> str:
    return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def render_history() -> None:
    for message in st.session_state["messages"]:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        st.chat_message(role).write(content)


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("会话控制面板")

        has_messages = bool(st.session_state["messages"])
        if st.button(
            "新建会话",
            width="stretch",
            icon="🔄",
            disabled=not has_messages,
            help="当前会话有聊天内容后才能新建会话。",
        ):
            save_session()
            st.session_state["messages"] = []
            st.session_state["current_session"] = create_session_name()
            st.rerun()

        st.text("历史会话")
        for session in load_sessions():
            col1, col2 = st.columns([4, 1])
            is_current_session = session == st.session_state["current_session"]

            with col1:
                if st.button(
                    session,
                    width="stretch",
                    icon="💬",
                    key=f"load_{session}",
                    type="primary" if is_current_session else "secondary",
                ):
                    load_session(session)
                    st.rerun()

            with col2:
                if st.button(
                    "",
                    width="stretch",
                    icon="❌",
                    key=f"delete_{session}",
                ):
                    delete_session(session)
                    st.rerun()

        st.divider()
        st.subheader("导师信息")

        st.session_state["nick_name"] = st.text_input(
            "昵称",
            placeholder="请输入昵称",
            value=st.session_state["nick_name"],
        )
        st.session_state["nature"] = st.text_area(
            "性格",
            placeholder="请输入性格",
            value=st.session_state["nature"],
        )


def stream_ai_response(client: OpenAI, prompt: str) -> None:
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        nature=st.session_state["nature"],
        nick_name=st.session_state["nick_name"],
    )
    response_placeholder = st.empty()
    full_response = ""

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state["messages"],
            ],
            stream=True,
        )

        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                response_placeholder.chat_message("assistant").write(full_response)
    except Exception as exc:
        st.session_state["messages"].pop()
        st.error(f"调用 DeepSeek API 失败：{exc}")
        return

    st.session_state["messages"].append(
        {"role": "assistant", "content": full_response},
    )
    save_session()


def main() -> None:
    load_dotenv()

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={},
    )
    init_session_state()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if LOGO_PATH.exists():
        st.logo(str(LOGO_PATH))

    st.title(APP_TITLE)
    st.caption(f"当前会话名称：{st.session_state['current_session']}")

    render_sidebar()
    render_history()

    if not api_key:
        st.warning("请先配置 DEEPSEEK_API_KEY 后再开始聊天。配置方式见 README.md。")
        st.chat_input("请输入你的内容", disabled=True)
        return

    prompt = st.chat_input("请输入你的内容")
    if prompt:
        stream_ai_response(get_client(api_key), prompt)


if __name__ == "__main__":
    main()
