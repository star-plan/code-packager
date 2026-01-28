from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Button, Label, Select, Checkbox, Log
from loguru import logger
import sys

from . import __version__

# Try to import actions, handle if not available (e.g. during install check)
try:
    from .actions import run_packaging_task
except ImportError:
    run_packaging_task = None

class CodePackagerApp(App):
    """Code Packager TUI Application"""
    
    TITLE = f"PackMyCode v{__version__}"
    
    CSS = """
    Container {
        padding: 1;
    }
    Label {
        margin-top: 1;
        margin-bottom: 0;
        color: auto 50%;
    }
    Input, Select {
        margin-bottom: 1;
    }
    Button {
        margin-top: 2;
        width: 100%;
    }
    Log {
        height: 1fr;
        border: solid $accent;
        margin-top: 1;
        background: $surface;
    }
    """
    
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("源代码目录 Source Directory"),
            Input(value=".", id="source_dir", placeholder="输入源代码目录 path to source code"),
            
            Label("输出文件 Output Filename"),
            Input(value="code_package.zip", id="output_zip", placeholder="输出的zip文件名"),
            
            Label("预设配置 Preset"),
            Select.from_values(["basic", "complete", "git-friendly", "lightweight"], value="basic", id="preset"),
            
            Label("选项 Options"),
            Checkbox("移除注释 Remove Comments", value=False, id="remove_comments"),
            
            Button("开始打包 Start Packaging", variant="primary", id="pack_btn"),
            
            Label("日志 Log"),
            Log(id="log", highlight=True)
        )
        yield Footer()

    def on_mount(self):
        # Redirect loguru to Textual Log widget
        log_widget = self.query_one(Log)
        logger.remove()
        
        def sink(message):
            # message is a record object if raw=False (default), but sink receives string if format is applied?
            # Actually loguru sink receives a message object which has .record
            # But simpler is just to write str(message)
            log_widget.write(str(message))
            
        logger.add(sink, format="{time:HH:mm:ss} | {level} | {message}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pack_btn":
            self.run_packaging()

    def run_packaging(self):
        if run_packaging_task is None:
            self.query_one(Log).write("Error: Could not import packaging logic.")
            return

        source = self.query_one("#source_dir", Input).value
        output = self.query_one("#output_zip", Input).value
        preset = self.query_one("#preset", Select).value
        remove_comments = self.query_one("#remove_comments", Checkbox).value
        
        self.query_one(Log).write(f"正在打包 {source} 到 {output} (预设: {preset})...")
        
        # Run synchronous task
        # Note: In a real TUI app, long running tasks should be in a worker.
        # But packaging is usually fast enough or acceptable to block for this simple tool.
        try:
            success = run_packaging_task(
                source_dir=source,
                output_zip=output,
                preset=preset if preset else "basic",
                remove_comments=remove_comments
            )
            
            if success:
                self.query_one(Log).write("✅ 打包成功! Packaging Successful!")
            else:
                self.query_one(Log).write("❌ 打包失败! Packaging Failed!")
        except Exception as e:
             self.query_one(Log).write(f"❌ 发生异常: {e}")

if __name__ == "__main__":
    app = CodePackagerApp()
    app.run()
