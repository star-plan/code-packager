# 📦 CodePackager — 终极代码打包工具 🚀

**轻松打包您的代码库，像专业人士一样排除不必要的文件！** 告别臃肿的压缩包，迎接干净、轻量的代码包。🎉

## ✨ 功能特性

- **🎯 多种预设方案**：从 4 种内置预设中选择，满足不同的打包需求
  - `basic`：排除常见的构建文件和缓存
  - `git-friendly`：保留 .git 目录但排除大文件
  - `complete`：排除所有不必要文件，包括 .git
  - `lightweight`：仅保留核心源代码

- **🧹 智能注释移除**：移除 Python、JavaScript、Java、C/C++ 文件中的注释
- **🗜️ 多种压缩方法**：支持 deflate、lzma 和 bzip2 压缩
- **📊 详细统计信息**：获取全面的打包统计数据
- **🌍 跨平台支持**：在 Windows、macOS 和 Linux 上无缝运行
- **⚡ 快速高效**：针对大型代码库优化，执行速度极快

## 🤔 为什么使用 CodePackager？

处理大型代码库时，手动打包可能是一场噩梦。CodePackager 通过以下方式简化流程：

- 自动跳过不需要的文件（如 `node_modules`、`*.log`、`__pycache__`）
- 为不同场景提供灵活的预设配置
- 提供注释移除和多种压缩方法等高级功能
- 保持压缩包干净且可部署
- 节省时间并减少人为错误

## 🚀 快速开始

### 安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/Deali-Axy/code-packager.git
   cd code-packager
   ```

2. **安装依赖**
   ```bash
   pdm install
   ```

### 基本用法

```bash
# 使用默认预设进行基本打包
python -m src.code_packager /path/to/source output.zip

# 使用特定预设
python -m src.code_packager /path/to/source output.zip --preset git-friendly

# 移除注释并使用 LZMA 压缩
python -m src.code_packager /path/to/source output.zip --preset complete --remove-comments --compression lzma

# 列出所有可用预设
python -m src.code_packager --list-presets
```

## 📋 命令行选项

```bash
用法: python -m src.code_packager [选项] 源目录 输出压缩包

参数:
  源目录        要打包的源代码目录
  输出压缩包    输出的 zip 文件路径

选项:
  -p, --preset 预设        选择预设: basic, git-friendly, complete, lightweight (默认: basic)
  -c, --config 配置        使用自定义配置文件
  -r, --remove-comments    从源代码文件中移除注释
  --compression 方法       压缩方法: deflate, lzma, bzip2 (默认: deflate)
  -l, --list-presets       列出所有可用预设
  -v, --verbose            显示详细输出
  -h, --help               显示帮助信息
```

## 📂 预设配置

| 预设 | 描述 | 使用场景 |
|------|------|----------|
| `basic` | 排除常见构建文件、缓存和 IDE 文件 | 一般开发项目 |
| `git-friendly` | 保留 .git 目录但排除大对象 | 共享带版本历史的项目 |
| `complete` | 排除所有不必要文件，包括 .git | 最终发布或分发 |
| `lightweight` | 仅保留核心源代码 | 最小化代码共享 |

## 📂 目录结构示例

打包前：
```
project/
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── node_modules/          # 被排除
├── __pycache__/          # 被排除
├── build/                # 被排除
├── .git/                 # 取决于预设
├── .vscode/              # 被排除
└── .gitignore
```

打包后（basic 预设）：
```
code_package.zip
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── .git/
└── .gitignore
```

## 🔧 高级功能

### 注释移除
支持移除以下语言的注释：
- Python (`.py`)
- JavaScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)

### 自定义配置
通过使用 `--config` 选项和自定义配置文件来创建您自己的排除规则。

### 压缩方法
- **deflate**：快速压缩，良好兼容性（默认）
- **lzma**：最佳压缩率，较慢
- **bzip2**：速度和压缩率的良好平衡

## 🤝 贡献

欢迎贡献！请随时：

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 如适用，添加测试
5. 提交 pull request

如需报告错误和功能请求，请[提交 issue](https://github.com/Deali-Axy/code-packager/issues)。

## 📄 许可证

本项目采用 MIT 许可证。详情请参见 [LICENSE](LICENSE)。

---

**由 [DealiAxy](https://github.com/Deali-Axy) 用 ❤️ 制作**