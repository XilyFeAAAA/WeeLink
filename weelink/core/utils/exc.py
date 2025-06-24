# standard library
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
    
def print_exc(exc_type, exc_value, exc_traceback):
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