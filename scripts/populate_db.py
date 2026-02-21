import os
import random
import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = "db.sqlite3"

if not os.path.exists(DB_PATH):
    print(f"O banco de dados [{DB_PATH}] ainda não existe")
    sys.exit()


turmas = [
    "B",
    "A",
    "C"
]
ano_turmas = [1, 2, 3, 4, 5,]

jogos = [
    "Aventura das Letras",
    "Mata-Mosca",
]

palavras = [
    "python",
    "escola",
    "computador",
    "algoritmo",
    "variavel",
    "função",
    "classe",
    "banco",
]

dificuldades = ["facil", "medio", "dificil"]


def random_datetime_last_days(days=30):
    now = datetime.now()
    delta = timedelta(
        days=random.randint(0, days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return now - delta


with sqlite3.connect(DB_PATH) as conn:
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Inserir turmas
    for turma in turmas:
        for ano in ano_turmas:
            cursor.execute(
                "INSERT OR IGNORE INTO turmas (ano, turma) VALUES (?, ?)",
                (ano, turma),
            )

    # Inserir jogos
    for nome in jogos:
        cursor.execute(
            "INSERT OR IGNORE INTO jogos (nome) VALUES (?)",
            (nome,),
        )

    # Buscar IDs existentes
    cursor.execute("SELECT id FROM turmas")
    turma_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM jogos")
    jogo_ids = [row[0] for row in cursor.fetchall()]

    # Gerar sessões
    for _ in range(1000):  # quantidade de sessões
        turma_id = random.choice(turma_ids)
        jogo_id = random.choice(jogo_ids)
        palavra = random.choice(palavras)
        dificuldade = random.choice(dificuldades)

        acertos = random.randint(0, 10)
        erros = random.randint(0, 5)
        tempo_total = round(random.uniform(10.0, 120.0), 2)

        data_execucao = random_datetime_last_days(60)

        cursor.execute(
            """
            INSERT INTO sessoes (
                turma_id,
                jogo_id,
                palavra,
                dificuldade,
                tempo_total,
                acertos,
                erros,
                data_execucao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                turma_id,
                jogo_id,
                palavra,
                dificuldade,
                tempo_total,
                acertos,
                erros,
                data_execucao,
            ),
        )

    conn.commit()

print("Banco populado com sucesso.")
