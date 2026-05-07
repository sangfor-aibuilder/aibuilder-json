# FastGPT JSON 配置导入功能说明文档

## 概述

FastGPT 支持通过 JSON 配置文件直接创建应用，这一功能允许用户：
1. **快速复用应用配置**：导出已有应用的配置并在其他环境中重建
2. **版本化管理**：将应用配置纳入版本控制系统
3. **批量部署**：通过 JSON 批量创建多个应用
4. **程序化创建**：通过 API 调用动态创建应用

## 功能入口

### 前端界面入口

JSON 导入功能位于 FastGPT 控制台的应用管理页面：

| 入口位置 | 文件路径 |
|---------|---------|
| JSON 导入弹窗组件 | `projects/app/src/pageComponents/dashboard/agent/JsonImportModal.tsx` |
| 应用列表页面 | `projects/app/src/pages/dashboard/agent/index.tsx` |
| 工具列表页面 | `projects/app/src/pages/dashboard/tool/index.tsx` |

### API 接口

| 接口 | 路径 | 方法 |
|------|------|------|
| 创建应用 | `/api/core/app/create` | POST |
| 前端 API 调用 | `projects/app/src/web/core/app/api.ts` | - |

## 应用类型识别机制

系统通过 JSON 中的特定字段自动识别应用类型：

```typescript
// 识别逻辑位于: packages/global/core/app/utils.ts

// 1. 简单应用识别
if ('aiSettings' in config) {
  return 'simple';  // 简单应用
}

// 2. 工作流应用识别
if (config.nodes.some((node) => node.flowNodeType === 'workflowStart')) {
  return 'advanced';  // 工作流应用
}

// 3. 插件/工具应用识别
if (config.nodes.some((node) => node.flowNodeType === 'pluginInput')) {
  return 'plugin';  // 插件应用
}
```

### 支持的导入类型

| 类型 | 标识字段 | 说明 |
|------|---------|------|
| **简单应用** | `aiSettings` | 基于表单配置的简单对话应用 |
| **工作流应用** | `nodes` + `workflowStart` 节点 | 可视化工作流编排的应用 |
| **插件应用** | `nodes` + `pluginInput` 节点 | 可复用的工具/插件 |

## 导入流程

### 1. 简单应用导入流程

```
用户粘贴 JSON → 解析 aiSettings → 调用 form2AppWorkflow() 转换 → 
生成工作流节点和边 → 调用创建 API
```

**转换函数**：`projects/app/src/pageComponents/app/detail/Edit/SimpleApp/utils.ts`
- `form2AppWorkflow()` (第 194-739 行)
- 将简单应用的表单配置转换为完整的工作流节点和边

### 2. 工作流/插件应用导入流程

```
用户粘贴 JSON → 解析 nodes 和 edges → 
验证节点类型和连接 → 调用创建 API
```

## JSON 数据结构

### 简单应用 JSON 结构

```typescript
interface SimpleAppConfig {
  aiSettings: {
    model: string;              // AI 模型名称
    systemPrompt?: string;      // 系统提示词
    temperature?: number;       // 温度参数 (0-2)
    maxToken?: number;          // 最大 Token 数
    isResponseText: boolean;    // 是否返回文本
    maxHistories: number;       // 最大历史轮数
    aiChatReasoning?: boolean;  // 是否开启推理
    aiChatTopP?: number;        // Top-P 参数
    aiChatStopSign?: string;    // 停止符
    aiChatResponseFormat?: string; // 响应格式
    aiChatJsonSchema?: string;  // JSON Schema
    useAgentSandbox?: boolean;  // 是否使用 Agent 沙箱
  };
  dataset: {
    datasets: SelectedDataset[];  // 知识库列表
    searchMode: string;           // 搜索模式
    limit?: number;               // 最大 Token 限制
    similarity?: number;          // 相似度阈值
    embeddingWeight?: number;     // 向量权重
    usingReRank?: boolean;        // 是否使用重排序
    rerankModel?: string;         // 重排序模型
    rerankWeight?: number;        // 重排序权重
    datasetSearchUsingExtensionQuery?: boolean; // 是否使用查询扩展
    datasetSearchExtensionModel?: string;       // 扩展模型
    datasetSearchExtensionBg?: string;          // 扩展背景
    collectionFilterMatch?: string;             // 集合过滤条件
  };
  selectedTools: SelectedTool[];  // 选中的工具列表
  selectedAgentSkills?: SelectedAgentSkill[]; // 选中的 Agent 技能
  chatConfig: AppChatConfig;      // 聊天配置
}
```

### 工作流应用 JSON 结构

```typescript
interface WorkflowAppConfig {
  nodes: StoreNodeItemType[];     // 工作流节点数组
  edges: StoreEdgeItemType[];     // 工作流边数组 (可选)
  chatConfig?: AppChatConfig;     // 聊天配置 (可选)
}
```

## 请求参数说明

### 创建应用 API 请求体

```typescript
interface CreateAppBody {
  parentId?: string | null;       // 父级文件夹 ID
  name: string;                   // 应用名称 (必填)
  avatar?: string;                // 应用头像
  intro?: string;                 // 应用介绍
  type: AppTypeEnum;              // 应用类型 (必填)
  modules: StoreNodeItemType[];   // 工作流节点数组
  edges?: StoreEdgeItemType[];    // 工作流边数组
  chatConfig?: AppChatConfig;     // 聊天配置
  templateId?: string;            // 模板 ID
  utmParams?: ShortUrlParams;     // UTM 参数
}
```

### 应用类型枚举

```typescript
enum AppTypeEnum {
  folder = 'folder',              // 文件夹
  toolFolder = 'toolFolder',      // 工具文件夹
  simple = 'simple',              // 简单应用
  chatAgent = 'chatAgent',        // 对话助手
  workflow = 'advanced',          // 工作流
  workflowTool = 'plugin',        // 插件/工具
  mcpToolSet = 'toolSet',         // MCP 工具集
  httpToolSet = 'httpToolSet',    // HTTP 工具集
  hidden = 'hidden'               // 隐藏应用
}
```

## 工作流节点系统

### 节点基础结构

每个工作流节点包含以下核心属性：

```typescript
interface StoreNodeItemType {
  nodeId: string;                 // 节点唯一 ID
  name: string;                   // 节点名称
  flowNodeType: FlowNodeTypeEnum; // 节点类型
  position?: { x: number; y: number }; // 画布位置
  
  // 可选属性
  parentNodeId?: string;          // 父节点 ID (用于嵌套)
  avatar?: string;                // 节点头像
  avatarLinear?: string;          // 渐变头像
  colorSchema?: NodeColorSchemaEnum; // 配色方案
  intro?: string;                 // 节点介绍
  toolDescription?: string;       // 工具描述
  showStatus?: boolean;           // 是否显示状态
  version?: string;               // 节点版本
  catchError?: boolean;           // 是否捕获错误
  
  // 数据配置
  inputs: FlowNodeInputItemType[];   // 输入配置数组
  outputs: FlowNodeOutputItemType[]; // 输出配置数组
  
  // 插件相关
  pluginId?: string;              // 插件 ID
  pluginData?: ToolData;          // 插件数据
  toolConfig?: NodeToolConfig;    // 工具配置
}
```

### 边的结构

```typescript
interface StoreEdgeItemType {
  source: string;                 // 源节点 ID
  sourceHandle: string;           // 源节点连接点 ID
  target: string;                 // 目标节点 ID
  targetHandle: string;           // 目标节点连接点 ID
}
```

## 聊天配置 (ChatConfig)

```typescript
interface AppChatConfig {
  welcomeText?: string;           // 欢迎语
  variables?: VariableItem[];     // 全局变量列表
  autoExecute?: AutoExecuteConfig; // 自动执行配置
  questionGuide?: QuestionGuideConfig; // 问题引导配置
  ttsConfig?: TTSConfig;          // 语音合成配置
  whisperConfig?: WhisperConfig;  // 语音识别配置
  scheduledTriggerConfig?: ScheduledTriggerConfig; // 定时触发配置
  chatInputGuide?: ChatInputGuideConfig; // 输入引导配置
  fileSelectConfig?: FileSelectConfig;   // 文件选择配置
  instruction?: string;           // 使用说明
}
```

## 使用示例

### 1. 通过前端界面导入

1. 进入 FastGPT 控制台
2. 点击"新建应用"或"导入"
3. 选择"JSON 导入"选项
4. 粘贴或上传 JSON 配置文件
5. 系统自动识别类型并创建应用

### 2. 通过 API 导入

```bash
curl -X POST https://your-fastgpt.com/api/core/app/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "name": "我的AI助手",
    "type": "advanced",
    "modules": [...],
    "edges": [...],
    "chatConfig": {...}
  }'
```

## 注意事项

1. **节点 ID 唯一性**：所有节点的 `nodeId` 必须在整个工作流中唯一
2. **边连接有效性**：`source` 和 `target` 必须对应存在的节点 ID
3. **输入引用格式**：引用其他节点输出的格式为 `['节点ID', '输出KEY']`
4. **知识库引用**：导入时引用的知识库 ID 必须存在于当前团队中
5. **模型可用性**：配置的 AI 模型必须在系统中已配置可用

## 相关文件路径

### 核心类型定义

| 文件 | 说明 |
|------|------|
| `packages/global/core/app/type.ts` | 应用核心类型定义 |
| `packages/global/core/app/formEdit/type.ts` | 简单应用表单类型 |
| `packages/global/core/workflow/type/node.ts` | 工作流节点类型 |
| `packages/global/core/workflow/type/edge.ts` | 工作流边类型 |
| `packages/global/core/workflow/type/io.ts` | 输入输出类型 |

### 节点模板定义

| 文件 | 说明 |
|------|------|
| `packages/global/core/workflow/template/system/workflowStart.ts` | 工作流开始节点 |
| `packages/global/core/workflow/template/system/aiChat/index.ts` | AI 对话节点 |
| `packages/global/core/workflow/template/system/datasetSearch.ts` | 知识库搜索节点 |
| `packages/global/core/workflow/template/system/toolCall.ts` | 工具调用节点 |
| `packages/global/core/workflow/template/system/http468.ts` | HTTP 请求节点 |
| `packages/global/core/workflow/template/system/sandbox/index.ts` | 代码执行节点 |
| `packages/global/core/workflow/template/system/classifyQuestion/index.ts` | 问题分类节点 |

### 前端实现

| 文件 | 说明 |
|------|------|
| `projects/app/src/pageComponents/dashboard/agent/JsonImportModal.tsx` | JSON 导入弹窗 |
| `projects/app/src/pageComponents/app/ImportAppConfigEditor.tsx` | 配置编辑器 |
| `projects/app/src/pages/api/core/app/create.ts` | 创建应用 API |

## 版本兼容性

- 工作流节点包含 `version` 字段用于版本管理
- 系统会根据版本号自动处理兼容性问题
- 建议在 JSON 中明确指定节点版本

---

*文档基于 FastGPT 源代码生成，最后更新日期：2025年*
