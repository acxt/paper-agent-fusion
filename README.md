# Paper Agent Fusion

**证据驱动的学术论文写作Agent系统**

## 核心特性

- ✅ **证据先行**：先检索证据 → 分析能写什么 → 根据证据写作
- ✅ **引用可追溯**：每个观点都有真实PDF来源（文件名+页码）
- ✅ **LangGraph编排**：并行写作多个章节，状态可持久化
- ✅ **极简设计**：核心代码 < 500行，易维护

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp .env.example .env
# 编辑.env填入OPENAI_API_KEY

# 3. 放入参考论文
cp your_papers/*.pdf data/papers/

# 4. 运行Agent
uv run python agent.py
```

## 架构设计

```
证据驱动5步流程：
1. Retrieve  - 检索相关证据
2. Analyze   - 分析能写什么
3. Cluster   - 证据按主题分组
4. Write     - 根据证据簇写作
5. Cite      - 映射引用编号
```

## 项目结构

- `agent.py` - LangGraph Agent主入口
- `core/` - 证据引擎核心（from files方案）
- `tools/` - Agent工具集
- `data/` - 论文和向量库

## 技术栈

- LangChain 1.1 + LangGraph 1.0.3
- Python 3.13 + uv包管理
- FAISS向量检索

---

**Version**: 0.1.0 (MVP)
**License**: MIT
