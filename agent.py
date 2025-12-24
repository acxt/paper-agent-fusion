"""Paper Agent Fusion - 主入口

这是整个系统的唯一运行文件，定义了LangGraph Agent。

设计原则：
1. 极简 - 只负责"编排"，不负责"执行"
2. 声明式 - 告诉LangGraph"做什么"，不是"怎么做"
3. 可测试 - 纯函数，无副作用
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量
load_load_dotenv()

# ============================================================
# 第1步：定义Agent配置（先不实现具体功能，只搭架子）
# ============================================================

# LLM配置
model = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "gpt-4o"),
    temperature=0.3,  # 略高温度，保持创造性
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

# Agent指令（简洁版）
INSTRUCTIONS = """你是一个学术论文写作Agent。

你的核心原则：
1. **证据先行** - 先检索证据，再决定写什么
2. **引用真实** - 每个观点都有PDF来源
3. **步骤可见** - 让用户看到你的思考过程

工作流程（5步）：
1. Retrieve - 检索相关文献
2. Analyze - 分析证据能支持什么观点
3. Cluster - 将证据按主题分组
4. Write - 根据证据簇写作段落
5. Cite - 映射引用编号

重要：如果证据不足，明确告知，不要硬写。
"""

# ============================================================
# 第2步：定义工具（暂时为空，下一步实现）
# ============================================================

tools = []  # TODO: 下一步添加检索工具

# ============================================================
# 第3步：创建Agent（最简版本）
# ============================================================

# 暂时用最简单的方式创建，验证依赖安装正确
if __name__ == "__main__":
    print("✅ Paper Agent Fusion - 初始化成功!")
    print(f"📦 使用模型: {os.getenv('LLM_MODEL', 'gpt-4o')}")
    print(f"🔧 LangGraph版本: (待添加)")
    print("\n🎯 下一步: 实现证据检索工具")
