from dadata import DadataAsync
from datetime import datetime

class Organization:
    
    def __init__(self, api_key: str) -> None:
        self.api = DadataAsync(api_key)
        
    # Поиск организацию по ИНН
    async def search(self, inn: str):
        return await self.api.find_by_id("party", inn)
    
    # Создает строку с данными об орг для отправки юзеру
    async def createOrgInfo(self, inn: str,state):
        org = await self.search(inn)
        data=await state.get_data()
        data['delo_name']=org[0].get('value')
        await state.set_data(data)
        if(len(org) < 1):
            return "no info"
        org = org[0]
        orgData = org['data']
        return f"{org['value']}\nИНН: {orgData['inn']}\nОГРН: {orgData['ogrn']} от {datetime.utcfromtimestamp(float(orgData['ogrn_date']) / 1000).strftime('%d.%m.%Y')}\n{orgData['management']['post']}: {orgData['management']['name']}\nТелефон: {'Нет' if orgData['phones'] == None else orgData['phones']}\nЭл. почта: {'Нет' if orgData['emails'] == None else orgData['emails']}"

    # Сбор данных об орг для создания pdf
    async def getOrg(self, inn):
        org = await self.search(inn)
        org = org[0]
        orgData = org[0]['data']
        info = {
            "cont_name": orgData['management']['name'],
            "cont_org": org['value'],
            "cont_inn": orgData['inn'],
            "cont_ogrn": orgData['ogrn'],
            "cont_adress": orgData['source'],
            "cont_fio": orgData['management']['name'],
            "cont_headstatus": orgData['management']['post'],
            "cont_email": '' if orgData['emails'] == None else orgData['emails'],
            "cont_phone": '' if orgData['phones'] == None else orgData['phones']
        }
        return info