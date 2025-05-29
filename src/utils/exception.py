from .log import logger
from src.error import HttpError
import asyncio
import inspect        
import sys
import datetime
import json
import pprint

def print_code_chain(exc_traceback, exc_type=None, exc_value=None):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\033[1;31m{'='*60}\033[0m")
    print(f"\033[1;31m[异常时间]\033[0m {now}")
    if exc_type and exc_value:
        print(f"\033[1;31m[异常类型]\033[0m {exc_type.__name__}")
        print(f"\033[1;31m[异常信息]\033[0m {exc_value}")
    print(f"\033[1;31m[执行代码链]\033[0m")
    tb = exc_traceback
    step = 1
    while tb:
        frame = tb.tb_frame
        lineno = tb.tb_lineno
        filename = frame.f_code.co_filename
        func_name = frame.f_code.co_name
        print(f"\033[1;35m第{step}步\033[0m  \033[1;33m函数名：{func_name}\033[0m  \033[1;34m路径：{filename}:{lineno}\033[0m")
        try:
            lines, start_line = inspect.getsourcelines(frame.f_code)
            code_line = lines[lineno - start_line].strip()
            print(f"  \033[0;36m报错代码: {code_line}\033[0m")
            
            print("  \033[0;32m当前作用域变量:\033[0m")
            locals_dict = frame.f_locals
            filtered_locals = {k: v for k, v in locals_dict.items() 
                             if not k.startswith('__') and not callable(v)}
            if filtered_locals:
                for var_name, var_value in filtered_locals.items():
                    try:
                        if isinstance(var_value, dict):
                            try:
                                value_str = json.dumps(var_value, ensure_ascii=False, indent=2)
                                if len(value_str) > 100:
                                    value_str = value_str[:97] + "..."
                            except Exception:
                                value_str = "[无法用json序列化]"
                        else:
                            value_str = pprint.pformat(var_value, compact=True, width=80)
                            if len(value_str) > 100:
                                value_str = value_str[:97] + "..."
                        print(f"    {var_name} = {value_str}")
                    except Exception:
                        print(f"    {var_name} = [无法序列化]")
            else:
                print("    无可用变量")
                
        except Exception:
            print("  \033[0;36m报错代码: [无法获取]\033[0m")
        tb = tb.tb_next
        step += 1
    print(f"\033[1;31m{'='*60}\033[0m")


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if exc_type is asyncio.CancelledError or exc_type is HttpError:
        return
    logger.error(f"global_exception_handler 处理到异常: {exc_type.__name__}")
    print_code_chain(exc_traceback, exc_type, exc_value)


def asyncio_exception_handler(loop, context):
    exc = context.get("exception")
    message = context.get("message")
    
    if exc:
        if isinstance(exc, asyncio.CancelledError):
            logger.debug("asyncio_exception_handler: asyncio.CancelledError 忽略.")
            return
        logger.error(f"asyncio_exception_handler 处理到来自循环 {loop} 的异常: {type(exc).__name__} - '{message}'")
        global_exception_handler(type(exc), exc, exc.__traceback__) # 直接调用
    else:
        if message and ("was cancelled" in message or "cancelling" in message):
            logger.debug(f"asyncio_exception_handler: 任务取消消息忽略: '{message}'")
            return
        logger.warning(f"asyncio_exception_handler: 捕获到异步异常上下文(无异常对象)来自循环 {loop}: {context}")


def set_default_exception_handlers():
    """设置系统默认的未捕获异常处理程序"""
    sys.excepthook = global_exception_handler
    try:
        loop = asyncio.get_event_loop_policy().get_event_loop()
        if not loop.is_closed():
            loop.set_exception_handler(asyncio_exception_handler)
            logger.debug(f"已为循环 {loop} 设置 asyncio 异常处理器。")
        else:
            logger.warning(f"获取到的主事件循环 {loop} 已关闭，无法设置 asyncio 异常处理器。")
    except RuntimeError: 
        logger.info("当前无事件循环，asyncio 异常处理器将主要由 asyncio.run() 或后续的循环实例管理。")
    except Exception as e:
        logger.error(f"设置默认 asyncio 异常处理器时发生未知错误: {e}")