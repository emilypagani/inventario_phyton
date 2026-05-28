from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

import sqlite3
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        inventario = json.loads(resultado[0])

        data_ultima_coleta = datetime.fromisoformat(
            inventario["data_coleta"]
        )

        agora = datetime.now()

        diferenca = agora - data_ultima_coleta

        segundos_offline = diferenca.total_seconds()

        if segundos_offline <= 300:

            inventario["status"] = "ONLINE"

        else:

            minutos = int(segundos_offline // 60)
            horas = int(minutos // 60)
            dias = int(horas // 24)

            if dias >= 1:

                inventario["status"] = (
                    f"OFFLINE há {dias} dia(s)"
                )

            elif horas >= 1:

                inventario["status"] = (
                    f"OFFLINE há {horas} hora(s)"
                )

            else:

                inventario["status"] = (
                    f"OFFLINE há {minutos} minuto(s)"
                )

        return inventario

    return {"erro": "Máquina não encontrada"}