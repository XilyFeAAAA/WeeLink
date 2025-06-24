# standard library
from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query

# local library
from weelink.core.plugin import PluginMetaData
from weelink.core.linkhub import Linkhub
from weelink.core.internal.config import conf
from weelink.dashboard.depends import login_required, get_linkhub

router = APIRouter()


@router.get("/list", dependencies=[Depends(login_required)])
async def plugin_list_api(linkhub: Annotated[Linkhub, Depends(get_linkhub)]):
    return {
        "plugins": [{
            "name": plugin.name,
            "author": plugin.author,
            "version": plugin.version,
            "desc": plugin.desc,
            "repo": plugin.repo,
            "enable": plugin.name not in conf.inactive_plugins
        } for plugin in linkhub.plugin.get_all_plugins()]
    }


@router.post("/switch", dependencies=[Depends(login_required)])
async def plugin_switch_api(
    plugin_name: Annotated[str, Body()],
    enable: Annotated[bool, Body()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    md: PluginMetaData = linkhub.plugin.get_one_plugin(plugin_name)
    module_str = str(md.module)
    
    if enable:
        if plugin_name in conf.inactive_plugins:
            conf.inactive_plugins.remove(plugin_name)
            conf.save()
        await linkhub.plugin.load_plugin(module_str)
        await linkhub.plugin.enable_plugin(plugin_name)
    else:
        if plugin_name not in conf.inactive_plugins:
            conf.inactive_plugins.append(plugin_name)
            conf.save()
        await linkhub.plugin.disable_plugin(plugin_name)


@router.post("/reload", dependencies=[Depends(login_required)])
async def plugin_reload_api(
    plugin_name: Annotated[str, Query()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    await linkhub.plugin.reload_plugin(plugin_name)


@router.post("/uninstall", dependencies=[Depends(login_required)])
async def plugin_uninstall_api(
    plugin_name: Annotated[str, Query()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    await linkhub.plugin.uninstall_plugin(plugin_name)


@router.get("/config", dependencies=[Depends(login_required)])
async def plugin_get_config_api(
    plugin_name: Annotated[str, Query()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    md: PluginMetaData = linkhub.plugin.get_one_plugin(plugin_name)
    scheme, conf = md.config.output()
    return {
        "scheme": scheme,
        "conf": conf
    }


@router.post("/config", dependencies=[Depends(login_required)])
async def plugin_post_config_api(
    plugin_name: Annotated[str, Body()],
    conf: Annotated[dict, Body()],
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    md: PluginMetaData = linkhub.plugin.get_one_plugin(plugin_name)
    return md.config.update(conf)

@router.post("/restart", dependencies=[Depends(login_required)])
async def plugin_restart_api(
    linkhub: Annotated[Linkhub, Depends(get_linkhub)]
):
    await linkhub.plugin.restart()
