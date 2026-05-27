from fastapi import FastAPI
import sqlite3
import json

app = FastAPI()

conn = sqlite3.connect(
    "inventario.db",
    check_same_thread=False
)

print("Banco conectado")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventarios (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    hostname TEXT,

    ip TEXT,

    usuario TEXT,

    data_coleta TEXT,

    dados TEXT
)
""")

conn.commit()

print("Tabela criada")

@app.get("/inventarios")
def listar_inventarios():

    cursor.execute(
        """
        SELECT
            id,
            hostname,
            ip,
            usuario
        FROM inventarios
        """
    )

    dados = cursor.fetchall()

    inventarios_formatados = []

    for item in dados:

        inventario = {
            "id": item[0],
            "hostname": item[1],
            "ip": item[2],
            "usuario": item[3]
        }

        inventarios_formatados.append(inventario)

    return inventarios_formatados

@app.post("/inventario")
def receber_inventario(inventario: dict):

    dados_json = json.dumps(inventario)

    cursor.execute(
        """
        INSERT INTO inventarios (
            hostname,
            ip,
            usuario,
            data_coleta,
            dados
        )

        VALUES (?, ?, ?, ?, ?)
        """,
        (
            inventario.get("hostname"),
            inventario.get("ip"),
            inventario.get("usuario"),
            inventario.get("data_coleta"),
            dados_json
        )
    )

    conn.commit()

    return {
        "status": "recebido"
    }


@app.get("/maquinas")
def listar_maquinas():

    cursor.execute(
        """
        SELECT
            hostname,
            MAX(data_coleta)
        FROM inventarios
        GROUP BY hostname
        """
    )

    dados = cursor.fetchall()

    maquinas = []

    for item in dados:
        maquina = {
            "hostname": item[0],
            "ultima_coleta": item[1]
        }

        maquinas.append(maquina)

    return maquinas

@app.get("/maquinas/{hostname}")
def buscar_maquina(hostname: str):
    cursor.execute(
        """
        SELECT dados
        FROM inventarios
        WHERE hostname = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (hostname,)
    )

    resultado = cursor.fetchone()

    if resultado:
        return json.loads(resultado[0])

    return {"erro": "Máquina não encontrada"}