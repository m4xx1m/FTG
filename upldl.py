# by @m4xx1m

# requires: humanize python-magic nest-asyncio

# welcome to sheetcode

import asyncio
import io
import logging
import os
import humanize
import magic
import nest_asyncio

from .. import loader, utils

nest_asyncio.apply()


@loader.tds
class UplDlbym4xx1mMod(loader.Module):
    """Uploading and downloading files on host"""
    strings = {
        "name": "upldl",
        "longFile": "<b>Content too long</b>",
        "noreply": "<b>No reply message</b>",
        "tnf_totxt": "<b>No text found</b>",
        "msgCap_totxt": '<code>{filename}</code>',
        "filename_totxt": '{id}.txt',
        "downloading": '<b>Downloading</b>',
        "file_not_found": '<b>No file found</b>',
        "downloaded": "<code>{path}</code>",
        "progress": "<b>Downloading {filename} ({fileSize})</b>\n<b>{total_downloaded}/{fileSize} ({percent_loaded})</b>",
        "filesize": "<code>{filename} ({filesize})</code>",
        "filesize_without_filename": "<code>{filesize}</code>",
        "cant_decode": "<code>{enc}</code>: <b>codec can\'t decode file</b>",
        "cant_find_enc": "<code>{enc}</code>: <b>Can't find encoding</b>",
        "emply_logs": "<b>Logs are empty</b>",
        "ignoreLongFileDoc": "Ignore exceeding the limit and show the last 4096 characters",
        "sizeThreshouldDoc": "Show progress stat if file more ... bytes (default 8MB)",
        "editTimeoutDoc": "Timeout for edit message in download progress (default 1.5 sec)"
    }

    progress_info = {"isrunned": False}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "ignoreLongFile",  # for .catlog and .cat
            True,
            self.strings['ignoreLongFileDoc'],

            "sizeThreshould",
            8388608,
            self.strings['sizeThreshouldDoc'],

            "editTimeout",
            1.5,
            self.strings['editTimeoutDoc'],

            "enable_.dl",
            False,
            "coming soon"
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def getenccmd(self, message):
        """.getenc + reply message
        showing encoding of replied file, but downloads the file completly"""
        client = self.client
        reply = await message.get_reply_message()
        if not reply:
            await message.edit(self.strings['noreply'])
            return
        if not reply.file:
            await message.edit(self.strings['file_not_found'])
            return

        file_content = await client.download_file(reply)
        enc = magic.Magic(mime_encoding=True).from_buffer(file_content)
        await message.edit(f'<code>{enc}</code>')

    async def catcmd(self, message):
        """.cat <encoding:optional> + reply message
        downloads a replied file and showing its content"""
        client = self.client
        reply = await message.get_reply_message()
        enc = utils.get_args(message)
        if enc:
            enc = enc[0]
        else:
            enc = None
        if not reply:
            await message.edit(self.strings['noreply'])
            return
        if not reply.file:
            await message.edit(self.strings['file_not_found'])
            return
        file_content = await client.download_file(reply)

        if not enc:
            enc = magic.Magic(mime_encoding=True).from_buffer(file_content)

        # if enc not in encodings.aliases.aliases:                                 # автор пидорас там нет us-ascii
        #     await message.edit(self.strings['cant_find_enc'].format(enc=enc))
        #     return

        try:
            file_content = file_content.decode(enc)
        except UnicodeDecodeError:
            await message.edit(self.strings['cant_decode'].format(enc=enc))
            return
        except LookupError:
            await message.edit(self.strings['cant_decode'].format(enc=enc))
            return
        if len(file_content) > 4096:
            if self.ignoreLongFile:
                file_content = file_content[len(file_content) - 4096::]
            else:
                await message.edit(self.strings['longFile'])
                return

        await message.edit(f"<code>{file_content}</code>")

    async def catlogcmd(self, message):
        """.catlog <level:default 40>
        same as .logs, but shows logs in message"""
        level = utils.get_args(message)
        if level:
            level = level[0]
            if not level.isdigit():
                level = None
        if not level:
            level = 40

        [handler] = logging.getLogger().handlers
        file_content = "\n".join(handler.dumps(int(level)))

        if not len(file_content) > 0:
            await message.edit(self.strings['emply_logs'])
            return
        if len(file_content) > 4096:
            if self.ignoreLongFile:
                file_content = file_content[len(file_content) - 4096::]
            else:
                await message.edit(self.strings['longFile'])
                return

        await message.edit(f"<code>{file_content}</code>")

    async def totxtcmd(self, message):
        """.totxt <filename:optional> + reply message
        write text from replied message to file"""
        client = self.client
        reply = await message.get_reply_message()
        filename = utils.get_args(message)[0]
        chat = message.chat
        outFile = io.BytesIO()

        if not reply:
            await message.edit(self.strings['noreply'])
            return
        if not filename:
            filename = f"{reply.id}.txt"

        outFile.name = filename
        outFile.write(reply.message.encode())
        outFile.seek(0)

        async with client.action(chat, 'document') as action:
            await client.send_file(
                entity=chat,
                file=outFile,
                caption=self.strings["msgCap_totxt"].format(filename=outFile.name),
                progress_callback=action.progress
            )

        await message.delete()

    async def sizecmd(self, message):
        """.size + file (in message or reply)"""
        reply = await message.get_reply_message()

        if message.file:
            msgWithFile = message
        elif reply.file:
            msgWithFile = reply
        else:
            await message.edit(self.strings["file_not_found"])
            return
        if msgWithFile.file.name:
            text = self.strings['filesize'].format(
                filesize=humanize.naturalsize(msgWithFile.file.size, binary=True),
                filename=msgWithFile.file.name
            )
        else:
            text = self.strings["filesize_without_filename"].format(
                filesize=humanize.naturalsize(msgWithFile.file.size, binary=True)
            )

        await message.edit(text)

    def progress(self, **kwargs):
        for key, arg in kwargs.items():
            self.progress_info[key] = arg

    # welcome to sheetcode
    async def print_progress_runner(self):
        while True:
            if self.progress_info['isrunned']:
                try:
                    await self.progress_info['message'].edit(
                        self.strings["progress"].format(
                            filename=self.progress_info['filename'],
                            fileSize=humanize.naturalsize(self.progress_info['total'], binary=True),
                            total_downloaded=humanize.naturalsize(self.progress_info['current'], binary=True),
                            percent_loaded=f"{round(self.progress_info['current'] / self.progress_info['total'] * 100, 1)}%"
                        )
                    )
                except:
                    return
            await asyncio.sleep(self.editTimeout)

    # welcome to sheetcode
    async def dlcmd(self, message):  # coming soon
        """.dl <path:default=$HOME> + reply file or file in message | DISABLED"""
        if not self.config['enable_.dl']:
            return
        client = self.client
        reply = await message.get_reply_message()
        args = utils.get_args(message)

        if message.media:
            messageWithFile = message
        elif reply and reply.media:
            messageWithFile = reply
        else:
            await message.edit(self.strings["file_not_found"])
            return

        if len(args) < 1:
            path = os.getenv('HOME') + '/' + messageWithFile.file.name
        else:
            path = args[0]
            path.replace('~', os.getenv('HOME'))
        if os.path.isdir(path):
            if not path.endswith('/'):
                path += '/'
            path += messageWithFile.file.name

        await message.edit(self.strings["downloading"])
        if messageWithFile.file.size >= self.sizeThreshould:
            print_progress_runner_task = self.client.loop.create_task(self.print_progress_runner())
            await messageWithFile.download_media(
                file=path,
                progress_callback=lambda c, t:
                self.progress(
                    isrunned=True,
                    current=c,
                    total=t,
                    message=message,
                    filename=messageWithFile.file.name
                )
            )
            print_progress_runner_task.cancel()

            # бюджетный debugger
            try:
                if print_progress_runner_task.exception():
                    await message.respond(f"<code>{print_progress_runner_task.exception()}</code>")
            except:
                pass
        else:
            await messageWithFile.download_media(path)
        await message.edit(self.strings["downloaded"].format(path=path))
