# FastGPT JSON 配置通用排障指南

> 本文档聚焦 FastGPT 工作流 JSON 在“可导入但运行异常”场景下的通用问题描述、根因与修复建议，和具体业务案例解耦。

## 1. 适用范围

当你遇到以下问题时，建议优先参考本文：

- JSON 可以导入，但运行中断或无输出
- 分支节点（如判断器）不按预期分流
- 指定回复节点无法正确引用上游输出
- 文件上传入口不可见或文件无法被下游节点读取
- 表单字段明明有默认值却被判定“未填写”

---

## 2. 高发问题与修复

### 2.1 节点存在但不触发

**典型现象**：
- 节点未执行，后续链路中断
- 部分分支永远不进入

**常见根因**：
- `flowNodeType` 与模板定义不一致
- `nodeId` 不唯一或被误改
- 边连接的 `source/target` 指向不存在节点
- `sourceHandle/targetHandle` 命名不符合规范

**修复建议**：
1. 确保所有 `nodeId` 唯一且稳定；
2. 普通边使用 `-source-right` → `-target-left`；
3. 判断器边使用 `-source-IF / -source-ELSE IF N / -source-ELSE`；
4. 检查每条边的 `source/target` 都能在 `nodes` 中找到对应 `nodeId`。

---

### 2.2 上游输出引用失效

**典型现象**：
- 节点执行了但输入为空
- 回复节点输出空白

**常见根因**：
- `inputs[].value` 引用了不存在的节点或输出键
- 混用不同引用格式

**修复建议**：
1. 标准引用格式（数组）：
```json
"value": ["nodeId", "outputKey"]
```
2. 检查被引用的 `outputKey` 是否确实存在于上游节点 `outputs`；
3. 不要引用临时字段名或未声明输出。

---

### 2.3 指定回复节点（answerNode）显示异常

**典型现象**：
- 回复节点不显示上游结果
- 输出固定文本或空文本

**常见根因**：
- 输入键不是 `text`
- `value` 格式与当前项目约定不一致

**修复建议**：
1. `answerNode` 输入键固定为：
```json
"key": "text"
```
2. 若项目约定使用字符串模板引用，上游输出建议统一为：
```json
"value": "{{$nodeId.outputKey$}}"
```
3. 若项目约定使用数组引用，则统一为：
```json
"value": ["nodeId", "outputKey"]
```
4. 在同一工作流内不要混用两套引用规则。

---

### 2.4 文件上传不可用或文件未被读取

**典型现象**：
- 聊天窗口没有文件上传按钮
- 文件上传后下游节点拿不到内容

**常见根因**：
- `chatConfig.fileSelectConfig` 未开启
- 未将上传文件传给解析节点（如 `readFiles`）
- 下游 AI 节点未接入文件解析结果

**修复建议**：
1. 在 `chatConfig` 开启文件上传：
```json
"fileSelectConfig": {
  "canSelectFile": true,
  "maxFiles": 10
}
```
2. 文件解析节点输入示例：
```json
"value": ["workflowStart-xxx", "userFiles"]
```
3. AI 节点输入应引用解析结果（如 `["readFiles-xxx", "system_text"]`）。

---

### 2.5 AI 节点“只有提示词，没有业务输入”

**典型现象**：
- 模型有输出，但内容空泛或偏题
- 结果不稳定，复现困难

**常见根因**：
- 仅配置了 `systemPrompt`，未注入有效 `userChatInput` / `fileUrlList`

**修复建议**：
1. `systemPrompt` 负责规则，`userChatInput`/`fileUrlList` 负责数据；
2. 至少保证一个有效业务输入：
   - 文本输入：`["nodeId","textOutput"]`
   - 文件输入：`["workflowStart-xxx","userFiles"]` 或其他文件数组输出

---

### 2.6 布尔开关字段（switch）校验歧义

**典型现象**：
- 默认 `false` 被视为“未填写”
- 只有选 `true` 才能继续

**常见根因**：
- `switch` 字段与前端 `required` 校验冲突

**修复建议**：
1. 布尔开关字段优先使用：
```json
"required": false,
"value": false
```
2. 若必须显式选择，可改用 `select`（是/否）避免歧义。

---

### 2.7 判断器分支逻辑正确但不命中

**典型现象**：
- IF/ELSE 配置看似正确，但总走 ELSE

**常见根因**：
- 条件关键词与上游实际输出不一致（大小写、空格、文案差异）
- 判断条件运算符使用不当（如应使用 `include` 却使用 `equalTo`）

**修复建议**：
1. 固定上游结论词集合（例如：`通过/复核/不通过`）；
2. 分支条件用可容错写法（常用 `include`）；
3. 调试时先打印上游原始输出再配置条件。

---

## 3. 导入前通用自检清单

- [ ] JSON 语法合法（可被 `JSON.parse` 解析）
- [ ] 所有 `nodeId` 唯一
- [ ] 所有边的 `source/target` 都存在
- [ ] `sourceHandle/targetHandle` 命名规范正确
- [ ] 判断器分支 handle 使用 `IF / ELSE IF N / ELSE`
- [ ] 上游引用都能定位到有效节点与输出键
- [ ] `answerNode` 的 `key` 为 `text`
- [ ] 指定回复 `value` 采用单一且一致的引用格式
- [ ] 文件型流程已开启 `chatConfig.fileSelectConfig.canSelectFile`
- [ ] AI 节点不仅有提示词，还接入了有效业务输入
- [ ] 开场白包含明确操作提示（如“请直接上传文件”）

---

## 4. 推荐验证流程

1. 先做静态检查：JSON 语法、节点 ID、边引用、输入引用；
2. 再做最小链路联调：开始节点 -> 1 个核心处理节点 -> 回复节点；
3. 最后验证分支：分别构造能命中 IF / ELSE IF / ELSE 的输入样例；
4. 保留一份“稳定可运行”的基线 JSON，后续改动基于基线迭代。

---

*文档目标：提供与业务场景解耦的通用排障方法，提升 JSON 工作流配置的导入成功率与运行稳定性。*

---

## 5. Default Output Rules (Enforced)

- Generated workflow JSON must include a default system config node: `flowNodeType: "userGuide"`.
- For designated reply nodes (`answerNode`), the `text` input should default to template-style variable reference:
  - `"value": "{{$nodeId.outputKey$}}"`
- Do not output array-style reference for `answerNode.text` (for example `["nodeId","outputKey"]`) unless user explicitly requests that style.
