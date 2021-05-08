from .. import loader                       # <<-- импортим хуйню

@loader.tds
class GavnischeMod(loader.Module):          # <<-- Это название модуля в лоадере (Gavnische (свое имя желательно с большой буквы) (главное чтобы с другим не совпадало) + Mod (обязательно)) (нигде не отображается похуй)
	"""описание модуля хули"""              # <<-- это описание модуля в хелпе
	strings = {"name": "Testtttt"}          # <<-- это название модуля в хелпе (по нему анлоадаем)

	async def client_ready(self, client, db):
		self.client = client
		self.db = db

	async def testetcmd(self, message):     # <<-- testcmd == testet + cmd | т.е. это будет реагировать на команды .testet (сила хакинтоша)
		"""нахуя описание ты че деьбил"""   # <<-- это описание команды в хелпе
		await message.edit('by m4xx1m')     # <<-- это код
		
