# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

import re
from typing import Callable, Dict, Tuple, Iterable

from nonebot import NoneBot
from hoshino import util
from hoshino.service import Service, Privilege
from hoshino.res import R
from .argparse import ArgParser
from .exception import *

sv = Service('clanbattle', manage_priv=Privilege.SUPERUSER, enable_on_default=True)
SORRY = 'ごめんなさい！嘤嘤嘤(〒︿〒)'

_registry:Dict[str, Tuple[Callable, ArgParser]] = {}

@sv.on_rex(re.compile(r'^[!！](.+)', re.DOTALL), event='group')
async def _clanbattle_bus(bot:NoneBot, ctx, match):
    cmd, *args = match.group(1).split()
    cmd = util.normalize_str(cmd)
    if cmd in _registry:
        func, parser = _registry[cmd]
        try:
            args = parser.parse(args, ctx['message'])
            await func(bot, ctx, args)
        except DatabaseError as e:
            await bot.send(ctx, f"DatabaseError: {e.message}\n{SORRY}\n※请及时联系维护组")
        except ClanBattleError as e:
            await bot.send(ctx, e.message, at_sender=True)
        except Exception as e:
            sv.logger.exception(e)
            sv.logger.error(f'{type(e)} occured when {func.__name__} handling message {ctx["message_id"]}.')
            await bot.send(ctx, f'Error: 机器人出现未预料的错误\n{SORRY}\n※请及时联系维护组', at_sender=True)


def cb_cmd(name, parser:ArgParser) -> Callable:
    if isinstance(name, str):
        name = (name, )
    if not isinstance(name, Iterable):
        raise ValueError('`name` of cb_cmd must be `str` or `Iterable[str]`')
    names = map(lambda x: util.normalize_str(x), name)
    def deco(func) -> Callable:
        for n in names:
            if n in _registry:
                sv.logger.warning(f'出现重名命令：{func.__name__} 与 {_registry[n].__name__}命令名冲突')
            else:
                _registry[n] = (func, parser)
        return func
    return deco


from .cmdv1 import *
from .cmdv2 import *


@cb_cmd('帮助', ArgParser('!帮助'))
async def cb_help(bot:NoneBot, ctx, args:ParseResult):
    msg = f'''
==================
- PCR会战管理v2.0 -
==================
快速开始指南

【必读事项】
※会战系命令均以感叹号!开头，半全角均可
※命令与参数之间必须以[空格]隔开
下面以使用场景-使用例给出常用指令的说明

【群初次使用】
!建会 Nリトルリリカル Sjp
!建会 N小小甜心 Stw
!建会 N今天版号批了吗 Scn

【注册成员】
!入会 祐树
!入会 佐树 @123456789

【上报伤害】
!出刀 514w
!收尾
!出补时刀 114w

【预约Boss】
!预约 5

【查询余刀&催刀】
!查刀
!催刀

※详细说明见命令一览表
'''
    await bot.send(ctx, msg, at_sender=True)
    msg = [
        f"命令一览表：\n{R.img('priconne/quick/Hoshino会战.png').cqcode}",
        "※图片更新较慢 前往github.com/Ice-Cirno/HoshinoBot/tree/master/hoshino/modules/priconne/clanbattle查看最新",
        "※使用前请【逐字】阅读必读事项"
    ]
    await bot.send(ctx, '\n'.join(msg), at_sender=True)
