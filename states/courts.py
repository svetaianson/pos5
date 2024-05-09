from aiogram.filters.state import StatesGroup, State

class CourtsNo(StatesGroup):
    NO = State()
    
class JudiProcss(StatesGroup):
    NO = State()
    
class JudiProccDate(StatesGroup):
    NO = State()
    
class MessageTrackNumber(StatesGroup):
    NO = State()
    
class RespectfulReason(StatesGroup):
    reason = State()
    
class OrderDetails(StatesGroup):
    details = State()
    
class Inn(StatesGroup):
    inn = State()
    
class Debt(StatesGroup):
    debt = State()
    
class Description(StatesGroup):
    desc = State()  

class FIO(StatesGroup):
    NO = State()  

class DATE(StatesGroup):
    NO = State()  
class adress(StatesGroup):
    NO = State()  
class prikaz(StatesGroup):
    NO = State()  