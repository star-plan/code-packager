# 📦 CodePackager — The Ultimate Code Packaging Tool 🚀

**Easily zip your codebase while excluding unnecessary files like a pro!** Say goodbye to bloated archives and hello to clean, lightweight packages. 🎉

## 🛠 Features

- **Dynamic Exclusions**: Reads `.gitignore` files to automatically exclude unwanted files and directories. 🧹
- **Global Rules**: Supports custom exclusion patterns via `exclude_patterns.txt`. 🌍
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux. 🖥️
- **Simple & Fast**: Intuitive design with blazing-fast execution. ⚡

## 🤔 Why Use CodePackager?

When working with large codebases, manual packaging can be a nightmare. CodePackager simplifies the process by:

- Automatically skipping files you don’t need (e.g., `node_modules`, `*.log`).
- Keeping your archives clean and deploy-ready.
- Saving time and reducing human errors.

## 🚀 Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/Deali-Axy/code-packager.git
   cd code-packager
   ```

2. **Install Dependencies**

   ```bash
   pdm install
   ```

3. **Run the tool**

   ```bash
   python src/code_packager/main.py
   ```

4. **Customize exclusions**

   - Add global rules to `exclude_patterns.txt`.
   - Use `.gitignore` files in your project for local exclusions.

## 📂 Example Directory Structure

Before packaging:

```css
project/
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
├── node_modules/
├── build/
└── .gitignore
```

After packaging:

```css
code_package.zip  
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── .gitignore
```

## ❤️ Contribute

Got an idea or found a bug? Feel free to [open an issue](https://github.com/Deali-Axy/code-packager/issues) or submit a pull request. Contributions are always welcome! 🤝

## 📜 License

This project is licensed under the MIT License. See LICENSE for details.
