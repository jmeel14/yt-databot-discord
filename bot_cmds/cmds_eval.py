from . import cmd_main
import re
from asyncio import sleep
import discord

async def await_coro(coro):
    try:
        awaited = await coro
        try:
            awaited_twice = await awaited
            try:
                awaited_thrice = await awaited_twice
                return awaited_thrice
            except:
                return awaited_twice
        except:
            return awaited
    except:
        return coro

async def cmd_func(cmd_trigger, cmd_str, msg_obj, **kwargs):
    try:
        eval_client = kwargs["self_client"]
        eval_http = kwargs["self_http"]
        eval_disc = discord
        eval_re = re.compile("^" + cmd_str.split()[0] + "\s(.*)", flags=re.DOTALL)
        eval_str = eval_re.search(cmd_str).groups()[0]
        
        eval_run = await await_coro(eval(eval_str))

        output_embed = cmd_main.Embed(
            title = "Evaluation output",
            description = "The code you requested to evaluate outputs the following:",
            colour = 0x00BB55
        )

        output_embed.add_field(
            name = "Input",
            value = "```py\n" + str(cmd_str) + "\n```",
            inline = False
        )

        output_embed.add_field(
            name = "Output",
            value = "```{0}```".format(eval_run)
        )
    except BaseException as EvalError:
        output_embed = cmd_main.Embed(
            title = "Evaluation output",
            description = "An error occurred evaluating your code:",
            colour = 0xDD0000
        )
        output_embed.add_field(
            name = "Error",
            value ="```{0}```".format(str(EvalError))
        )
    out_msg = await msg_obj.channel.send(
        content = None,
        embed = output_embed
    )
    return {
        "output_admin": True,
        "output_msg": out_msg,
        "trigger_msg": msg_obj
    }

async def cmd_func2(cmd_trigger, cmd_str, msg_obj, **kwargs):
    try:
        exec_client = kwargs["self_client"]
        exec_http = kwargs["self_http"]
        exec_re = re.compile("^" + cmd_str.split()[0] + "\s(.*)", re.DOTALL)
        exec_str = exec_re.search(cmd_str).groups()[0]
        exec_run = await await_coro(exec(exec_str))

        output_embed = cmd_main.Embed(
            title = "Evaluation output",
            description = "The code you requested to evaluate outputs the following:",
            colour = 0x00BB55
        )

        output_embed.add_field(
            name = "Input",
            value = "```py\n" + str(cmd_str) + "\n```",
            inline = False
        )

        output_embed.add_field(
            name = "output",
            value = "```py\n" + str(exec_run) + "\n```"
        )
    except BaseException as EvalError:
        try:
            print(exec_str)
        except:
            pass
        output_embed = cmd_main.Embed(
            title = "Evaluation output",
            description = "An error occurred evaluating your code:",
            colour = 0xDD0000
        )
        output_embed.add_field(
            name = "Error",
            value = EvalError.args
        )
    out_msg = await msg_obj.channel.send(
        content = None,
        embed = output_embed
    )

    return {
        "output_admin": True,
        "output_msg": out_msg,
        "trigger_mg": msg_obj
    }

cmd_eval = cmd_main.Command(
    "Eval",
    "eval evaluate evaluation evaluator",
    "This command outputs developer-level functions, and is admin-only.",
    cmd_func,
    True
)
cmd_exec = cmd_main.Command(
    "Exec",
    "exec execute executor execution",
    "This command outputs developer-level functions, and is admin-only.",
    cmd_func2,
    True
)
