from aiogram import types
from config import dp, bot, org
from datetime import datetime, timedelta
from database import Database
from aiogram.fsm.context import FSMContext
from states.courts import CourtsNo, JudiProcss, JudiProccDate, MessageTrackNumber, RespectfulReason, OrderDetails, Inn, Debt, Description,DATE,FIO,adress, prikaz
import re
import os
from aiogram.types.input_file import FSInputFile
import docx
from docx2pdf import convert
import asyncio
import urllib.request
import aiohttp
import io
from docx2pdf import convert
import platform
import subprocess


class MessageHandler():
    def __init__(self) -> None:
        self.db = Database()

    async def start(self, message: types.Message):
        await self.run(message)
    
    async def run(self, message: types.Message):
        cityBtns = [['Москва', 'moscow'], ['Санкт-Петербург', 'spb'], ['Другой', 'other']]
        markup = self.createInlineButtons(cityBtns)
        await message.answer("Проверьте есть ли на вас судебный приказ и легко отмените его. \n Выберите город:", reply_markup=markup)
    async def callBack(self, message: types.CallbackQuery, state: FSMContext):
        data = message.data
        
        if(data == "other"):
            await message.message.answer("К сожелению на данный момент доступны только 2 города!")
            await self.start(message.message)
        
        elif(data == 'moscow' or data == 'spb'):
            await state.set_data({"city": data})
            await self.checkReceived(message.message)
        
        elif(data == 'received'):
            await state.set_state(CourtsNo.NO.state)
            await message.message.answer("Введите номер судебного участка (или название суда)")
            
        elif(data == 'check'):
            await message.message.answer("Найдите информацию здесь https://mirsud.spb.ru/cases/")
        elif(data == 'checkCourtTrue'):
            await state.set_state(JudiProcss.NO.state)
            await message.message.answer("Введите номер дела (производство №)")
            
        elif(data == 'checkCourtFalse'):
            await state.set_state(CourtsNo.NO.state)
            await message.message.answer("Введите еще раз номер судебного участка или наберите текстом полное наименование судаи ФИО судьи")
        
        elif(data == 'gosUslugi' or data == 'otherMethod'):
            data = await state.get_data()
            data['messGetType'] = 'Госуслуги' if data == 'gosUslugi' else 'Другой'
            data['track']=None
            await state.set_data(data)
            await self.whenGetLetter(message.message,state)
            
        elif(data == 'orderedLetter'):
            data = await state.get_data()
            data['messGetType'] = 'Почта России'
            await state.set_data(data)
            await state.set_state(MessageTrackNumber.NO)
            await message.message.answer("Введите трек-номер (цифры под штрих-кодом на конверте с приказом)")
        
        elif(data == 'orgTrue'):
            await state.set_state(Debt.debt)
            await message.message.answer("Введите сумму задолженности (число в рублях, копейки указать после запятой)")
            
        elif(data == 'orgFalse'):
            await state.set_state(Inn.inn)
            await message.message.answer("Введите ИНН еще раз")

        elif(data == 'checkDateTrue'):
            data = await state.get_data()
            data['DATE']=datetime.now().date()
            await state.set_data(data)
            await state.set_state(FIO.NO)
            await message.message.answer("Введите ФИО:")

        elif(data == 'checkDateFalse'):
            await message.message.answer("«Введите дату которая будет указана на возражении")
            await state.set_state(DATE.NO)
        elif(data == 'checkDovolenTrue'):
            await state.set_state(prikaz.NO)
            await message.message.answer("Замечательно! Через десять дней вы получите напоминание, чтобы подтвердить факт отмены судебного приказа.")
            await self.prikaz(message, state)

        elif(data == 'checkDovolenFalse'):
            await message.message.answer("Вы поможете нам с рассказать миру о полезном сервисе, а мы поможем вам проконтролировать отмену вашего судебного приказа")
            await self.zaebat(message.message,state)
        elif(data == 'prikazTrue'):
            data=await state.get_data()
            await message.message.answer(f'''Судебный приказ по делу {data['num']} ОТМЕНЕН!
Поздравляем! Не забывайте периодически проверять новые дела на сайте суда. Также вы можете проверить 
информацию по своим родственникам.''')
        
        elif(data == 'prikazFalse'):
            await self.prikaz(message,state)
        elif(data == 'prikazOther'):
            await message.message.answer('Напишите @shkolaupravdoma чтобы получить памятку как принудить к закону и добросовестности управляшку или ЕИРЦ')

    async def checkReceived(self, message: types.Message):
        btns = [['Уже получен', 'received'], ['Проверить наличие', 'check']]
        markup = self.createInlineButtons(btns)
        await message.answer("Выберите что хотите сделать:", reply_markup=markup)

    


    async def getCourt(self, message: types.Message, state: FSMContext, sud_uchastok=None):
        data = await state.get_data()
        city = data['city']
        text = message.text
        court = self.db.select(f"{city}_courts", "*", f"id = {text}")
        data['sud_uchastok']=text
        data['court'] = {
            'id': text,
            'name': court[5],
            'phone': court[6],
            'email': court[4],
            'place': court[2],
            'adress':court[3]
        }
        await state.set_data(data)
        f"Реквизиты мирового суда:\nСудебный участок №{court[0]}\nМировой судья: {court[5]}\nАдрес: {court[3]}\nТелефон: {court[6]}\nЭлектронный адрес: {court[4]}\nСайт: {court[9]}\nВерно?"
        if not court or len(court) < 1 or court == None:
            return await message.answer("Мировой суд с таким номером не найден!\n\nВведите корректный номер суда:") 
        
        text = self.createMessage(court)
        
        btns = [['Да', 'checkCourtTrue'], ['Нет', 'checkCourtFalse']]
        markup = self.createInlineButtons(btns)
        await message.answer(text, reply_markup=markup)
        await state.set_state(CourtsNo.NO)

    def createInlineButtons(self, text: list[list[str]], rowWidth: int = 3):
        buttons = []
        for value in text:
            buttons.append(
                [types.InlineKeyboardButton(text=value[0], callback_data=value[1])]
            )
        markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        return markup
    async def createJudiProccLink(self, message: types.Message,state: FSMContext):
        no = message.text
        data = await state.get_data()
        data['num']=no
        await state.set_data(data)
        
        link = f"https://mirsud.spb.ru/cases/detail/{data['sud_uchastok']}/?id={no}"
        btns = [['Заказное письмо', 'orderedLetter'], ['Госуслуги', 'gosUslugi'], ['Другой', 'otherMethod']]
        markup = self.createInlineButtons(btns)
        await message.answer(f"Вот ссылка на ваше дело {link}\n\nУточните способ получения вами судебного приказа", reply_markup=markup)
   
    async def prikaz(self, message: types.Message,state: FSMContext):
        await asyncio.sleep(20)
        data=await state.get_data()
        link = f"https://mirsud.spb.ru/cases/detail/{data['sud_uchastok']}/?id={data['num']}"
        btns = [['Да, приказ отменен', 'prikazTrue'], ['Нет, еще не отменили', 'prikazFalse'],['Ой, мне отказано, нужна помощь юриста', 'prikazOther']]
        markup = self.createInlineButtons(btns)
        await bot.send_message(message.from_user.id,f'Посмотрите отменили ли судебный приказ {link}', reply_markup=markup)


    async def checkRusMail(self, message: types.Message, state: FSMContext):
        no = message.text
        text = f"Зайдите сюда https://www.pochta.ru/tracking?barcode={no} (или введите здесь трек-номер: https://www.pochta.ru/tracking)\n и скачайте отчет о доставке который желательно приложить к письму)"
        await message.answer(text)
        await state.set_state(MessageTrackNumber.NO)
        data=await state.get_data()
        data["track"]=message.text
        await state.set_data(data)
        await self.whenGetLetter(message,state)
    
    async def checkDate(self, message: types.Message, state: FSMContext):
        date=message.text
        data=await state.get_data()
        data["data_nachala"]=message.text
        await state.set_data(data)
        dateRegxp = r"\d{2}.\d{2}.\d{4}"
        
        if not re.match(dateRegxp, date):
            await message.answer("Не корректный формат даты!\n\nВвеитье дату в формате: дд.мм.гггг(21.12.2023)")
        else:
            now = datetime.now() - timedelta(10)
            dt = date.split('.')
            after = datetime(day=int(dt[0]), month=int(dt[1]), year=int(dt[2]))
            await state.set_state(JudiProcss.NO)
            if now >= after:
                await state.set_state(RespectfulReason.reason)
                await message.answer("<b>ВНИМАНИЕ! Введите уважительную причину пропуска срока подачи возражения (например: болезнь, уход за больным, запланированный ранее отъезд, отсутствие в стране). Обязательно приложите документы подтверждающие уважительность причины задержки с подачей возражения</b>")
            else:
                await self.askOrderDetails(message,state)
    
    async def askOrderDetails(self, message: types.Message,state:FSMContext):
        await state.set_state(OrderDetails.details)
        await message.answer('''Введите реквизиты судебного приказа (найти в тексте):
Введите ИНН организации которая хочет получить с вас деньги:
                             ''')
        await state.set_state(Inn.inn)
    
    async def setOrderDetails(self, message: types.Message, state: FSMContext):
        await state.set_state(OrderDetails.details)
        data = await state.get_data()
        data['orderDet'] = message.text
        await state.set_data(data)

    async def setInn(self, message: types.Message, state: FSMContext):
        await state.set_state(Inn.inn)
        inn = message.text
        data = await state.get_data()
        data['inn'] = inn
        await state.set_data(data)
       
        # Получает инфо. об органзиации по ИНН(dadata)
        
        orgInfo = await org.createOrgInfo(inn,state)
        if(orgInfo == 'no info'):
            await state.set_state(Inn.inn)
            return await message.answer(f"По ИНН: {inn} не найдено компаний.\nПовтаритье попытку:")
        
        orgInfo += '\n\nВерно?'
        btns = [['Да', 'orgTrue'], ['Нет', 'orgFalse']]
        markup = self.createInlineButtons(btns)
        await message.answer(orgInfo, reply_markup=markup)
        
    async def setReason(self, message: types.Message, state: FSMContext):
        await state.set_state(RespectfulReason.reason)
        data = await state.get_data()
        data['reason'] = message.text
        await state.set_data(data)
        await self.askOrderDetails(message,state)
    
    async def setDebt(self, message: types.Message, state: FSMContext):
        await state.set_state(Debt.debt)
        data = await state.get_data()
        data['debt'] = message.text
        await state.set_data(data)
        await state.set_state(Description.desc)
        await message.answer("Введите описание задолженности (слово в слово с текста судебного приказа)")
       
    # Записывает задолженость 
    async def setDesc(self, message: types.Message, state: FSMContext):
        await state.set_state(Description.desc)
        data = await state.get_data()
        data['desc'] = message.text
        await state.set_data(data)
        btns = [['Да', 'checkDateTrue'], ['Нет', 'checkDateFalse']]
        markup = self.createInlineButtons(btns)
        await message.answer("Создать возражение на данный судебный приказ с текущей датой?",reply_markup=markup)
    
    async def getFIO(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        data['fio']=message.text
        await state.set_data(data)
        await state.set_state(adress.NO)
        await message.answer("Введите адресс помещения где образовалась задолженность")
        
    async def getDATE(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        data['DATE']=message.text
        await state.set_data(data)
        await state.set_state(FIO.NO)
        await message.answer("Введите ФИО:")

    async def getPDF(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        data['adress']=message.text
        data['data']=datetime.now().date()
        await state.set_data(data)
        a=data['fio']
        response = urllib.request.urlopen("https://docs.google.com/document/d/18W5XldNpojEXU0gFnKN1p-tczpS20-J8y4hGprHNkao/export?format=docx")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://docs.google.com/document/d/18W5XldNpojEXU0gFnKN1p-tczpS20-J8y4hGprHNkao/export?format=docx") as response:
                if response.status == 200:
                    content = await response.read()
                    a=io.BytesIO(content)
                    doc = docx.Document(a)
                    paragraphs = doc.paragraphs
                    for paragraph in paragraphs:
                        if 'delo_data0' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_data0}}', "out")
                        if 'delo_summ2' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_summ2}}', "out")
                        if 'delo_datafrom' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_datafrom}}', "out")
                        if 'delo_datatill' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_datatill}}', "out")
                        if 'delo_inn' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_inn}}', data['inn'])
                        if 'cont_fio' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{cont_fio}}', str(data['court'].get('name')))
                        if 'cont_name' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{cont_name}}', str(data['court'].get('place')))
                        if 'cont_adress' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{cont_adress}}', str(data['court'].get('adress')))
                        if 'cont_phone' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{cont_phone}}', str(data['court'].get('phone')))
                        if 'cont_email' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{cont_email}}', str(data['court'].get('email')))
                        if 'fio' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{fio}}', str(data['fio']))
                        if 'delo_adress' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_adress}}', str(data['adress']))
                        if 'delo_way' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_way}}', str(data['messGetType']))
                        if 'delo_data' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_data}}', str(data['data_nachala']))
                        if 'delo_name' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_name}}', str(data['delo_name']))
                        if 'delo_num' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_num}}', str(data['num']))
                        if 'delo_data2' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_data2}}', str(data['DATE']))#/////////////
                        if 'data' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{data}}', str(data['data']))
                        if 'delo_trek' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_trek}}', str(data['track']))
                        if 'delo_summ' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_summ}}', str(data['debt']))
                        if 'delo_mean' in paragraph.text:
                            paragraph.text = paragraph.text.replace('{{delo_mean}}', str(data['desc']))
                    doc.save(f'./docks/{a}.docx')
                    print("||||||||||||||||||||||||||||||||||||||")
        os_name = platform.system()
        if os_name == 'Windows':
            convert(f'./docks/{a}.docx', f'./docks/{a}.pdf')
        elif os_name == 'Linux':
            command = ['libreoffice', '--convert-to',
                        'pdf', '--outdir', "./docks", f'./{a}.docx']
            subprocess.run(command, check=True)
        document = FSInputFile(f'./docks/{a}.pdf')
        await bot.send_document(message.chat.id, document)
        await message.answer("ВАЖНО! Очень внимательно проверьте все реквизиты суда и реквизиты дела перед отправкой возражения в суд")
        await message.answer(''' Пожалуйста, если вы довольны результатом то разместите пост на своей странице в 
социальной сети:''')
        await message.answer('''
«Важная информация! Активизировались управляшки и РКЦ по выдаче судебных приказов по долгам за 
ЖКУ. 
Почти всегда суммы задолженностей в судебных приказах завышены или вообще не обоснованы, ведь 
никаких договорных отношений с «должниками» скорее всего не существует, скорее всего это просто 
незаконные «хотелки» третьих лиц. Эти жулики от ЖКХ думают, что никто не будет возражать на их 
беспредел. 
Но, не нужно покорно ждать когда приставы спишут деньги со счетов или заблокируют кредитки.
Проверьте прямо сейчас есть ли на вас судебный приказ и легко отмените его. Подробности здесь -> 
t.me/prikazunet_bot»''')
        await self.zaebat(message,state)
    async def zaebat(self,message: types.Message, state: FSMContext):
        btns = [['Да', 'checkDovolenTrue'], ['Нет', 'checkDovolenFalse']]
        markup = self.createInlineButtons(btns)
        await message.answer("Вы разместили этот пост у себя в соцсети?",reply_markup=markup)

    async def whenGetLetter(self, message: types.Message,state: FSMContext):
        await state.set_state(JudiProccDate.NO)
        await message.answer("Введите дату получения письма с судебным приказом (указанный в отчете)\n\nФормат даты: ДД.ММ.ГГГГ(21.12.2023)")
    
    #async def clear(self,  message: types.Message,state: FSMContext):
        #print(message.story())
    
    def createMessage(self, data: tuple[str, int]):
        return f"""
        Реквизиты мирового суда:\nСудебный участок №{data[0]}\nМировой судья: {data[5]}\nАдрес: {data[3]}\nТелефон: {data[6]}\nЭлектронный адрес: {data[4]}\nСайт: {data[9]}\nВерно?
        """.strip()