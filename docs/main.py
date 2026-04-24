
#uvicorn main:app --reload


from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Staff as DBStaff, News as DBNews, Material as DBMaterial 
from schemas import Staff, StaffCreate, News, NewsCreate, Material, MaterialCreate 
from pathlib import Path

# Создаём таблицы при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Кафедра компьютерной безопасности | ЧелГУ",
    description="Официальный сайт кафедры компьютерной безопасности Челябинского государственного университета"
)


from fastapi.responses import FileResponse

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        
        db.close()

# === HTML-страницы ===

@app.get("/")
def read_index(request: Request, db: Session = Depends(get_db)):
    staff = db.query(DBStaff).all()
    news = db.query(DBNews).order_by(DBNews.date.desc()).limit(5).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "staff": staff,
        "news": news,
        "title": "Кафедра компьютерной безопасности — ЧелГУ"
    })


# === API ===

@app.get("/api/staff", response_model=list[Staff])
def get_staff(db: Session = Depends(get_db)):
    return db.query(DBStaff).all()

@app.post("/api/staff", response_model=Staff)
def create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    db_staff = DBStaff(**staff.model_dump())
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@app.delete("/api/staff/{staff_id}", status_code=204)
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = db.query(DBStaff).filter(DBStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    db.delete(staff)
    db.commit()
    return  # 204 No Content



@app.get("/staff/{staff_id}")
def staff_detail(staff_id: int, request: Request, db: Session = Depends(get_db)):
    staff = db.query(DBStaff).filter(DBStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    return templates.TemplateResponse("staff/detail.html", {
        "request": request,
        "staff": staff,
        "title": f"{staff.fio} — Кафедра КБ"
    })

# === Новые страницы ===

@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "title": "О кафедре"})

@app.get("/about/history")
def about_history(request: Request):
    return templates.TemplateResponse("about_history.html", {
        "request": request,
        "title": "История кафедры"
    })

@app.get("/about/specialty")
def about_specialty(request: Request):
    return templates.TemplateResponse("about_specialty.html", {
        "request": request,
        "title": "Специальность"
    })

@app.get("/about/staff")
def about_staff(request: Request, db: Session = Depends(get_db)):
    staff = db.query(DBStaff).all()
    return templates.TemplateResponse("about_staff.html", {
        "request": request,
        "staff": staff,
        "title": "Преподаватели"
    })

@app.get("/news")
def news_page(request: Request, db: Session = Depends(get_db)):
    news = db.query(DBNews).order_by(DBNews.date.desc()).all()
    return templates.TemplateResponse("news.html", {
        "request": request,
        "news": news,
        "title": "Новости"
    })


from parse_all_news import parse_kb_csu_news_all

@app.post("/admin/update-news-all")
def update_all_news_from_kb():
    """Парсит ВСЕ новости со всех страниц (шаг = 4)"""
    parse_kb_csu_news_all()
    return {"status": "Все новости успешно загружены"}


@app.get("/education")
def education_page(request: Request):
    return templates.TemplateResponse("education.html", {"request": request, "title": "Учебная деятельность"})

@app.get("/science")
def science_page(request: Request):
    return templates.TemplateResponse("science.html", {"request": request, "title": "Научная деятельность"})

@app.get("/student")
def student_page(request: Request):
    return templates.TemplateResponse("student.html", {"request": request, "title": "Студенту"})

@app.get("/applicant")
def applicant_page(request: Request):
    return templates.TemplateResponse("applicant.html", {"request": request, "title": "Абитуриенту"})


UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/materials")
def materials_page(request: Request, db: Session = Depends(get_db)):
    disciplines = db.query(DBMaterial.discipline).distinct().all()  # ✅
    disciplines = [d[0] for d in disciplines if d[0]]
    return templates.TemplateResponse("materials.html", {
        "request": request,
        "disciplines": disciplines,
        "title": "Учебные материалы"
    })

@app.get("/materials/{discipline}")
def materials_by_discipline(
    discipline: str,
    request: Request,
    db: Session = Depends(get_db)
):
    materials = db.query(DBMaterial).filter(DBMaterial.discipline == discipline).all()  # ✅
    return templates.TemplateResponse("material_list.html", {
        "request": request,
        "discipline": discipline,
        "materials": materials
    })

@app.get("/preview/{material_id}")
def preview_material(
    material_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    material = db.query(DBMaterial).filter(DBMaterial.id == material_id).first()  # ✅
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    return templates.TemplateResponse("preview.html", {
        "request": request,
        "material": material
    })

@app.post("/api/materials", response_model=Material, status_code=201)
def create_material(material: MaterialCreate, db: Session = Depends(get_db)) -> Material:
    db_material = DBMaterial(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material  # FastAPI автоматически преобразует ORM → Pydantic благодаря from_attributes=True
