import socket
import platform
import os
import psutil
import subprocess

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
    cpu = subprocess.check_output('powershell "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"',shell=True).decode().strip()
    return cpu

def pegar_gpu(): 
    gpu = subprocess.check_output('powershell "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"',shell=True).decode().strip()
    return gpu

def pegar_memoriaram():
    ram = psutil.virtual_memory()
    ram_gb = ram.total / (1024 ** 3)
    return ram_gb

def pegar_discos():

    lista_discos = []

    discos = subprocess.check_output(
        'powershell "Get-PhysicalDisk | Select FriendlyName, MediaType, Size"',
        shell=True
    ).decode()

    linhas = discos.splitlines()

    for linha in linhas:

        linha = linha.strip()

        if (
            linha
            and "FriendlyName" not in linha
            and "-----" not in linha
        ):

            partes = linha.split()

            tipo = partes[-2]
            tamanho = partes[-1]

            tamanho_gb = int(tamanho) / (1024 ** 3)

            nome = " ".join(partes[:-2])

            info_disco = {
                "nome": nome,
                "tipo": tipo,
                "tamanho": tamanho_gb
            }

            lista_discos.append(info_disco)
    return lista_discos

def pegar_usuario():
    usuario = os.getlogin()
    return usuario

def montar_inventario():
    
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
        'hostname' : hostname,
        'usuario' : usuario,
        'ip' : ip,
        
        'sistema' : sistema,
        'versao' : versao,
        
        'cpu' : cpu,
        'gpu' : gpu,
        
        'ram_gb' : ram_gb,
        'lista_discos' : lista_discos        
    }
    return inventario

def gerar_html(hostname, usuario, ip, sistema, versao, cpu, gpu, ram_gb, lista_discos):
    html = f"""
<!DOCTYPE html>
<html lang="pt-br">

<head>
    <meta charset="UTF-8">
    <title>Inventário do Sistemas</title>

    <style>

        body {{
            background-color: #0f172a;
            color: white;
            font-family: Arial;
            padding: 30px;
        }}

        h1 {{
            color: #38bdf8;
        }}

        .card {{
            background-color: #1e293b;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}

        .titulo {{
            color: #38bdf8;
            font-size: 20px;
            margin-bottom: 10px;
        }}

    </style>

</head>

<body>

    <h1>Inventário do Sistemas</h1>

    <div class="card">
        <div class="titulo">Computador</div>

        <p><strong>Hostname:</strong> {hostname}</p>
        <p><strong>Usuário:</strong> {usuario}</p>
        <p><strong>IP:</strong> {ip}</p>
        <p><strong>Sistema:</strong> {sistema} {versao}</p>
    </div>

    <div class="card">
        <div class="titulo">Hardware</div>

        <p><strong>CPU:</strong> {cpu}</p>
        <p><strong>RAM:</strong> {ram_gb:.2f} GB</p>
        <p><strong>GPU:</strong> {gpu}</p>
    </div>

</body>

</html>
"""

    return html

def main():
    
    inventario = montar_inventario()
    
    html = gerar_html(
    inventario['hostname'],
    inventario['usuario'],
    inventario['ip'],
    inventario['sistema'],
    inventario['versao'],
    inventario['cpu'],
    inventario['gpu'],
    inventario['ram_gb'],
    inventario['lista_discos']
)

    with open("inventario.html", "w", encoding="utf-8") as arquivo:
        arquivo.write(html)

    os.startfile("inventario.html")

    print('Diagnóstico de Configurações: \n')
    print(f'Nome da Máquinas: {inventario ['hostname']} \n')
    print(f'Usuário Conectado: {inventario ['usuario']} \n')
    print(f'IP: {inventario ['ip']} \n')
    print(f'Sistema Operacional: {inventario ['sistema']} {inventario ['versao']} \n')
    print(f'CPU: {inventario ['cpu']} \n')
    print(f'GPU: {inventario ['gpu']} \n')
    print(f'Memória RAM: {inventario ['ram_gb']:.2f} GB \n')
    print(f'Discos:')
    for disco in inventario["lista_discos"]:
        print(f'{disco['nome']} ({disco['tipo']})')
        print(f'Total: {disco['tamanho']:.2f} GB \n')
        
if __name__ == "__main__":
    main()
