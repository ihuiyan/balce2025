# Deepseek API 配置
import os

# 优先从环境变量读取
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', "sk-395d444899dd4c6da3f049ab30e10db2")
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', "https://api.deepseek.com")
