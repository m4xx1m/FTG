# -*- coding: utf-8 -*-

# by @m4xx1m
# thanks for idea and configs to @KeyZenD

# requires: lottie

# module in beta mode, btw я уезжаю на дачу

from .. import loader, utils
import io
import logging
from lottie.exporters import exporters
from lottie.importers import importers

configs = [
    [
        ["8", "4"], ["7", "4"]
    ],
    [
        ["8", "2"], ["6", "7"], ["3", "4"], ["[5]", "[0]"]
    ],
    [
        [f"[{str(cnt)}]", "[30]"] for cnt in range(30)               # ["[0]", "[30]"], ["[1]", "[30]"], ["[2]", "[30]"]
    ],
]


class Distorter:
    @staticmethod
    def tgs_to_json(input_file: bytes) -> str:
        infile = io.BytesIO(input_file)

        for p in importers:
            if 'tgs' in p.extensions:
                importer = p
                break

        outfile = io.StringIO()
        exporter = exporters.get_from_extension('json')
        an = importer.process(infile)
        exporter.process(an, outfile)
        return outfile.getvalue()

    @staticmethod
    def json_to_tgs(input_file: str) -> bytes:
        infile = io.BytesIO(input_file.encode())

        for p in importers:
            if 'json' in p.extensions:
                importer = p
                break

        outfile = io.BytesIO()
        exporter = exporters.get_from_extension('tgs')
        an = importer.process(infile)
        exporter.process(an, outfile)
        return outfile.getvalue()

    def distort(self, target: bytes, config: list) -> io.BytesIO:
        distorted = self.tgs_to_json(target)

        for cf in config:
            distorted = distorted.replace(cf[0], cf[1])

        outFile = io.BytesIO()
        outFile.name = "distorted.tgs"
        try:
            outFile.write(self.json_to_tgs(distorted))
        except: return None
        outFile.seek(0)
        return outFile

    def distorting(self, input_file: bytes, configs: list):
        return_files = []

        for conf in configs:
            try:
                distorted = self.distort(
                    target=input_file,
                    config=conf
                )
            except Exception as err:
                logging.error(f'Error in Distorter:\n{err}')
                return 

            if distorted:
                return_files.append(distorted)

        return return_files


@loader.tds
class TgsdMod(loader.Module):
    """TGS Distorter"""
    strings = {
        "name": "TGSd",
        "only_animated": "<b>Only animated stickers</b>",
        "noreply": "<b>No reply message</b>",
        "distorting": "<b>Distorting..</b>",
        "uploading": "<b>Uploading</b>"

    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def tgsdcmd(self, message):
        client = self.client
        reply = await message.get_reply_message()

        if not reply:
            await message.edit(self.strings['noreply'])
            return

        if reply and not reply.document or reply.document.mime_type != "application/x-tgsticker":
            await message.edit(self.strings['only_animated'])
            return

        await message.edit(self.strings['distorting'])
        ds = Distorter()
        distorted_stickers = ds.distorting(
            input_file=await client.download_file(reply),
            configs=configs
        )

        await message.edit(self.strings['uploading'])
        for file in distorted_stickers:
            try:
                msg = await reply.reply(file=file)
            except Exception as err:
                logging.error(f'Error uploading distorted sticker:\n{err}')
                # await message.edit('Uploading failed.')
                continue
            if msg.media.document.mime_type == 'application/x-bad-tgsticker':
                await msg.delete()

        await message.delete()
