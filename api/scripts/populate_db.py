import random
from datetime import datetime, timedelta

from api.database import SessionLocal
from api.models import (
    TurmasModel,
    AlunosModel,
    JogosModel,
    SessoesModel,
)

nomes = ["Joao", "Maria", "Jose"]
sobrenomes = ["Silva", "Santos"]

turmas = ["A", "B", "C", "D"]
anos = [1, 2, 3, 4, 5]

jogos = [
    "Aventura das Letras",
    "Mata-Mosca",
    "Soletrando",
]

palavras = [
    "python",
    "escola",
    "computador",
    "algoritmo",
    "variavel",
    "funcao",
    "classe",
    "banco",
]

dificuldades = ["facil", "medio", "dificil"]


def random_datetime_last_days(days=60):
    now = datetime.now()
    delta = timedelta(
        days=random.randint(0, days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return now - delta


def main():
    db = SessionLocal()

    # -----------------------------
    # Turmas
    # -----------------------------

    for ano in anos:
        for turma in turmas:
            exists = (
                db.query(TurmasModel)
                .filter_by(ano=ano, turma=turma)
                .first()
            )

            if not exists:
                db.add(TurmasModel(ano=ano, turma=turma))

    db.commit()

    turma_ids = [t.id for t in db.query(TurmasModel).all()]

    # -----------------------------
    # Jogos
    # -----------------------------

    for nome in jogos:
        exists = db.query(JogosModel).filter_by(nome=nome).first()
        if not exists:
            db.add(JogosModel(nome=nome))

    db.commit()

    jogo_ids = [j.id for j in db.query(JogosModel).all()]

    # -----------------------------
    # Alunos
    # -----------------------------

    alunos_ra = []

    for i in range(100):
        nome = f"{random.choice(nomes)} {random.choice(sobrenomes)}"
        ra = f"2025{i:04d}"
        turma_id = random.choice(turma_ids)

        aluno = db.query(AlunosModel).filter_by(ra=ra).first()

        if not aluno:
            aluno = AlunosModel(
                nome=nome,
                ra=ra,
                turma_id=turma_id,
            )
            db.add(aluno)

        alunos_ra.append(ra)

    db.commit()

    # -----------------------------
    # Sessões
    # -----------------------------

    sessoes = []

    for _ in range(5000):

        turma_id = random.choice(turma_ids)
        jogo_id = random.choice(jogo_ids)
        aluno_ra = random.choice(alunos_ra)

        acertos = random.randint(0, 10)
        erros = random.randint(0, 5)

        sessao = SessoesModel(
            turma_id=turma_id,
            jogo_id=jogo_id,
            aluno_ra=aluno_ra,
            palavra=random.choice(palavras),
            dificuldade=random.choice(dificuldades),
            tempo_total=round(random.uniform(10, 120), 2),
            acertos=acertos,
            erros=erros,
            data_execucao=random_datetime_last_days(),
        )

        sessoes.append(sessao)

    db.bulk_save_objects(sessoes)
    db.commit()

    db.close()

    print("Banco populado com sucesso.")


if __name__ == "__main__":
    main()
