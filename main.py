import asyncio
import logging
import sys
from aiogram import types
from aiogram.filters.command import CommandStart
from messageHandler import MessageHandler, CourtsNo, JudiProcss, JudiProccDate, MessageTrackNumber, OrderDetails, RespectfulReason, Inn, Debt, Description, DATE, FIO, adress
from config import dp, bot
from aiogram.fsm.context import FSMContext
handler = MessageHandler()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await handler.start(message)

@dp.callback_query()
async def callBack(message: types.CallbackQuery, state: FSMContext):
    await handler.callBack(message, state)

@dp.message(CourtsNo.NO)
async def getCourt(message: types.Message, state: FSMContext):
    #await handler.clear(message,state)
    await handler.getCourt(message, state, message.text)
@dp.message(JudiProcss.NO)
async def createJudiProccLink(message: types.Message, state: FSMContext):
    await handler.createJudiProccLink(message,state)
    await state.set_state(JudiProcss.NO)

@dp.message(MessageTrackNumber.NO)
async def checkRusMail(message: types.Message,state: FSMContext):
    await handler.checkRusMail(message,state)
    
@dp.message(JudiProccDate.NO)
async def checkDate(message: types.Message, state: FSMContext):
    await handler.checkDate(message,state)
    
@dp.message(OrderDetails.details)
async def setOrderDetails(message: types.Message, state: FSMContext):
    await handler.setOrderDetails(message, state)
    
@dp.message(Inn.inn)
async def setInn(message: types.Message, state: FSMContext):
    await handler.setInn(message, state)
    
@dp.message(RespectfulReason.reason)
async def getCourt(message: types.Message, state: FSMContext):
    await handler.setReason(message, state)

@dp.message(Debt.debt)
async def getCourt(message: types.Message, state: FSMContext):
    await handler.setDebt(message, state)

@dp.message(Description.desc)
async def getCourt(message: types.Message, state: FSMContext):
    await handler.setDesc(message, state)

@dp.message(FIO.NO)
async def getFIO(message: types.Message,state: FSMContext):
    await handler.getFIO(message, state)

@dp.message(DATE.NO)
async def getDATE(message: types.Message,state: FSMContext):
    await handler.getDATE(message, state)

@dp.message(adress.NO)
async def getPDF(message: types.Message,state: FSMContext):
    await handler.getPDF(message, state)

@dp.message(adress.NO)
async def prikaz(message: types.Message,state: FSMContext):
    await handler.prikaz(message, state)

async def main() -> None:
    await dp.start_polling(bot)


    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())