# 更新日志

本文件记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.3.6]

### 修复

- 增强 `transpose_im` 的异常兜底与版本兼容能力：
  - 异常捕获从 `NotImplementedError` 扩大为 `Exception`，兼容 EXIF 数据损坏、字节截断等导致的 `OSError` 等异常。
  - 回退分支转置完成后丢弃已损坏的 EXIF 信息，避免残留方向标签导致二次旋转。
  - 兼容 Pillow 8：`ExifTags.Base.Orientation` 替换为常量 `0x0112`，`Image.Transpose` 通过 `getattr` 回退到 `Image`。
- `save_img_to_file` 当 `im.format` 为空时默认使用 `JPEG`，避免 `fmt` 为 `None` 导致 `AttributeError`。

## [1.3.5]

### 修复

- 修复 `ImageOps.exif_transpose` 处理 multistrip 图像时抛出 `NotImplementedError` 的问题。
  - 新增 `transpose_im` 函数封装 EXIF 方向转置逻辑，优先使用 `exif_transpose`，失败时回退到手动读取 Orientation 标签进行转置。
  - `pre_processing` 和 `ProcessorCtr.handle_img_actions` 统一使用 `transpose_im`。

## [1.3.4]

### 新增

- 支持 `animation` 参数保留动画效果。

### 修复

- 调整 `ProcessorCtr.save_img_to_file` 根据 format 处理 mode：
  - JPEG 场景判断中单词拼写错误 `"GBA"` → `"RGB"`。
  - 增加透明场景对 mode 判断的处理，解决 `P` 模式下丢失 info 中的透明信息。

## [1.3.3]

### 修复

- 调整 `blur` 取值范围，从 `[1, 50]` 调整为 `[1, 512]`。
- 修复 `mode=P` 的图片保存 `JPEG` 报错的问题（JPEG 仅支持 RGB 或 L）。
- 修复 `ImageFormat.WEBP` 的值，统一为大写 `WEBP`。

## [1.3.2]

### 修复

- 设置 `Image.MAX_IMAGE_PIXELS` 使 `PROCESSOR_MAX_PIXEL` 真实生效。
- 修复关于 `ImageFile` 对象的 typing 声明。

## [1.3.1]

### 修复

- 修复函数名称 `process_image_obj`。

## [1.3.0]

### 新增

- 新增 `process_image_obj` 直接处理 Pillow `Image` 对象作为输入参数。

### 变更

- 枚举 `OpAction` 中移除保存图像需要的参数 key。
- 调整方法 `process_image` 中参数位置，允许 `out_path` 为空，并增加 `kwargs` 透传 `Image.save` 函数参数。

## [1.2.4]

### 新增

- 扩展配置 `PROCESSOR_TEMP_DIR` 设置临时目录（可配置使用 `/dev/shm`）。

### 修复

- 输入地址是 URL 链接资源时，下载后保存临时文件前尝试解析出 URL 中文件后缀。

## [1.2.3]

### 修复

- 修复 `save_img_to_file` 函数中 `im.format` 可能为空的问题。

## [1.2.2]

### 变更

- 调整 `Image.open` 统一使用 `with` 上下文管理器，避免内存泄漏。
- 调整依赖 `py-enum>=2.1.1` 解决 mypy 检测枚举的问题。

### 修复

- 修复函数 `trans_uri_to_im` 在复制 Image 时丢失 info 信息的问题。

## [1.2.1]

### 修复

- 修复 `merge` 操作中参数 `p` 的处理，调整成在处理 `bg` 参数之后。
- 修正文档说明。

## [1.2.0]

### 新增

- 支持处理 URL 链接地址资源。

### 变更

- 方法 `process_image_by_path` 名称变更为 `process_image`。
- 在将处理参数对外开放场景下限制输入资源（默认无限制）：
  - `PROCESSOR_WORKSPACES` — 限制水印等资源系统文件路径（`startswith` 匹配）。
  - `PROCESSOR_ALLOW_DOMAINS` — 限制链接地址域名（`endswith` 匹配）。

## [1.1.0]

### 修复

- 修复 `resize` 等场景按照比例计算像素时，用 `round` 替换 `int` 操作。

## [1.0.3]

### 修复

- 去掉对 `typing_extensions` 的依赖。

## [1.0.1]

### 修复

- 修复命令行 `img-processor` 输出文件命名的问题。

## [1.0.0] - 2024-06-23

### 新增

- 首次发布。
