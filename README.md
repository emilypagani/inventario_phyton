# Inventário de Hardware

Sistema de inventário de hardware desenvolvido em Python para coleta e monitoramento de informações da máquina.

O projeto coleta automaticamente dados como CPU, GPU, memória RAM, discos, utilização de armazenamento e informações do sistema, gerando um dashboard HTML visual e enviando os dados para uma API FastAPI com persistência em SQLite.

---

# Funcionalidades

- Coleta de hardware
- Monitoramento de discos
- Dashboard HTML visual
- API REST com FastAPI
- Persistência em SQLite
- Histórico de inventários
- Consulta de máquinas via endpoint

---

# Tecnologias utilizadas

- Python
- FastAPI
- SQLite
- HTML
- CSS
- JavaScript
- Psutil

---

# Arquitetura

```txt
Agente Python
↓
API FastAPI
↓
SQLite
↓
Dashboard HTML
```

---

# Endpoints

```http
GET /inventarios
GET /maquinas
GET /maquinas/{hostname}
POST /inventario
```

---

# Como executar

## Rodar API

```bash
py -m uvicorn servidor:app --reload
```

## Rodar agente

```bash
py inventario.py
```

---

# Próximos passos

- Dashboard em tempo real consumindo dados da API
- Status online/offline das máquinas
- Histórico de alterações de hardware
- Coleta avançada via WMI/CIM
---

# Autor

Emily Pagani
