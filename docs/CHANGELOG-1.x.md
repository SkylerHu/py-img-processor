# Release Notes

## 1.2.4
- feat: 扩展配置`PROCESSOR_TEMP_DIR`设置临时目录
    - 可配置使用 /dev/shm 目录

## 1.2.3
- fix: 修复`save_img_to_file`函数中im.format可能为空的问题

## 1.2.2
- perf: 调整Image.open都使用with的方式使用，避免内存泄漏
- fix: 修复函数 `trans_uri_to_im` 在 copy im 时丢失 info 信息的问题
- chore: 调整依赖 `py-enum>=2.1.1` 解决 mypy 检测枚举的问题

## 1.2.1
- fix: 修复 `merge` 操作中参数 `p` 的处理，调整成在处理 `bg` 参数之后
- docs: 修正文档说明

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
