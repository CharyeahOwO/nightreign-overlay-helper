# 对话摘要

## 需求概览
- 构建项目为 exe，并确认输出位置
- 将 config.yaml 中 6 个窗口相关配置添加到设置界面以便切换
- 修复配置/日志默认存储路径导致的保存问题，确保可写、可恢复，并完善异常处理
- 修复完成后重新构建项目

## 已完成工作
- 执行构建脚本 build.bat，生成 exe
- 在设置界面增加 6 个窗口兼容选项并写回 config.yaml
- 调整配置读写路径与可写性检查，支持自动回退与迁移
- 完成基础编译检查与重建

## 关键改动
- 新增可写路径选择与迁移逻辑，避免因权限导致配置无法保存
- 配置文件改为写入用户可写目录，并在首次启动时从默认 config.yaml 复制
- 设置界面新增 6 个窗口兼容开关并保存到配置

## 变更文件
- src/ui/settings.py
- src/common.py
- src/config.py

## 构建与验证
- 已执行 python -m py_compile src/common.py src/config.py src/ui/settings.py src/app.py
- 已执行 .\build.bat，输出目录 dist\nightreign-overlay-helper

## 输出位置
- dist/nightreign-overlay-helper/nightreign-overlay-helper.exe
