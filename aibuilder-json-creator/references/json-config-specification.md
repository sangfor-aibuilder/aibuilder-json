# FastGPT JSON 配置规范准则文档

> 本文档提供 FastGPT 通过 JSON 配置创建应用的完整规范说明。遵循本文档可以生成符合规范、可直接导入的 JSON 配置文件。

## 目录

1. [基础结构规范](#1-基础结构规范)
2. [应用类型定义](#2-应用类型定义)
3. [简单应用配置规范](#3-简单应用配置规范)
4. [工作流应用配置规范](#4-工作流应用配置规范)
5. [节点配置详细规范](#5-节点配置详细规范)
6. [输入项配置规范](#6-输入项配置规范)
7. [输出项配置规范](#7-输出项配置规范)
8. [边连接配置规范](#8-边连接配置规范)
9. [聊天配置规范](#9-聊天配置规范)
10. [变量配置规范](#10-变量配置规范)
11. [完整配置示例](#11-完整配置示例)
12. [验证检查清单](#12-验证检查清单)

---

## 1. 基础结构规范

### 1.1 根对象结构

FastGPT 支持两种根对象结构，系统自动识别：

#### 类型 A：简单应用 (Simple App)

```json
{
  "aiSettings": { ... },      // 必填：AI 配置对象
  "dataset": { ... },         // 可选：知识库配置
  "selectedTools": [...],     // 可选：工具列表
  "chatConfig": { ... }       // 可选：聊天配置
}
```

**识别规则**：根对象包含 `aiSettings` 字段时，识别为简单应用。

#### 类型 B：工作流应用 (Workflow App)

```json
{
  "nodes": [...],             // 必填：节点数组
  "edges": [...],             // 可选：边数组
  "chatConfig": { ... }       // 可选：聊天配置
}
```

**识别规则**：根对象包含 `nodes` 数组且包含 `workflowStart` 类型节点时，识别为工作流应用。

### 1.2 通用字段规范

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `nodes` | Array | 条件必填 | 工作流节点数组 (工作流应用必填) |
| `edges` | Array | 否 | 工作流边连接数组 |
| `chatConfig` | Object | 否 | 聊天配置对象 |
| `aiSettings` | Object | 条件必填 | AI 配置 (简单应用必填) |
| `dataset` | Object | 否 | 知识库配置 |
| `selectedTools` | Array | 否 | 工具列表 |

---

## 2. 应用类型定义

### 2.1 AppTypeEnum 枚举值

```typescript
enum AppTypeEnum {
  "folder" = "folder",                  // 文件夹
  "toolFolder" = "toolFolder",          // 工具文件夹
  "simple" = "simple",                  // 简单应用
  "chatAgent" = "chatAgent",            // 对话助手
  "workflow" = "advanced",              // 工作流应用
  "workflowTool" = "plugin",            // 插件/工具
  "mcpToolSet" = "toolSet",             // MCP 工具集
  "httpToolSet" = "httpToolSet",        // HTTP 工具集
  "hidden" = "hidden"                   // 隐藏应用
}
```

### 2.2 类型自动映射

| 检测条件 | 映射类型 |
|----------|----------|
| 存在 `aiSettings` | `simple` |
| 存在 `workflowStart` 节点 | `advanced` |
| 存在 `pluginInput` 节点 | `plugin` |

---

## 3. 简单应用配置规范

### 3.1 aiSettings 对象规范

```typescript
interface AiSettings {
  model: string;                          // 必填：AI 模型名称
  systemPrompt?: string;                  // 可选：系统提示词
  temperature?: number;                   // 可选：温度参数 (0-2)
  maxToken?: number;                      // 可选：最大 Token 数
  isResponseText: boolean;                // 必填：是否返回文本
  maxHistories: number;                   // 必填：最大历史轮数 (0-100)
  aiChatReasoning?: boolean;              // 可选：是否开启推理
  aiChatTopP?: number;                    // 可选：Top-P 参数 (0-1)
  aiChatStopSign?: string;                // 可选：停止符
  aiChatResponseFormat?: string;          // 可选：响应格式
  aiChatJsonSchema?: string;              // 可选：JSON Schema
  useAgentSandbox?: boolean;              // 可选：是否使用 Agent 沙箱
}
```

#### 配置示例

```json
{
  "aiSettings": {
    "model": "gpt-4o",
    "systemPrompt": "你是一个专业的AI助手，请帮助用户解决问题。",
    "temperature": 0.7,
    "maxToken": 2000,
    "isResponseText": true,
    "maxHistories": 6,
    "aiChatReasoning": false,
    "aiChatTopP": 1,
    "useAgentSandbox": false
  }
}
```

### 3.2 dataset 对象规范

```typescript
interface DatasetConfig {
  datasets: SelectedDataset[];            // 必填：知识库列表
  searchMode: DatasetSearchModeEnum;      // 必填：搜索模式
  limit?: number;                         // 可选：最大 Token 限制
  similarity?: number;                    // 可选：相似度阈值 (0-1)
  embeddingWeight?: number;               // 可选：向量权重 (0-1)
  usingReRank?: boolean;                  // 可选：是否使用重排序
  rerankModel?: string;                   // 可选：重排序模型
  rerankWeight?: number;                  // 可选：重排序权重 (0-1)
  datasetSearchUsingExtensionQuery?: boolean; // 可选：是否使用查询扩展
  datasetSearchExtensionModel?: string;   // 可选：扩展模型
  datasetSearchExtensionBg?: string;      // 可选：扩展背景
  collectionFilterMatch?: string;         // 可选：集合过滤条件
}

interface SelectedDataset {
  datasetId: string;                      // 必填：知识库 ID
  avatar: string;                         // 必填：知识库头像
  name: string;                           // 必填：知识库名称
  vectorModel: {
    model: string;                        // 必填：向量模型
  };
}

enum DatasetSearchModeEnum {
  "embedding" = "embedding",              // 向量搜索
  "fullTextRecall" = "fullTextRecall",    // 全文检索
  "mixedRecall" = "mixedRecall"           // 混合搜索
}
```

#### 配置示例

```json
{
  "dataset": {
    "datasets": [
      {
        "datasetId": "64f8a1b2c3d4e5f6g7h8i9j0",
        "avatar": "/icon/dataset.svg",
        "name": "产品知识库",
        "vectorModel": {
          "model": "text-embedding-3-small"
        }
      }
    ],
    "searchMode": "embedding",
    "limit": 5000,
    "similarity": 0.4,
    "embeddingWeight": 0.5,
    "usingReRank": false,
    "rerankWeight": 0.5,
    "datasetSearchUsingExtensionQuery": true
  }
}
```

### 3.3 selectedTools 数组规范

```typescript
interface SelectedTool {
  id: string;                             // 必填：工具模板 ID
  flowNodeType: string;                   // 必填：节点类型
  templateType: string;                   // 必填：模板类型
  name: string;                           // 必填：工具名称
  intro?: string;                         // 可选：工具介绍
  avatar?: string;                        // 可选：工具头像
  isTool?: boolean;                       // 可选：是否可作为工具调用
  configStatus?: "noConfig" | "waitingForConfig" | "configured" | "invalid"; // 可选：配置状态
  inputs: ToolInputItem[];                // 必填：输入配置
  outputs: ToolOutputItem[];              // 必填：输出配置
}
```

### 3.4 selectedAgentSkills 数组规范

```typescript
interface SelectedAgentSkill {
  skillId: string;                        // 必填：技能 ID
  name: string;                           // 必填：技能名称
  description?: string;                   // 可选：技能描述
  avatar?: string;                        // 可选：技能头像
}
```

---

## 4. 工作流应用配置规范

### 4.1 节点数组 (nodes)

节点数组包含所有工作流节点，每个节点遵循以下规范：

```typescript
interface StoreNodeItemType {
  nodeId: string;                         // 必填：节点唯一 ID
  name: string;                           // 必填：节点显示名称
  flowNodeType: FlowNodeTypeEnum;         // 必填：节点类型枚举
  position?: {                            // 可选：画布位置坐标
    x: number;
    y: number;
  };
  
  // 可选属性
  parentNodeId?: string;                  // 父节点 ID (用于嵌套节点如循环)
  avatar?: string;                        // 节点图标路径
  avatarLinear?: string;                  // 节点渐变图标
  colorSchema?: NodeColorSchemaEnum;      // 配色方案
  intro?: string;                         // 节点介绍
  toolDescription?: string;               // 工具描述 (用于工具调用)
  showStatus?: boolean;                   // 是否显示运行状态
  version?: string;                       // 节点版本号
  catchError?: boolean;                   // 是否捕获错误继续执行
  
  // 数据配置 (必填)
  inputs: FlowNodeInputItemType[];        // 输入配置数组
  outputs: FlowNodeOutputItemType[];      // 输出配置数组
  
  // 插件相关 (可选)
  pluginId?: string;                      // 插件 ID
  pluginData?: ToolData;                  // 插件数据
  toolConfig?: NodeToolConfig;            // 工具配置
}
```

### 4.2 FlowNodeTypeEnum 节点类型枚举

```typescript
enum FlowNodeTypeEnum {
  // 基础节点
  "emptyNode" = "emptyNode",
  "systemConfig" = "userGuide",           // 系统配置节点
  "pluginConfig" = "pluginConfig",        // 插件配置节点
  "globalVariable" = "globalVariable",    // 全局变量节点
  "comment" = "comment",                  // 注释节点
  "workflowStart" = "workflowStart",      // 工作流开始节点
  
  // AI 节点
  "chatNode" = "chatNode",                // AI 对话节点
  "agent" = "agent",                      // Agent 节点
  "toolCall" = "tools",                   // 工具调用节点
  
  // 知识库节点
  "datasetSearchNode" = "datasetSearchNode",   // 知识库搜索节点
  "datasetConcatNode" = "datasetConcatNode",   // 知识库合并节点
  
  // 交互节点
  "answerNode" = "answerNode",            // 直接回复节点
  "classifyQuestion" = "classifyQuestion", // 问题分类节点
  "contentExtract" = "contentExtract",    // 内容提取节点
  "customFeedback" = "customFeedback",    // 自定义反馈节点
  "userSelect" = "userSelect",            // 用户选择节点
  "formInput" = "formInput",              // 表单输入节点
  
  // 工具节点
  "httpRequest468" = "httpRequest468",    // HTTP 请求节点
  "lafModule" = "lafModule",              // Laf 函数节点
  "code" = "code",                        // 代码执行节点
  "textEditor" = "textEditor",            // 文本编辑节点
  "readFiles" = "readFiles",              // 文件读取节点
  
  // 逻辑节点
  "ifElseNode" = "ifElseNode",            // 条件分支节点
  "variableUpdate" = "variableUpdate",    // 变量更新节点
  "loop" = "loop",                        // 循环节点
  "loopStart" = "loopStart",              // 循环开始节点
  "loopEnd" = "loopEnd",                  // 循环结束节点
  
  // 插件节点
  "pluginInput" = "pluginInput",          // 插件输入节点
  "pluginOutput" = "pluginOutput",        // 插件输出节点
  "tool" = "tool",                        // 工具节点
  "toolSet" = "toolSet",                  // 工具集节点
  "appModule" = "appModule",              // 应用模块节点
  "pluginModule" = "pluginModule"         // 插件模块节点
}
```

### 4.3 NodeColorSchemaEnum 配色方案枚举

```typescript
enum NodeColorSchemaEnum {
  "blue" = "blue",
  "blueDark" = "blueDark",
  "blueLight" = "blueLight",
  "purple" = "purple",
  "indigo" = "indigo",
  "lime" = "lime",
  "orange" = "orange",
  "red" = "red",
  "gray" = "gray"
}
```

### 4.4 边数组 (edges)

边定义节点之间的连接关系：

```typescript
interface StoreEdgeItemType {
  source: string;                         // 必填：源节点 ID
  sourceHandle: string;                   // 必填：源节点连接点 ID
  target: string;                         // 必填：目标节点 ID
  targetHandle: string;                   // 必填：目标节点连接点 ID
}
```

#### 连接点 ID 命名规范

```
源连接点: {nodeId}-source-{direction}     // 如: node123-source-right
目标连接点: {nodeId}-target-{direction}   // 如: node456-target-left

direction 可选值: left, right, top, bottom
```

---

## 5. 节点配置详细规范

### 5.1 工作流开始节点 (workflowStart)

**节点类型**: `workflowStart`

**必填字段**:
- `nodeId`: 节点唯一标识
- `name`: "工作流开始"
- `flowNodeType`: "workflowStart"
- `inputs`: 用户输入配置
- `outputs`: 输出变量定义

**标准配置示例**:

```json
{
  "nodeId": "workflowStart-123456789",
  "name": "工作流开始",
  "flowNodeType": "workflowStart",
  "position": { "x": 100, "y": 100 },
  "avatar": "core/workflow/template/workflowStart",
  "avatarLinear": "core/workflow/template/workflowStartLinear",
  "colorSchema": "blue",
  "inputs": [
    {
      "key": "userChatInput",
      "renderTypeList": ["reference", "textarea"],
      "valueType": "string",
      "label": "用户问题",
      "toolDescription": "user question",
      "required": true
    }
  ],
  "outputs": [
    {
      "id": "userChatInput",
      "key": "userChatInput",
      "label": "用户问题",
      "type": "static",
      "valueType": "string"
    },
    {
      "id": "userFiles",
      "key": "userFiles",
      "label": "用户文件",
      "type": "static",
      "valueType": "arrayString"
    }
  ]
}
```

### 5.2 AI 对话节点 (chatNode)

**节点类型**: `chatNode`

**完整配置示例**:

```json
{
  "nodeId": "chatNode-987654321",
  "name": "AI 对话",
  "flowNodeType": "chatNode",
  "position": { "x": 500, "y": 100 },
  "avatar": "core/workflow/template/aiChat",
  "avatarLinear": "core/workflow/template/aiChatLinear",
  "colorSchema": "blueDark",
  "showStatus": true,
  "version": "4.9.7",
  "catchError": false,
  "inputs": [
    {
      "key": "model",
      "renderTypeList": ["settingLLMModel", "reference"],
      "label": "AI 模型",
      "valueType": "string",
      "value": "gpt-4o",
      "required": true
    },
    {
      "key": "temperature",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "number",
      "value": 0.7
    },
    {
      "key": "maxToken",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "number",
      "value": 2000
    },
    {
      "key": "isResponseAnswerText",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "boolean",
      "value": true
    },
    {
      "key": "aiChatQuoteRole",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string",
      "value": "system"
    },
    {
      "key": "quoteTemplate",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "quotePrompt",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "aiChatVision",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "boolean",
      "value": true
    },
    {
      "key": "aiChatReasoning",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "boolean",
      "value": true
    },
    {
      "key": "aiChatTopP",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "number"
    },
    {
      "key": "aiChatStopSign",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "aiChatResponseFormat",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "aiChatJsonSchema",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "systemPrompt",
      "renderTypeList": ["textarea", "reference"],
      "label": "系统提示词",
      "valueType": "string",
      "value": "你是一个专业的AI助手。",
      "maxLength": 100000,
      "isRichText": true
    },
    {
      "key": "history",
      "renderTypeList": ["numberInput", "reference"],
      "label": "对话历史",
      "valueType": "chatHistory",
      "value": 6,
      "min": 0,
      "max": 50,
      "required": true
    },
    {
      "key": "quoteQA",
      "renderTypeList": ["settingDatasetQuotePrompt"],
      "label": "",
      "debugLabel": "知识库引用",
      "valueType": "datasetQuote"
    },
    {
      "key": "fileUrlList",
      "renderTypeList": ["reference", "input"],
      "label": "用户文件",
      "valueType": "arrayString"
    },
    {
      "key": "userChatInput",
      "renderTypeList": ["reference", "textarea"],
      "label": "用户问题",
      "toolDescription": "user question",
      "valueType": "string",
      "value": ["workflowStart-123456789", "userChatInput"],
      "required": true
    }
  ],
  "outputs": [
    {
      "id": "history",
      "key": "history",
      "label": "新上下文",
      "description": "包含本次对话历史",
      "valueType": "chatHistory",
      "type": "static",
      "required": true
    },
    {
      "id": "answerText",
      "key": "answerText",
      "label": "AI 回复内容",
      "description": "AI 生成的回复文本",
      "valueType": "string",
      "type": "static",
      "required": true
    },
    {
      "id": "reasoningText",
      "key": "reasoningText",
      "label": "推理内容",
      "valueType": "string",
      "type": "static",
      "required": false,
      "invalid": true
    },
    {
      "id": "error",
      "key": "error",
      "label": "错误信息",
      "valueType": "string",
      "type": "error"
    }
  ]
}
```

### 5.3 知识库搜索节点 (datasetSearchNode)

**节点类型**: `datasetSearchNode`

**配置示例**:

```json
{
  "nodeId": "datasetSearch-abcdef123",
  "name": "知识库搜索",
  "flowNodeType": "datasetSearchNode",
  "position": { "x": 500, "y": 300 },
  "avatar": "core/workflow/template/datasetSearch",
  "avatarLinear": "core/workflow/template/datasetSearchLinear",
  "colorSchema": "blueLight",
  "showStatus": true,
  "version": "4.9.2",
  "catchError": false,
  "inputs": [
    {
      "key": "datasets",
      "renderTypeList": ["selectDataset", "reference"],
      "label": "选择知识库",
      "value": [
        {
          "datasetId": "64f8a1b2c3d4e5f6g7h8i9j0",
          "avatar": "/icon/dataset.svg",
          "name": "产品知识库",
          "vectorModel": { "model": "text-embedding-3-small" }
        }
      ],
      "valueType": "selectDataset",
      "required": true
    },
    {
      "key": "similarity",
      "renderTypeList": ["selectDatasetParamsModal"],
      "label": "",
      "value": 0.4,
      "valueType": "number"
    },
    {
      "key": "limit",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": 5000,
      "valueType": "number"
    },
    {
      "key": "searchMode",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": "embedding",
      "valueType": "string"
    },
    {
      "key": "embeddingWeight",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": 0.5,
      "valueType": "number"
    },
    {
      "key": "usingReRank",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": false,
      "valueType": "boolean"
    },
    {
      "key": "rerankModel",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "rerankWeight",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": 0.5,
      "valueType": "number"
    },
    {
      "key": "datasetSearchUsingExtensionQuery",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": true,
      "valueType": "boolean"
    },
    {
      "key": "datasetSearchExtensionModel",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string"
    },
    {
      "key": "datasetSearchExtensionBg",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": "",
      "valueType": "string"
    },
    {
      "key": "authTmbId",
      "renderTypeList": ["hidden"],
      "label": "",
      "value": false,
      "valueType": "boolean"
    },
    {
      "key": "userChatInput",
      "renderTypeList": ["reference", "textarea"],
      "label": "用户问题",
      "toolDescription": "content to search",
      "valueType": "string",
      "value": ["workflowStart-123456789", "userChatInput"],
      "required": true
    },
    {
      "key": "collectionFilterMatch",
      "renderTypeList": ["textarea", "reference"],
      "label": "集合过滤",
      "valueType": "string",
      "isPro": true
    }
  ],
  "outputs": [
    {
      "id": "datasetQuoteQA",
      "key": "datasetQuoteQA",
      "label": "知识库引用",
      "description": "搜索到的知识库内容",
      "type": "static",
      "valueType": "datasetQuote"
    },
    {
      "id": "error",
      "key": "error",
      "label": "错误信息",
      "valueType": "string",
      "type": "error"
    }
  ]
}
```

### 5.4 HTTP 请求节点 (httpRequest468)

**节点类型**: `httpRequest468`

**配置示例**:

```json
{
  "nodeId": "http-xyz789",
  "name": "HTTP 请求",
  "flowNodeType": "httpRequest468",
  "position": { "x": 500, "y": 500 },
  "avatar": "core/workflow/template/httpRequest",
  "avatarLinear": "core/workflow/template/httpRequestLinear",
  "colorSchema": "indigo",
  "showStatus": true,
  "catchError": false,
  "inputs": [
    {
      "key": "system_addInputParam",
      "renderTypeList": ["addInputParam"],
      "label": "",
      "valueType": "dynamic",
      "required": false,
      "customInputConfig": {
        "selectValueTypeList": ["string", "number", "boolean", "object", "arrayString", "arrayNumber", "arrayBoolean", "arrayObject", "arrayAny", "any", "chatHistory", "datasetQuote", "dynamic", "selectDataset"],
        "showDescription": false,
        "showDefaultValue": true
      }
    },
    {
      "key": "system_httpMethod",
      "renderTypeList": ["custom"],
      "valueType": "string",
      "label": "",
      "value": "POST",
      "required": true
    },
    {
      "key": "system_httpTimeout",
      "renderTypeList": ["custom"],
      "valueType": "number",
      "label": "",
      "value": 30,
      "min": 5,
      "max": 600,
      "required": true
    },
    {
      "key": "system_httpReqUrl",
      "renderTypeList": ["hidden"],
      "valueType": "string",
      "label": "",
      "value": "https://api.example.com/data",
      "required": false
    },
    {
      "key": "system_header_secret",
      "renderTypeList": ["hidden"],
      "valueType": "object",
      "label": "",
      "required": false
    },
    {
      "key": "system_httpHeaders",
      "renderTypeList": ["custom"],
      "valueType": "any",
      "value": [
        { "key": "Content-Type", "type": "string", "value": "application/json" },
        { "key": "Authorization", "type": "string", "value": "Bearer token123" }
      ],
      "label": "",
      "required": false
    },
    {
      "key": "system_httpParams",
      "renderTypeList": ["hidden"],
      "valueType": "any",
      "value": [],
      "label": "",
      "required": false
    },
    {
      "key": "system_httpJsonBody",
      "renderTypeList": ["hidden"],
      "valueType": "any",
      "value": "{\"key\": \"value\"}",
      "label": "",
      "required": false
    },
    {
      "key": "system_httpFormBody",
      "renderTypeList": ["hidden"],
      "valueType": "any",
      "value": [],
      "label": "",
      "required": false
    },
    {
      "key": "system_httpContentType",
      "renderTypeList": ["hidden"],
      "valueType": "string",
      "value": "application/json",
      "label": "",
      "required": false
    }
  ],
  "outputs": [
    {
      "key": "addOutputParam",
      "renderTypeList": ["addOutputParam"],
      "label": "",
      "valueType": "dynamic",
      "canEdit": true,
      "customFieldConfig": {
        "selectValueTypeList": ["string", "number", "boolean", "object", "arrayString", "arrayNumber", "arrayBoolean", "arrayObject", "arrayAny", "any", "chatHistory", "datasetQuote", "dynamic", "selectDataset"],
        "showDescription": true,
        "showDefaultValue": false
      }
    },
    {
      "id": "httpRawResponse",
      "key": "httpRawResponse",
      "label": "原始响应",
      "description": "HTTP 完整响应数据",
      "valueType": "any",
      "type": "static",
      "required": true
    },
    {
      "id": "error",
      "key": "error",
      "label": "错误信息",
      "valueType": "string",
      "type": "error"
    }
  ]
}
```

### 5.5 代码执行节点 (code)

**节点类型**: `code`

**配置示例**:

```json
{
  "nodeId": "code-node456",
  "name": "代码执行",
  "flowNodeType": "code",
  "position": { "x": 800, "y": 300 },
  "avatar": "core/workflow/template/codeRun",
  "avatarLinear": "core/workflow/template/codeRunLinear",
  "colorSchema": "lime",
  "showStatus": true,
  "catchError": false,
  "inputs": [
    {
      "key": "system_addInputParam",
      "renderTypeList": ["addInputParam"],
      "label": "",
      "valueType": "dynamic",
      "required": false,
      "customInputConfig": {
        "selectValueTypeList": ["string", "number", "boolean", "object", "arrayString", "arrayNumber", "arrayBoolean", "arrayObject", "arrayAny", "any", "chatHistory", "datasetQuote", "dynamic", "selectDataset"],
        "showDescription": false,
        "showDefaultValue": true
      }
    },
    {
      "key": "data1",
      "renderTypeList": ["reference"],
      "valueType": "string",
      "canEdit": true,
      "label": "data1",
      "customInputConfig": {
        "selectValueTypeList": ["string", "number", "boolean", "object", "arrayString", "arrayNumber", "arrayBoolean", "arrayObject", "arrayAny", "any", "chatHistory", "datasetQuote", "dynamic", "selectDataset"],
        "showDescription": false,
        "showDefaultValue": true
      },
      "required": true
    },
    {
      "key": "data2",
      "renderTypeList": ["reference"],
      "valueType": "string",
      "canEdit": true,
      "label": "data2",
      "customInputConfig": {
        "selectValueTypeList": ["string", "number", "boolean", "object", "arrayString", "arrayNumber", "arrayBoolean", "arrayObject", "arrayAny", "any", "chatHistory", "datasetQuote", "dynamic", "selectDataset"],
        "showDescription": false,
        "showDefaultValue": true
      },
      "required": true
    },
    {
      "key": "codeType",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "string",
      "value": "js"
    },
    {
      "key": "code",
      "renderTypeList": ["custom"],
      "label": "",
      "valueType": "string",
      "value": "function main({data1, data2}) {\n  return {\n    result: data1 + data2,\n    data2: data2\n  };\n}"
    }
  ],
  "outputs": [
    {
      "key": "addOutputParam",
      "renderTypeList": ["addOutputParam"],
      "label": "",
      "valueType": "dynamic",
      "canEdit": true,
      "customFieldConfig": {
        "selectValueTypeList": ["string", "number", "boolean", "object", "arrayString", "arrayNumber", "arrayBoolean", "arrayObject", "arrayAny", "any", "chatHistory", "datasetQuote", "dynamic", "selectDataset"],
        "showDescription": false,
        "showDefaultValue": false
      }
    },
    {
      "id": "rawResponse",
      "key": "rawResponse",
      "label": "完整响应数据",
      "valueType": "object",
      "type": "static"
    },
    {
      "id": "qLUQfhG0ILRX",
      "type": "dynamic",
      "key": "result",
      "valueType": "string",
      "label": "result"
    },
    {
      "id": "gR0mkQpJ4Og8",
      "type": "dynamic",
      "key": "data2",
      "valueType": "string",
      "label": "data2"
    },
    {
      "id": "error",
      "key": "error",
      "label": "错误信息",
      "valueType": "string",
      "type": "error"
    }
  ]
}
```

### 5.6 问题分类节点 (classifyQuestion)

**节点类型**: `classifyQuestion`

**配置示例**:

```json
{
  "nodeId": "classify-789xyz",
  "name": "问题分类",
  "flowNodeType": "classifyQuestion",
  "position": { "x": 500, "y": 700 },
  "avatar": "core/workflow/template/questionClassify",
  "avatarLinear": "core/workflow/template/questionClassifyLinear",
  "colorSchema": "purple",
  "showStatus": true,
  "version": "4.9.2",
  "inputs": [
    {
      "key": "model",
      "renderTypeList": ["selectLLMModel", "reference"],
      "label": "AI 模型",
      "valueType": "string",
      "value": "gpt-4o-mini",
      "required": true
    },
    {
      "key": "systemPrompt",
      "renderTypeList": ["textarea", "reference"],
      "label": "背景信息",
      "valueType": "string",
      "value": "请根据用户的问题将其分类到以下类别中：",
      "maxLength": 100000,
      "isRichText": true
    },
    {
      "key": "history",
      "renderTypeList": ["numberInput", "reference"],
      "label": "对话历史",
      "valueType": "chatHistory",
      "value": 6,
      "min": 0,
      "max": 50,
      "required": true
    },
    {
      "key": "userChatInput",
      "renderTypeList": ["reference", "textarea"],
      "label": "用户问题",
      "toolDescription": "user question",
      "valueType": "string",
      "value": ["workflowStart-123456789", "userChatInput"],
      "required": true
    },
    {
      "key": "agents",
      "renderTypeList": ["custom"],
      "valueType": "any",
      "label": "",
      "value": [
        { "value": "问候", "key": "wqre" },
        { "value": "产品咨询", "key": "sdfa" },
        { "value": "技术支持", "key": "agex" },
        { "value": "其他问题", "key": "othr" }
      ]
    }
  ],
  "outputs": [
    {
      "id": "cqResult",
      "key": "cqResult",
      "label": "分类结果",
      "valueType": "string",
      "type": "static",
      "required": true
    }
  ]
}
```

### 5.7 工具调用节点 (tools)

**节点类型**: `tools`

**配置示例**:

```json
{
  "nodeId": "toolCall-111222",
  "name": "工具调用",
  "flowNodeType": "tools",
  "position": { "x": 800, "y": 100 },
  "avatar": "core/workflow/template/toolCall",
  "avatarLinear": "core/workflow/template/toolCallLinear",
  "colorSchema": "indigo",
  "showStatus": true,
  "version": "4.9.2",
  "catchError": false,
  "inputs": [
    {
      "key": "model",
      "renderTypeList": ["settingLLMModel", "reference"],
      "label": "AI 模型",
      "valueType": "string",
      "value": "gpt-4o",
      "required": true
    },
    {
      "key": "temperature",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "number",
      "value": 0.5
    },
    {
      "key": "maxToken",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "number",
      "value": 2000
    },
    {
      "key": "isResponseAnswerText",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "boolean",
      "value": true
    },
    {
      "key": "aiChatVision",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "boolean",
      "value": true
    },
    {
      "key": "aiChatReasoning",
      "renderTypeList": ["hidden"],
      "label": "",
      "valueType": "boolean",
      "value": true
    },
    {
      "key": "useAgentSandbox",
      "renderTypeList": ["switch"],
      "label": "使用 Agent 沙箱",
      "valueType": "boolean",
      "value": false
    },
    {
      "key": "systemPrompt",
      "renderTypeList": ["textarea", "reference"],
      "label": "系统提示词",
      "valueType": "string",
      "value": "你是一个智能助手，可以根据用户需要使用工具。",
      "maxLength": 100000,
      "isRichText": true
    },
    {
      "key": "history",
      "renderTypeList": ["numberInput", "reference"],
      "label": "对话历史",
      "valueType": "chatHistory",
      "value": 6,
      "min": 0,
      "max": 50,
      "required": true
    },
    {
      "key": "fileUrlList",
      "renderTypeList": ["reference", "input"],
      "label": "用户文件",
      "valueType": "arrayString"
    },
    {
      "key": "userChatInput",
      "renderTypeList": ["reference", "textarea"],
      "label": "用户问题",
      "toolDescription": "user question",
      "valueType": "string",
      "value": ["workflowStart-123456789", "userChatInput"],
      "required": true
    }
  ],
  "outputs": [
    {
      "id": "answerText",
      "key": "answerText",
      "label": "AI 回复内容",
      "description": "AI 生成的回复文本",
      "valueType": "string",
      "type": "static",
      "required": true
    },
    {
      "id": "error",
      "key": "error",
      "label": "错误信息",
      "valueType": "string",
      "type": "error"
    }
  ],
  "toolConfig": {
    "systemToolSet": {
      "toolId": "system-search",
      "toolList": [
        { "toolId": "bing-search", "name": "Bing 搜索", "description": "使用 Bing 搜索网络信息" },
        { "toolId": "calculator", "name": "计算器", "description": "执行数学计算" }
      ]
    }
  }
}
```

### 5.8 判断器节点 (ifElseNode)

**节点类型**: `ifElseNode`

**功能说明**: 根据条件判断执行不同分支，支持 IF / ELSE IF / ELSE 多分支逻辑。

**条件操作符 (VariableConditionEnum)**:

| 操作符 | 说明 | 适用类型 |
|--------|------|----------|
| `isEmpty` | 为空 | 所有类型 |
| `isNotEmpty` | 不为空 | 所有类型 |
| `equalTo` | 等于 | 字符串、数字、布尔 |
| `notEqual` | 不等于 | 字符串、数字、布尔 |
| `greaterThan` | 大于 | 数字 |
| `greaterThanOrEqualTo` | 大于等于 | 数字 |
| `lessThan` | 小于 | 数字 |
| `lessThanOrEqualTo` | 小于等于 | 数字 |
| `include` | 包含 | 字符串、数组 |
| `notInclude` | 不包含 | 字符串、数组 |
| `startWith` | 以...开头 | 字符串 |
| `endWith` | 以...结尾 | 字符串 |
| `reg` | 正则匹配 | 字符串 |
| `lengthEqualTo` | 长度等于 | 数组、字符串 |
| `lengthNotEqualTo` | 长度不等于 | 数组、字符串 |
| `lengthGreaterThan` | 长度大于 | 数组、字符串 |
| `lengthGreaterThanOrEqualTo` | 长度大于等于 | 数组、字符串 |
| `lengthLessThan` | 长度小于 | 数组、字符串 |
| `lengthLessThanOrEqualTo` | 长度小于等于 | 数组、字符串 |

**输入配置规范**:

- **键名**: 必须是 `ifElseList`
- **结构**: `value` 是数组，每个元素代表一个条件分支
- **条件组结构**:
  - `condition`: 逻辑关系，`"AND"` 或 `"OR"`
  - `list`: 条件列表，每个条件包含：
    - `variable`: 左侧变量，格式 `["nodeId", "outputKey"]`
    - `condition`: 条件操作符（见上表）
    - `value`: 右侧值（字符串）
    - `valueType`: 值类型，`"input"` 或 `"reference"`

**输出配置规范**:

- **键名**: `ifElseResult`
- **类型**: `string`
- **可能值**: `"IF"`, `"ELSE IF 1"`, `"ELSE IF 2"`, ..., `"ELSE"`

**边连接规范**:

判断器节点的源连接点使用特殊命名：

```
{nodeId}-source-IF
{nodeId}-source-ELSE IF 1
{nodeId}-source-ELSE IF 2
...
{nodeId}-source-ELSE
```

**完整配置示例 (IF-ELSE)**:

```json
{
  "nodeId": "ifElse-1704067200",
  "name": "判断器",
  "flowNodeType": "ifElseNode",
  "position": { "x": 600, "y": 200 },
  "avatar": "core/workflow/template/ifelse",
  "avatarLinear": "core/workflow/template/ifelseLinear",
  "colorSchema": "greenLight",
  "showStatus": true,
  "inputs": [
    {
      "key": "ifElseList",
      "renderTypeList": ["hidden"],
      "valueType": "any",
      "label": "",
      "value": [
        {
          "condition": "AND",
          "list": [
            {
              "variable": ["code-node-id", "score"],
              "condition": "greaterThanOrEqualTo",
              "value": "70",
              "valueType": "input"
            }
          ]
        }
      ]
    }
  ],
  "outputs": [
    {
      "id": "ifElseResult",
      "key": "ifElseResult",
      "label": "判断结果",
      "valueType": "string",
      "type": "static"
    }
  ]
}
```

**多分支配置示例 (IF - ELSE IF - ELSE)**:

```json
{
  "key": "ifElseList",
  "renderTypeList": ["hidden"],
  "valueType": "any",
  "label": "",
  "value": [
    {
      "condition": "AND",
      "list": [
        {
          "variable": ["code-node-id", "score"],
          "condition": "greaterThanOrEqualTo",
          "value": "90",
          "valueType": "input"
        }
      ]
    },
    {
      "condition": "AND",
      "list": [
        {
          "variable": ["code-node-id", "score"],
          "condition": "greaterThanOrEqualTo",
          "value": "70",
          "valueType": "input"
        },
        {
          "variable": ["code-node-id", "score"],
          "condition": "lessThan",
          "value": "90",
          "valueType": "input"
        }
      ]
    }
  ]
}
```

对应的边连接：

```json
{
  "edges": [
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-IF",
      "target": "excellent-node",
      "targetHandle": "excellent-node-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-ELSE IF 1",
      "target": "good-node",
      "targetHandle": "good-node-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-ELSE",
      "target": "fail-node",
      "targetHandle": "fail-node-target-left"
    }
  ]
}
```

**常见错误**:

| 错误 | 正确 |
|------|------|
| `"key": "condition"` | `"key": "ifElseList"` |
| `"operator": "EQUAL"` | `"condition": "equalTo"` |
| `"sourceHandle": "...-source-right"` | `"sourceHandle": "...-source-IF"` |
| `"id": "pass"` (自定义输出) | `"id": "ifElseResult"` |

---

## 6. 输入项配置规范

### 6.1 FlowNodeInputItemType 结构

```typescript
interface FlowNodeInputItemType {
  // 基础字段
  key: string;                            // 必填：输入项唯一键名
  label: string;                          // 必填：显示标签
  valueType: WorkflowIOValueTypeEnum;     // 必填：值类型
  
  // 渲染配置
  renderTypeList: FlowNodeInputTypeEnum[]; // 必填：渲染类型列表
  selectedTypeIndex?: number;             // 可选：选中的渲染类型索引
  
  // 值配置
  value?: any;                            // 可选：默认值或引用值
  valueDesc?: string;                     // 可选：值描述
  defaultValue?: any;                     // 可选：默认值
  
  // 验证配置
  required?: boolean;                     // 可选：是否必填 (默认 false)
  description?: string;                   // 可选：字段描述
  toolDescription?: string;               // 可选：工具描述
  debugLabel?: string;                    // 可选：调试标签
  
  // 约束配置
  min?: number;                           // 可选：最小值/长度
  max?: number;                           // 可选：最大值/长度
  maxLength?: number;                     // 可选：最大长度
  minLength?: number;                     // 可选：最小长度
  step?: number;                          // 可选：步长
  precision?: number;                     // 可选：精度
  
  // UI 配置
  placeholder?: string;                   // 可选：占位符
  isRichText?: boolean;                   // 可选：是否富文本
  list?: Array<{label: string, value: string}>; // 可选：选项列表
  markList?: Array<{label: string, value: number}>; // 可选：标记列表
  
  // 引用配置
  referencePlaceholder?: string;          // 可选：引用占位符
  
  // 文件配置
  canSelectFile?: boolean;                // 可选：是否可选文件
  canSelectImg?: boolean;                 // 可选：是否可选图片
  canSelectVideo?: boolean;               // 可选：是否可选视频
  canSelectAudio?: boolean;               // 可选：是否可选音频
  canSelectCustomFileExtension?: boolean; // 可选：是否可选自定义扩展名
  customFileExtensionList?: string[];     // 可选：自定义扩展名列表
  canLocalUpload?: boolean;               // 可选：是否可本地上传
  canUrlUpload?: boolean;                 // 可选：是否可 URL 上传
  maxFiles?: number;                      // 可选：最大文件数
  
  // 时间配置
  timeGranularity?: 'day' | 'hour' | 'minute' | 'second'; // 可选：时间粒度
  timeRangeStart?: string;                // 可选：时间范围开始
  timeRangeEnd?: string;                  // 可选：时间范围结束
  
  // 知识库配置
  datasetOptions?: SelectedDataset[];     // 可选：知识库选项
  
  // 动态输入配置
  customInputConfig?: CustomFieldConfig;  // 可选：自定义输入配置
  canEdit?: boolean;                      // 可选：是否可编辑
  
  // 高级配置
  isPro?: boolean;                        // 可选：是否 Pro 功能
  isToolOutput?: boolean;                 // 可选：是否工具输出
  deprecated?: boolean;                   // 可选：是否已弃用
  enum?: string;                          // 可选：枚举值
  inputList?: InputConfig[];              // 可选：输入列表配置
}

interface CustomFieldConfig {
  selectValueTypeList?: WorkflowIOValueTypeEnum[]; // 可选值类型列表
  showDefaultValue?: boolean;             // 是否显示默认值
  showDescription?: boolean;              // 是否显示描述
}
```

### 6.2 FlowNodeInputTypeEnum 输入渲染类型

```typescript
enum FlowNodeInputTypeEnum {
  "reference" = "reference",                   // 引用其他节点输出
  "input" = "input",                           // 单行文本输入
  "textarea" = "textarea",                     // 多行文本输入
  "numberInput" = "numberInput",               // 数字输入
  "switch" = "switch",                         // 开关/布尔值
  "select" = "select",                         // 下拉选择
  "multipleSelect" = "multipleSelect",         // 多选
  "JSONEditor" = "JSONEditor",                 // JSON 编辑器
  "addInputParam" = "addInputParam",           // 动态添加参数
  "customVariable" = "customVariable",         // 外部变量
  "selectApp" = "selectApp",                   // 选择应用
  "selectLLMModel" = "selectLLMModel",         // 选择 LLM 模型
  "settingLLMModel" = "settingLLMModel",       // 设置 LLM 模型
  "selectDataset" = "selectDataset",           // 选择知识库
  "selectDatasetParamsModal" = "selectDatasetParamsModal", // 知识库参数弹窗
  "settingDatasetQuotePrompt" = "settingDatasetQuotePrompt", // 知识库引用提示词
  "hidden" = "hidden",                         // 隐藏字段
  "custom" = "custom",                         // 自定义渲染
  "selectSkill" = "selectSkill",               // 选择技能
  "selectTool" = "selectTool",                 // 选择工具
  "fileSelect" = "fileSelect",                 // 文件选择
  "timePointSelect" = "timePointSelect",       // 时间点选择
  "timeRangeSelect" = "timeRangeSelect",       // 时间范围选择
  "password" = "password"                      // 密码输入
}
```

### 6.3 引用值格式

当 `renderTypeList` 包含 `reference` 且 `value` 为引用时，格式为：

```typescript
// 单引用格式
type ReferenceValue = [string, string?];

// 示例：引用 workflowStart 节点的 userChatInput 输出
"value": ["workflowStart-123456789", "userChatInput"]

// 示例：引用整个节点输出
"value": ["datasetSearch-abcdef123", ""]

// 数组引用格式 (用于多选引用)
type ReferenceArrayValue = Array<[string, string?]>;

// 示例
"value": [
  ["node1-id", "output1"],
  ["node2-id", "output2"]
]
```

---

## 7. 输出项配置规范

### 7.1 FlowNodeOutputItemType 结构

```typescript
interface FlowNodeOutputItemType {
  // 基础字段
  id: string;                             // 必填：输出项唯一 ID
  key: string;                            // 必填：输出项键名
  type: FlowNodeOutputTypeEnum;           // 必填：输出类型
  
  // 值配置
  valueType?: WorkflowIOValueTypeEnum;    // 可选：值类型
  valueDesc?: string;                     // 可选：值描述
  value?: any;                            // 可选：默认值
  defaultValue?: any;                     // 可选：默认值
  
  // 显示配置
  label?: string;                         // 可选：显示标签
  description?: string;                   // 可选：描述
  
  // 验证配置
  required?: boolean;                     // 可选：是否必填
  
  // 动态字段配置
  customFieldConfig?: CustomFieldConfig;  // 可选：自定义字段配置
  
  // 有效性配置
  invalid?: boolean;                      // 可选：是否无效 (某些条件下)
  invalidCondition?: Function;            // 可选：无效条件函数
  
  // 其他
  deprecated?: boolean;                   // 可选：是否已弃用
}
```

### 7.2 FlowNodeOutputTypeEnum 输出类型

```typescript
enum FlowNodeOutputTypeEnum {
  "hidden" = "hidden",                       // 隐藏输出
  "error" = "error",                         // 错误输出
  "source" = "source",                       // 源连接点
  "static" = "static",                       // 静态输出
  "dynamic" = "dynamic"                      // 动态输出 (可添加)
}
```

---

## 8. 边连接配置规范

### 8.1 边的基本结构

```typescript
interface StoreEdgeItemType {
  source: string;                         // 源节点 ID
  sourceHandle: string;                   // 源节点连接点 ID
  target: string;                         // 目标节点 ID
  targetHandle: string;                   // 目标节点连接点 ID
}
```

### 8.2 连接点 ID 命名规范

连接点 ID 遵循以下命名约定：

```
// 源连接点 (出边)
{nodeId}-source-{direction}

// 目标连接点 (入边)
{nodeId}-target-{direction}

// direction 可选值：left, right, top, bottom
```

**示例**：
- `workflowStart-123-source-right` - 工作流开始节点的右侧输出
- `chatNode-456-target-left` - AI 对话节点的左侧输入

### 8.3 常见连接模式

#### 线性连接

```
[workflowStart] --右出--> [AI对话] --右出--> [直接回复]
```

```json
{
  "edges": [
    {
      "source": "workflowStart-id",
      "sourceHandle": "workflowStart-id-source-right",
      "target": "chatNode-id",
      "targetHandle": "chatNode-id-target-left"
    },
    {
      "source": "chatNode-id",
      "sourceHandle": "chatNode-id-source-right",
      "target": "answerNode-id",
      "targetHandle": "answerNode-id-target-left"
    }
  ]
}
```

#### 分支连接 (问题分类)

```
                    ┌--> [分支1处理]
[开始] --> [分类器] --┼--> [分支2处理]
                    └--> [分支3处理]
```

```json
{
  "edges": [
    {
      "source": "workflowStart-id",
      "sourceHandle": "workflowStart-id-source-right",
      "target": "classify-id",
      "targetHandle": "classify-id-target-left"
    },
    {
      "source": "classify-id",
      "sourceHandle": "classify-id-source-wqre",
      "target": "branch1-id",
      "targetHandle": "branch1-id-target-left"
    },
    {
      "source": "classify-id",
      "sourceHandle": "classify-id-source-sdfa",
      "target": "branch2-id",
      "targetHandle": "branch2-id-target-left"
    }
  ]
}
```

#### 条件分支连接 (判断器节点)

判断器节点使用特殊的连接点命名：

```
              ┌--> IF --> [通过处理]
[输入] --> [判断器]
              └--> ELSE --> [不通过处理]
```

```json
{
  "edges": [
    {
      "source": "input-node-id",
      "sourceHandle": "input-node-id-source-right",
      "target": "ifElse-node-id",
      "targetHandle": "ifElse-node-id-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-IF",
      "target": "pass-node-id",
      "targetHandle": "pass-node-id-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-ELSE",
      "target": "reject-node-id",
      "targetHandle": "reject-node-id-target-left"
    }
  ]
}
```

**多分支条件连接**:

```json
{
  "edges": [
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-IF",
      "target": "excellent-node-id",
      "targetHandle": "excellent-node-id-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-ELSE IF 1",
      "target": "good-node-id",
      "targetHandle": "good-node-id-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-ELSE IF 2",
      "target": "average-node-id",
      "targetHandle": "average-node-id-target-left"
    },
    {
      "source": "ifElse-node-id",
      "sourceHandle": "ifElse-node-id-source-ELSE",
      "target": "fail-node-id",
      "targetHandle": "fail-node-id-target-left"
    }
  ]
}
```

---

## 9. 聊天配置规范

### 9.1 AppChatConfigType 结构

```typescript
interface AppChatConfigType {
  welcomeText?: string;                   // 欢迎语
  variables?: VariableItem[];             // 全局变量列表
  autoExecute?: AutoExecuteConfig;        // 自动执行配置
  questionGuide?: QuestionGuideConfig;    // 问题引导配置
  ttsConfig?: TTSConfig;                  // 语音合成配置
  whisperConfig?: WhisperConfig;          // 语音识别配置
  scheduledTriggerConfig?: ScheduledTriggerConfig; // 定时触发配置
  chatInputGuide?: ChatInputGuideConfig;  // 输入引导配置
  fileSelectConfig?: FileSelectConfig;    // 文件选择配置
  instruction?: string;                   // 使用说明
}
```

### 9.2 各配置项详细规范

#### 自动执行配置

```typescript
interface AutoExecuteConfig {
  open: boolean;                          // 是否开启自动执行
  defaultPrompt: string;                  // 默认提示词
}
```

#### 问题引导配置

```typescript
interface QuestionGuideConfig {
  open: boolean;                          // 是否开启问题引导
  model?: string;                         // 使用的模型
  customPrompt?: string;                  // 自定义提示词
}
```

#### TTS 配置

```typescript
interface TTSConfig {
  type: 'none' | 'web' | 'model';         // TTS 类型
  model?: string;                         // TTS 模型
  voice?: string;                         // 音色
  speed?: number;                         // 语速
}
```

#### 语音识别配置

```typescript
interface WhisperConfig {
  open: boolean;                          // 是否开启语音识别
  autoSend: boolean;                      // 是否自动发送
  autoTTSResponse: boolean;               // 是否自动语音回复
}
```

#### 定时触发配置

```typescript
interface ScheduledTriggerConfig {
  cronString: string;                     // Cron 表达式
  timezone: string;                       // 时区
  defaultPrompt: string;                  // 默认提示词
}
```

#### 输入引导配置

```typescript
interface ChatInputGuideConfig {
  open: boolean;                          // 是否开启输入引导
  customUrl: string;                      // 自定义 URL
}
```

### 9.3 聊天配置示例

```json
{
  "chatConfig": {
    "welcomeText": "欢迎使用 AI 助手！请输入您的问题。",
    "variables": [
      {
        "type": "input",
        "key": "userName",
        "label": "用户姓名",
        "description": "请输入您的姓名",
        "required": true,
        "valueType": "string",
        "renderTypeList": ["input"]
      },
      {
        "type": "select",
        "key": "language",
        "label": "语言偏好",
        "description": "选择回复语言",
        "required": false,
        "valueType": "string",
        "value": "zh",
        "renderTypeList": ["select"],
        "list": [
          { "label": "中文", "value": "zh" },
          { "label": "English", "value": "en" }
        ]
      }
    ],
    "questionGuide": {
      "open": true,
      "model": "gpt-4o-mini",
      "customPrompt": "根据对话内容生成3个后续问题"
    },
    "ttsConfig": {
      "type": "web",
      "voice": "zh-CN-XiaoxiaoNeural",
      "speed": 1.0
    },
    "whisperConfig": {
      "open": true,
      "autoSend": false,
      "autoTTSResponse": false
    },
    "fileSelectConfig": {
      "canSelectFile": true,
      "canSelectImg": true,
      "maxFiles": 10
    },
    "instruction": "这是一个通用的 AI 助手，可以回答各种问题。"
  }
}
```

---

## 10. 变量配置规范

### 10.1 VariableInputEnum 变量类型

```typescript
enum VariableInputEnum {
  "input" = "input",                       // 单行输入
  "textarea" = "textarea",                 // 多行文本
  "numberInput" = "numberInput",           // 数字输入
  "select" = "select",                     // 下拉选择
  "multipleSelect" = "multipleSelect",     // 多选
  "timePointSelect" = "timePointSelect",   // 时间点选择
  "timeRangeSelect" = "timeRangeSelect",   // 时间范围选择
  "switch" = "switch",                     // 开关
  "password" = "password",                 // 密码
  "file" = "file",                         // 文件
  "llmSelect" = "llmSelect",               // 模型选择
  "datasetSelect" = "datasetSelect"        // 知识库选择
}
```

### 10.2 VariableItemType 变量项结构

```typescript
interface VariableItemType {
  // 基础字段
  type: VariableInputEnum;                // 变量类型
  key: string;                            // 变量键名 (唯一标识)
  label: string;                          // 显示标签
  description: string;                    // 变量描述
  
  // 值配置
  valueType?: WorkflowIOValueTypeEnum;    // 值类型
  value?: any;                            // 默认值
  defaultValue?: any;                     // 默认值
  
  // 验证
  required?: boolean;                     // 是否必填
  
  // 渲染配置
  renderTypeList?: FlowNodeInputTypeEnum[]; // 渲染类型
  
  // 选项配置 (select/multipleSelect)
  list?: Array<{label: string, value: string}>; // 选项列表
  
  // 文件配置
  canSelectFile?: boolean;
  canSelectImg?: boolean;
  canSelectVideo?: boolean;
  canSelectAudio?: boolean;
  maxFiles?: number;
  
  // 时间配置
  timeGranularity?: 'day' | 'hour' | 'minute' | 'second';
}
```

### 10.3 变量配置示例

```json
{
  "variables": [
    {
      "type": "input",
      "key": "userName",
      "label": "用户姓名",
      "description": "请输入您的姓名，用于个性化回复",
      "valueType": "string",
      "renderTypeList": ["input"],
      "required": true,
      "value": ""
    },
    {
      "type": "numberInput",
      "key": "age",
      "label": "年龄",
      "description": "请输入您的年龄",
      "valueType": "number",
      "renderTypeList": ["numberInput"],
      "required": false,
      "min": 0,
      "max": 150,
      "value": 25
    },
    {
      "type": "select",
      "key": "language",
      "label": "语言偏好",
      "description": "选择您偏好的语言",
      "valueType": "string",
      "renderTypeList": ["select"],
      "required": true,
      "value": "zh",
      "list": [
        { "label": "中文", "value": "zh" },
        { "label": "English", "value": "en" },
        { "label": "日本語", "value": "ja" }
      ]
    },
    {
      "type": "multipleSelect",
      "key": "interests",
      "label": "兴趣爱好",
      "description": "选择您的兴趣爱好（可多选）",
      "valueType": "arrayString",
      "renderTypeList": ["multipleSelect"],
      "required": false,
      "value": [],
      "list": [
        { "label": "阅读", "value": "reading" },
        { "label": "音乐", "value": "music" },
        { "label": "运动", "value": "sports" },
        { "label": "旅游", "value": "travel" }
      ]
    },
    {
      "type": "switch",
      "key": "notifications",
      "label": "开启通知",
      "description": "是否接收消息通知",
      "valueType": "boolean",
      "renderTypeList": ["switch"],
      "required": false,
      "value": true
    },
    {
      "type": "textarea",
      "key": "bio",
      "label": "个人简介",
      "description": "简单介绍您自己",
      "valueType": "string",
      "renderTypeList": ["textarea"],
      "required": false,
      "maxLength": 500,
      "value": ""
    },
    {
      "type": "file",
      "key": "avatar",
      "label": "头像上传",
      "description": "上传您的头像",
      "valueType": "arrayString",
      "renderTypeList": ["fileSelect"],
      "required": false,
      "canSelectFile": true,
      "canSelectImg": true,
      "maxFiles": 1
    }
  ]
}
```

---

## 11. 完整配置示例

### 11.1 简单应用完整示例

```json
{
  "aiSettings": {
    "model": "gpt-4o",
    "systemPrompt": "你是一个专业的AI助手，请用友好、专业的方式回答用户问题。",
    "temperature": 0.7,
    "maxToken": 2000,
    "isResponseText": true,
    "maxHistories": 6,
    "aiChatReasoning": false,
    "aiChatTopP": 1,
    "useAgentSandbox": false
  },
  "dataset": {
    "datasets": [
      {
        "datasetId": "64f8a1b2c3d4e5f6g7h8i9j0",
        "avatar": "/icon/dataset.svg",
        "name": "产品知识库",
        "vectorModel": {
          "model": "text-embedding-3-small"
        }
      }
    ],
    "searchMode": "embedding",
    "limit": 3000,
    "similarity": 0.4,
    "embeddingWeight": 0.5,
    "usingReRank": false,
    "rerankWeight": 0.5,
    "datasetSearchUsingExtensionQuery": true
  },
  "selectedTools": [],
  "selectedAgentSkills": [],
  "chatConfig": {
    "welcomeText": "欢迎使用 AI 助手！请问有什么可以帮助您？",
    "variables": [
      {
        "type": "input",
        "key": "userName",
        "label": "您的姓名",
        "description": "请输入您的姓名以便个性化服务",
        "valueType": "string",
        "renderTypeList": ["input"],
        "required": true
      }
    ],
    "questionGuide": {
      "open": true,
      "model": "gpt-4o-mini"
    },
    "ttsConfig": {
      "type": "none"
    },
    "whisperConfig": {
      "open": false,
      "autoSend": false,
      "autoTTSResponse": false
    }
  }
}
```

### 11.2 工作流应用完整示例

```json
{
  "nodes": [
    {
      "nodeId": "workflowStart-1704067200",
      "name": "工作流开始",
      "flowNodeType": "workflowStart",
      "position": { "x": 100, "y": 200 },
      "avatar": "core/workflow/template/workflowStart",
      "colorSchema": "blue",
      "inputs": [
        {
          "key": "userChatInput",
          "renderTypeList": ["reference", "textarea"],
          "valueType": "string",
          "label": "用户问题",
          "required": true
        }
      ],
      "outputs": [
        {
          "id": "userChatInput",
          "key": "userChatInput",
          "label": "用户问题",
          "type": "static",
          "valueType": "string"
        }
      ]
    },
    {
      "nodeId": "datasetSearch-1704067201",
      "name": "搜索知识库",
      "flowNodeType": "datasetSearchNode",
      "position": { "x": 400, "y": 100 },
      "avatar": "core/workflow/template/datasetSearch",
      "colorSchema": "blueLight",
      "showStatus": true,
      "inputs": [
        {
          "key": "datasets",
          "renderTypeList": ["selectDataset", "reference"],
          "label": "选择知识库",
          "value": [
            {
              "datasetId": "64f8a1b2c3d4e5f6g7h8i9j0",
              "avatar": "/icon/dataset.svg",
              "name": "产品知识库",
              "vectorModel": { "model": "text-embedding-3-small" }
            }
          ],
          "valueType": "selectDataset",
          "required": true
        },
        {
          "key": "similarity",
          "renderTypeList": ["selectDatasetParamsModal"],
          "label": "",
          "value": 0.4,
          "valueType": "number"
        },
        {
          "key": "limit",
          "renderTypeList": ["hidden"],
          "label": "",
          "value": 3000,
          "valueType": "number"
        },
        {
          "key": "searchMode",
          "renderTypeList": ["hidden"],
          "label": "",
          "value": "embedding",
          "valueType": "string"
        },
        {
          "key": "userChatInput",
          "renderTypeList": ["reference", "textarea"],
          "label": "用户问题",
          "valueType": "string",
          "value": ["workflowStart-1704067200", "userChatInput"],
          "required": true
        }
      ],
      "outputs": [
        {
          "id": "datasetQuoteQA",
          "key": "datasetQuoteQA",
          "label": "知识库引用",
          "type": "static",
          "valueType": "datasetQuote"
        },
        {
          "id": "error",
          "key": "error",
          "label": "错误信息",
          "valueType": "string",
          "type": "error"
        }
      ]
    },
    {
      "nodeId": "chatNode-1704067202",
      "name": "AI 对话",
      "flowNodeType": "chatNode",
      "position": { "x": 800, "y": 200 },
      "avatar": "core/workflow/template/aiChat",
      "colorSchema": "blueDark",
      "showStatus": true,
      "version": "4.9.7",
      "inputs": [
        {
          "key": "model",
          "renderTypeList": ["settingLLMModel", "reference"],
          "label": "AI 模型",
          "valueType": "string",
          "value": "gpt-4o",
          "required": true
        },
        {
          "key": "temperature",
          "renderTypeList": ["hidden"],
          "label": "",
          "valueType": "number",
          "value": 0.7
        },
        {
          "key": "maxToken",
          "renderTypeList": ["hidden"],
          "label": "",
          "valueType": "number",
          "value": 2000
        },
        {
          "key": "systemPrompt",
          "renderTypeList": ["textarea", "reference"],
          "label": "系统提示词",
          "valueType": "string",
          "value": "你是一个专业的AI助手。请根据知识库内容回答用户问题。",
          "maxLength": 100000,
          "isRichText": true
        },
        {
          "key": "history",
          "renderTypeList": ["numberInput", "reference"],
          "label": "对话历史",
          "valueType": "chatHistory",
          "value": 6,
          "min": 0,
          "max": 50,
          "required": true
        },
        {
          "key": "quoteQA",
          "renderTypeList": ["settingDatasetQuotePrompt"],
          "label": "",
          "debugLabel": "知识库引用",
          "valueType": "datasetQuote",
          "value": ["datasetSearch-1704067201", "datasetQuoteQA"]
        },
        {
          "key": "userChatInput",
          "renderTypeList": ["reference", "textarea"],
          "label": "用户问题",
          "valueType": "string",
          "value": ["workflowStart-1704067200", "userChatInput"],
          "required": true
        }
      ],
      "outputs": [
        {
          "id": "history",
          "key": "history",
          "label": "新上下文",
          "valueType": "chatHistory",
          "type": "static",
          "required": true
        },
        {
          "id": "answerText",
          "key": "answerText",
          "label": "AI 回复内容",
          "valueType": "string",
          "type": "static",
          "required": true
        },
        {
          "id": "error",
          "key": "error",
          "label": "错误信息",
          "valueType": "string",
          "type": "error"
        }
      ]
    },
    {
      "nodeId": "answerNode-1704067203",
      "name": "直接回复",
      "flowNodeType": "answerNode",
      "position": { "x": 1200, "y": 200 },
      "avatar": "core/workflow/template/answer",
      "colorSchema": "blue",
      "inputs": [
        {
          "key": "text",
          "renderTypeList": ["reference", "textarea"],
          "label": "回复内容",
          "valueType": "string",
          "value": ["chatNode-1704067202", "answerText"],
          "required": true
        }
      ],
      "outputs": []
    }
  ],
  "edges": [
    {
      "source": "workflowStart-1704067200",
      "sourceHandle": "workflowStart-1704067200-source-right",
      "target": "datasetSearch-1704067201",
      "targetHandle": "datasetSearch-1704067201-target-left"
    },
    {
      "source": "workflowStart-1704067200",
      "sourceHandle": "workflowStart-1704067200-source-right",
      "target": "chatNode-1704067202",
      "targetHandle": "chatNode-1704067202-target-left"
    },
    {
      "source": "datasetSearch-1704067201",
      "sourceHandle": "datasetSearch-1704067201-source-right",
      "target": "chatNode-1704067202",
      "targetHandle": "chatNode-1704067202-target-left"
    },
    {
      "source": "chatNode-1704067202",
      "sourceHandle": "chatNode-1704067202-source-right",
      "target": "answerNode-1704067203",
      "targetHandle": "answerNode-1704067203-target-left"
    }
  ],
  "chatConfig": {
    "welcomeText": "欢迎使用 AI 助手！我可以帮您查询产品信息。",
    "variables": [],
    "questionGuide": {
      "open": true,
      "model": "gpt-4o-mini"
    },
    "ttsConfig": {
      "type": "none"
    },
    "whisperConfig": {
      "open": false,
      "autoSend": false,
      "autoTTSResponse": false
    }
  }
}
```

---

## 12. 验证检查清单

在提交 JSON 配置之前，请检查以下项目：

### 12.1 基础结构验证

- [ ] JSON 格式有效，无语法错误
- [ ] 根对象包含 `aiSettings` (简单应用) 或 `nodes` (工作流应用)
- [ ] 所有必填字段已填写

### 12.2 节点验证

- [ ] 每个节点都有唯一的 `nodeId`
- [ ] `flowNodeType` 是有效的枚举值
- [ ] `name` 字段不为空
- [ ] `inputs` 是数组类型
- [ ] `outputs` 是数组类型

### 12.3 输入验证

- [ ] 每个输入项都有 `key` 字段
- [ ] `renderTypeList` 是有效的数组
- [ ] `valueType` 是有效的枚举值
- [ ] 引用值的格式正确 `["nodeId", "outputKey"]`

### 12.4 输出验证

- [ ] 每个输出项都有唯一的 `id`
- [ ] `key` 字段不为空
- [ ] `type` 是有效的枚举值
- [ ] 动态输出项有正确的 `key` 和 `valueType`

### 12.5 边验证

- [ ] `source` 和 `target` 对应存在的节点 ID
- [ ] `sourceHandle` 和 `targetHandle` 格式正确
- [ ] 没有重复或冲突的边定义
- [ ] 判断器节点的 `sourceHandle` 使用 `IF`, `ELSE IF N`, `ELSE` 格式

### 12.8 判断器节点验证

- [ ] 输入键名为 `ifElseList`，不是 `condition`
- [ ] `value` 是数组，不是对象
- [ ] 条件对象使用 `condition` 字段，不是 `operator`
- [ ] 条件操作符使用小驼峰命名（如 `equalTo`, `greaterThan`）
- [ ] 输出键名为 `ifElseResult`，类型为 `string`
- [ ] 边连接的 `sourceHandle` 使用 `IF`, `ELSE IF 1`, `ELSE` 等

### 12.6 知识库验证

- [ ] `datasetId` 是有效的 MongoDB ObjectId 格式
- [ ] `vectorModel.model` 不为空
- [ ] `searchMode` 是有效的枚举值

### 12.7 模型验证

- [ ] `model` 值在系统配置中存在
- [ ] `temperature` 在 0-2 范围内
- [ ] `maxToken` 是正整数
- [ ] `maxHistories` 在 0-100 范围内

---

## 附录

### A. WorkflowIOValueTypeEnum 值类型枚举

```typescript
enum WorkflowIOValueTypeEnum {
  "string" = "string",
  "number" = "number",
  "boolean" = "boolean",
  "object" = "object",
  "arrayString" = "arrayString",
  "arrayNumber" = "arrayNumber",
  "arrayBoolean" = "arrayBoolean",
  "arrayObject" = "arrayObject",
  "arrayAny" = "arrayAny",
  "any" = "any",
  "chatHistory" = "chatHistory",
  "datasetQuote" = "datasetQuote",
  "dynamic" = "dynamic",
  "selectDataset" = "selectDataset"
}
```

### B. NodeInputKeyEnum 常用输入键名

| 键名 | 说明 |
|------|------|
| `model` | AI 模型 |
| `systemPrompt` | 系统提示词 |
| `temperature` | 温度参数 |
| `maxToken` | 最大 Token 数 |
| `history` | 对话历史 |
| `userChatInput` | 用户输入 |
| `datasets` | 知识库列表 |
| `similarity` | 相似度阈值 |
| `limit` | 最大限制 |
| `quoteQA` | 知识库引用 |
| `system_httpMethod` | HTTP 方法 |
| `system_httpReqUrl` | HTTP 请求 URL |
| `system_httpHeaders` | HTTP 请求头 |
| `system_httpJsonBody` | HTTP JSON 请求体 |
| `code` | 代码内容 |
| `codeType` | 代码类型 |
| `agents` | 分类代理列表 |
| `ifElseList` | 判断器条件列表 |

### C. NodeOutputKeyEnum 常用输出键名

| 键名 | 说明 |
|------|------|
| `userChatInput` | 用户输入 |
| `history` | 对话历史 |
| `answerText` | AI 回复文本 |
| `reasoningText` | 推理内容 |
| `datasetQuoteQA` | 知识库引用 |
| `error` | 错误信息 |
| `httpRawResponse` | HTTP 原始响应 |
| `rawResponse` | 原始响应数据 |
| `cqResult` | 分类结果 |
| `ifElseResult` | 判断器结果 |
| `newContext` | 新上下文 |

---

*本文档详细描述了 FastGPT JSON 配置的完整规范。如需了解更多信息，请参考源代码中的类型定义文件。*

*最后更新：2025年*

## 13. 排障指引

通用 JSON 配置排障与修复方案已拆分至独立文档：

- `docs/json-config-troubleshooting.md`

建议在出现“可导入但运行异常”“节点引用失效”“分支不触发”“文件上传不可用”等问题时，优先阅读该文档并按自检清单逐项排查。
