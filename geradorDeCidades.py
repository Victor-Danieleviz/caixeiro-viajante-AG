import random

#parametros que podem ser alterados
LIMITE = 1000 #distancia maxima da posicao x e y
QUANTIDADE = 80 #quantidade de cidades a serem geradas

def gerar_cidades(quantidade=QUANTIDADE, limite=LIMITE, nome_arquivo='cidades.txt'):
    with open(nome_arquivo, 'w') as f:
        for cidade_id in range(1, quantidade + 1):
            x = random.randint(1, limite)
            y = random.randint(1, limite)
            f.write(f"{cidade_id} {x} {y}\n")

    print(f"{quantidade} cidades salvas em '{nome_arquivo}'.")

gerar_cidades()














