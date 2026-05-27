import socket
import platform
import os
import psutil
import subprocess
import sqlite3
import json
import requests
import time

from datetime import datetime


def pegar_data_coleta():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def pegar_hostname():
    hostname = socket.gethostname()
    return hostname


def pegar_ip(hostname):
    ip = socket.gethostbyname(hostname)
    return ip


def pegar_sistemaop():
    sistema = platform.system()
    return sistema


def pegar_versaosistema():
    versao = platform.release()
    return versao


def pegar_cpu():
    cpu = (
        subprocess.check_output(
            'powershell "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"',
            shell=True,
        )
        .decode()
        .strip()
    )
    return cpu


def pegar_gpu():
    gpu = (
        subprocess.check_output(
            'powershell "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"',
            shell=True,
        )
        .decode()
        .strip()
    )
    return gpu


def pegar_memoriaram():
    ram = psutil.virtual_memory()
    ram_gb = ram.total / (1024**3)
    return ram_gb


def pegar_discos():

    lista_discos = []

    volumes = subprocess.check_output(
        'powershell "Get-CimInstance Win32_LogicalDisk -Filter \\"DriveType=3\\" | Select-Object DeviceID, Size, FreeSpace"',
        shell=True,
    ).decode()

    linhas = volumes.splitlines()

    for linha in linhas:
        linha = linha.strip()

        if linha and "DeviceID" not in linha and "-----" not in linha:
            partes = linha.split()

            unidade = partes[0]
            tamanho = int(partes[1])
            livre = int(partes[2])

            tamanho_gb = tamanho / (1024**3)
            livre_gb = livre / (1024**3)
            usado_gb = tamanho_gb - livre_gb
            percentual_usado = (usado_gb / tamanho_gb) * 100

            info_disco = {
                "unidade": unidade,
                "tamanho": tamanho_gb,
                "livre": livre_gb,
                "usado": usado_gb,
                "percentual_usado": percentual_usado,
            }

            lista_discos.append(info_disco)

    return lista_discos


def pegar_usuario():
    usuario = os.getlogin()
    return usuario


def montar_inventario():
    data_coleta = pegar_data_coleta()
    hostname = pegar_hostname()
    usuario = pegar_usuario()
    ip = pegar_ip(hostname)

    sistema = pegar_sistemaop()
    versao = pegar_versaosistema()

    cpu = pegar_cpu()
    gpu = pegar_gpu()

    ram_gb = pegar_memoriaram()

    lista_discos = pegar_discos()

    inventario = {
        "data_coleta": data_coleta,
        "hostname": hostname,
        "usuario": usuario,
        "ip": ip,
        "sistema": sistema,
        "versao": versao,
        "cpu": cpu,
        "gpu": gpu,
        "ram_gb": ram_gb,
        "lista_discos": lista_discos,
    }
    return inventario


def enviar_inventario(inventario):

    url = "http://127.0.0.1:8000/inventario"

    resposta = requests.post(url, json=inventario)

    if resposta.status_code == 200:
        return True

    else:
        return False


def gerar_html(
    data_coleta, hostname, usuario, ip, sistema, versao, cpu, gpu, ram_gb, lista_discos
):

    cards_discos = ""

    for disco in lista_discos:
        cards_discos += f"""
        <div class="card">
        <div class="titulo">💾 Disco {disco['unidade']}</div>
            <p><strong>Total:</strong> {disco['tamanho']:.2f} GB</p>
            <p><strong>Usado:</strong> {disco['usado']:.2f} GB</p>
            <p><strong>Livre:</strong> {disco['livre']:.2f} GB</p>
            <p><strong>Uso:</strong> {disco['percentual_usado']:.2f}%</p>

            <div class="barra">
                <div class="barra-uso" style="width: {disco['percentual_usado']:.2f}%;"></div>
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html lang="pt-br">

<head>
    <meta charset="UTF-8">
    <title>Inventário do Sistema</title>

    <style>
        body {{
            background-color: #0f172a;
            color: white;
            font-family: Arial, sans-serif;
            padding: 30px;
        }}

        .container {{
            max-width: 1100px;
            margin: auto;
        }}

        h1 {{
            color: #38bdf8;
            margin-bottom: 5px;
        }}

        .subtitulo {{
            color: #94a3b8;
            margin-bottom: 30px;
        }}
        
        <p class="subtitulo">Coleta realizada em {data_coleta}</p>

        button {{
            background-color: #38bdf8;
            color: #0f172a;
            border: none;
            padding: 10px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px;
        }}

        .card {{
            background-color: #1e293b;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
        }}

        .titulo {{
            color: #38bdf8;
            font-size: 20px;
            margin-bottom: 10px;
        }}

        p {{
            color: #e2e8f0;
            line-height: 1.5;
        }}

        strong {{
            color: #f8fafc;
        }}

        .barra {{
            width: 100%;
            height: 12px;
            background-color: #334155;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 12px;
        }}

        .barra-uso {{
            height: 100%;
            background-color: #38bdf8;
        }}
        
        button {{
            background-color: #38bdf8;
            color: #0f172a;
            border: none;
            padding: 10px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 20px;
        }}

        button:hover {{
            background-color: #0ea5e9;
        }}

        #ultima-atualizacao {{
            color: #94a3b8;
            font-size: 14px;
        }}
        
        .topo {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .botao-atualizar {{
            background-color: #38bdf8;
            color: #0f172a;
            border: none;
            width: 48px;
            height: 48px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 24px;
            font-weight: bold;
            transition: 0.5s;
        }}

        .botao-atualizar:hover {{
            background-color: #0ea5e9;
            transform: rotate(180deg);
        }}
    </style>

</head>

<script>
    function atualizarPagina() {{
        location.reload();
    }}

    const agora = new Date();

    document.getElementById("ultima-atualizacao").innerText =
        "Página carregada em: " + agora.toLocaleString("pt-BR");
</script>

<body>

    <div class="container">

        <div class="topo">

    <div>
        <h1>Inventário do Sistema</h1>
        <p class="subtitulo">
            Coleta realizada em {data_coleta}
        </p>
    </div>

    <button
        class="botao-atualizar"
        onclick="atualizarPagina()">

        ↻

    </button>

</div>

<p id="ultima-atualizacao"></p>

        <div class="grid">

            <div class="card">
                <div class="titulo">🖥️ Computador</div>

                <p><strong>Hostname:</strong> {hostname}</p>
                <p><strong>Usuário:</strong> {usuario}</p>
                <p><strong>IP:</strong> {ip}</p>
                <p><strong>Sistema:</strong> {sistema} {versao}</p>
            </div>

            <div class="card">
                <div class="titulo">⚙️ Hardware</div>

                <p><strong>CPU:</strong> {cpu}</p>
                <p><strong>GPU:</strong> {gpu}</p>
                <p><strong>Memória RAM:</strong> {ram_gb:.2f} GB</p>
            </div>

        </div>

        <h2>Discos</h2>

        <div class="grid">
            {cards_discos}
        </div>

    </div>

</body>

</html>
"""

    return html


def main():
    inventario = montar_inventario()

    status = enviar_inventario(inventario)

    html = gerar_html(
        inventario["data_coleta"],
        inventario["hostname"],
        inventario["usuario"],
        inventario["ip"],
        inventario["sistema"],
        inventario["versao"],
        inventario["cpu"],
        inventario["gpu"],
        inventario["ram_gb"],
        inventario["lista_discos"],
    )

    json_inventario = json.dumps(inventario, indent=4, ensure_ascii=False)

    with open("inventario.html", "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    with open("inventario.json", "w", encoding="utf-8") as arquivo_json:
        arquivo_json.write(json_inventario)

    os.startfile("inventario.html")

    print("Diagnóstico de Configurações:\n")
    print(f"Data da coleta: {inventario['data_coleta']}\n")
    print(f"Nome da Máquina: {inventario['hostname']}\n")
    print(f"Usuário Conectado: {inventario['usuario']}\n")
    print(f"IP: {inventario['ip']}\n")
    print(f"Sistema Operacional: {inventario['sistema']} {inventario['versao']}\n")
    print(f"CPU: {inventario['cpu']}\n")
    print(f"GPU: {inventario['gpu']}\n")
    print(f"Memória RAM: {inventario['ram_gb']:.2f} GB\n")

    print("Discos:")
    for disco in inventario["lista_discos"]:
        print(f"Disco {disco['unidade']}")
        print(f"Total: {disco['tamanho']:.2f} GB")
        print(f"Usado: {disco['usado']:.2f} GB")
        print(f"Livre: {disco['livre']:.2f} GB")
        print(f"Uso: {disco['percentual_usado']:.2f}%\n")

    if status:
        print("Status API: ONLINE\n")
    else:
        print("Status API: OFFLINE\n")
    # print(json_inventario)


if __name__ == "__main__":
    # while True:

    #     main()

    #     print("Aguardando próxima coleta...\n")

    #     time.sleep(60)
    main()
