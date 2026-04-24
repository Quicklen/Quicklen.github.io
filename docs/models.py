# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

# models.py
class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    fio = Column(String, index=True)
    position = Column(String)
    degree = Column(String)
    email = Column(String)
    photo_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)  # ← новое поле

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)          # краткое описание (опционально)
    date = Column(DateTime, default=datetime.utcnow)
    external_link = Column(String, unique=True, nullable=False)

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)          # Название книги/методички
    author = Column(String)                     # Автор
    discipline = Column(String, index=True)     # Дисциплина: "Алгебра", "Криптография" и т.д.
    description = Column(Text)                  # Аннотация
    file_path = Column(String, nullable=True)   # Путь к PDF (если разрешено публиковать)
    preview_text = Column(Text, nullable=True)  # Текст для предпросмотра (первые абзацы)
    external_link = Column(String, nullable=True)  # Ссылка на Лань/Юрайт/сайт изд-ва
    year = Column(Integer)