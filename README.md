# 📦 CodePackager — The Ultimate Code Packaging Tool 🚀

**Easily zip your codebase while excluding unnecessary files like a pro!** Say goodbye to bloated archives and hello to clean, lightweight packages. 🎉

## ✨ Features

- **🎯 Multiple Presets**: Choose from 4 built-in presets for different packaging needs
  - `basic`: Exclude common build files and caches
  - `git-friendly`: Keep .git directory but exclude large files
  - `complete`: Exclude all unnecessary files including .git
  - `lightweight`: Keep only core source code

- **🧹 Smart Comment Removal**: Remove comments from Python, JavaScript, Java, C/C++ files
- **🗜️ Multiple Compression Methods**: Support for deflate, lzma, and bzip2 compression
- **📊 Detailed Statistics**: Get comprehensive packaging statistics
- **🌍 Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **⚡ Fast & Efficient**: Optimized for large codebases with blazing-fast execution

## 🤔 Why Use CodePackager?

When working with large codebases, manual packaging can be a nightmare. CodePackager simplifies the process by:

- Automatically skipping files you don't need (e.g., `node_modules`, `*.log`, `__pycache__`)
- Providing flexible preset configurations for different scenarios
- Offering advanced features like comment removal and multiple compression methods
- Keeping your archives clean and deploy-ready
- Saving time and reducing human errors

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Deali-Axy/code-packager.git
   cd code-packager
   ```

2. **Install dependencies**
   ```bash
   pdm install
   ```

### Basic Usage

```bash
# Basic packaging with default preset
python -m src.code_packager /path/to/source output.zip

# Use a specific preset
python -m src.code_packager /path/to/source output.zip --preset git-friendly

# Remove comments and use LZMA compression
python -m src.code_packager /path/to/source output.zip --preset complete --remove-comments --compression lzma

# List all available presets
python -m src.code_packager --list-presets
```

## 📋 Command Line Options

```bash
Usage: python -m src.code_packager [OPTIONS] SOURCE_DIR OUTPUT_ZIP

Arguments:
  SOURCE_DIR    Source code directory to package
  OUTPUT_ZIP    Output zip file path

Options:
  -p, --preset PRESET       Choose preset: basic, git-friendly, complete, lightweight (default: basic)
  -c, --config CONFIG       Use custom configuration file
  -r, --remove-comments     Remove comments from source code files
  --compression METHOD      Compression method: deflate, lzma, bzip2 (default: deflate)
  -l, --list-presets        List all available presets
  -v, --verbose             Show detailed output
  -h, --help                Show help message
```

## 📂 Preset Configurations

| Preset | Description | Use Case |
|--------|-------------|----------|
| `basic` | Excludes common build files, caches, and IDE files | General development projects |
| `git-friendly` | Keeps .git directory but excludes large objects | Sharing projects with version history |
| `complete` | Excludes everything unnecessary including .git | Final release or distribution |
| `lightweight` | Keeps only essential source code | Minimal code sharing |

## 📂 Example Directory Structure

Before packaging:
```
project/
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── node_modules/          # Excluded
├── __pycache__/          # Excluded
├── build/                # Excluded
├── .git/                 # Depends on preset
├── .vscode/              # Excluded
└── .gitignore
```

After packaging (basic preset):
```
code_package.zip
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── .git/
└── .gitignore
```

## 🔧 Advanced Features

### Comment Removal
Supports removing comments from:
- Python (`.py`)
- JavaScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)

### Custom Configuration
Create your own exclusion rules by using the `--config` option with a custom configuration file.

### Compression Methods
- **deflate**: Fast compression, good compatibility (default)
- **lzma**: Best compression ratio, slower
- **bzip2**: Good balance between speed and compression

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

For bug reports and feature requests, please [open an issue](https://github.com/Deali-Axy/code-packager/issues).

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Made with ❤️ by [DealiAxy](https://github.com/Deali-Axy)**
