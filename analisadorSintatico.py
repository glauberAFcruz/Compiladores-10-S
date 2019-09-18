import json

def analisadorSintatico(tokens):
  # TODO: implementar essa funcao
  arvore = []
  erros = []
  _tokens = tokens["tokens"]     # lista de tokens
  is_abre_parenteses = False     # flag abre parenteses dos parametros de funcao
  is_definicao = False           # flag definicao da funcao
  
  funcao_ramo = []               # lista ramo da funcao
  parametros_ramo = []           # lista ramo parametros-funcao
  parametro_item = []            # lista ramo cada parametro-item
  funcao_retorno = []            # lista ramo retorno-funcao
  funcao_corpo = []              # lista ramo funcao-corpo
  
  for tkn, i in zip(_tokens, range(len(_tokens))):
    grupo = tkn["grupo"]
    texto = tkn["texto"]
    local = tkn["local"]
    if grupo in ('quebra-linha', 'comentario'): # ignora comentario e quebra de linha
        continue
    
    # identificar funcoes
    if grupo == "identificador":
        if _tokens[i+1]["grupo"] == "dois-pontos":
            if _tokens[i+2]["grupo"] == "reservado":
                if _tokens[i+2]["texto"] == "Funcao":
                    if len(funcao_ramo) > 0:
                        # adiciona a funcao construida na ultima iteracao
                        arvore.append({"tipo":"regra","grupo":"funcao","ramo":funcao_ramo})
                        funcao_ramo = []
                    funcao_ramo.append({"tipo":"token","folha":tkn})                 # identificador
                    funcao_ramo.append({"tipo":"token","folha":_tokens[i+1]})        # dois pontos
                    funcao_ramo.append({"tipo":"regra","tipo-funcao":_tokens[i+2]})  # Funcao
                    is_definicao = False
                    
    # identificar parametros da funcao
    if texto == "(" and not is_definicao:
        is_abre_parenteses = True
        parametros_ramo.append({"tipo":"token","folha":tkn}) # abre parenteses (
        continue
     
    # finalizacao dos parametos identificados
    if texto == ")" and not is_definicao:
        is_abre_parenteses = False
        if len(parametro_item) > 0:
            # adiciona item encontrado
            parametros_ramo.append({"tipo":"regra","grupo":"parametro-item","ramo":parametro_item})
            parametro_item = []
        parametros_ramo.append({"tipo":"token","folha":tkn}) # fecha parenteses )
        funcao_ramo.append({"tipo":"regra","grupo":"funcao-parametros","ramo": parametros_ramo}) # parametro da funcao
        parametros_ramo = []
        continue
    
    # se identificou parametros
    if is_abre_parenteses:
        if grupo != "virgula":
            parametro_item.append({"tipo":"token","folha":tkn}) # virgula ,
            continue
        
        # se possuir item para adicionar no ramo de parametros
        if len(parametro_item) > 0:
            parametros_ramo.append({"tipo":"regra","grupo":"parametro-item","ramo":parametro_item})
            parametro_item = []
        parametros_ramo.append({"tipo":"token","folha":tkn})
        continue
    
    # padrao para identificar inicio do corpo de funcao
    if grupo == "atribuicao" and _tokens[i+1]["grupo"] == "abre-chaves":
        # ainda nao defini os padroes para identificar o corpo da funcao
        continue
    
    
  # adiciona na arvore a ultima funcao encontrada
  arvore.append({"tipo":"regra","grupo":"funcao","ramo":funcao_ramo})
  
  # define o grupo programa da arvore
  arvore = [{"tipo":"regra", "grupo":"programa", "ramo":arvore}]
  return {"arvore":arvore,"erros":erros}
analisadorSintatico(tokens)
