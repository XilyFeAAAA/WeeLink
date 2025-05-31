from src.utils import logger
import asyncio
import inspect
import sys
import datetime
import json
import pprint


# 定义 ANSI 颜色代码以便于管理和阅读
class Colors:
    RED = '\033[1;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;34m'
    MAGENTA = '\033[1;35m'
    CYAN = '\033[0;36m'
    WHITE_BOLD = '\033[1;37m'
    RESET = '\033[0m'
    HIGHLIGHT_CODE = '\033[1;93;100m'
    BRIGHT_RED = '\033[0;91m'

class Exc:
    
    def __init__(self) -> None:
        self._ori_sys_excepthook = None
        self._ori_async_excepthook = {}

    def sync_exc_hook(self, exc_type, exc_value, exc_traceback):
        """
        打印优化后的异常追踪信息，包括颜色高亮、上下文代码和仅在错误源头帧显示局部变量。
        对于 KeyboardInterrupt 不显示错误跟踪，而是直接退出。
        """
        # 特殊处理 KeyboardInterrupt，不显示堆栈跟踪
        if exc_type is KeyboardInterrupt:
            sys.exit()
            
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        separator = f"{Colors.RED}{'='*70}{Colors.RESET}"
        frame_separator = f"   {Colors.RED}{'-'*65}{Colors.RESET}"

        print(separator)
        print(f"{Colors.RED}[异常时间]{Colors.RESET} {Colors.WHITE_BOLD}{now}{Colors.RESET}") # 稍作修改，标明是异步任务
        if exc_type and exc_value:
            print(f"{Colors.RED}[异常类型]{Colors.RESET} {Colors.WHITE_BOLD}{exc_type.__name__}{Colors.RESET}")
            print(f"{Colors.RED}[异常信息]{Colors.RESET} {Colors.BRIGHT_RED}{exc_value}{Colors.RESET}")

        print(f"{Colors.RED}[执行代码链]{Colors.RESET}")

        tb = exc_traceback
        frame_index = 0
        frames = []

        while tb:
            frames.append((tb.tb_frame, tb.tb_lineno, frame_index))
            tb = tb.tb_next
            frame_index += 1
        
        last_frame_index = len(frames) - 1 if frames else -1
        
        display_frame_count = min(5, len(frames))
        for i, (frame, lineno, frame_index) in enumerate(frames[-display_frame_count:]):
            code = frame.f_code
            filename = code.co_filename
            func_name = code.co_name

            if i > 0:
                print(frame_separator)

            print(f"{Colors.MAGENTA}--> 第 {frame_index + 1} 帧{Colors.RESET} "
                f"{Colors.YELLOW}函数: {func_name}{Colors.RESET} "
                f"{Colors.BLUE}文件: {filename}:{lineno}{Colors.RESET}")

            try:
                lines, start_line = inspect.getsourcelines(code)
                actual_line_index_in_lines_list = lineno - start_line
                context_lines_count = 1
                display_start = max(0, actual_line_index_in_lines_list - context_lines_count)
                display_end = min(len(lines), actual_line_index_in_lines_list + context_lines_count + 1)

                for j in range(display_start, display_end):
                    line_num_prefix = f"  {j + start_line:4d} "
                    line_content = lines[j].rstrip('\n')
                    if j == actual_line_index_in_lines_list:
                        print(f"{Colors.CYAN}{line_num_prefix} >> {Colors.HIGHLIGHT_CODE}{line_content}{Colors.RESET}")
                    else:
                        print(f"{Colors.CYAN}{line_num_prefix}    {Colors.RESET}{line_content}")
            except Exception:
                print(f"    {Colors.CYAN}代码行: [无法获取源代码]{Colors.RESET}")

            if frame_index == last_frame_index:
                print(f"    {Colors.GREEN}当前作用域变量:{Colors.RESET}")
                locals_dict = frame.f_locals
                filtered_locals = {}
                for k, v in locals_dict.items():
                    if not k.startswith('__') and \
                    not inspect.ismodule(v) and \
                    not inspect.isfunction(v) and \
                    not inspect.isbuiltin(v) and \
                    not inspect.isclass(v):
                        filtered_locals[k] = v
                if filtered_locals:
                    for var_name, var_value in filtered_locals.items():
                        try:
                            value_str = ""
                            if isinstance(var_value, dict):
                                try:
                                    value_str = json.dumps(var_value, ensure_ascii=False, indent=2, default=str)
                                except Exception:
                                    value_str = f"[字典无法完全JSON序列化: {pprint.pformat(var_value, compact=True, width=60)}]"
                            elif isinstance(var_value, (list, tuple, set)):
                                value_str = pprint.pformat(var_value, compact=True, width=60)
                            else:
                                value_str = repr(var_value)
                            max_len = 150
                            if len(value_str) > max_len:
                                value_str = value_str[:max_len - 3] + "..."
                            print(f"      {Colors.YELLOW}{var_name}{Colors.RESET} = {Colors.WHITE_BOLD}{value_str}{Colors.RESET}")
                        except Exception as e_ser:
                            print(f"      {Colors.YELLOW}{var_name}{Colors.RESET} = {Colors.BRIGHT_RED}[变量序列化失败: {e_ser}]{Colors.RESET}")
                else:
                    print(f"      {Colors.WHITE_BOLD}无相关局部变量可显示。{Colors.RESET}")
                print()
        print(separator)
    
    
    async def async_exc_hook(self, loop, context):
        # 从 context 中提取异常信息
        exc_value = context.get('exception')
        exc_type = None
        exc_traceback = None

        if exc_value:
            exc_type = type(exc_value)
            exc_traceback = exc_value.__traceback__
        else:
            # 如果没有异常对象，可能只是一个错误消息
            print(f"{Colors.RED}捕获到 asyncio 错误 (无异常对象):{Colors.RESET}")
            print(f"  {Colors.YELLOW}消息:{Colors.RESET} {context.get('message')}")
            print(f"  {Colors.YELLOW}Future:{Colors.RESET} {context.get('future')}")
            print(f"{Colors.RED}{'='*70}{Colors.RESET}")
            return # 没有 traceback 可以打印

        # 调用我们增强的打印函数
        self.sync_exc_hook(exc_type, exc_value, exc_traceback)
    
    def install_exception_hook(self, loop: asyncio.AbstractEventLoop) -> None:
        """注册全局异常"""

        # 设置 sys.excepthook
        if sys.excepthook != self.sync_exc_hook:
            self._ori_sys_excepthook = sys.excepthook
            sys.excepthook = self.sync_exc_hook
            logger.info("全局错误处理器: sys.excepthook 已成功安装")
        
        
        # 设置 asyncio 异常处理
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                logger.error("全局错误处理器: 未找到正在运行的 asyncio 事件循环。若要为特定循环设置处理器，请明确传递 loop 参数。")
        
        if loop:
            loop_id = id(loop)
            if (async_hook := loop.get_exception_handler()) != self.async_exc_hook: # 避免重复保存
                self._ori_async_excepthook[loop_id] = async_hook
            
            loop.set_exception_handler(self.async_exc_hook)
            logger.info(f"全局错误处理器: asyncio 异常处理器已安装。")
        else:
            logger.error("全局错误处理器: 未提供或未找到活动的 asyncio 循环，asyncio 异常处理器未安装。")
            
    
    
    def uninstall_exception_hook(self, loop: asyncio.AbstractEventLoop) -> None:
        """卸载全局异常"""
        
        if sys.excepthook == self.sync_exc_hook:
            sys.excepthook = self._ori_sys_excepthook
            logger.info("全局错误处理器: sys.excepthook 已恢复。")
            self.sync_exc_hook = None
            
        
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                logger.error("全局错误处理器: 未找到正在运行的 asyncio 事件循环。若要为特定循环设置处理器，请明确传递 loop 参数。")
        
        if loop:
            loop_id = id(loop)
            if loop.get_exception_handler() == self.async_exc_hook:
                ori_async_exc_hook = self._ori_async_excepthook.pop(loop_id)
                loop.set_exception_handler(ori_async_exc_hook)
                logger.info(f"全局错误处理器: asyncio 异常处理器重置为默认。")