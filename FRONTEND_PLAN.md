# 前端方案设计

## 架构概览

```
paper-agent-fusion/
├── backend/                    # 后端（刚才创建的）
│   ├── agent.py               # LangGraph Agent
│   ├── core/                  # 证据引擎
│   └── tools/                 # Agent工具
│
├── frontend/                   # 前端（从deep-agents-ui迁移）
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── EvidenceFlow.vue      # ⭐ 证据流程可视化
│   │   │   ├── StepCard.vue          # 单步显示
│   │   │   ├── CitationViewer.vue    # 引用查看器
│   │   │   └── SectionEditor.vue     # 章节编辑器
│   │   ├── stores/
│   │   │   └── paperStore.ts         # Pinia状态管理
│   │   └── api/
│   │       └── client.ts             # 后端API调用
│   └── public/
│
└── README.md
```

## 前后端通信设计

### API端点设计（极简版）

```typescript
// frontend/src/api/client.ts

export interface PaperConfig {
  title: string;
  outline: string;
  dataSources: string[];  // ["local", "online"]
}

export interface EvidenceStep {
  step: 1 | 2 | 3 | 4 | 5;
  name: "Retrieve" | "Analyze" | "Cluster" | "Write" | "Cite";
  status: "pending" | "running" | "completed" | "error";
  data: any;
}

// 主API调用
export const api = {
  // 开始写作
  async startWriting(config: PaperConfig) {
    return fetch("/api/paper/start", {
      method: "POST",
      body: JSON.stringify(config)
    });
  },

  // 获取实时进度（SSE）
  streamProgress(paperId: string) {
    return new EventSource(`/api/paper/${paperId}/stream`);
  },

  // 重新执行某一步
  async regenerateStep(paperId: string, step: number) {
    return fetch(`/api/paper/${paperId}/step/${step}/regenerate`, {
      method: "POST"
    });
  }
};
```

### 后端API实现（FastAPI）

```python
# backend/api.py (新增文件)

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio

app = FastAPI()

class PaperConfig(BaseModel):
    title: str
    outline: str
    data_sources: list[str]

@app.post("/api/paper/start")
async def start_writing(config: PaperConfig):
    """开始论文写作"""
    # TODO: 调用agent.py的LangGraph Agent
    return {"paper_id": "xxx", "status": "started"}

@app.get("/api/paper/{paper_id}/stream")
async def stream_progress(paper_id: str):
    """SSE流式推送进度"""
    async def event_generator():
        # 模拟5步流程
        steps = ["Retrieve", "Analyze", "Cluster", "Write", "Cite"]
        for i, step in enumerate(steps, 1):
            yield f"data: {{'step': {i}, 'name': '{step}', 'status': 'running'}}\n\n"
            await asyncio.sleep(2)
            yield f"data: {{'step': {i}, 'name': '{step}', 'status': 'completed'}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/paper/{paper_id}/step/{step}/regenerate")
async def regenerate_step(paper_id: str, step: int):
    """重新生成某一步"""
    return {"status": "regenerating", "step": step}
```

## UI组件设计（5个核心组件）

### 1. EvidenceFlow.vue - 证据流程可视化

```vue
<template>
  <div class="evidence-flow">
    <h2>📊 证据驱动写作流程</h2>

    <div class="steps">
      <StepCard
        v-for="step in steps"
        :key="step.id"
        :step="step"
        @regenerate="handleRegenerate"
      />
    </div>

    <div class="evidence-report">
      <h3>📝 证据报告</h3>
      <p>使用证据: {{ usedEvidence.length }}条</p>
      <p>覆盖率: {{ coverageRate }}%</p>
      <p>证据缺口: {{ gaps.join(', ') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const steps = ref([
  { id: 1, name: "Retrieve", status: "completed", data: {...} },
  { id: 2, name: "Analyze", status: "running", data: null },
  { id: 3, name: "Cluster", status: "pending", data: null },
  { id: 4, name: "Write", status: "pending", data: null },
  { id: 5, name: "Cite", status: "pending", data: null },
]);

function handleRegenerate(stepId: number) {
  api.regenerateStep(currentPaperId, stepId);
}
</script>
```

### 2. StepCard.vue - 单步展示

```vue
<template>
  <div class="step-card" :class="step.status">
    <div class="step-header">
      <span class="step-number">{{ step.id }}</span>
      <h3>{{ step.name }}</h3>
      <span class="status-badge">{{ step.status }}</span>
    </div>

    <div class="step-content" v-if="step.data">
      <!-- 根据不同步骤显示不同内容 -->
      <div v-if="step.name === 'Retrieve'">
        <p>检索到 {{ step.data.docs.length }} 条证据</p>
        <ul>
          <li v-for="doc in step.data.docs.slice(0, 3)">
            {{ doc.source }} (p.{{ doc.page }})
          </li>
        </ul>
      </div>

      <div v-if="step.name === 'Analyze'">
        <p>可写主题: {{ step.data.available_themes.join(', ') }}</p>
        <p class="text-red">证据缺口: {{ step.data.gaps.join(', ') }}</p>
      </div>
    </div>

    <button @click="$emit('regenerate', step.id)" class="btn-regenerate">
      🔄 重新生成本步
    </button>
  </div>
</template>
```

### 3. CitationViewer.vue - 引用查看器

```vue
<template>
  <div class="citation-viewer">
    <h3>📚 引用列表</h3>

    <div v-for="citation in citations" :key="citation.id" class="citation-item">
      <span class="citation-number">[{{ citation.id }}]</span>
      <span class="citation-source">{{ citation.source }}</span>
      <span class="citation-page">p.{{ citation.page }}</span>
      <button @click="viewPDF(citation.source, citation.page)">
        查看PDF
      </button>
    </div>

    <div class="citation-stats">
      <p>总引用数: {{ citations.length }}</p>
      <p>引用覆盖率: 100%</p>
    </div>
  </div>
</template>
```

## 迁移步骤（3步完成）

### Step 1: 复制deep-agents-ui基础

```bash
# 1. 复制agents项目的UI
cp -r /path/to/agents/deep-agents-ui /path/to/paper-agent-fusion/frontend

# 2. 清理不需要的组件
cd frontend/src/components
rm -rf Chat.vue Research.vue  # 删除不相关组件

# 3. 保留核心框架
# 保留: App.vue, router, stores
```

### Step 2: 创建新组件

```bash
# 创建证据流程相关组件
frontend/src/components/
├── EvidenceFlow.vue      # 主流程可视化
├── StepCard.vue          # 单步卡片
├── CitationViewer.vue    # 引用查看
└── SectionEditor.vue     # 章节编辑
```

### Step 3: 连接后端API

```typescript
// frontend/src/api/client.ts
const API_BASE = "http://localhost:8000";  // FastAPI后端

export const api = {
  startWriting: (config) => fetch(`${API_BASE}/api/paper/start`, ...),
  streamProgress: (paperId) => new EventSource(`${API_BASE}/api/paper/${paperId}/stream`),
};
```

## 开发服务器启动

```bash
# 后端 (端口8000)
cd paper-agent-fusion
uv run uvicorn backend.api:app --reload

# 前端 (端口3000)
cd frontend
npm run dev
```

## 前后端集成验证

1. 后端启动：`http://localhost:8000`
2. 前端启动：`http://localhost:3000`
3. 前端调用：`/api/paper/start`
4. 后端响应：返回paper_id
5. SSE连接：实时推送5步进度

---

## 为什么分前后端？

1. **开发效率**: 后端和前端可以并行开发
2. **技术解耦**: Python后端 + Vue前端，各自用最适合的技术
3. **部署灵活**: 后端可以部署到LangGraph Cloud，前端部署到Vercel
4. **测试独立**: 后端用pytest，前端用Vitest

---

## 下一步（Milestone 2更新）

### 原计划
- ⏳ Milestone 2: 证据引擎核心

### 新计划（分成2.1和2.2）
- ⏳ Milestone 2.1: 后端证据引擎（今天）
- ⏳ Milestone 2.2: 前端UI复用（明天）

---

**总结**：

前端方案已补充完整！现在我们有：
- ✅ 后端：Python + LangGraph + 证据引擎
- ✅ 前端：Vue3 + 复用deep-agents-ui
- ✅ 通信：FastAPI + SSE实时推送

准备好继续吗？我现在可以：
1. 先完成后端核心（citations.py + evidence.py）
2. 或者先搭建前端框架（复制deep-agents-ui）

你想先做哪个？
