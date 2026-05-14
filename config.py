# config.py
import streamlit as st
import os

ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
MODEL_NAME = "glm-4-flash"

def get_zhipu_api_key():
    """
    获取智谱API Key，优先从Streamlit的secrets中读取。
    如果本地没有secrets.toml，会尝试从环境变量中读取。
    """
    # 1. 尝试从 Streamlit secrets 读取（云端部署）
    try:
        api_key = st.secrets["ZHIPU_API_KEY"]
        print("正在使用 Streamlit secrets 中的 API Key")
        return api_key
    except Exception:
        pass
    
    # 2. 尝试从环境变量读取（本地开发，不推荐硬编码）
    api_key = os.environ.get("ZHIPU_API_KEY")
    if api_key:
        print("正在使用环境变量中的 API Key")
        return api_key
    
    # 3. 如果都没有，抛出明确错误
    raise Exception("❌ 无法找到智谱 API Key。请配置 Streamlit secrets 或环境变量 ZHIPU_API_KEY")

# 获取 API Key（不再硬编码）
ZHIPU_API_KEY = get_zhipu_api_key()