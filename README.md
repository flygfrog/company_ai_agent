# Company AI Agent

本项目是尧唐科技暑期实习项目，目标是建立一个部署在公司服务器上的 AI Agent 系统，通过钉钉聊天机器人接收用户指令，辅助处理公司日常重复性工作。

## 第一版目标

用户在钉钉中输入工作内容，机器人自动生成规范日报。

## 初步功能

1. 钉钉机器人消息接收
2. Python 后端服务
3. 大模型 API 调用
4. 日报 / 周报生成
5. 后续扩展 RAG 知识库和工具调用

## 项目结构

```text
company-ai-agent/
├─ docs/
├─ src/
├─ tests/
├─ README.md
├─ requirements.txt
└─ .env.example
```

## src文件记录

1. 把日报生成 prompt 单独放到 prompts.py，不要全写在 main.py 里。
2. 把“生成日报”的逻辑放进 agent.py。这个文件的作用是：以后你不管从 FastAPI、钉钉机器人还是命令行调用日报功能，都统一走这里。
3. 把 main.py 简化成只负责接收请求和返回结果。
