# docs.telethon.dev читаем

from .. import loader, utils                    # импортим хуйню
import logging
from telethon.tl.custom.message import Message  # ну а как же без хажлайтов)
import asyncio

logger = logging.getLogger(__name__)        # ну получаем логер иче

@loader.tds
class GavnischeMod(loader.Module):          # это название модуля в лоадере (Gavnische (свое имя желательно с большой буквы) (главное чтобы с другим не совпадало) + Mod (обязательно)) (нигде не отображается похуй)
	"""описание модуля хули"""              # это описание модуля в хелпе
	strings = {
		"name":   "Testtttt",               # это название модуля в хелпе (по нему анлоадаем)

		"author": "by m4xx1m",              # редачить/отправлять сообщения лучше через self.strings, так можно менять перевод через встроенную в фтг утилиту
		"why":	  "Зачем вы отправили <code>{message}</code>",
		"docOfMod": "opisanie",
		"paramdoc": "it's PARAM",
		"keyInfo": "<b>Key:</b> <code>{key}</code> <b>| Item:</b> <code>{item}</code>"
	}

	def __init__(self):                    
		self.config = loader.ModuleConfig(
				# первая переменная
				"AUTHOR",                        # название переменной в конфиге
				"m4xx1m",                        # данные
				self.strings['docOfMod'],		 # описание

				# вторая
				"PARAM",
				88005553535,
				self.strings['paramdoc']
			)


	async def client_ready(self, client, db):
		self.client = client                		# получаем клиент
		self.db = db                        		# получаем фтг базу данных


	async def testetcmd(self, message: Message):    # testcmd == testet + cmd | т.е. это будет реагировать на команды .testet (сила хакинтоша)
		"""ебать"""                         		# это описание команды в хелпе
		# client = message.client					# можно так, если лень писать client_ready

		await message.edit(self.strings['author'])  
		logger.debug('ахуеть')
		ms = await message.respond(self.strings["why"].format(message=message.text))
		await asyncio.sleep(2)

		for t in range(3):
			await ms.edit(str(3-t))
			await asyncio.sleep(1)

		await message.delete()
		
		for key, value in self.config.items():
			await ms.edit(self.strings['keyInfo'].format(key=key, item=value))
			await asyncio.sleep(2)
		
