# https://github.com/glauberAFcruz/Compiladores-10-S

import json

def analisadorSintatico(tokens):
  # TODO: implementar essa funcao
  arvore = []
  erros = []
  _tokens = tokens["tokens"]     # lista de tokens
  is_abre_parenteses = False     # flag abre parenteses dos parametros de funcao
  is_definicao = False           # flag definicao da funcao
  is_variavel = False 			 # flag deteccao de variavel
  
  funcao_ramo = []               # lista ramo da funcao
  parametros_ramo = []           # lista ramo parametros-funcao
  parametro_item = []            # lista ramo cada parametro-item
  funcao_retorno = []            # lista ramo retorno-funcao
  funcao_corpo = []              # lista ramo funcao-corpo
  variavel = []				     # lista ramo variavel
  
  # loop tokens e indices dos tokens
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
        _tkn1 = _tokens[i-1]
        _tkn2 = _tokens[i-2]
        
        # padrao para identificar retorno de funcao
        if _tkn1["grupo"] == "reservado" and _tkn1["texto"] != "Funcao" and _tkn2["grupo"] == "dois-pontos":
            funcao_retorno.append({"tipo":"token","folha":_tkn2})
            funcao_retorno.append({"tipo":"regra","grupo":"tipo","ramo":_tkn1})
            funcao_ramo.append({"tipo":"regra","grupo":"funcao-retorno","ramo":funcao_retorno})
            funcao_retorno = []
        funcao_ramo.append({"tipo":"token","folha":tkn}) # atribuicao ::
        is_definicao = True
        continue
    
    # definicao do corpo da funcao
    if is_definicao:
        
        if texto == "}":
            funcao_corpo.append({"tipo":"token","folha":tkn}) # fecha-chaves }
            funcao_ramo.append({"tipo":"regra","grupo":"funcao-corpo","ramo":funcao_corpo})
            funcao_corpo = []
            is_variavel = False
            continue
        if texto == "{":
            funcao_corpo.append({"tipo":"token","folha":tkn}) # abre-chaves {
            continue

		# deteccao de variavel
        if grupo == "identificador" and _tokens[i+1]["grupo"] == "dois-pontos":
            is_variavel = True            
        if is_variavel:
			# adiciona folha na variavel
            if grupo in ("identificador","dois-pontos","atribuicao"):
                variavel.append({"tipo":"token","folha":tkn})
                continue
			# adiciona ramo regra na variavel
            if grupo == "reservado":
                variavel.append({"tipo":"regra","grupo":"tipo","ramo": tkn})
                continue

			# adiciona a variavel detectada no corpo da funcao
            variavel.append({"tipo":"regra","grupo":"expressao","ramo":tkn})
            funcao_corpo.append({"tipo":"regra","grupo":"variavel","ramo":variavel})
            variavel = []
            is_variavel = False
            continue
        
		# define o retorno da funcao
        if grupo == "reservado" and texto == "retorna":
            _retorno_ramo = []
            _retorno_ramo.append({'tipo':'token','folha':tkn})
            _retorno_ramo.append({'tipo':'regra','grupo':'expressao','ramo':[{'tipo':'token','folha':_tokens[i+1]}]})
            funcao_corpo.append({"tipo":"regra","grupo":"retorno","ramo":_retorno_ramo})

  # adiciona na arvore a ultima funcao encontrada
  arvore.append({"tipo":"regra","grupo":"funcao","ramo":funcao_ramo})
  
  # define o grupo programa da arvore
  arvore = [{"tipo":"regra", "grupo":"programa", "ramo":arvore}]
  return {"arvore":arvore,"erros":erros}

# ALERTA: Nao modificar o codigo fonte apos esse aviso

def testaAnalisadorSintatico(tokens, teste):
  # Caso o resultado nao seja igual ao teste
  # ambos sao mostrados e a execucao termina  
  resultado = json.dumps(analisadorSintatico(tokens), indent=2)
  teste = json.dumps(teste, indent=2)
  if resultado != teste:
    # Mostra o teste e o resultado lado a lado  
    resultadoLinhas = resultado.split('\n')
    testeLinhas = teste.split('\n')
    if len(resultadoLinhas) > len(testeLinhas):
      testeLinhas.extend(
        [' '] * (len(resultadoLinhas)-len(testeLinhas))
      )
    elif len(resultadoLinhas) < len(testeLinhas):
      resultadoLinhas.extend(
        [' '] * (len(testeLinhas)-len(resultadoLinhas))
      )
    linhasEmPares = enumerate(zip(testeLinhas, resultadoLinhas))
    maiorTextoNaLista = str(len(max(testeLinhas, key=len)))
    maiorIndice = str(len(str(len(testeLinhas))))
    titule = '{:<'+maiorIndice+'} + {:<'+maiorTextoNaLista+'} + {}'
    objeto = '{:<'+maiorIndice+'} | {:<'+maiorTextoNaLista+'} | {}'
    print(titule.format('', 'teste', 'resultado'))
    print(objeto.format('', '', ''))
    for indice, (esquerda, direita) in linhasEmPares:
      print(objeto.format(indice, esquerda, direita))
    # Termina a execucao
    print ("\n): falha :(")
    quit()

# Tokens que passados para a funcao analisadorSintatico
tokens = {
  "tokens":[
    # Comentario    
    {
      "grupo":"comentario", "texto": "-- funcao inicial", 
      "local":{"linha":1,"indice":0}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":1,"indice":17}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":2,"indice":0}
    },
    # Funcao inicio
    {
      "grupo":"identificador", "texto": "inicio", 
      "local":{"linha":3,"indice":0}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":6}
    },
    {
      "grupo":"reservado", "texto": "Funcao", 
      "local":{"linha":3,"indice":7}
    },
    {
      "grupo":"abre-parenteses", "texto": "(", 
      "local":{"linha":3,"indice":13}
    },
    {
      "grupo":"identificador", "texto": "valor", 
      "local":{"linha":3,"indice":14}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":19}
    },
    {
      "grupo":"reservado", "texto": "Logica", 
      "local":{"linha":3,"indice":20}
    },
    {
      "grupo":"virgula", "texto": ",", 
      "local":{"linha":3,"indice":26}
    },
    {
      "grupo":"identificador", "texto": "item", 
      "local":{"linha":3,"indice":27}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":31}
    },
    {
      "grupo":"reservado", "texto": "Texto", 
      "local":{"linha":3,"indice":32}
    },
    {
      "grupo":"fecha-parenteses", "texto": ")", 
      "local":{"linha":3,"indice":37}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":3,"indice":38}
    },
    {
      "grupo":"reservado", "texto": "Numero", 
      "local":{"linha":3,"indice":39}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":3,"indice":45}
    },
    {
      "grupo":"abre-chaves", "texto": "{", 
      "local":{"linha":3,"indice":47}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":3,"indice":48}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":4,"indice":0}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":4,"indice":1}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":5,"indice":0}
    },
    # Funcao tiposDeVariaveis
    {
      "grupo":"identificador", "texto": "tiposDeVariaveis", 
      "local":{"linha":6,"indice":0}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":6,"indice":16}
    },
    {
      "grupo":"reservado", "texto": "Funcao", 
      "local":{"linha":6,"indice":17}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":6,"indice":23}
    },
    {
      "grupo":"abre-chaves", "texto": "{", 
      "local":{"linha":6,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":6,"indice":26}
    },
    # textoVar:Texto::'#'exemplo##'
    {
      "grupo":"identificador", "texto": "textoVar", 
      "local":{"linha":7,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":7,"indice":10}
    },
    {
      "grupo":"reservado", "texto": "Texto", 
      "local":{"linha":7,"indice":11}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":7,"indice":16}
    },
    {
      "grupo":"texto", "texto": "'#'exemplo##'", 
      "local":{"linha":7,"indice":18}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":7,"indice":31}
    },
    # numeroVar:Numero::1234
    {
      "grupo":"identificador", "texto": "numeroVar", 
      "local":{"linha":8,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":8,"indice":11}
    },
    {
      "grupo":"reservado", "texto": "Numero", 
      "local":{"linha":8,"indice":12}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":8,"indice":18}
    },
    {
      "grupo":"numero", "texto": "1234", 
      "local":{"linha":8,"indice":20}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":8,"indice":24}
    },
    # logicoVar:Logico::Sim
    {
      "grupo":"identificador", "texto": "logicoVar", 
      "local":{"linha":9,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":9,"indice":11}
    },
    {
      "grupo":"reservado", "texto": "Logico", 
      "local":{"linha":9,"indice":12}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":9,"indice":18}
    },
    {
      "grupo":"logico", "texto": "Sim", 
      "local":{"linha":9,"indice":20}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":9,"indice":23}
    },
    # Fecha Funcao
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":10,"indice":0}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":10,"indice":1}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":11,"indice":0}
    },
    # Funcao tiposDeFluxoDeControle
    {
      "grupo":"identificador", "texto": "tiposDeFluxoDeControle", 
      "local":{"linha":12,"indice":0}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":12,"indice":22}
    },
    {
      "grupo":"reservado", "texto": "Funcao", 
      "local":{"linha":12,"indice":23}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":12,"indice":29}
    },
    {
      "grupo":"reservado", "texto": "Logico", 
      "local":{"linha":12,"indice":30}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":12,"indice":36}
    },
    {
      "grupo":"abre-chaves", "texto": "{", 
      "local":{"linha":12,"indice":38}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":12,"indice":39}
    },
    # resultado:Logico::Nao
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":13,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":13,"indice":11}
    },
    {
      "grupo":"reservado", "texto": "Logico", 
      "local":{"linha":13,"indice":12}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":13,"indice":18}
    },
    {
      "grupo":"logico", "texto": "Nao", 
      "local":{"linha":13,"indice":20}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":13,"indice":23}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":14,"indice":0}
    },
    # contador:Numero::0
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":23,"indice":2}
    },
    {
      "grupo":"dois-pontos", "texto": ":", 
      "local":{"linha":23,"indice":10}
    },
    {
      "grupo":"reservado", "texto": "Numero", 
      "local":{"linha":23,"indice":11}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":23,"indice":17}
    },
    {
      "grupo":"numero", "texto": "0", 
      "local":{"linha":23,"indice":19}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":23,"indice":20}
    },
    # enquanto(contador < 10){
    {
      "grupo":"reservado", "texto": "enquanto", 
      "local":{"linha":24,"indice":2}
    },
    {
      "grupo":"abre-parenteses", "texto": "(", 
      "local":{"linha":24,"indice":10}
    },
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":24,"indice":11}
    },
    {
      "grupo":"operador-menor", "texto": "<", 
      "local":{"linha":24,"indice":20}
    },
    {
      "grupo":"numero", "texto": "10", 
      "local":{"linha":24,"indice":22}
    },
    {
      "grupo":"fecha-parenteses", "texto": ")", 
      "local":{"linha":24,"indice":24}
    },
    {
      "grupo":"abre-chaves", "texto": "{",
      "local":{"linha":24,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":24,"indice":26}
    },
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":25,"indice":4}
    },
    {
      "grupo":"atribuicao", "texto": "::", 
      "local":{"linha":25,"indice":12}
    },
    {
      "grupo":"identificador", "texto": "contador", 
      "local":{"linha":25,"indice":14}
    },
    {
      "grupo":"operador-mais", "texto": "+", 
      "local":{"linha":25,"indice":23}
    },
    {
      "grupo":"texto", "texto": "'a'", 
      "local":{"linha":25,"indice":25}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":25,"indice":28}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":26,"indice":2}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":26,"indice":3}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":27,"indice":0}
    },
    # Fecha Funcao
    {
      "grupo":"reservado", "texto": "retorna", 
      "local":{"linha":28,"indice":2}
    },    
    {
      "grupo":"identificador", "texto": "resultado", 
      "local":{"linha":28,"indice":10}
    },
    {
      "grupo":"quebra-linha", "texto": "\n", 
      "local":{"linha":28,"indice":19}
    },
    {
      "grupo":"fecha-chaves", "texto": "}", 
      "local":{"linha":29,"indice":0}
    }
  ], "erros":[ ]
} 

# Resultado esperado da execucao da funcao analisadorSintatico
teste = {
  "arvore":[
    {
      "tipo":"regra",
      "grupo":"programa",
      "ramo":[
        {
          "tipo":"regra",
          "grupo":"funcao",
          "ramo":[
            {
              "tipo":"token",
              "folha":{
                "grupo":"identificador", "texto": "inicio", 
                "local":{"linha":3,"indice":0}
              }
            },
            {
              "tipo":"token",
              "folha":{
                "grupo":"dois-pontos", "texto": ":", 
                "local":{"linha":3,"indice":6}
              }
            },
            {
              "tipo":"regra",
              "grupo":"tipo-funcao",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"reservado", "texto": "Funcao", 
                    "local":{"linha":3,"indice":7}
                  }
                }
              ]
            },
            {
              "tipo":"regra",
              "grupo":"funcao-parametros",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"abre-parenteses", "texto": "(", 
                    "local":{"linha":3,"indice":13}
                  }
                },
                {
                  "tipo":"regra",
                  "grupo":"parametro-item",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "valor", 
                        "local":{"linha":3,"indice":14}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":3,"indice":19}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Logica", 
                            "local":{"linha":3,"indice":20}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"virgula", "texto": ",", 
                    "local":{"linha":3,"indice":26}
                  }
                },
                {
                  "tipo":"regra",
                  "grupo":"parametro-item",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "item", 
                        "local":{"linha":3,"indice":27}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":3,"indice":31}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Texto", 
                            "local":{"linha":3,"indice":32}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"fecha-parenteses", "texto": ")", 
                    "local":{"linha":3,"indice":37}
                  }
                }
              ]
            },
            {
              "tipo":"regra",
              "grupo":"funcao-retorno",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"dois-pontos", "texto": ":", 
                    "local":{"linha":3,"indice":38}
                  }
                },
                {
                  "tipo":"regra",
                  "grupo":"tipo",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"reservado", "texto": "Numero", 
                        "local":{"linha":3,"indice":39}
                      }
                    }
                  ]
                }
              ]
            },
            {
              "tipo":"token",
              "folha":{
                "grupo":"atribuicao", "texto": "::", 
                "local":{"linha":3,"indice":45}
              }
            },
            {
              "tipo":"regra",
              "grupo":"funcao-corpo",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"abre-chaves", "texto": "{", 
                    "local":{"linha":3,"indice":47}
                  }
                },
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"fecha-chaves", "texto": "}", 
                    "local":{"linha":4,"indice":0}
                  }
                }
              ]
            }
          ]        
        },
        {
          "tipo":"regra",
          "grupo":"funcao",
          "ramo":[
            {
              "tipo":"token",
              "folha":{
                "grupo":"identificador", "texto": "tiposDeVariaveis", 
                "local":{"linha":6,"indice":0}
              }
            },
            {
              "tipo":"token",
              "folha":{
                "grupo":"dois-pontos", "texto": ":", 
                "local":{"linha":6,"indice":16}
              }
            },
            {
              "tipo":"regra",
              "grupo":"tipo-funcao",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"reservado", "texto": "Funcao", 
                    "local":{"linha":6,"indice":17}
                  }
                }
              ]
            },
            {
              "tipo":"token",
              "folha":{
                "grupo":"atribuicao", "texto": "::", 
                "local":{"linha":6,"indice":23}
              }
            },
            {
              "tipo":"regra",
              "grupo":"funcao-corpo",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"abre-chaves", "texto": "{", 
                    "local":{"linha":6,"indice":25}
                  }
                },
                {
                  "tipo":"regra",
                  "grupo":"variavel",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "textoVar", 
                        "local":{"linha":7,"indice":2}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":7,"indice":10}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Texto", 
                            "local":{"linha":7,"indice":11}
                          }
                        }
                      ]
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"atribuicao", "texto": "::", 
                        "local":{"linha":7,"indice":16}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"expressao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"texto", "texto": "'#'exemplo##'", 
                            "local":{"linha":7,"indice":18}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"regra",
                  "grupo":"variavel",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "numeroVar", 
                        "local":{"linha":8,"indice":2}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":8,"indice":11}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Numero", 
                            "local":{"linha":8,"indice":12}
                          }
                        }
                      ]
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"atribuicao", "texto": "::", 
                        "local":{"linha":8,"indice":18}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"expressao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"numero", "texto": "1234", 
                            "local":{"linha":8,"indice":20}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"regra",
                  "grupo":"variavel",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "logicoVar", 
                        "local":{"linha":9,"indice":2}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":9,"indice":11}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Logico", 
                            "local":{"linha":9,"indice":12}
                          }
                        }
                      ]
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"atribuicao", "texto": "::", 
                        "local":{"linha":9,"indice":18}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"expressao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"logico", "texto": "Sim", 
                            "local":{"linha":9,"indice":20}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"fecha-chaves", "texto": "}", 
                    "local":{"linha":10,"indice":0}
                  }
                }
              ]
            }
          ]
        },
        {
          "tipo":"regra",
          "grupo":"funcao",
          "ramo":[
            {
              "tipo":"token",
              "folha":{
                "grupo":"identificador", "texto": "tiposDeFluxoDeControle", 
                "local":{"linha":12,"indice":0}
              }
            },
            {
              "tipo":"token",
              "folha":{
                "grupo":"dois-pontos", "texto": ":", 
                "local":{"linha":12,"indice":22}
              }
            },
            {
              "tipo":"regra",
              "grupo":"tipo-funcao",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"reservado", "texto": "Funcao", 
                    "local":{"linha":12,"indice":23}
                  }
                }
              ]
            },
            {
              "tipo":"regra",
              "grupo":"funcao-retorno",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"dois-pontos", "texto": ":", 
                    "local":{"linha":12,"indice":29}
                  }
                },
                {
                  "tipo":"regra",
                  "grupo":"tipo",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"reservado", "texto": "Logico", 
                        "local":{"linha":12,"indice":30}
                      }
                    }
                  ]
                }
              ]
            },
            {
              "tipo":"token",
              "folha":{
                "grupo":"atribuicao", "texto": "::", 
                "local":{"linha":12,"indice":36}
              }
            },
            {
              "tipo":"regra",
              "grupo":"funcao-corpo",
              "ramo":[
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"abre-chaves", "texto": "{", 
                    "local":{"linha":12,"indice":38}
                  }
                },
                {
                  "tipo":"regra",
                  "grupo":"variavel",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "resultado", 
                        "local":{"linha":13,"indice":2}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":13,"indice":11}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Logico", 
                            "local":{"linha":13,"indice":12}
                          }
                        }
                      ]
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"atribuicao", "texto": "::", 
                        "local":{"linha":13,"indice":18}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"expressao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"logico", "texto": "Nao", 
                            "local":{"linha":13,"indice":20}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"regra",
                  "grupo":"variavel",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"identificador", "texto": "contador", 
                        "local":{"linha":23,"indice":2}
                      }
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"dois-pontos", "texto": ":", 
                        "local":{"linha":23,"indice":10}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"tipo",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"reservado", "texto": "Numero", 
                            "local":{"linha":23,"indice":11}
                          }
                        }
                      ]
                    },
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"atribuicao", "texto": "::", 
                        "local":{"linha":23,"indice":17}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"expressao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"numero", "texto": "0", 
                            "local":{"linha":23,"indice":19}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"regra",
                  "grupo":"repeticao",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"reservado", "texto": "enquanto", 
                        "local":{"linha":24,"indice":2}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"condicao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"abre-parenteses", "texto": "(", 
                            "local":{"linha":24,"indice":10}
                          }
                        },
                        {
                          "tipo":"regra",
                          "grupo":"expressao",
                          "ramo":[
                            {
                              "tipo":"token",
                              "folha":{
                                "grupo":"identificador", "texto": "contador", 
                                "local":{"linha":24,"indice":11}
                              }
                            }
                          ]
                        },
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"operador-menor", "texto": "<", 
                            "local":{"linha":24,"indice":20}
                          }
                        },
                        {
                          "tipo":"regra",
                          "grupo":"expressao",
                          "ramo":[
                            {
                              "tipo":"token",
                              "folha":{
                                "grupo":"numero", "texto": "10", 
                                "local":{"linha":24,"indice":22}
                              }
                            }
                          ]
                        },
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"fecha-parenteses", "texto": ")", 
                            "local":{"linha":24,"indice":24}
                          }
                        }
                      ]
                    },
                    {
                      "tipo":"regra",
                      "grupo":"repeticao-corpo",
                      "ramo":[
                        {
                          "tipo":"regra",
                          "grupo":"atribuicao",
                          "ramo":[
                            {
                              "tipo":"token",
                              "folha":{
                                "grupo":"identificador", "texto": "contador", 
                                "local":{"linha":25,"indice":4}
                              }
                            },
                            {
                              "tipo":"token",
                              "folha":{
                                "grupo":"atribuicao", "texto": "::", 
                                "local":{"linha":25,"indice":12}
                              }
                            },
                            {
                              "tipo":"regra",
                              "grupo":"expressao",
                              "ramo":[
                                {
                                  "tipo":"token",
                                  "folha":{
                                    "grupo":"identificador", "texto": "contador", 
                                    "local":{"linha":25,"indice":14}
                                  }
                                },
                                {
                                  "tipo":"token",
                                  "folha":{
                                    "grupo":"operador-mais", "texto": "+", 
                                    "local":{"linha":25,"indice":23}
                                  }
                                },
                                {
                                  "tipo":"token",
                                  "folha":{
                                    "grupo":"texto", "texto": "'a'", 
                                    "local":{"linha":25,"indice":25}
                                  }
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"regra",
                  "grupo":"retorno",
                  "ramo":[
                    {
                      "tipo":"token",
                      "folha":{
                        "grupo":"reservado", "texto": "retorna", 
                        "local":{"linha":28,"indice":2}
                      }
                    },
                    {
                      "tipo":"regra",
                      "grupo":"expressao",
                      "ramo":[
                        {
                          "tipo":"token",
                          "folha":{
                            "grupo":"identificador", "texto": "resultado", 
                            "local":{"linha":28,"indice":10}
                          }
                        }
                      ]
                    }
                  ]
                },
                {
                  "tipo":"token",
                  "folha":{
                    "grupo":"fecha-chaves", "texto": "}", 
                    "local":{"linha":29,"indice":0}
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "erros":[]
}

# Execucao do teste que valida a funcao testaAnalisadorSintatico
testaAnalisadorSintatico(tokens, teste)

print("(: sucesso :)")