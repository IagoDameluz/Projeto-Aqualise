import os

ARQUIVO = "dados.txt"
MEDIA_BR = 5.8  # m3 por pessoa, por mes (referencia SNIS 2023)

MESES = (
    "Janeiro", "Fevereiro", "Marco", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
)

# lista de dicionarios: cada item guarda "mes", "consumo" e "custo"
registros = []


# ---------------- carregar e salvar no arquivo ----------------

def carregar():
    registros.clear()
    if os.path.exists(ARQUIVO):
        arquivo = open(ARQUIVO, "r", encoding="utf-8")
        for linha in arquivo:                      # le linha por linha
            partes = linha.strip().split(";")
            if len(partes) == 3:
                mes = partes[0]
                consumo = float(partes[1])
                custo = float(partes[2])
                registros.append({"mes": mes, "consumo": consumo, "custo": custo})
        arquivo.close()


def salvar(mes, consumo, custo):
    arquivo = open(ARQUIVO, "a", encoding="utf-8")
    linha = mes + ";" + str(round(consumo, 2)) + ";" + str(round(custo, 2)) + "\n"
    arquivo.write(linha)
    arquivo.close()


def somar(lista, chave, i=0):
    """Soma os valores de uma chave da lista de dicionarios, chamando a si mesma."""
    if i == len(lista):          # caso base: chegou ao fim da lista
        return 0
    return lista[i][chave] + somar(lista, chave, i + 1)


# ---------------- opcao 1: registrar consumo ----------------

def registrar_consumo(mes, consumo, custo):
    """
    Recebe os dados ja capturados pelo formulario web e aplica as
    mesmas regras de validacao.
    """
    mes = mes.strip().capitalize()

    if mes not in MESES:
        return {"ok": False, "mensagem": "Mes invalido. Digite um mes completo, ex: Maio."}

    for r in registros:                  # repeticao: procura duplicata
        if r["mes"] == mes:
            return {"ok": False, "mensagem": mes + " ja foi registrado!"}

    consumo = float(consumo)
    custo = float(custo)

    if consumo < 0 or custo < 0:
        return {"ok": False, "mensagem": "Valores nao podem ser negativos."}

    registros.append({"mes": mes, "consumo": consumo, "custo": custo})
    salvar(mes, consumo, custo)
    return {"ok": True, "mensagem": "Dado salvo com sucesso!"}


# ---------------- opcao 2: ver historico ----------------

def ver_historico():
    """Retorna a lista de registros (com preco por m3 calculado) e os totais."""
    if len(registros) == 0:
        return None

    linhas = []
    for r in registros:                  # repeticao: monta cada linha
        preco_m3 = r["custo"] / r["consumo"]
        linhas.append({
            "mes": r["mes"],
            "consumo": r["consumo"],
            "custo": r["custo"],
            "preco_m3": round(preco_m3, 2)
        })

    total_consumo = somar(registros, "consumo")
    total_custo = somar(registros, "custo")
    media = total_consumo / len(registros)

    return {
        "linhas": linhas,
        "total_consumo": round(total_consumo, 2),
        "total_custo": round(total_custo, 2),
        "media": round(media, 2)
    }


# ---------------- opcao 3: comparar com a media BR ----------------

def comparar_media(pessoas):
    if len(registros) == 0:
        return None

    pessoas = int(pessoas)
    total_consumo = somar(registros, "consumo")
    media_casa = total_consumo / len(registros)
    media_br = MEDIA_BR * pessoas

    resultado = {
        "pessoas": pessoas,
        "media_casa": round(media_casa, 2),
        "media_br": round(media_br, 2),
        "percentual": round((media_casa / media_br) * 100, 1) if media_br > 0 else 0,
    }

    if media_casa > media_br:
        diferenca = ((media_casa - media_br) / media_br) * 100
        resultado["situacao"] = "acima"
        resultado["diferenca"] = round(diferenca, 1)
    elif media_casa < media_br:
        diferenca = ((media_br - media_casa) / media_br) * 100
        resultado["situacao"] = "abaixo"
        resultado["diferenca"] = round(diferenca, 1)
    else:
        resultado["situacao"] = "igual"
        resultado["diferenca"] = 0

    return resultado


# ---------------- opcao 4: calcular economia ----------------

def calcular_economia(meta):
    if len(registros) == 0:
        return None

    meta = float(meta)

    total_consumo = somar(registros, "consumo")
    total_custo = somar(registros, "custo")
    media_consumo = total_consumo / len(registros)
    preco_m3 = total_custo / total_consumo

    reducao = media_consumo * (meta / 100)
    economia_mes = reducao * preco_m3
    economia_ano = economia_mes * 12

    return {
        "meta": meta,
        "economia_mes": round(economia_mes, 2),
        "economia_ano": round(economia_ano, 2),
    }


# ---------------- opcao 5: gerar relatorio ----------------

def gerar_relatorio():
    if len(registros) == 0:
        return None

    total_consumo = somar(registros, "consumo")
    total_custo = somar(registros, "custo")
    media_consumo = total_consumo / len(registros)

    melhor = registros[0]
    pior = registros[0]
    for r in registros:                  # repeticao: procura o melhor e o pior mes
        if r["consumo"] < melhor["consumo"]:
            melhor = r
        if r["consumo"] > pior["consumo"]:
            pior = r

    return {
        "periodo_inicio": registros[0]["mes"],
        "periodo_fim": registros[len(registros) - 1]["mes"],
        "total_consumo": round(total_consumo, 2),
        "total_custo": round(total_custo, 2),
        "media_consumo": round(media_consumo, 2),
        "melhor_mes": melhor["mes"],
        "melhor_consumo": melhor["consumo"],
        "pior_mes": pior["mes"],
        "pior_consumo": pior["consumo"],
    }
