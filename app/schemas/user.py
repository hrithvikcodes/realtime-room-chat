from pydantic import BaseModel, Field, EmailStr



class CreateUser(BaseModel):
    email: EmailStr
    name: str
    
    password: str 

class LoginUser(CreateUser):
    pass
