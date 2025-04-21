import random
import math
import unicodedata
import csv
from itertools import product

class Individuo:
    def __init__(self, id, rota):
        self.distancia_total = None
        self.id = id
        self.gene = rota

    def percorrer_caminho(self, caminho, mundo):
        self.gene = caminho
        ultima_posicao = 0
        distancia_percorrida = 0
        for i in range(len(caminho)):
            distancia_percorrida += mundo[ultima_posicao][caminho[i]]
            ultima_posicao = caminho[i]
        distancia_percorrida += mundo[ultima_posicao][0]
        self.distancia_total = distancia_percorrida

class Geracao:
    def __init__(self, lista_individuos, num_geracao):
        self.lista_individuos = lista_individuos
        self.num_geracao = num_geracao

    def ranking_fitness(self):
        self.lista_individuos.sort(key=lambda ind: ind.distancia_total)

    def crossover(self, taxa_mutacao, matriz_distancias, elitismo=False):
        nova_geracao = []
        if elitismo:
            melhor_individuo = self.lista_individuos[0]
            nova_geracao.append(melhor_individuo.gene)
        pais = self.lista_individuos[:2]
        while len(nova_geracao) < len(self.lista_individuos):
            pai1 = random.choice(pais).gene
            pai2 = random.choice(pais).gene
            corte1 = random.randint(1, len(pai1) - 2)
            corte2 = random.randint(corte1 + 1, len(pai1) - 1)
            filho_parcial = pai1[corte1:corte2]
            restante = [cidade for cidade in pai2 if cidade not in filho_parcial and cidade != 0]
            filho = [0] + filho_parcial + restante
            if random.random() < taxa_mutacao:
                i, j = random.sample(range(1, len(filho)), 2)
                filho[i], filho[j] = filho[j], filho[i]
            nova_geracao.append(filho)
        return nova_geracao

def ler_cidades(nome_arquivo='cidades_80.txt'):
    cidades = []
    with open(nome_arquivo, 'r') as f:
        for linha in f:
            partes = linha.strip().split()
            if len(partes) == 3:
                cidade_id = int(partes[0]) - 1
                x = int(partes[1])
                y = int(partes[2])
                cidades.append((x, y))
    return cidades

def calcular_matriz_distancias(cidades):
    n = len(cidades)
    matriz = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                xi, yi = cidades[i]
                xj, yj = cidades[j]
                matriz[i][j] = math.hypot(xi - xj, yi - yj)
    return matriz

def gerar_caminho_aleatorio(cidades):
    caminho = list(range(1, len(cidades)))
    random.shuffle(caminho)
    return [0] + caminho

def registrar_parametros(f, geracoes, individuos, taxa_mutacao, elitismo):
    f.write(f"Numero de geracoes: {geracoes}\n")
    f.write(f"Numero de individuos: {individuos}\n")
    f.write(f"Taxa de mutacao: {taxa_mutacao}\n")
    f.write(f"Elitismo: {elitismo}\n")
    f.write("="*50 + "\n\n")

def executar_algoritmo(geracoes, individuos, taxa_mutacao, elitismo):
    cidades = ler_cidades()
    matriz_distancias = calcular_matriz_distancias(cidades)
    geracao_inicial = []
    for i in range(individuos):
        rota = gerar_caminho_aleatorio(cidades)
        individuo = Individuo(i, rota)
        individuo.percorrer_caminho(rota, matriz_distancias)
        geracao_inicial.append(individuo)
    geracao_anterior = Geracao(geracao_inicial, 0)
    geracao_anterior.ranking_fitness()
    filhos = geracao_anterior.crossover(taxa_mutacao, matriz_distancias, elitismo)
    melhor_distancia = float('inf')
    melhor_geracao = -1
    distancias = []
    geracoes_melhores = []
    for i in range(geracoes):
        nova_geracao = []
        for j in range(len(filhos)):
            individuo = Individuo(i * 100 + j, filhos[j])
            individuo.percorrer_caminho(filhos[j], matriz_distancias)
            nova_geracao.append(individuo)
        geracao_atual = Geracao(nova_geracao, i + 1)
        geracao_atual.ranking_fitness()
        filhos = geracao_atual.crossover(taxa_mutacao, matriz_distancias, elitismo)
        melhor_atual = geracao_atual.lista_individuos[0]
        if melhor_atual.distancia_total < melhor_distancia:
            melhor_distancia = melhor_atual.distancia_total
            melhor_geracao = i + 1
        distancias.append(melhor_distancia)
        geracoes_melhores.append(melhor_geracao)
    melhor_individuo = geracao_atual.lista_individuos[0]
    return melhor_individuo.gene, melhor_individuo.distancia_total, melhor_geracao, distancias, geracoes_melhores

if __name__ == '__main__':
    distancias_totais = []
    geracoes_totais = []
    individuos_list = [8, 16]
    mutacoes_list = [0.0, 0.05, 0.1, 0.2]
    elitismos_list = [False, True]
    combinacoes = list(product(individuos_list, mutacoes_list, elitismos_list))

    # Cria CSV
    with open('resultados.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['NomeArquivo', 'MediaMenoresDistancias', 'MenorDistancia', 'GeracaoMelhorIndividuo', 'MediaGeracoesMelhores'])

        for individuos, taxa_mutacao, elitismo in combinacoes:
            print(f"\nRodando para: {individuos} individuos | {taxa_mutacao} mutacao | elitismo={elitismo}")
            distancias_totais = []
            geracoes_totais = []
            nome_arquivo = f"resultados_m{taxa_mutacao}_i{individuos}_e{int(elitismo)}.txt"

            with open(nome_arquivo, 'w') as f:
                registrar_parametros(f, geracoes=1000, individuos=individuos, taxa_mutacao=taxa_mutacao, elitismo=elitismo)
                for i in range(100):
                    caminho, distancia, geracao, distancias, geracoes_melhores = executar_algoritmo(
                        geracoes=1000, individuos=individuos, taxa_mutacao=taxa_mutacao, elitismo=elitismo)
                    f.write(f"Execucao {i+1}:\n")
                    f.write(f"Caminho: {caminho + [caminho[0]]}\n")
                    f.write(f"Distancia: {round(distancia, 2)}\n")
                    f.write(f"Geracao do melhor individuo: {geracao}\n")
                    f.write("\n" + "="*50 + "\n")
                    distancias_totais.append((distancia, geracao))

                distancias_apenas = [d for d, _ in distancias_totais]
                geracoes_melhores = [g for _, g in distancias_totais]
                media_distancia = sum(distancias_apenas) / len(distancias_apenas)
                menor_distancia, geracao_melhor_distancia = min(distancias_totais, key=lambda x: x[0])
                media_geracoes = sum(geracoes_melhores) / len(geracoes_melhores)

                f.write("\nEstatisticas Finais:\n")
                f.write(f"Media das Menores Distancias: {round(media_distancia, 2)}\n")
                f.write(f"Menor Distancia: {round(menor_distancia, 2)}\n")
                f.write(f"Geracao do Melhor Individuo (Menor Distancia): {geracao_melhor_distancia}\n")
                f.write(f"Media das Geracoes onde encontrou os melhores individuos: {round(media_geracoes, 2)}\n")

                writer.writerow([
                    nome_arquivo,
                    round(media_distancia, 2),
                    round(menor_distancia, 2),
                    geracao_melhor_distancia,
                    round(media_geracoes, 2)
                ])

            print(f"✔ Finalizado e salvo: {nome_arquivo}")
