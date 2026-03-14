import random
from datetime import datetime, timedelta
from api.database import SessionLocal
from api.models import TurmasModel, AlunosModel, JogosModel, SessoesModel

# --- Dados mais ricos e variados ---

nomes_masculinos = [
    "João", "Pedro", "Lucas", "Mateus", "Gabriel", "Rafael", "Bruno",
    "Felipe", "Thiago", "Diego", "Vitor", "Gustavo", "Henrique", "Arthur",
    "Leonardo", "Eduardo", "Daniel", "Carlos", "André", "Rodrigo",
]
nomes_femininos = [
    "Maria", "Ana", "Julia", "Beatriz", "Larissa", "Camila", "Fernanda",
    "Isabela", "Leticia", "Mariana", "Natalia", "Patricia", "Renata",
    "Sabrina", "Tatiane", "Vanessa", "Yasmin", "Carolina", "Aline", "Bruna",
]
sobrenomes = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Ferreira", "Rodrigues", "Almeida", "Nascimento", "Carvalho", "Mendes",
    "Gomes", "Martins", "Araújo", "Barbosa", "Ribeiro", "Cardoso", "Dias",
]

turmas = ["A", "B", "C", "D"]
anos = [1, 2, 3, 4, 5]

jogos = [
    "Aventura das Letras",
    "Mata-Mosca",
    "Soletrando",
]

# Palavras agrupadas por dificuldade percebida
palavras_por_dificuldade = {
    "facil": [
        "gato", "bola", "casa", "pato", "fogo", "mala", "lobo", "cama",
        "copo", "dado", "mato", "rato", "boca", "dedo", "pele",
    ],
    "medio": [
        "escola", "livro", "janela", "cadeira", "caneta", "borracha",
        "floresta", "planeta", "família", "criança", "amizade", "música",
        "viagem", "história", "memória",
    ],
    "dificil": [
        "algoritmo", "variável", "computador", "programação", "biblioteca",
        "coeficiente", "democracia", "fotossíntese", "paleontologia",
        "probabilidade", "trigonometria", "arqueologia", "microbiologia",
        "constituição", "perpendicular",
    ],
}

dificuldades = ["facil", "medio", "dificil"]


def random_datetime_last_days(days=90):
    now = datetime.now()
    # Concentra mais sessões nos dias úteis e horário escolar (8h-17h)
    dia = random.randint(0, days)
    hora = random.choices(
        range(24),
        weights=[1,1,1,1,1,1,1,2,5,8,8,6,5,8,8,6,4,3,2,2,1,1,1,1],
        k=1
    )[0]
    minuto = random.randint(0, 59)
    delta = timedelta(days=dia, hours=hora, minutes=minuto)
    return now - delta


def perfil_aluno():
    """Retorna um perfil com habilidade base e consistência para simular variação natural."""
    habilidade = random.gauss(0.65, 0.18)   # média 65%, desvio alto
    habilidade = max(0.1, min(0.98, habilidade))
    consistencia = random.uniform(0.5, 1.0)  # quão consistente é o aluno
    velocidade = random.gauss(55, 25)        # tempo base em segundos
    velocidade = max(10, min(180, velocidade))
    return {"habilidade": habilidade, "consistencia": consistencia, "velocidade": velocidade}


def calcular_sessao(perfil, dificuldade, jogo_id):
    """Gera acertos/erros/tempo baseados no perfil do aluno e dificuldade."""
    multiplicador_dific = {"facil": 1.2, "medio": 1.0, "dificil": 0.65}
    taxa_base = perfil["habilidade"] * multiplicador_dific[dificuldade]
    # Adiciona ruído por sessão (dia ruim, dia bom)
    variacao = random.gauss(0, 0.12 * (1 - perfil["consistencia"] + 0.1))
    taxa = max(0.0, min(1.0, taxa_base + variacao))

    total_tentativas = random.randint(5, 15)
    acertos = round(total_tentativas * taxa)
    erros = total_tentativas - acertos

    # Tempo inversamente proporcional à habilidade, com ruído
    tempo = perfil["velocidade"] * multiplicador_dific[dificuldade] ** -0.5
    tempo += random.gauss(0, 10)
    tempo = round(max(5.0, min(300.0, tempo)), 2)

    return acertos, erros, tempo


def main():
    db = SessionLocal()

    # --- Turmas ---
    for ano in anos:
        for turma in turmas:
            if not db.query(TurmasModel).filter_by(ano=ano, turma=turma).first():
                db.add(TurmasModel(ano=ano, turma=turma))
    db.commit()
    turma_objs = db.query(TurmasModel).all()
    turma_ids = [t.id for t in turma_objs]

    # --- Jogos ---
    for nome in jogos:
        if not db.query(JogosModel).filter_by(nome=nome).first():
            db.add(JogosModel(nome=nome))
    db.commit()
    jogo_ids = [j.id for j in db.query(JogosModel).all()]

    # --- Alunos com perfil individual ---
    alunos_data = []  # (ra, perfil, turma_id)
    for i in range(150):
        sexo = random.choice(["M", "F"])
        nome_proprio = random.choice(nomes_masculinos if sexo == "M" else nomes_femininos)
        nome = f"{nome_proprio} {random.choice(sobrenomes)}"
        ra = f"2025{i:04d}"
        turma_id = random.choice(turma_ids)
        perfil = perfil_aluno()

        aluno = db.query(AlunosModel).filter_by(ra=ra).first()
        if not aluno:
            db.add(AlunosModel(nome=nome, ra=ra, turma_id=turma_id))
        alunos_data.append((ra, perfil, turma_id))
    db.commit()

    # --- Sessões com comportamento realista ---
    sessoes = []

    # Alguns alunos são mais ativos (mais sessões)
    pesos_atividade = [random.paretovariate(2) for _ in alunos_data]
    total_peso = sum(pesos_atividade)
    pesos_norm = [p / total_peso for p in pesos_atividade]

    for _ in range(8000):
        # Escolhe aluno com peso (simula alunos mais e menos ativos)
        idx = random.choices(range(len(alunos_data)), weights=pesos_norm, k=1)[0]
        ra, perfil, turma_id = alunos_data[idx]

        jogo_id = random.choice(jogo_ids)
        dificuldade = random.choices(
            dificuldades,
            weights=[0.4, 0.4, 0.2],  # facil e medio mais comuns
            k=1
        )[0]
        palavra = random.choice(palavras_por_dificuldade[dificuldade])
        acertos, erros, tempo = calcular_sessao(perfil, dificuldade, jogo_id)

        sessoes.append(SessoesModel(
            turma_id=turma_id,
            jogo_id=jogo_id,
            aluno_ra=ra,
            palavra=palavra,
            dificuldade=dificuldade,
            tempo_total=tempo,
            acertos=acertos,
            erros=erros,
            data_execucao=random_datetime_last_days(),
        ))

    db.bulk_save_objects(sessoes)
    db.commit()
    db.close()
    print("Banco populado com sucesso.")


if __name__ == "__main__":
    main()
