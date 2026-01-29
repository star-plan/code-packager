# Code Packager 使用指南

## 概述

Code Packager 是一个灵活的代码打包工具，支持多种配置方案和高级功能，帮助您轻松创建干净、轻量的代码压缩包。

## 新功能特性

### ✨ 多种预设方案
- **basic**: 基础方案 - 排除常见的构建文件和缓存
- **git-friendly**: Git友好方案 - 保留.git目录但排除大文件
- **complete**: 完整方案 - 排除所有不必要文件，包括.git
- **lightweight**: 轻量级方案 - 只保留核心源代码
- **custom**: 自定义方案 - 使用exclude_patterns.conf文件

### 🚀 高级功能
- **去除代码注释**: 支持 Python, JavaScript, Java, C/C++ 等语言
- **多种压缩方法**: deflate, lzma, bzip2
- **详细统计信息**: 文件数量、大小、压缩率等
- **命令行参数**: 灵活的配置选项

## 使用方法

### 无需安装直接运行 (推荐)

如果您安装了 `uv`，可以直接运行：

```bash
uvx pack-my-code
```

### 基本用法

如果您已安装该工具（通过 `pip` 或 `uv tool`）：

```bash
# 使用基础方案打包
pack-my-code /path/to/source output.zip

# 指定预设方案
pack-my-code /path/to/source output.zip --preset git-friendly

# 去除代码注释
pack-my-code /path/to/source output.zip --preset basic --remove-comments

# 使用LZMA压缩
pack-my-code /path/to/source output.zip --compression lzma
```

### 查看可用选项

```bash
# 列出所有预设方案
pack-my-code --list-presets

# 查看帮助信息
pack-my-code --help
```

### 高级用法

```bash
# 使用自定义配置文件
pack-my-code /path/to/source output.zip --config my_config.conf

# 详细输出模式
pack-my-code /path/to/source output.zip --verbose

# 组合多个选项
pack-my-code /path/to/source output.zip \
  --preset complete \
  --remove-comments \
  --compression lzma \
  --verbose
```

## 命令行参数详解

| 参数 | 简写 | 说明 |
|------|------|------|
| `--preset` | `-p` | 选择预设方案 (basic, git-friendly, complete, lightweight, custom) |
| `--config` | `-c` | 使用自定义配置文件 |
| `--remove-comments` | `-r` | 去除代码注释 |
| `--compression` | | 压缩方法 (deflate, lzma, bzip2) |
| `--list-presets` | `-l` | 列出所有可用的预设方案 |
| `--verbose` | `-v` | 显示详细输出 |
| `--help` | `-h` | 显示帮助信息 |

## 预设方案详解

### Basic (基础方案)
适用于大多数项目的日常打包需求，排除：
- 依赖目录 (node_modules, venv, __pycache__ 等)
- IDE文件 (.vscode, .idea 等)
- 临时文件 (*.log, *.tmp, *.bak 等)
- 编译产物 (*.pyc, *.o 等)

### Git-friendly (Git友好方案)
保留版本控制信息，适用于需要Git历史的场景：
- 包含基础方案的所有排除项
- 保留 .git 目录结构
- 排除 .git/objects 和 .git/logs (减少大小)

### Complete (完整方案)
最彻底的清理，适用于最终发布：
- 排除所有版本控制目录
- 排除所有依赖和构建产物
- 排除所有临时和缓存文件
- 排除压缩文件

### Lightweight (轻量级方案)
只保留核心源代码，适用于代码审查：
- 最严格的过滤规则
- 排除媒体文件
- 排除配置和密钥文件
- 只保留源代码文件

## 自定义配置

您可以创建自己的配置文件，使用 .gitignore 语法：

```bash
# my_config.conf
node_modules/
*.log
*.tmp
build/
dist/
```

然后使用：
```bash
pack-my-code /path/to/source output.zip --config my_config.conf
```

## 统计信息

打包完成后，工具会显示详细的统计信息：
- 总文件数量和包含/排除的文件数
- 原始大小和压缩后大小
- 压缩率
- 处理时间
- 去除注释的文件数量（如果启用）

## 注意事项

1. **去除注释功能**：目前支持 Python, JavaScript, TypeScript, Java, C/C++ 等语言，但可能不完美处理复杂的字符串和注释嵌套情况。

2. **压缩方法选择**：
   - `deflate`: 速度快，兼容性好（默认）
   - `lzma`: 压缩率高，但速度较慢
   - `bzip2`: 平衡压缩率和速度

3. **配置文件路径**：自定义配置文件支持绝对路径和相对路径。

4. **大文件处理**：对于非常大的项目，建议使用 `--verbose` 选项监控进度。