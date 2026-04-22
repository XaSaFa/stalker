# Projecte Aventura – Resum tècnic

## Descripció general
Joc d'aventura de text/gràfic tipus point-and-click, amb un CRUD d'administració separat.
Dos servidors FastAPI independents que comparteixen la mateixa base de dades MariaDB.

---

## Stack tecnològic
- **Backend**: Python 3, FastAPI, Jinja2, PyMySQL
- **Base de dades**: MariaDB (base de dades: `Aventura`)
- **Frontend**: HTML + CSS + JS vanilla (sessionStorage per inventari)
- **Fitxers compartits**: `config.py`, `database.py`, `requirements.txt`

---

## Estructura de directoris

```
projecte/
├── config.py               # Credencials BBDD
├── database.py             # execute_query, execute_single
├── requirements.txt
│
├── crud/                   # Administració (port 8000)
│   ├── main.py
│   ├── static/css/style.css
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── localitzacions_list.html
│       ├── localitzacio_form.html
│       ├── camins_list.html
│       ├── cami_form.html
│       ├── objectes_list.html
│       ├── objecte_form.html
│       ├── combinacions_list.html
│       ├── combinacio_form.html
│       ├── interaccions_list.html
│       └── interaccio_form.html
│
└── joc/                    # Joc (port 8002)
    ├── joc.py
    ├── static/
    │   ├── css/style_joc.css
    │   └── img/            # Imatges de sales i objectes
    └── templates/
        ├── seleccio_inici.html
        └── juga.html
```

---

## Base de dades: taules

### `localitzacions`
| Camp | Tipus | Notes |
|---|---|---|
| id | BIGINT PK AI | |
| nom | VARCHAR(100) | |
| descripcio | TEXT | Decodificar de bytes UTF-8 |
| imatge | VARCHAR(250) | Ruta relativa: `/static/img/sala.jpg` |

### `camins`
| Camp | Tipus | Notes |
|---|---|---|
| id | BIGINT PK AI | |
| nom1 | VARCHAR(50) | Nom vist des de localitzacio1 |
| nom2 | VARCHAR(50) | Nom vist des de localitzacio2 |
| localitzacio1 | BIGINT UNSIGNED | |
| localitzacio2 | BIGINT UNSIGNED | |
| tancat | BOOLEAN | DEFAULT FALSE |

### `objectes`
| Camp | Tipus | Notes |
|---|---|---|
| id | BIGINT PK AI | |
| nom | VARCHAR(100) | |
| descripcio | TEXT | Decodificar de bytes UTF-8 |
| imatge | VARCHAR(250) | Ruta relativa |
| localitzacio_id | BIGINT | NULL = a l'inventari inicial |
| pos_x | FLOAT | % horitzontal sobre la imatge (0-100) |
| pos_y | FLOAT | % vertical sobre la imatge (0-100) |
| agafable | BOOLEAN | Si el jugador el pot recollir |
| usos | INT | -1 = il·limitats, 1 = desapareix en usar-lo |
| mida | FLOAT | % relatiu a l'amplada de la imatge de la sala |

### `combinacions`
| Camp | Tipus | Notes |
|---|---|---|
| id | BIGINT PK AI | |
| objecte_a | BIGINT FK→objectes | |
| objecte_b | BIGINT FK→objectes | Simètric: A+B = B+A |
| resultat_id | BIGINT FK→objectes | Objecte que es crea |

> Els dos objectes originals desapareixen de l'inventari. El resultat s'afegeix.

### `interaccions`
| Camp | Tipus | Notes |
|---|---|---|
| id | BIGINT PK AI | |
| objecte_id | BIGINT FK→objectes | Objecte de l'inventari que s'usa |
| target_tipus | ENUM('objecte','cami') | Sobre què s'usa |
| target_id | BIGINT | ID de l'objecte decorat o del camí |
| resultat_tipus | ENUM('obrir_cami','crear_objecte','missatge') | |
| resultat_id | BIGINT nullable | ID objecte creat (si escau) |
| resultat_missatge | VARCHAR(250) | Text si resultat_tipus='missatge' |
| consumeix | BOOLEAN | L'objecte desapareix de l'inventari? |

---

## CRUD (port 8000) – Rutes

| Mètode | Ruta | Acció |
|---|---|---|
| GET | `/` | Pàgina principal |
| GET/POST | `/localitzacions` | Llistar / crear |
| GET/POST | `/localitzacions/nova` | Formulari nou |
| GET/POST | `/localitzacions/{id}/editar` | Editar |
| POST | `/localitzacions/{id}/eliminar` | Eliminar (bloquejat si té camins) |
| GET/POST | `/camins` | Llistar / crear |
| GET/POST | `/camins/nou` | Formulari nou |
| GET/POST | `/camins/{id}/editar` | Editar |
| POST | `/camins/{id}/eliminar` | Eliminar |
| GET/POST | `/objectes` | Llistar / crear |
| GET/POST | `/objectes/nou` | Formulari nou |
| GET/POST | `/objectes/{id}/editar` | Editar |
| POST | `/objectes/{id}/eliminar` | Eliminar |
| GET/POST | `/combinacions` | Llistar / crear |
| GET/POST | `/combinacions/nova` | Formulari nou |
| GET/POST | `/combinacions/{id}/editar` | Editar |
| POST | `/combinacions/{id}/eliminar` | Eliminar |
| GET/POST | `/interaccions` | Llistar / crear |
| GET/POST | `/interaccions/nova` | Formulari nou |
| GET/POST | `/interaccions/{id}/editar` | Editar |
| POST | `/interaccions/{id}/eliminar` | Eliminar |

---

## JOC (port 8002) – Rutes i API

| Mètode | Ruta | Acció |
|---|---|---|
| GET | `/` | Selecció de localització inicial |
| GET | `/juga/{id}` | Mostrar sala amb objectes i sortides |
| GET | `/api/interaccio` | Params: `objecte_id`, `target_tipus`, `target_id` |
| GET | `/api/combinacio` | Params: `objecte_a`, `objecte_b` |

### `/api/interaccio` – Resposta
```json
{
  "ok": true,
  "consumeix": true,
  "resultat_tipus": "obrir_cami | crear_objecte | missatge",
  "missatge": "Text opcional",
  "resultat_id": 5,
  "nom_resultat": "Clau daurada",
  "objecte_nou": { "id": 5, "nom": "...", "imatge": "...", "usos": -1, "mida": 10 }
}
```

### `/api/combinacio` – Resposta
```json
{
  "ok": true,
  "objecte_nou": { "id": 7, "nom": "...", "descripcio": "...", "imatge": "...", "usos": -1, "mida": 10 }
}
```

---

## Lògica del joc (juga.html – JS)

### Inventari
- Persistit a `sessionStorage` com a JSON: `[{id, nom, descripcio, imatge, usos}, ...]`
- Funcions: `getInventari()`, `setInventari()`, `afegirAInventari()`, `eliminarDeInventari()`, `actualitzarUsos()`, `renderInventari()`

### Objectes sobre la imatge
- `position: absolute` dins `.imatge-contenidor` (`position: relative`)
- Posició: `left: pos_x%`, `top: pos_y%`, amb `transform: translate(-50%, -50%)`
- Mida: calculada en JS via `ajustarObjectes()` → `amplada_imatge * mida / 100` en píxels
- S'ajusta en `onload` de la imatge i en `resize` de la finestra

### Menú contextual
- Objecte de la sala: **Examinar / Agafar / Utilitzar**
- Objecte de l'inventari: **Examinar / Utilitzar / Llençar**
- Camí tancat: **Utilitzar objecte** (obre popup de selecció)

### Flux "Utilitzar"
1. Clic "Utilitzar" → `iniciarUs(objecteId, objecteNom, origen)`
2. S'obre popup amb tres seccions: objectes sala, camins tancats, objectes inventari
3. Clic target → `tancarPopupUsar()` + `executarInteraccio(objecteId, targetTipus, targetId)`
4. API retorna resultat → s'aplica a la UI sense recarregar

> **Important**: `objecteId` es passa per valor en cada closure. No hi ha variable global `objecteEnUs` (es va eliminar per un bug de condició de carrera).

### Flux "Combinar"
1. Clic "Utilitzar" a objecte inventari → secció "Combinar" al popup
2. Clic objecte B → `executarCombinacio(objecteAId, objecteBId)`
3. API `/api/combinacio` retorna `objecte_nou`
4. S'eliminen A i B de l'inventari, s'afegeix el resultat

### Obrir camí a la UI
- `obrirCamiUI(camiId)` substitueix el `<button>` tancat per un `<a>` navegable sense recarregar la pàgina
- El servidor també actualitza `camins.tancat = FALSE` a la BBDD

---

## Particularitats i bugs coneguts

### Decodificació `descripcio`
El camp `descripcio` de `localitzacions` i `objectes` es guarda com a `bytes` UTF-8 (comportament de PyMySQL amb camps `TEXT`). Cal decodificar sempre:
```python
if isinstance(obj.get('descripcio'), bytes):
    obj['descripcio'] = obj['descripcio'].decode('utf-8')
```

### Compatibilitat FastAPI/Starlette
La sintaxi `TemplateResponse("template.html", {"request": request, ...})` (diccionari) és compatible amb totes les versions. No usar la sintaxi nova amb `request=` com a kwarg separat.

### Imatges
- Rutes relatives que comencen per `/static/img/`
- Carpeta física: `joc/static/img/`
- El CRUD guarda el path tal com s'introdueix al formulari

---

## SQL de creació (schema complet)
```sql
CREATE DATABASE IF NOT EXISTS Aventura CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE Aventura;

CREATE TABLE localitzacions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    descripcio TEXT DEFAULT NULL,
    imatge VARCHAR(250) DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE camins (
    id BIGINT NOT NULL AUTO_INCREMENT,
    nom1 VARCHAR(50) NOT NULL,
    nom2 VARCHAR(50) NOT NULL,
    localitzacio1 BIGINT UNSIGNED NOT NULL,
    localitzacio2 BIGINT UNSIGNED NOT NULL,
    tancat BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE objectes (
    id BIGINT NOT NULL AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    descripcio TEXT DEFAULT NULL,
    imatge VARCHAR(250) DEFAULT NULL,
    localitzacio_id BIGINT DEFAULT NULL,
    pos_x FLOAT NOT NULL DEFAULT 50,
    pos_y FLOAT NOT NULL DEFAULT 50,
    agafable BOOLEAN NOT NULL DEFAULT TRUE,
    usos INT NOT NULL DEFAULT -1,
    mida FLOAT NOT NULL DEFAULT 100,
    PRIMARY KEY (id),
    FOREIGN KEY (localitzacio_id) REFERENCES localitzacions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE combinacions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    objecte_a BIGINT NOT NULL,
    objecte_b BIGINT NOT NULL,
    resultat_id BIGINT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (objecte_a) REFERENCES objectes(id) ON DELETE CASCADE,
    FOREIGN KEY (objecte_b) REFERENCES objectes(id) ON DELETE CASCADE,
    FOREIGN KEY (resultat_id) REFERENCES objectes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE interaccions (
    id BIGINT NOT NULL AUTO_INCREMENT,
    objecte_id BIGINT NOT NULL,
    target_tipus ENUM('objecte','cami') NOT NULL,
    target_id BIGINT NOT NULL,
    resultat_tipus ENUM('obrir_cami','crear_objecte','missatge') NOT NULL,
    resultat_id BIGINT DEFAULT NULL,
    resultat_missatge VARCHAR(250) DEFAULT NULL,
    consumeix BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id),
    FOREIGN KEY (objecte_id) REFERENCES objectes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
