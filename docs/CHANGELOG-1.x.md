# Release Notes

## 1.2.0
- feat: 支持处理链接地址资源
    - 方法 `process_image_by_path` 名称变更为 `process_image`
- fix: `settings` 在将处理参数对外开放场景下限制输入资源；默认无限制
    - `PROCESSOR_WORKSPACES` tuple, 限制水印等资源系统文件路径 （startswith匹配）
    - `PROCESSOR_ALLOW_DOMAINS` tuple, 限制链接地址域名 （endswith匹配）

## 1.1.0
- fix: 修复 `resize` 等场景按照比例计算像素时，用 `round` 替换 `int` 操作

## 1.0.3
- fix: 去掉对`typing_extensions`的依赖

## 1.0.1
- fix: 修复命令行`img-processor`输出文件命名的问题

## 1.0.0 (2024-06-23)
- build: lib发版
