from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import database as db

app = FastAPI(title="Aventura")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_localitzacio(id: int):
    """Obté una localització per ID i decodifica la descripció"""
    loc = db.execute_single("SELECT * FROM localitzacions WHERE id = %s", (id,))
    if loc and isinstance(loc.get('descripcio'), bytes):
        try:
            loc['descripcio'] = loc['descripcio'].decode('utf-8')
        except:
            loc['descripcio'] = ''
    return loc


def get_sortides(localitzacio_id: int):
    """Obté els camins disponibles des d'una localització donada"""
    query = """
        SELECT 
            c.id,
            c.nom,
            c.localitzacio1,
            c.localitzacio2,
            CASE 
                WHEN c.localitzacio1 = %s THEN c.localitzacio2
                ELSE c.localitzacio1
            END as desti_id
        FROM camins c
        WHERE c.localitzacio1 = %s OR c.localitzacio2 = %s
    """
    return db.execute_query(query, (localitzacio_id, localitzacio_id, localitzacio_id))


# ==================== JUGA ====================

@app.get("/", response_class=HTMLResponse)
async def seleccionar_inici(request: Request):
    """Pantalla de selecció de localització inicial"""
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY id")
    return templates.TemplateResponse(
        "seleccio_inici.html",
        {"request": request, "localitzacions": localitzacions}
    )


@app.get("/juga/{id}", response_class=HTMLResponse)
async def mostrar_localitzacio(request: Request, id: int):
    """Mostra la localització actual amb les seves sortides"""
    localitzacio = get_localitzacio(id)
    if not localitzacio:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    sortides = get_sortides(id)
    return templates.TemplateResponse(
        "juga.html",
        {
            "request": request,
            "localitzacio": localitzacio,
            "sortides": sortides,
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
