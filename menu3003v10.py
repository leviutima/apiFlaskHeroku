from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import oracledb

app = Flask(__name__)
CORS(app)  # Ativar o CORS para todos os domínios

def incluir_formulario_duvida(instrucao_sql, conn):
    try:
        desc = input("Digite a dúvida do cliente: ")
        seg_empresa = input("Digite o segmento da empresa do cliente: ")
        cliente_id = int(input("Digite o código do cliente: "))
        especialista_id = int(input("Digite o código do especialista: "))
    except ValueError:
        print("Insira o código do cliente e do especialista!")
    except Exception as e:
        print(f"Erro de transação com o banco de dados!: {e}")
    else:
        str_inserir_formularioduvida = f"""INSERT INTO TB_FORMULARIODUVIDAS (DESC_FORM,SEG_EMPRESA,FK_CLIENTE_ID_CLIE,FK_ESPECIALISTA_ID_ESPEC) VALUES ('{desc}','{seg_empresa}',{cliente_id},{especialista_id})"""
        instrucao_sql.execute(str_inserir_formularioduvida)
        conn.commit()
        print("Formulário de dúvida adicionado com sucesso!")
    finally:
        print("Operação finalizada!")

@app.route('/contatenos', methods=['POST'])
def incluir_cliente_formulario():
    novo_cliente_formulario = request.get_json()

    nome = novo_cliente_formulario['nm_clie']
    sobrenome = novo_cliente_formulario['sobrenome']
    email = novo_cliente_formulario['email']
    empresa = novo_cliente_formulario['empresa']
    tamanho_empresa = novo_cliente_formulario['tamanho_empresa']
    pais = novo_cliente_formulario['pais']
    cargo = novo_cliente_formulario['cargo']
    telefone = novo_cliente_formulario['telefone']
    desc = novo_cliente_formulario['desc_form']
    seg_empresa = novo_cliente_formulario['seg_empresa']

    conexao, instrucao_sql, conn = conectar_bancodedados()
    if not conexao:
        return "Erro ao conectar ao banco de dados", 500

    try:
        str_inserir_clientes = f"""INSERT INTO TB_CLIENTE (NM_CLIE,SOBRENOME,EMAIL,EMPRESA,TAMANHO_EMPRESA,PAIS,CARGO,TELEFONE) VALUES ('{nome}','{sobrenome}','{email}','{empresa}',{tamanho_empresa},'{pais}','{cargo}','{telefone}')"""
        instrucao_sql.execute(str_inserir_clientes)

        str_id_cliente = f"""SELECT * FROM (SELECT * FROM tb_cliente ORDER BY ROWID DESC) WHERE ROWNUM = 1"""
        cliente_oracle = instrucao_sql.execute(str_id_cliente).fetchall()

        if not cliente_oracle:
            raise Exception("Não foi possível recuperar o ID do cliente")

        id_clie = cliente_oracle[0][0]

        str_inserir_formularioduvida = f"""INSERT INTO TB_FORMULARIODUVIDAS (DESC_FORM,SEG_EMPRESA,FK_CLIENTE_ID_CLIE,FK_ESPECIALISTA_ID_ESPEC) VALUES ('{desc}','{seg_empresa}',{id_clie},1)"""
        instrucao_sql.execute(str_inserir_formularioduvida)

        conn.commit()

        return "Formulário enviado com sucesso!"
    except Exception as e:
        conn.rollback()
        return f"Erro ao processar a requisição: {e}", 500
    finally:
        instrucao_sql.close()
        conn.close()

def conectar_bancodedados():
    try:
        dsnStr = oracledb.makedsn("oracle.fiap.com.br",1521,"orcl")
        conn = oracledb.connect(user='RM553791',password='180298',dsn=dsnStr)
        instrucao_sql = conn.cursor()
    except Exception as e:
        print("Erro: ", e)
        conectado = False
        instrucao_sql = ""
        conn = ""
    else:
        conectado = True

    return conectado, instrucao_sql, conn

def exibir(instrucao_sql, str_consulta, nm_tabela):
    tabela_oracle = instrucao_sql.execute(str_consulta).fetchall()
    df = pd.DataFrame(tabela_oracle)
    colunas = instrucao_sql.description
    for i in range(len(colunas)):
        df = df.rename(columns={i: colunas[i][0]})
    print(f"\nEXIBIÇÃO DE DADOS DA TABELA {nm_tabela}")
    print(df)
    return df

def atualizar_cliente(instrucao_sql, conn):
    try:
        id = int(input("\nDigite o código do cliente a ser atualizado: "))
        nome = input("Digite o nome do cliente: ")
        sobrenome = input("Digite o sobrenome do cliente: ")
        email = input("Digite o email do cliente: ")
        empresa = input("Digite a empresa do cliente: ")
        tamanho_empresa = int(input("Digite o tamanho da empresa do cliente: "))
        pais = input("Digite o país do cliente (2 dígitos): ")
        cargo = input("Digite o cargo do cliente: ")
        telefone = input("Digite o telefone do cliente: ")
    except ValueError:
        print("Insira dados numéricos para o ID e o tamanho da empresa!")
    except Exception as e:
        print(f"Erro de transação com o banco de dados!: {e}")
    else:
        str_atualizar = f"""UPDATE TB_CLIENTE SET NM_CLIE = '{nome}', SOBRENOME = '{sobrenome}', EMAIL = '{email}', EMPRESA = '{empresa}', TAMANHO_EMPRESA = {tamanho_empresa}, PAIS = '{pais}', CARGO = '{cargo}', TELEFONE = '{telefone}' WHERE ID_CLIE = {id}"""
        instrucao_sql.execute(str_atualizar)
        conn.commit()
        print("Cliente atualizado com sucesso!")
    finally:
        print("Operação finalizada!")

def atualizar_especialista(instrucao_sql, conn):
    try:
        id = int(input("\nDigite o código do especialista a ser atualizado: "))
        nome = input("Digite o nome do especialista: ")
        email = input("Digite o email do especialista: ")
        telefone = input("Digite o telefone do especialista: ")
    except ValueError:
        print("Insira dados numéricos para o ID!")
    except Exception as e:
        print(f"Erro de transação com o banco de dados!: {e}")
    else:
        str_atualizar = f"""UPDATE TB_ESPECIALISTA SET NM_ESPEC = '{nome}', EMAIL_ESPEC = '{email}', TELEFONE_ESPEC = '{telefone}' WHERE ID_ESPEC = {id}"""
        instrucao_sql.execute(str_atualizar)
        conn.commit()
        print("Especialista atualizado com sucesso!")
    finally:
        print("Operação finalizada!")

def atualizar_formularioduvida(instrucao_sql, conn):
    try:
        id = int(input("\nDigite o código do formulário a ser atualizado: "))
        desc = input("Digite a dúvida do cliente: ")
        seg_empresa = input("Digite o segmento da empresa do cliente: ")
        cliente_id = int(input("Digite o código do cliente: "))
        especialista_id = int(input("Digite o código do especialista: "))
    except ValueError:
        print("Insira dados numéricos para o ID, código do cliente e código do especialista!")
    except Exception as e:
        print(f"Erro de transação com o banco de dados!: {e}")
    else:
        str_atualizar = f"""UPDATE TB_FORMULARIODUVIDAS SET DESC_FORM = '{desc}', SEG_EMPRESA = '{seg_empresa
