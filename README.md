# AIBuilder JSON Config

> Enterprise-grade FastGPT workflow JSON generator by Sangfor

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

[English](#english) | [中文](#中文)

---

## English

### 🎯 What is AIBuilder JSON Config?

AIBuilder JSON Config is a professional tool that transforms natural-language business requirements into production-ready FastGPT workflow JSON configurations. Developed by **Sangfor**, this tool ensures your AI workflows are correctly structured, validated, and import-ready.

### ✨ Key Features

- **Natural Language to JSON**: Convert business process descriptions into FastGPT-importable JSON
- **Strict Validation**: Built-in validation rules ensure your workflows are error-free
- **Production-Ready**: Generate complete workflows with error handling, branching, and user guidance
- **Enterprise-Grade**: Follows best practices for enterprise AI deployment
- **Comprehensive Documentation**: Detailed references for all node types and configurations

### 🚀 Quick Start

#### Platform Compatibility

This tool works with **any AI agent platform that supports skills**, including:

- **Claude Code** (Anthropic's official CLI)
- **OpenClaw** (Open-source Claude alternative)
- **Costrict.ai** (AI workflow platform)
- **Trae** (AI development environment)
- Any other platform with skill/plugin support

#### Installation

**For Claude Code** (example):

1. Copy the `aibuilder-json-config` folder to your skills directory:
   
   ```bash
   cp -r aibuilder-json-config ~/.claude/skills/
   ```

2. Restart Claude Code or reload skills

**For other platforms**: Follow your platform's skill installation guide and place the `aibuilder-json-config` folder in the appropriate skills directory.

#### Python Requirements

The `scripts/` directory contains Python utility scripts for validating and inspecting FastGPT JSON configurations:

- `validate_fastgpt_json.py` — Validate workflow JSON against runtime contracts
- `inspect_official_templates.py` — Print node IO contracts from templates

**Prerequisites**:

- Python 3.9+ installed on your system
- No third-party dependencies required (uses only standard library)

**Verify installation**:

```bash
python --version
```

**Usage example**:

```bash
python scripts/validate_fastgpt_json.py path/to/workflow.json
python scripts/inspect_official_templates.py
```

#### Basic Usage

In Claude Code, describe your workflow requirements:

```
Create a FastGPT workflow for HR resume screening:
- User uploads resume PDF
- Extract candidate information (name, experience, skills)
- Score the resume based on job requirements
- Classify as: Excellent / Good / Need Review / Reject
- Return structured evaluation report
```

The tool will:

1. Analyze your requirements
2. Confirm assumptions and critical options
3. Generate complete FastGPT JSON with all nodes, edges, and configurations
4. Validate the output
5. Save to a `.json` file ready for import

### 📚 What's Included

#### Core Skill

- `SKILL.md`: Main skill definition and workflow rules

#### Comprehensive References

- `generation-hard-rules.md`: Mandatory generation rules
- `required-input-rules.md`: User input collection rules
- `ifelse-rules.md`: Conditional branching rules
- `dataset-rules.md`: Knowledge base retrieval rules
- `classify-rules.md`: Question classification rules
- `node-selection-rules.md`: Node type selection guide
- `node-field-contracts.md`: Field-level runtime contracts
- `json-config-specification.md`: Complete JSON schema
- `json-config-runtime-reference.md`: Runtime-accurate templates
- `json-config-troubleshooting.md`: Common issues and solutions
- `validation-checklist.md`: Pre-import validation checklist
- `protocol-v1.md`: Skill protocol specification

### 🎨 Supported Node Types

- **Input Collection**: `workflowStart`, `formInput`, `userSelect`
- **File Processing**: `readFiles`
- **AI Reasoning**: `chatNode`, `agent`, `tools`
- **Data Extraction**: `contentExtract`
- **Knowledge Retrieval**: `datasetSearchNode`, `datasetConcatNode`
- **Classification**: `classifyQuestion`
- **Branching**: `ifElseNode`
- **Text Processing**: `textEditor`
- **HTTP Requests**: `httpRequest468`
- **State Management**: `variableUpdate`
- **Loops**: `loop`
- **Query Optimization**: `cfr`
- **Output**: `answerNode`
- **System Config**: `userGuide`

### 🔧 Advanced Features

#### Requirement Enrichment

The tool automatically adds:

- Error handling paths
- Default configurations
- User guidance text
- Input validation
- Fallback messages

#### Strict Validation

Every generated workflow is validated for:

- Node input/output completeness
- Edge connectivity
- Reference validity
- Branch handle correctness
- Layout spacing requirements

#### Production-Ready Output

Generated workflows include:

- Markdown-formatted welcome text
- Chinese user-facing labels
- Structured intermediate outputs
- Complete metadata
- UTF-8 encoding

### 📖 Documentation

For detailed documentation, see the `references/` folder:

- Start with `generation-hard-rules.md` for core principles
- Check `node-selection-rules.md` for choosing the right nodes
- Review `validation-checklist.md` before importing

### 🤝 Use Cases

- **HR Automation**: Resume screening, candidate evaluation
- **Customer Service**: Ticket classification, FAQ routing
- **Document Processing**: Contract analysis, compliance checking
- **Knowledge Management**: RAG workflows, document Q&A
- **Business Process**: Approval workflows, decision trees

### 🏢 About Sangfor AIBuilder

This tool is part of the **Sangfor AIBuilder** ecosystem, an enterprise-grade RAG platform based on FastGPT.

**Sangfor AIBuilder** offers:

- 🔒 Enterprise security & compliance
- 🏢 Private deployment options
- 🛡️ Advanced security features
- 📞 Enterprise support & SLA
- 🚀 Production-ready capabilities

[Learn more about Sangfor AIBuilder →](https://www.sangfor.com/aibuilder)

### 📄 License

Apache 2.0 License. See [LICENSE](LICENSE) for details.

### 🔗 Links

- [Sangfor AIBuilder](https://www.sangfor.com/aibuilder)
- [FastGPT](https://github.com/labring/FastGPT)
- [AIBuilder Enterprise Toolkit](https://github.com/sangfor-aibuilder/aibuilder-enterprise-toolkit)

### 👥 Join Our Community

Join the **AIBuilder Developer Community** for:
- Technical discussions and support
- Latest updates and releases
- Best practices and use cases
- Direct communication with the team

<div align="center">
  <img src="aibuilderqcoder.JPG" alt="AIBuilder Developer Community QR Code" width="300">
  <p><em>Scan to join our developer community</em></p>
</div>

---

## 中文

### 🎯 什么是 AIBuilder JSON Config？

AIBuilder JSON Config 是一个专业工具，可以将自然语言业务需求转换为生产就绪的 FastGPT 工作流 JSON 配置。由**SANGFOR AIBuilder Team**开发，确保您的 AI 工作流结构正确、经过验证且可直接导入。

### ✨ 核心功能

- **自然语言转 JSON**：将业务流程描述转换为 FastGPT 可导入的 JSON
- **严格验证**：内置验证规则确保工作流无错误
- **生产就绪**：生成包含错误处理、分支和用户指导的完整工作流
- **企业级**：遵循企业 AI 部署最佳实践
- **完整文档**：所有节点类型和配置的详细参考

### 🚀 快速开始

#### 平台兼容性

本工具适用于**任何支持 skills 的 AI Agent 平台**，包括：

- **Claude Code**（Anthropic 官方 CLI）
- **OpenClaw**（开源 Claude 替代方案）
- **Costrict.ai**（AI 工作流平台）
- **Trae**（AI 开发环境）
- 任何其他支持 skill/plugin 的平台

#### 安装

**以 Claude Code 为例**：

1. 将 `aibuilder-json-config` 文件夹复制到 skills 目录：
   
   ```bash
   cp -r aibuilder-json-config ~/.claude/skills/
   ```

2. 重启 Claude Code 或重新加载 skills

**其他平台**：按照您平台的 skill 安装指南，将 `aibuilder-json-config` 文件夹放置到相应的 skills 目录。

#### Python 环境要求

`scripts/` 目录包含用于验证和检查 FastGPT JSON 配置的 Python 工具脚本：

- `validate_fastgpt_json.py` — 验证工作流 JSON 是否符合运行时契约
- `inspect_official_templates.py` — 打印模板中的节点 IO 契约

**前置条件**：

- 系统已安装 Python 3.9+
- 无需第三方依赖（仅使用标准库）

**验证安装**：

```bash
python --version
```

**使用示例**：

```bash
python scripts/validate_fastgpt_json.py path/to/workflow.json
python scripts/inspect_official_templates.py
```

#### 基础使用

在 Claude Code 中描述您的工作流需求：

```
创建一个 FastGPT 工作流用于 HR 简历筛选：
- 用户上传简历 PDF
- 提取候选人信息（姓名、经验、技能）
- 根据岗位要求对简历打分
- 分类为：优秀 / 良好 / 需要复审 / 拒绝
- 返回结构化评估报告
```

工具会：

1. 分析您的需求
2. 确认假设和关键选项
3. 生成包含所有节点、边和配置的完整 FastGPT JSON
4. 验证输出
5. 保存为可直接导入的 `.json` 文件

### 📚 包含内容

#### 核心 Skill

- `SKILL.md`：主 skill 定义和工作流规则

#### 完整参考文档

- `generation-hard-rules.md`：强制生成规则
- `required-input-rules.md`：用户输入收集规则
- `ifelse-rules.md`：条件分支规则
- `dataset-rules.md`：知识库检索规则
- `classify-rules.md`：问题分类规则
- `node-selection-rules.md`：节点类型选择指南
- `node-field-contracts.md`：字段级运行时契约
- `json-config-specification.md`：完整 JSON 模式
- `json-config-runtime-reference.md`：运行时准确模板
- `json-config-troubleshooting.md`：常见问题和解决方案
- `validation-checklist.md`：导入前验证清单
- `protocol-v1.md`：Skill 协议规范

### 🎨 支持的节点类型

- **输入收集**：`workflowStart`、`formInput`、`userSelect`
- **文件处理**：`readFiles`
- **AI 推理**：`chatNode`、`agent`、`tools`
- **数据提取**：`contentExtract`
- **知识检索**：`datasetSearchNode`、`datasetConcatNode`
- **分类**：`classifyQuestion`
- **分支**：`ifElseNode`
- **文本处理**：`textEditor`
- **HTTP 请求**：`httpRequest468`
- **状态管理**：`variableUpdate`
- **循环**：`loop`
- **查询优化**：`cfr`
- **输出**：`answerNode`
- **系统配置**：`userGuide`

### 🔧 高级功能

#### 需求增强

工具自动添加：

- 错误处理路径
- 默认配置
- 用户指导文本
- 输入验证
- 回退消息

#### 严格验证

每个生成的工作流都会验证：

- 节点输入/输出完整性
- 边连接性
- 引用有效性
- 分支句柄正确性
- 布局间距要求

#### 生产就绪输出

生成的工作流包含：

- Markdown 格式的欢迎文本
- 中文用户界面标签
- 结构化中间输出
- 完整元数据
- UTF-8 编码

### 📖 文档

详细文档请查看 `references/` 文件夹：

- 从 `generation-hard-rules.md` 开始了解核心原则
- 查看 `node-selection-rules.md` 选择正确的节点
- 导入前查看 `validation-checklist.md`

### 🤝 使用场景

- **HR 自动化**：简历筛选、候选人评估
- **客户服务**：工单分类、FAQ 路由
- **文档处理**：合同分析、合规检查
- **知识管理**：RAG 工作流、文档问答
- **业务流程**：审批工作流、决策树

### 🏢 关于深信服 AIBuilder

本工具是 **深信服 AIBuilder** 生态系统的一部分，这是一个基于 FastGPT 的企业级 RAG 平台。

**深信服 AIBuilder** 提供：

- 🔒 企业安全与合规
- 🏢 私有化部署选项
- 🛡️ 高级安全功能
- 📞 企业级支持与 SLA
- 🚀 生产就绪能力



### 📄 许可证

Apache 2.0 许可证。详见 [LICENSE](LICENSE)。

### 🔗 链接

- [深信服 AIBuilder](https://www.sangfor.com/aibuilder)
- [FastGPT](https://github.com/labring/FastGPT)
- [AIBuilder 企业工具包](https://github.com/sangfor-aibuilder/aibuilder-enterprise-toolkit)

### 👥 加入开发者社群

加入 **AIBuilder 开发者社群**，获取：
- 技术讨论和支持
- 最新更新和发布
- 最佳实践和使用案例
- 与团队直接沟通

<div align="center">
  <img src="aibuilderqcoder.JPG" alt="AIBuilder 开发者社群二维码" width="300">
  <p><em>扫码加入开发者社群</em></p>
</div>

---

Made with ❤️ by [Sangfor](https://www.sangfor.com)
