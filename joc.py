from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import database as db

app = FastAPI(title="Aventura")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_localitzacio(id: int):
    loc = db.execute_single("SELECT * FROM localitzacions WHERE id = %s", (id,))
    if loc and isinstance(loc.get('descripcio'), bytes):
        try:
            loc['descripcio'] = loc['descripcio'].decode('utf-8')
        except:
            loc['descripcio'] = ''
    return loc


def get_sortides(localitzacio_id: int):
    query = """
        SELECT
            c.id,
            c.nom1, c.nom2,
            c.localitzacio1, c.localitzacio2,
            c.tancat,
            CASE
                WHEN c.localitzacio1 = %s THEN c.localitzacio2
                ELSE c.localitzacio1
            END as desti_id,
            CASE
                WHEN c.localitzacio1 = %s THEN c.nom1
                ELSE c.nom2
            END as nom
        FROM camins c
        WHERE c.localitzacio1 = %s OR c.localitzacio2 = %s
    """
    return db.execute_query(query, (localitzacio_id, localitzacio_id, localitzacio_id, localitzacio_id))


def get_objectes_sala(localitzacio_id: int):
    query = """
        SELECT id, nom, descripcio, imatge, pos_x, pos_y, agafable, usos, mida
        FROM objectes
        WHERE localitzacio_id = %s
    """
    objectes = db.execute_query(query, (localitzacio_id,))
    for obj in objectes:
        if obj.get('descripcio') and isinstance(obj['descripcio'], bytes):
            try:
                obj['descripcio'] = obj['descripcio'].decode('utf-8')
            except:
                obj['descripcio'] = ''
    return objectes


# ==================== API PER AL JOC ====================

@app.get("/api/interaccio")
async def api_interaccio(objecte_id: int, target_tipus: str, target_id: int):
    """
    Comprova si hi ha una interacció definida entre un objecte i un target.
    Retorna el resultat o null si no existeix.
    """
    query = """
        SELECT i.*, o.nom as nom_resultat_obj
        FROM interaccions i
        LEFT JOIN objectes o ON i.resultat_id = o.id
        WHERE i.objecte_id = %s
          AND i.target_tipus = %s
          AND i.target_id = %s
        LIMIT 1
    """
    result = db.execute_single(query, (objecte_id, target_tipus, target_id))
    if not result:
        return JSONResponse({"ok": False, "missatge": "No passa res especial."})

    # Si obre un camí, actualitzem la BBDD
    if result['resultat_tipus'] == 'obrir_cami':
        db.execute_query(
            "UPDATE camins SET tancat = FALSE WHERE id = %s",
            (result['target_id'],),
            fetch=False
        )

    # Construir resposta
    resposta = {
        "ok": True,
        "consumeix": bool(result['consumeix']),
        "resultat_tipus": result['resultat_tipus'],
        "missatge": result['resultat_missatge'] or "",
        "resultat_id": result['resultat_id'],
        "nom_resultat": result['nom_resultat_obj'] or "",
    }

    # Si crea un objecte, retornem les dades completes
    if result['resultat_tipus'] == 'crear_objecte' and result['resultat_id']:
        obj_nou = db.execute_single(
            "SELECT id, nom, descripcio, imatge, usos, mida FROM objectes WHERE id = %s",
            (result['resultat_id'],)
        )
        if obj_nou:
            if isinstance(obj_nou.get('descripcio'), bytes):
                try:
                    obj_nou['descripcio'] = obj_nou['descripcio'].decode('utf-8')
                except:
                    obj_nou['descripcio'] = ''
            resposta['objecte_nou'] = dict(obj_nou)

    return JSONResponse(resposta)


@app.get("/api/combinacio")
async def api_combinacio(objecte_a: int, objecte_b: int):
    """
    Comprova si hi ha una combinació entre dos objectes de l'inventari.
    La combinació és simètrica (A+B = B+A).
    """
    query = """
        SELECT c.*, o.nom as nom_resultat,
               o.descripcio, o.imatge, o.usos, o.mida
        FROM combinacions c
        JOIN objectes o ON c.resultat_id = o.id
        WHERE (c.objecte_a = %s AND c.objecte_b = %s)
           OR (c.objecte_a = %s AND c.objecte_b = %s)
        LIMIT 1
    """
    result = db.execute_single(query, (objecte_a, objecte_b, objecte_b, objecte_a))
    if not result:
        return JSONResponse({"ok": False, "missatge": "Aquests dos objectes no es poden combinar."})

    obj_nou = {
        "id":         result['resultat_id'],
        "nom":        result['nom_resultat'],
        "descripcio": result['descripcio'].decode('utf-8') if isinstance(result['descripcio'], bytes) else (result['descripcio'] or ''),
        "imatge":     result['imatge'] or '',
        "usos":       result['usos'],
        "mida":       result['mida'],
    }
    return JSONResponse({"ok": True, "objecte_nou": obj_nou})


# ==================== JUGA ====================

@app.get("/", response_class=HTMLResponse)
async def seleccionar_inici(request: Request):
    localitzacions = db.execute_query("SELECT id, nom FROM localitzacions ORDER BY id")
    return templates.TemplateResponse(
        "seleccio_inici.html",
        {"request": request, "localitzacions": localitzacions}
    )


@app.get("/juga/{id}", response_class=HTMLResponse)
async def mostrar_localitzacio(request: Request, id: int):
    localitzacio = get_localitzacio(id)
    if not localitzacio:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    sortides = get_sortides(id)
    objectes = get_objectes_sala(id)

    return templates.TemplateResponse(
        "juga.html",
        {
            "request":     request,
            "localitzacio": localitzacio,
            "sortides":    sortides,
            "objectes":    objectes,
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
