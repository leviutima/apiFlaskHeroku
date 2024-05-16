import os
import oracledb
import pandas as pd
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def conectar_bancodedados():
    try:
        dsnStr = oracledb.makedsn("oracle.fiap.com.br", 1521, "orcl")
        conn = oracledb.connect(user='RM553791', password='180298', dsn=dsnStr)
        instrucao_sql = conn.cursor()
    except Exception as e:
        print("Erro: ", e)
        conectado = False
        instrucao_sql = ""
        conn = ""
    else:
        conectado = True

    return conectado, instrucao_sql, conn

@app.route('/')
def home():
    return 'API está no ar!'

@app.route('/contatenos', methods=['POST'])
def incluir_cliente_formulario():
    novo_cliente_formulario = request.get_json()

    # separação de dados do cliente
    nome = novo_cliente_formulario['nm_clie']
    sobrenome = novo_cliente_formulario['sobrenome']
    email = novo_cliente_formulario['email']
    empresa = novo_cliente_formulario['empresa']
    tamanho_empresa = novo_cliente_formulario['tamanho_empresa']
    pais = novo_cliente_formulario['pais']
    cargo = novo_cliente_formulario['cargo']
    telefone = novo_cliente_formulario['telefone']

    # separação de dados do formulário
    desc = novo_cliente_formulario['desc_form']
    seg_empresa = novo_cliente_formulario['seg_empresa']

    # conexao com o banco de dados
    conexao, instrucao_sql, conn = conectar_bancodedados()
    if not conexao:
        return "Erro ao conectar ao banco de dados", 500

    try:
        # inserção de dados do cliente
        str_inserir_clientes = f"""INSERT INTO TB_CLIENTE (NM_CLIE,SOBRENOME,EMAIL,EMPRESA,TAMANHO_EMPRESA,PAIS,CARGO,TELEFONE) VALUES ('{nome}','{sobrenome}','{email}','{empresa}',{tamanho_empresa},'{pais}','{cargo}','{telefone}')"""
        instrucao_sql.execute(str_inserir_clientes)

        # coletar id do cliente gerado automaticamente
        str_id_cliente = f"""SELECT * FROM (SELECT * FROM tb_cliente ORDER BY ROWID DESC) WHERE ROWNUM = 1"""
        cliente_oracle = instrucao_sql.execute(str_id_cliente).fetchall()

        if not cliente_oracle:
            raise Exception("Não foi possível recuperar o ID do cliente")

        id_clie = cliente_oracle[0][0]

        # inserção de dados do formulário
        str_inserir_formularioduvida = f"""INSERT INTO TB_FORMULARIODUVIDAS (DESC_FORM,SEG_EMPRESA,FK_CLIENTE_ID_CLIE,FK_ESPECIALISTA_ID_ESPEC) VALUES ('{desc}','{seg_empresa}',{id_clie},1)"""
        instrucao_sql.execute(str_inserir_formularioduvida)

        # commit
        conn.commit()

        return "Formulário enviado com sucesso!"
    except Exception as e:
        conn.rollback()
        return f"Erro ao processar a requisição: {e}", 500
    finally:
        instrucao_sql.close()
        conn.close()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
