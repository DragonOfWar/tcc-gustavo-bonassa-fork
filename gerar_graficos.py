import matplotlib.pyplot as plt
import scikit_posthocs as sp
import numpy as np
import csv
import os
from scipy import stats

# Config
QNT_ITERACOES = 5
CLASSIFICADORES = ["axgb", "incremental", "hat", "arf"]
DATASETS = ["agr_a", "agr_g", "airlines", "elec", "hyper_f", "sea_a", "sea_g"]

# Diretorios
def criar_dir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


CAMINHO_RESULTADOS_RAW = "resultados_raw"
CAMINHO_RESULTADOS = "resultados"
CAMINHO_FIGURAS_ACURACIAS = "graficos_acuracias"
CAMINHO_FIGURAS_KAPPA = "graficos_kappa"
CAMINHO_FIGURAS_FN = "graficos_fn"
criar_dir(CAMINHO_FIGURAS_ACURACIAS)
criar_dir(CAMINHO_FIGURAS_KAPPA)
criar_dir(CAMINHO_FIGURAS_FN)


# Gerar graficos das acuracias
def gerar_graficos(coluna, dir, nome):
    for d in DATASETS:
        for i in range(1, QNT_ITERACOES + 1):
            print(f"Gerando gráfico de {nome}: processando {d} iteração {i}", end="\r")
            ys = {c: [] for c in CLASSIFICADORES}
            xs = []
            xs_pronto = False
            for c in CLASSIFICADORES:
                with open(
                    f"{CAMINHO_RESULTADOS_RAW}/resultados_{c}_{d}_{i}.csv", "r"
                ) as csvfile:
                    csvr = csv.reader(
                        # Preprocessar o csv pra remover os comentarios
                        filter(lambda l: l[0] != "#", csvfile),
                        delimiter=",",
                    )
                    next(csvr)  # ignorar primeira linha (cabeçalho)
                    for l in csvr:
                        if not xs_pronto:
                            xs.append(int(l[0]))
                        ys[c].append(float(l[coluna]))
                xs_pronto = True
            for c, y in ys.items():
                plt.plot(xs, y, label=c)
            plt.xlabel("amostras")
            plt.ylabel(nome)
            plt.legend()
            plt.grid()
            plt.savefig(f"{dir}/{d}_{i}.png")
            plt.clf()


gerar_graficos(2, CAMINHO_FIGURAS_ACURACIAS, "acuracia")
gerar_graficos(4, CAMINHO_FIGURAS_KAPPA, "kappa")

# Executar teste de friedman-nemenyi nas acuracias
# tempos = {c: [] for c in CLASSIFICADORES}

COLUNA_ACURACIA = 2
COLUNA_KAPPA = 4
COLUNA_TEMPO = 5

# Ler resultados
for d in DATASETS:
    acuracias = {c: [] for c in CLASSIFICADORES}
    kappas = {c: [] for c in CLASSIFICADORES}
    for c in CLASSIFICADORES:
        for i in range(1, QNT_ITERACOES + 1):
            with open(
                f"{CAMINHO_RESULTADOS_RAW}/resultados_{c}_{d}_{i}.csv"
            ) as csvfile:
                csvr = csv.reader(
                    # Preprocessar o csv pra remover os comentarios
                    filter(lambda l: l[0] != "#", csvfile),
                    delimiter=",",
                )
                next(csvr)  # Descartar primeira linha (cabeçalho)
                for l in csvr:
                    acuracias[c].append(l[COLUNA_ACURACIA])
                    kappas[c].append(l[COLUNA_KAPPA])
                    # tempos[c].append(l[COLUNA_TEMPO])

    data_a = np.array(list(acuracias.values()))
    data_k = np.array(list(kappas.values()))

    print(sp.posthoc_nemenyi_friedman(data_a.T))
    print(sp.posthoc_nemenyi_friedman(data_k.T))
