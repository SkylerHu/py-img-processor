#!/usr/bin/env python
# coding=utf-8
import typing
import os
import sys
import argparse
import traceback

from imgprocessor import VERSION
from imgprocessor.processor import process_image_by_path


def main(argv: typing.Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="img-processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="图像处理",
    )

    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "-P", "--path", type=str, required=True, help="输入图像的文件路径/目录，若是目录可以批量处理目录下所有图像"
    )
    parser.add_argument("--action", type=str, nargs="+", help="操作参数，可对同一个文件多组操作")
    parser.add_argument("-O", "--output", type=str, required=True, help="输出图像目录")
    parser.add_argument("--overwrite", action="store_true", help="是否覆盖输出路径中已有文件")

    args = parser.parse_args(argv)

    path = args.path
    base_dir = path
    # 初始化输入图像文件列表
    file_paths = []
    if os.path.isdir(path):
        for path, dir_list, file_list in os.walk(path):
            for file_name in file_list:
                p = os.path.join(path, file_name)
                file_paths.append(p)
    else:
        file_paths = [path]
        base_dir = os.path.dirname(path)

    total = len(file_paths)
    count = 0
    # 输出目录
    output = args.output
    for file_path in file_paths:
        count += 1
        f_tag = f"{count}/{total}\t处理 {file_path}"
        print(f_tag, flush=True, end="\r")
        # 相对path的相对路径
        if not base_dir or base_dir in [".", "./"]:
            relative_path = file_path
        else:
            relative_path = file_path.split(base_dir, 1)[-1]
        relative_path = relative_path.strip("/")

        prefix, ext = os.path.splitext(relative_path)
        ac_num = len(args.action)
        for idx, param_str in enumerate(args.action):
            # 初始化目标文件路径
            if os.path.isdir(output):
                if ac_num == 1:
                    target_name = relative_path
                else:
                    target_name = f"{prefix}-{idx}.{ext}"
                out_path = os.path.join(output, target_name)
            else:
                out_path = output

            tag = f"{f_tag}\t action={idx+1}\t 保存于 {out_path}"
            print(f"{tag}\t ...", flush=True, end="\r")

            # 判断目标文件是否存在
            if os.path.exists(out_path):
                if not args.overwrite:
                    print(f"\033[31m{tag} 目标文件已存在\033[0m", file=sys.stderr, flush=True)
                    print("处理中断，可以添加参数 \033[33m--overwrite\033[0m 覆盖现有文件", file=sys.stderr, flush=True)
                    return 1

                tag = f"{tag}\t \033[33moverwrite\033[0m"

            cur_out_dir = os.path.dirname(out_path)
            if not os.path.exists(cur_out_dir):
                os.makedirs(cur_out_dir)
            try:
                process_image_by_path(file_path, out_path, param_str)
                print(f"{tag}\t 成功", flush=True)
            except Exception as e:
                print(f"{tag}\t \033[31m失败：{e}\033[0m", file=sys.stderr, flush=True)
                print(traceback.format_exc(), file=sys.stderr, flush=True)

    return 0


# if __name__ == "__main__":
#     raise SystemExit(main())
