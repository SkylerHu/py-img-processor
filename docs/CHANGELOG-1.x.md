# Release Notes
## 1.3.3
- fix: 调整`blur`取值范围，从`[1,50]`调整为`[1,512]`
- fix: 修复`mode=P`的图片保存`JPEG`报错的问题
    - JPEG 仅支持真彩色（RGB）或灰度图（L）
- fix: 修复 `ImageFormat.WEBP` 的值，`WebP`统一调整为大写`WEBP`

## 1.3.2
- fix: 设置 `Image.MAX_IMAGE_PIXELS` 使 `PROCESSOR_MAX_PIXEL` 真实生效
- chore: 修复关于 `ImageFile` 对象的typing声明

## 1.3.1
- fix: 修复函数名称`process_image_obj`

## 1.3.0
- refactor: 枚举 `OpAction` 中移除了保存图像需要的参数key
- fix: 调整方法 `process_image` 中参数位置，允许 `out_put` 可以为空，并增加 kwargs 透传Image.save函数的参数
- feat: 新增 `preocess_image_obj` 直接可以处理 `Image` 对象作为输入参数；


## 1.2.4
- feat: 扩展配置`PROCESSOR_TEMP_DIR`设置临时目录
    - 可配置使用 /dev/shm 目录
- fix: 输入地址是url链接资源时，下载后保存临时文件前尝试解析出url中文件后缀用于suffix

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
