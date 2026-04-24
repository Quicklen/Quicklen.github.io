# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# schemas.py
class StaffBase(BaseModel):
    fio: str
    position: str
    degree: str
    email: str
    photo_url: Optional[str] = None
    bio: Optional[str] = None  # ← новое поле

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    id: int

    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    content: str

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

class Material(BaseModel):
    id: int
    title: str
    author: str
    discipline: str
    description: str
    preview_text: Optional[str] = None
    external_link: Optional[str] = None
    file_path: Optional[str] = None
    year: int
    
class MaterialBase(BaseModel):
    title: str
    author: str
    discipline: str
    description: str
    file_path: Optional[str] = None
    preview_text: Optional[str] = None
    external_link: Optional[str] = None
    year: int

class MaterialCreate(MaterialBase):
    title: str
    author: str
    discipline: str
    description: str
    preview_text: Optional[str] = None
    external_link: Optional[str] = None
    file_path: Optional[str] = None  # только для внутренних PDF
    year: int

class Material(MaterialBase):
    id: int

    class Config:
        from_attributes = True