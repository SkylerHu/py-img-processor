# 贡献者指南

感谢你对 py-img-processor 的关注！本指南将帮助你快速上手开发流程。

## 前置要求

- Python >= 3.9
- [pre-commit](https://pre-commit.com/)
- （可选）[tox](https://tox.wiki/) 用于多版本测试

## 搭建开发环境

1. **克隆仓库并创建虚拟环境：**

```bash
git clone https://github.com/skylerhu/py-img-processor.git
cd py-img-processor
python3.9 -m venv .env
source .env/bin/activate
```

2. **安装依赖：**

```bash
pip install -r requirements_dev.txt
pip install -e ./          # 以可编辑模式安装，方便边开发边测试
```

3. **安装 pre-commit 钩子：**

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## 项目结构

| 路径 | 说明 |
| --- | --- |
| `imgprocessor/` | 核心库源代码 |
| `tests/` | 测试用例目录 |
| `tests/conftest.py` | Pytest 全局 fixtures 配置 |
| `tests/settings/` | 兼容 Django 的测试配置 |
| `docs/` | 文档（MkDocs） |
| `Makefile` | 构建、测试、发版命令（执行 `make help` 查看） |
| `pytest.ini` | Pytest 配置 |
| `.coveragerc` | 覆盖率配置（在 pytest.ini 中引用） |
| `.pre-commit-config.yaml` | Pre-commit 钩子配置 |
| `tox.ini` | 多 Python 版本测试矩阵 |
| `MANIFEST.in` | 打包清单配置 |

## 运行测试

```bash
# 运行完整测试套件
pytest tests

# 运行所有 Python 版本的测试
tox run
```

通过 `use_special_tmp` 参数可将处理后的图像保存至 `.tmp/output/`，便于与 `tests/imgs/expected` 中的预期结果进行肉眼对比：

```bash
pytest tests --use_special_tmp
```

## 提交信息规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<类型>: <描述>
```

常用类型：`feat`（新功能）、`fix`（修复）、`docs`（文档）、`chore`（杂项）、`refactor`（重构）、`perf`（性能）、`test`（测试）、`build`（构建）。

## 提交 Pull Request

提交 PR 之前，请确认以下事项：

- [ ] 新代码包含测试用例
- [ ] 所有测试通过 — `make test-all`
- [ ] 覆盖率达标 — `make coverage`
- [ ] 本地打包成功 — `make dist`

## 构建文档

```bash
mkdocs build --clean    # 生成静态站点
mkdocs serve            # 启动本地预览服务
```

文档通过 [Read the Docs](https://readthedocs.org/) 发布，需在 ReadTheDocs 控制台手动触发构建。

## 打包发版

以下命令均定义在 `Makefile` 中：

```bash
make clean-build                                    # 清除构建缓存
python setup.py sdist bdist_wheel                   # 构建源码包和 wheel
twine check dist/py*(.whl|.tar.gz)                  # 检查包元数据
twine upload -r pypi dist/py*(.whl|.tar.gz)         # 上传至 PyPI
```

> 上传 PyPI 需要在 `~/.pypirc` 中配置用户名和密码。

## 其他

- 可考虑使用 [pillow-simd](https://github.com/uploadcare/pillow-simd) 提升性能——参见[性能测试](https://python-pillow.org/pillow-perf/)。
