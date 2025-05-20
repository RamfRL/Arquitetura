##########################################################################################
## PROJETO: Gerenciamento de Escritório de Arquitetura
## PROGRAMA: arquitetura.py
## ENDEREÇO: C:\Arquiteto_flask
## DATA: 05/02/2025
## ATUALIZAÇÃO: 13/03/2025
## FUNÇÃO: Programa principal
##########################################################################################
from enum import nonmember
from flask import Flask, render_template
# Importar o Flask - flask_sqlalchemy - Banco de Dados
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from numpy.f2py.crackfortran import endifs
from sqlalchemy.orm import DeclarativeBase
from werkzeug.utils import secure_filename
import sqlite3
from sqlite3 import Error
import xlsxwriter
import pandas as pd
import xlrd
import openpyxl
from openpyxl import load_workbook
import time
import datetime
from time import *
import os
import shutil
from os import path
import sys


#################################################################################
# ( 1) - Criar uma instância da classe Flask
app = Flask(__name__)

#################################################################################
# ( 2)- Configuração do banco de dados SQLite

DATABASE = 'arquitetura.db'

#############################################################################################
# DECLARA VARIÁVEIS
# IDENTIFICA O USUÁRIO ATIVO
global cod_usu_ativo
global nome_usu_ativo
lista_estados = ['AC-Acre', 'AL-Alagoas', 'AP-Amapá', 'AM-Amazonas', 'BA-Bahia',
                 'CE-Ceará', 'DF-Distrito Federal', 'ES-Espirito Santo', 'GO-Goiás',
                 'MA-Maranhão', 'MS-Mato Grosso do Sul', 'MT-Mato Grosso', 'MG-Minas Gerais',
                 'PA-Pará', 'PB-Paraíba', 'PR-Paraná', 'PE-Pernambuco', 'PI-Piauí',
                 'RJ-Rio de Janeiro', 'RN-Rio Grande do Norte', 'RS-Rio Grande do Sul',
                 'RO-Rondônia', 'RR-Roraima', 'SC-Santa Catarina', 'SP-São Paulo',
                 'SE-Sergipe', 'TO-Tocantins']

lista_tipopessoa = ['PF-Pessoa Física', 'PJ-Pessoa Jurídica']
lista_atividadecliente = ['']
lista_tipocliente = ['']

# Configura o SQLAlchemy com o URI do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///arquitetura.db"
app.config['SECRET_KEY'] = 'ramf'

########################################################################################################################
# DEFINIÇÕES PARA UPLOAD DE ARQUIVOS

# LISTA DE EXTENSÕES PERMITIDAS PARA UPLOAD
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
########################################################################################################################


# Cria um objeto SQLAlchemy associado à aplicação Flask
db = SQLAlchemy(app)

########################################################################################################################
# IMPORTANTE - Função para conectar ao banco de dados
#wait = input(f"Na função get_db o resultado é {db} e erro_conexado é {erro_conexao}")
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

########################################################################################################################
#Rota para INICIALIZAR o Banco de Dados - NÃ ESTÁ SENDO USADA
@app.route('/initdb')
def initialize_database():
    init_db()
    flash('Banco de Dados Arquitetura incializado!', category="warning")
    return 'Database inicializado'

######################################################################################################
# Função para INICIALIZAR O BANCO DE DADOS
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


#################################################################################
# FUNÇÃO PARA PREPARAR OS ARQUIVOS PARA DOWNLOAD
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#################################################################################
#Rota para ENCERRAR o SISTEMA - Não está funcionando
@app.route("/sair")
def sair():
    #wait = input(f"Na função de encerrar a aplicação.")
    quit()
    #exit()


#################################################################################
# ( 3) - ACIONA O ACESSO AO SISTEMA - ARQUIVO:\templates\acesso.html
@app.route("/")
def login():
    # session['_flashes'].clear()
    # Renderiza o template do formulário
    return render_template('acesso.html')


#################################################################################
# ( 4) - TELA PRINCIPAL DO SISTEMA - ARQUIVO:\templates\principal.html
@app.route('/principal')
def principal():
    # Renderiza o template do formulário da Tela Principal
    #return render_template('principal.html', cod_usu_ativo, nom_usu_ativo)
    return redirect(url_for("principal"))


#################################################################################
# Rota para obter o usuário por ID
@app.route('/acesso', methods=['POST'])
def acesso():
    #flash('', category="warning")
    #session.pop('_flashes', None)
    #session['_flashes'].clear()
    #flashes = session.get('_flashes', [])
    #print(flashes)
    id = request.form.get('id_usuario')
    pw = request.form.get('pw_usuario')

    ################################################################################################
    # GUARDA A DATA E A HORA DO ACESSO
    data_acesso = str(datetime.datetime.now())[:19]
    #wait = input(f"A data_agora em string  é {data_agora}.")
    data_acesso = data_acesso.replace('-', '').replace('.', '')
    #wait = input(f"A data de acesso final é {data_sem_traco}.")
    if not id or not pw:
        flash('As informações devem ser digitadas!', category="warning")
        mensagem = ""
        return render_template('acesso.html', mens=mensagem)
    else:
        if id.isdigit() == False:
            flash('Atenção! O ID do usuário deve ser um número. Verifique!', category="warning")
            mensagem = ""
            return render_template('acesso.html', mens = mensagem)
    # flash(f'Usuário digitado: {id} - Senha digitada: {pw}', category="warning")
    db = None
    db = get_db()
    cursor = db.cursor()
    ####################################################################################################################
    # CRIA A  TABELA DE USUÁRIOS - CRIA SE NÃO EXISTIR
    ####################################################################################################################
    tab_usuarios = "usuarios"
    sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_usuarios
    sqlquery2 = " (id_usuario INTEGER PRIMARY KEY, nome_usuario CHAR(80) NOT NULL, data_nasc_usuario CHAR(10), tipo_usuario CHAR(2), cpf_usuario VARCHAR(14),\
    cnpj_usuario VARCHAR(19),fone_usuario VARCHAR(15), email_usuario VARCHAR(50), cargo_usuario CHAR(50), autoridade_usuario INTEGER NOT NULL, \
    senha_usuario VARCHAR(50), ultimo_acesso VARCHAR(20))"
    sqlquery = sqlquery1 + sqlquery2
    # cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id,))
    cursor.execute(sqlquery)
    db.commit()
    ########################################################################################
    ## MONTA A QUERY PARA TESTAR SE UMA TABELA EXISTE  NO BANCO DE DADOS
    ## O SQLITE CRIA A TABELA slite_master COM O ESQUEMA DO BANCO DE DADOS
    schema_BD = "sqlite_master"
    ########################################################################################
    # VAI TRAZER O NOME DAS TABELAS QUE SÃO IGUAIS AO NOME DA TABELA DIGITADA
    sqlquery1 = "SELECT name from " + schema_BD
    sqlquery2 = " where type = 'table' and name = '" + tab_usuarios + "' COLLATE NOCASE;"
    sqlquery = sqlquery1 + sqlquery2
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sqlquery)
    dados = cursor.fetchall()
    tamanho_dados = len(dados)

    if tamanho_dados == 0:
        mensagem = ""
        return render_template('acesso.html', mens=mensagem)
    else:
        for table in dados:
            if table[0] != "" and table[0] == tab_usuarios:
                mensagem = ""
            else:
                flash('Tabela de usuários não encontrada no Banco de Dados!', category="warning")
                mensagem = ""
                return render_template('acesso.html', mens = mensagem)

    ######################################################################################################
    # MONTA A QUERY PARA LER A TABELA DE USUÁRIOS
    #wait = input("Vamos ler a tabela de usuarios")
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    cod_usu = nome_usu = data_nasc_usu = tipo_usu = cpf_usu = cnpj_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ""
    if tamanho_dados != 0:
        mensagem = ""
        for usu in dados:
            cod_usu = str(usu[0]).zfill(5)
            nome_usu = usu[1]
            data_nasc_usu = usu[2]
            tipo_usu = usu[3]
            cpf_usu = usu[4]
            cnpj_usu = usu[5]
            fone_usu = usu[6]
            email_usu = usu[7]
            cargo_usu = usu[8]
            autoridade_usu = usu[9]
            psw_usu = usu[10]
        ################################################################################################################
        # ATENÇÃO! CONFIRMAR SE A SENHA ESTÁ CORRETA
        if pw.strip() != psw_usu.strip():
            flash('Atenção! Senha não confere. Verifique!', category="error")
            mensagem = ""
            return render_template('acesso.html', mens = mensagem)
        else:
            ############################################################################################################
            # GRAVAR A DATA E O HORÁRIO DO ACESSO NA TABELA USUARIO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute('UPDATE usuarios SET ultimo_acesso = ? WHERE id_usuario = ?', (data_acesso, id,))
            db.commit()
            mensagem = None
            return render_template('principal.html', mens = mensagem, cod_usu_ativo = cod_usu, nome_usu_ativo = nome_usu)
    else:
        flash('Usuário não encontrado. Verifique!', category="warning")
        #mensagem = "Atenção! Usuário não encontrado. Verifique!"
        mensagem = ""
        #return redirect(url_for("login"))
        return render_template('acesso.html', mens=mensagem)


########################################################################################################################
# Rota para o Menu Principal
@app.route('/menu_principal', methods=['POST'])
def menu_principal():
    flash('', category="warning")
    ####################################################################################################################
    # IDENTIFICA A OPÇÃO SELECIONADA NO MENU
    opcao_menu = request.form.get('opcoes')

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO - COMO TEXTO PARA ENVIAR AO FORM
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    cod_usu = int(request.form.get('usuario_ativo')[:5])
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()
    #wait = input(f"Função menu_principal - O Usuário cod_usu é {cod_usu}.")
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (cod_usu,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    cod_usu = nome_usu = tipo_usu = cpf_usu = cnpj_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ""
    if tamanho_dados != 0:
        mensagem = ""
        for usu in dados:
            cod_usu = str(usu[0]).zfill(5)
            nome_usu = usu[1]
            # data_nasc_usu = usu[2]
            # tipo_usu = usu[3]
            # cpf_usu = usu[4]
            # cnpj_usu = usu[5]
            # fone_usu = usu[6]
            # email_usu = usu[7]
            # cargo_usu = usu[8]
            autoridade_usu = usu[9]
            # psw_usu = usu[10]
            # wait = input(f"Dados da tabela usuário: Autoridade do Usuário: {autoridade_usu}.")
        # return render_template('/usuarios.html')
        # return redirect(url_for("principal"), cod_usu, nome_usu)
        nome_usu_ativo = nome_usu
    else:
        flash('Usuário não encontrado. Verifique!', category="warning")
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # COMEÇA A TRATAR AS OPÇÕES DO MENU
    if opcao_menu == ("manutencao_usuarios"):
        mensagem = ""
        ################################################################################################################
        # TESTA A AUTORIDADE DE ACESSO DO USUÁRIO - 1 E 2 são administradores
        # wait = input(f"Função menu_principal - Usuário encontrado. Autoridade de acesso é {autoridade_usu}")
        if int(autoridade_usu) > 1:
            flash('Sem autoridade para acesso. Verifique!', category="warning")
            # mensagem = "Sem autoridade para acesso!"
            mensagem = ""
            return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)
        else:
            ############################################################################################################
            # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM usuarios")
            dados = cursor.fetchall()
            default_pessoa = "PF"
            mensagem = ""
            return render_template('usuarios.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                                   nome_usu_ativo=nome_usu_ativo, dados_usuarios=dados, lista_tipopessoa=lista_tipopessoa, default_pessoa=default_pessoa)

    elif opcao_menu == ("alteracao_senha"):
        #wait = input(f"Opção selecionada é {opcao_menu}.")
        mensagem = ""
        return render_template('alter_senha.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                               nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo)

    elif opcao_menu == ("lojas"):
        ####################################################################################################################
        # CRIA A  TABELA DE LOJAS - CRIA SE NÃO EXISTIR
        ################################################################################################################
        db = None
        db = get_db()
        cursor = db.cursor()
        tab_lojas = "lojas"
        # MONTA A QUERY PARA CRIAR A TABELA DE USUÁRIOS SE NÃO EXISTIR
        sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_lojas
        sqlquery2 = " (id_loja INTEGER PRIMARY KEY, nome_loja CHAR(80) NOT NULL, cnpj_loja VARCHAR(19), atividade_loja CHAR(30), contato_loja CHAR(50), \
                    fone_loja VARCHAR(15), email_loja VARCHAR(50), cidade_loja CHAR(80) NOT NULL, uf_loja CHAR(2) NOT NULL)"
        sqlquery = sqlquery1 + sqlquery2
        cursor.execute(sqlquery)
        db.commit()

        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM lojas")
        dados = cursor.fetchall()
        default_estados = 'PR'
        mensagem = ""
        return render_template('lojas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                               nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, dados_lojas=dados, lista_estados=lista_estados, default_estados=default_estados)

    elif opcao_menu == ("clientes"):
        ####################################################################################################################
        # CRIA A  TABELA DE CLIENTES - CRIA SE NÃO EXISTIR
        ################################################################################################################
        db = None
        db = get_db()
        cursor = db.cursor()
        # DEFINE O NOME DA TABELA DE CLIENTES
        tab_clientes = "clientes"
        # MONTA A QUERY PARA CRIAR A TABELA DE CLIENTES SE NÃO EXISTIR
        sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_clientes
        sqlquery2 = (" (id_cliente INTEGER PRIMARY KEY, nome_cliente CHAR(80) NOT NULL, razao_social_cliente CHAR(80) NOT NULL, \
                    nome_fantasia_cliente CHAR(80) NOT NULL, fone_cliente VARCHAR(15), email_cliente VARCHAR(50), cpf_cliente VARCHAR(14), \
                    cnpj_cliente VARCHAR(19), tipo_cliente CHAR(60), atividade_cliente CHAR(50), contato_cliente CHAR(50), cpf_contato_cliente VARCHAR(14), \
                    data_nasc_cont_cliente CHAR(10), cidade_cliente CHAR(80), uf_cliente CHAR(2) NOT NULL, endereco_cliente CHAR(80), \
                    cep_cliente VARCHAR(10), usuario_cliente CHAR(80))")
        sqlquery = sqlquery1 + sqlquery2
        cursor.execute(sqlquery)
        db.commit()
        ################################################################################################################
        # BUSCA OS TIPOS DE ATIVIDADES PARA LISTAR NO FORM CLIENTES
        lista_atividadecliente = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM atividade")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for ativ in dados:
                cod_ativ = str(ativ[0]).zfill(2)
                nome_ativ = ativ[1]
                lista_atividadecliente.append(cod_ativ+"-"+nome_ativ)
        default_atividade = "01"
        ################################################################################################################
        # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM CLIENTES
        lista_tipocliente = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tipo_cliente")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for tip in dados:
                cod_tip = str(tip[0]).zfill(2)
                nome_tip = tip[1]
                lista_tipocliente.append(cod_tip+"-"+nome_tip)
        default_tipocliente = "01"
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA CLIENTES PARA LISTAR NO FORM CLIENTES
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM clientes")
        dados = cursor.fetchall()
        default_estados = 'PR'
        mensagem = ""
        return render_template('clientes.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                               cod_usuario=cod_usu_ativo, dados_clientes=dados, lista_atividadecliente=lista_atividadecliente, default_atividade=default_atividade,
                               lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente, lista_estados=lista_estados, default_estados=default_estados)

    elif opcao_menu==("atividade") or opcao_menu==("tipo_cliente") or opcao_menu==("tipo_projeto") or opcao_menu==("tipo_despesa") or opcao_menu==("tipo_situacao"):
        ####################################################################################################################
        # CRIA AS TABELAS DE ATIVIDADE OU TIPOS SE NÃO EXISTIREM
        ################################################################################################################
        sqlquery2 = ""
        cadastrode = ""
        # DEFINE O NOME DAS TABELAS DE TIPOS
        if opcao_menu==("atividade"):
            tab_tipo="atividade"
            cadastrode="Atividade"
            sqlquery2 = " (id_atividade INTEGER PRIMARY KEY, nome_atividade CHAR(80) NOT NULL)"
        elif opcao_menu==("tipo_cliente"):
            tab_tipo="tipo_cliente"
            cadastrode="Tipo de Cliente"
            sqlquery2 = " (id_tipo_cliente INTEGER PRIMARY KEY, tipo_cliente CHAR(80) NOT NULL)"
        elif opcao_menu == ("tipo_projeto"):
            tab_tipo="tipo_projeto"
            cadastrode="Tipo de Projeto"
            sqlquery2 = " (id_tipo_projeto INTEGER PRIMARY KEY, tipo_projeto CHAR(80) NOT NULL)"
        elif opcao_menu == ("tipo_despesa"):
            tab_tipo="tipo_despesa"
            cadastrode="Tipo de Despesa"
            sqlquery2 = " (id_tipo_despesa INTEGER PRIMARY KEY, tipo_despesa CHAR(80) NOT NULL)"
        elif opcao_menu == ("tipo_situacao"):
            tab_tipo="tipo_situacao"
            cadastrode="Tipo de Situacao"
            sqlquery2 = " (id_tipo_situacao INTEGER PRIMARY KEY, tipo_situacao CHAR(80) NOT NULL)"
        # MONTA A QUERY PARA CRIAR A TABELA DE ATIVIDADES OU TIPOS SE NÃO EXISTIREM
        sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_tipo
        sqlquery = sqlquery1 + sqlquery2
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute(sqlquery)
        db.commit()

        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA TIPOS OU ATIVIDADES PARA LISTAR NO FORM TIPOS
        db = None
        db = get_db()
        cursor = db.cursor()
        sqlquery = "SELECT * FROM " + tab_tipo
        cursor.execute(sqlquery)
        dados = cursor.fetchall()
        id_atividade=nome_atividade=id_tipo_cliente=tipo_cliente=id_tipo_projeto=tipo_projeto=id_tipo_despesa=tipo_despesa=id_tipo_situacao=tipo_situacao=""
        mensagem = ""
        return render_template('tipos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                               nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, tab_tipo=tab_tipo, cadastrode=cadastrode,
                               dados_tipos=dados)

    elif opcao_menu == ("cadastro_projeto"):
        ################################################################################################################
        # CRIA A  TABELA DE PROJETOS - CRIA SE NÃO EXISTIR
        ################################################################################################################
        db = None
        db = get_db()
        cursor = db.cursor()
        # DEFINE O NOME DA TABELA DE PROJETOS
        tab_projetos = "projetos"
        # MONTA A QUERY PARA CRIAR A TABELA DE PROJETOS SE NÃO EXISTIR
        sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_projetos
        sqlquery2 = (" (id_projeto INTEGER PRIMARY KEY, nome_projeto CHAR(50) NOT NULL, desc_projeto CHAR(80) NOT NULL, id_tipo_projeto INTEGER,\
                    id_cliente INTEGER, id_tipo_cliente INTEGER, nome_cliente CHAR(80) NOT NULL, cidade_projeto CHAR(80), uf_projeto CHAR(2) NOT NULL, \
                    endereco_projeto CHAR(80), cep_projeto VARCHAR(10), data_contato_projeto CHAR(10), data_inicio_projeto CHAR(10), \
                    data_fim_projeto CHAR(10), usuario_projeto CHAR(80), prazo_projeto VARCHAR(40), estudo_preliminar_inicio CHR(10), \
                    estudo_preliminar_fim CHR(10), anteprojeto_inicio CHR(10), anteprojeto_fim CHR(10), projeto_legal_inicio CHAR(10),\
                    projeto_legal_fim CHAR(10), projeto_executivo_inicio CHAR(10), projeto_executivo_fim CHAR(10), viabilidade_inicio CHAR(10), \
                    viabilidade_fim CHAR(10), viabilidade_prazo VARCHAR(50))")
        sqlquery = sqlquery1 + sqlquery2
        cursor.execute(sqlquery)
        db.commit()
        ################################################################################################################
        # CRIA A TABELA DE TAREFAS DE PROJETOS - CRIA SE NÃO EXISTIR
        ################################################################################################################
        db = None
        db = get_db()
        cursor = db.cursor()
        # DEFINE O NOME DA TABELA DE TAREFAS DE PROJETOS
        tab_projetos = "projetos_tarefas"
        # MONTA A QUERY PARA CRIAR A TABELA DE TAREFAS DE PROJETOS SE NÃO EXISTIR
        sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_projetos
        sqlquery2 = (" (id_projeto INTEGER, nome_projeto CHAR(50) NOT NULL, id_tipo_projeto INTEGER,\
                    id_cliente INTEGER, id_tipo_cliente INTEGER, nome_cliente CHAR(80) NOT NULL, id_tarefa INTEGER, \
                    desc_tarefa CHAR(80), tarefa_prazo VARCHAR(50), tarefa_inicio CHAR(10), tarefa_fim CHAR(10))")
        sqlquery = sqlquery1 + sqlquery2
        cursor.execute(sqlquery)
        db.commit()
        ################################################################################################################
        # BUSCA OS TIPOS DE PROJETOS     PARA LISTAR NO FORM PROJETOS
        lista_tipoprojeto = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tipo_projeto")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for tip in dados:
                idtipo_projeto = str(tip[0]).zfill(2)
                tipo_projeto = tip[1]
                lista_tipoprojeto.append(idtipo_projeto+"-"+tipo_projeto)
        default_tipoprojeto = "01"
        ################################################################################################################
        # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS
        lista_tipocliente = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tipo_cliente")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for tip in dados:
                cod_tip = str(tip[0]).zfill(2)
                nome_tip = tip[1]
                lista_tipocliente.append(cod_tip+"-"+nome_tip)
        default_tipocliente = "01"
        ################################################################################################################
        # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS
        lista_clientes = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM clientes")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for cli in dados:
                cod_cli = str(cli[0]).zfill(2)
                nome_cli = cli[1]
                lista_clientes.append(cod_cli+"-"+nome_cli)
        default_clientes = "01"
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM projetos")
        dados = cursor.fetchall()
        default_estados = 'PR'
        mensagem = ""
        return render_template('projetos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                               cod_usuario=cod_usu_ativo, dados_projetos=dados, lista_tipoprojeto=lista_tipoprojeto, default_tipoprojeto=default_tipoprojeto,
                               lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente, lista_clientes=lista_clientes,
                               default_clientes=default_clientes, lista_estados=lista_estados, default_estados=default_estados)

    elif opcao_menu == ("tarefas_projeto"):
        ################################################################################################################
        # CRIA A TABELA DE TAREFAS DE PROJETOS - CRIA SE NÃO EXISTIR
        ################################################################################################################
        db = None
        db = get_db()
        cursor = db.cursor()
        # DEFINE O NOME DA TABELA DE PROJETOS
        tab_projetos = "projetos_tarefas"
        # MONTA A QUERY PARA CRIAR A TABELA DE PROJETOS SE NÃO EXISTIR
        sqlquery1 = "CREATE TABLE IF NOT EXISTS " + tab_projetos
        sqlquery2 = (" (id_projeto INTEGER, nome_projeto CHAR(50) NOT NULL, id_tipo_projeto INTEGER,\
                    id_cliente INTEGER, id_tipo_cliente INTEGER, nome_cliente CHAR(80) NOT NULL, id_tarefa INTEGER, \
                    desc_tarefa CHAR(80), tarefa_prazo VARCHAR(50), tarefa_inicio CHAR(10), tarefa_fim CHAR(10))")
        sqlquery = sqlquery1 + sqlquery2
        cursor.execute(sqlquery)
        db.commit()
        ################################################################################################################
        # BUSCA OS TIPOS DE PROJETOS   PARA LISTAR NO FORM PROJETOS
        lista_tipoprojeto = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tipo_projeto")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for tip in dados:
                idtipo_projeto = str(tip[0]).zfill(2)
                tipo_projeto = tip[1]
                lista_tipoprojeto.append(idtipo_projeto+"-"+tipo_projeto)
        default_tipoprojeto = "01"
        ################################################################################################################
        # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS
        lista_tipocliente = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tipo_cliente")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for tip in dados:
                cod_tip = str(tip[0]).zfill(2)
                nome_tip = tip[1]
                lista_tipocliente.append(cod_tip+"-"+nome_tip)
        default_tipocliente = "01"
        ################################################################################################################
        # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS
        lista_clientes = ['']
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM clientes")
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        if tamanho_dados != 0:
            for cli in dados:
                cod_cli = str(cli[0]).zfill(2)
                nome_cli = cli[1]
                lista_clientes.append(cod_cli+"-"+nome_cli)
        default_clientes = "01"
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM projetos")
        dados_projetos = cursor.fetchall()
        default_estados = 'PR'
        mensagem = ""
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA DE TAREFAS DE PROJETOS PARA LISTAR NO FORM PROJETOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM projetos_tarefas order by id_projeto, id_tarefa")
        dados_tarefas = cursor.fetchall()
        default_estados = 'PR'
        mensagem = ""
        return render_template('projetos_tarefas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                               cod_usuario=cod_usu_ativo, dados_projetos=dados_projetos, dados_tarefas=dados_tarefas, lista_tipoprojeto=lista_tipoprojeto, default_tipoprojeto=default_tipoprojeto,
                               lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente, lista_clientes=lista_clientes,
                               default_clientes=default_clientes, lista_estados=lista_estados, default_estados=default_estados)

    elif opcao_menu == ("sair"):
        sys.exit(0)

    else:
        return redirect(url_for("principal"))


#################################################################################
# Rota para Manutenção de Usuários
@app.route('/mantem_usuarios', methods=['GET', 'POST'])
def mantem_usuarios():
    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_busca_usuario')
    #wait = input(f"O botão acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()
    #wait = input(f"Na função mantem_usuarios - Usuário ativo é {cod_usu_ativo} e nome do usuário ativo é {nome_usu_ativo}.")

    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE USUÁRIOS
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE USUÁRIOS
    if botao_acionado == "Limpar":
        cod_usu = nome_usu = data_nasc_usu = tipo_usu = cpf_usu = cnpj_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ult_acesso_usuario = ""
        mensagem = ""
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios")
        dados = cursor.fetchall()
        default_pessoa = "PF"
        return render_template('usuarios.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu, nome_usuario=nome_usu, data_nasc_usu=data_nasc_usu, tipo_usu=tipo_usu, cpf_usuario=cpf_usu,
                           cnpj_usu=cnpj_usu, fone_usuario=fone_usu, email_usuario=email_usu, cargo_usuario=cargo_usu,
                           autoridade_usuario=autoridade_usu, psw_usuario=psw_usu, ult_acesso_usuario=ult_acesso_usuario, dados_usuarios=dados, lista_tipopessoa=lista_tipopessoa, default_pessoa=default_pessoa)

    ####################################################################################################################
    # LOCALIZA UM USUÁRIO
    elif botao_acionado == "Localizar":
        ################################################################################################################
        # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
        if request.form.get('cod_usuario') == "":
            flash('Atenção! O código do usuário deve ser digitado. Verifique!', category="warning")
        else:
            codigo_usu = int(request.form.get('cod_usuario'))
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (codigo_usu,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            cod_usu = nome_usu = data_nasc_usu = tipo_usu = cpf_usu = cnpj_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ult_acesso_usuario = ""
            #wait = input(f"Na função mantem_usuarios O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca do usuário")
            if tamanho_dados != 0:
                mensagem = ""
                for usu in dados:
                    cod_usu = str(usu[0]).zfill(5)
                    nome_usu = usu[1]
                    data_nasc_usu = usu[2]
                    tipo_usu = usu[3]
                    cpf_usu = usu[4]
                    cnpj_usu = usu[5]
                    fone_usu = usu[6]
                    email_usu = usu[7]
                    cargo_usu = usu[8]
                    autoridade_usu = usu[9]
                    psw_usu = usu[10]
                    ult_acesso_usu = usu[11]
                    ####################################################################################################
                    # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
                    db = None
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM usuarios")
                    dados = cursor.fetchall()

                    return render_template('usuarios.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                    cod_usuario = int(cod_usu), nome_usuario=nome_usu, data_nasc_usu=data_nasc_usu, tipo_usuario=tipo_usu,cpf_usuario=cpf_usu, cnpj_usuario=cnpj_usu,
                    fone_usuario=fone_usu, email_usuario=email_usu, cargo_usuario=cargo_usu, autoridade_usuario=autoridade_usu,
                    psw_usuario=psw_usu, ult_acesso_usuario=ult_acesso_usu, lista_tipopessoa=lista_tipopessoa, dados_usuarios=dados)
            else:
                flash('Usuário não encontrado. Verifique!', category="warning")
                mensagem = ""
                # return redirect(url_for("login"))
                #return render_template('usuarios.html', mens=mensagem, cod_usu_ativo = cod_usu_ativo, nome_usu_ativo = nome_usu_ativo)

    ####################################################################################################################
    # ALTERAR UM USUÁRIO
    elif botao_acionado == "Alterar":
        ################################################################################################################
        # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
        if request.form.get('cod_usuario') == "":
            flash('Atenção! O código do usuário deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
            codigo_usu = int(request.form.get('cod_usuario'))
            nome_usu = request.form.get('nome_usuario')
            data_nasc_usu = request.form.get('dtnasc_usuario')
            tipo_usu = request.form.get('tipo_pessoa')
            cpf_usu = request.form.get('cpf_usuario')
            cnpj_usu = request.form.get('cnpj_usuario')
            fone_usu = request.form.get('fone_usuario')
            email_usu = request.form.get('email_usuario')
            cargo_usu = request.form.get('cargo_usuario')
            autoridade_usu = request.form.get('autoridade_usuario')
            senha_usu = request.form.get('senha_usuario')
            ult_acesso_usu = request.form.get('ult_acesso_usuario')

            ############################################################################################################
            # ALTERAR UM  USUARIO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE usuarios SET nome_usuario = ?, data_nasc_usuario = ?, tipo_usuario = ?, cpf_usuario = ?, cnpj_usuario = ?, \
                            fone_usuario = ?, email_usuario = ?, cargo_usuario = ?, autoridade_usuario = ?, senha_usuario = ? \
                           WHERE id_usuario = ?", (nome_usu, data_nasc_usu, tipo_usu, cpf_usu, cnpj_usu, fone_usu, email_usu, cargo_usu,
                           autoridade_usu, senha_usu, codigo_usu,))
            db.commit()
            flash('Registro alterado com sucesso!', category="warning")

    ####################################################################################################################
    # INCLUIR UM USUÁRIO
    elif botao_acionado == "Incluir":
        ################################################################################################################
        # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
        if request.form.get('cod_usuario') == "":
            flash('Atenção! O código do usuário deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
            codigo_usu = int(request.form.get('cod_usuario'))

            ############################################################################################################
            # INCLUIR UM  USUARIO - TESTA SE JÁ É CADASTRADO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (codigo_usu,))
            dados = cursor.fetchall()
            # db.commit()
            tamanho_dados = len(dados)
            cod_usu = nome_usu = cpf_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ""
            #wait = input(f"Na função mantem_usuarios O tamanho_dados de Incluir é {tamanho_dados}. Fazendo a busca do usuário")
            if tamanho_dados != 0:
                flash('Atenção! Usuário já cadastrado. Verifique!', category="warning")
                #mensagem = "Atenção! Usuário já cadastrado. Verifique!"
            else:
                # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
                codigo_usu = int(request.form.get('cod_usuario'))
                nome_usu = request.form.get('nome_usuario')
                data_nasc_usu = request.form.get('dtnasc_usuario')
                tipo_usu = request.form.get('tipo_pessoa')
                cpf_usu = request.form.get('cpf_usuario')
                cnpj_usu = request.form.get('cnpj_usuario')
                fone_usu = request.form.get('fone_usuario')
                email_usu = request.form.get('email_usuario')
                cargo_usu = request.form.get('cargo_usuario')
                autoridade_usu = request.form.get('autoridade_usuario')
                senha_usu = request.form.get('senha_usuario')
                ult_acesso_usu = request.form.get('ult_acesso_usuario')

                # A SENHA PADRÃO É 111
                senha_usu = "111"
                ult_acesso_usu = ""
                dados_grava = (codigo_usu, nome_usu, data_nasc_usu, tipo_usu, cpf_usu, cnpj_usu, fone_usu, email_usu, cargo_usu, autoridade_usu, senha_usu, ult_acesso_usu)
                cursor.execute("INSERT INTO usuarios (id_usuario, nome_usuario, data_nasc_usuario, tipo_usuario, cpf_usuario, cnpj_usuario, \
                               fone_usuario, email_usuario, cargo_usuario, autoridade_usuario, senha_usuario, ultimo_acesso) \
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", dados_grava)
                db.commit()
                flash('Registro incluído com sucesso!', category="warning")

    ####################################################################################################################
    # EXCLUIR UM USUÁRIO
    elif botao_acionado == "Excluir":
        ################################################################################################################
        # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
        if request.form.get('cod_usuario') == "":
            flash('Atenção! O código do usuário deve ser digitado. Verifique!', category="warning")
        else:
            # ESTA MENSAGEM VEM DO INPUT mensagem_excluir - oculto no form USUÁRIOS
            mensagem = request.form.get('mensagem_excluir')
            #wait = input(f"Mensagem {mensagem}.")
            if mensagem == "Sim":
                # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
                codigo_usu = int(request.form.get('cod_usuario'))
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (codigo_usu,))
                dados = cursor.fetchall()
                db.commit()
                flash('Registro excluído com sucesso!', category="warning")
                # mensagem = "Registro excluído com sucesso!"
            else:
                flash('Exclusão cancelada!', category="warning")

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    dados = cursor.fetchall()
    cod_usu = nome_usu = data_nasc_usu = tipo_usu = cpf_usu = cnpj_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ult_acesso_usu = ""
    mensagem = ""
    default_pessoa = "PF"
    return render_template('usuarios.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
    nome_usu_ativo=nome_usu_ativo, cod_usuario = cod_usu, nome_usuario=nome_usu, data_nasc_usu=data_nasc_usu, tipo_usuario=tipo_usu, cpf_usuario=cpf_usu,
    cnpj_usuario=cnpj_usu, fone_usuario=fone_usu, email_usuario=email_usu, cargo_usuario=cargo_usu,
    autoridade_usuario=autoridade_usu, psw_usuario=psw_usu, ult_acesso_usuario=ult_acesso_usu, lista_tipopessoa=lista_tipopessoa, default_pessoa=default_pessoa, dados_usuarios=dados)


########################################################################################################################
# Rota para Alteração de Senha
@app.route('/alter_senha', methods=['GET', 'POST'])
def alter_senha():
    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_altera_senha')
    #wait = input(f"O botão acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()

    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE USUÁRIOS
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE USUÁRIOS
    elif botao_acionado == "Limpar":
        psw_atual = psw_novo = mensagem = ""
    else:
        # IDENTIFICA O CÓDIGO DO USUÁRIO DIGITADO
        psw_atual = request.form.get('senha_usuario_atual')
        psw_atual = psw_atual.strip()
        psw_novo = request.form.get('senha_usuario_nova')
        psw_novo = psw_novo.strip()

        if psw_atual == "" or psw_novo == "":
            flash('Atenção! As senhas devem ser digitadas. Verifique!', category="warning")
            mensagem = ""
        else:
            db = None
            db = get_db()
            cursor = db.cursor()
            cod_usu = int(cod_usu_ativo)
            psw_usu = ""
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (cod_usu,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for usu in dados:
                    psw_usu = usu[7]

            if psw_atual != psw_usu.strip():
                flash('Atenção! Senha atual não confere. Verifique!', category="error")
                mensagem = ""
            else:
                ########################################################################################################
                # GRAVAR A NOVA SENHA DO USUARIO
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute('UPDATE usuarios SET senha_usuario = ? WHERE id_usuario = ?', (psw_novo, cod_usu,))
                db.commit()
                mensagem = ""
                flash('Senha alterada com sucesso', category="warning")

    return render_template('alter_senha.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                           nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, psw_atual=psw_atual, psw_novo=psw_novo)


########################################################################################################################
# ROTA PARA EDITAR O USUÁRIO SELECIONADO NA TABLE
@app.route('/edita_usuario/<int:record_id>, <cod_usu_ativo>, <nome_usu_ativo>')
def edita_usuario(record_id, cod_usu_ativo, nome_usu_ativo):

    codigo_usu = record_id
    #wait = input(f"Na função edita_usuario - O código do Usuário ativo é {cod_usu}.")
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    #wait = input(f"Na função edita_usuario - O código do Usuário ativo lido é {cod_usu_ativo}.")
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (codigo_usu,))
    dados = cursor.fetchall()
    # db.commit()
    tamanho_dados = len(dados)
    cod_usu = nome_usu = tipo_usu = cpf_usu = cnpj_usu = fone_usu = email_usu = cargo_usu = autoridade_usu = psw_usu = ""

    if tamanho_dados != 0:
        for usu in dados:
            cod_usu = str(usu[0]).zfill(5)
            nome_usu = usu[1]
            data_nasc_usu = usu[2]
            tipo_usu = usu[3]
            cpf_usu = usu[4]
            cnpj_usu = usu[5]
            fone_usu = usu[6]
            email_usu = usu[7]
            cargo_usu = usu[8]
            autoridade_usu = usu[9]
            psw_usu = usu[10]
            ult_acesso_usu = usu[11]

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    dados = cursor.fetchall()
    mensagem = ""
    return render_template('usuarios.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu, nome_usuario=nome_usu, data_nasc_usu=data_nasc_usu, tipo_usuario=tipo_usu, cpf_usuario=cpf_usu,
                           cnpj_usuario=cnpj_usu, fone_usuario=fone_usu, email_usuario=email_usu, cargo_usuario=cargo_usu,
                           autoridade_usuario=autoridade_usu, psw_usuario=psw_usu, ult_acesso_usuario=ult_acesso_usu, lista_tipopessoa=lista_tipopessoa, dados_usuarios=dados)


########################################################################################################################
# Rota para Manutenção de Lojas
@app.route('/mantem_lojas', methods=['GET', 'POST'])
def mantem_lojas():

    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_busca_loja')
    #wait = input(f"O botão de lojas acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()

    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE LOJAS
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE LOJAS
    if botao_acionado == "Limpar":
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM lojas")
        dados = cursor.fetchall()
        cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""
        mensagem = ""
        default_estados = "PR"
        return render_template('lojas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_loja=cod_loja, nome_loja=nome_loja, cnpj_loja=cnpj_loja, atividade_loja=atividade_loja,
                           contato_loja=contato_loja, fone_loja=fone_loja, email_loja=email_loja, cidade_loja=cidade_loja,
                           uf_loja=uf_loja, dados_lojas=dados, lista_estados=lista_estados, default_estados=default_estados)

    ####################################################################################################################
    # LOCALIZA UMA LOJA
    elif botao_acionado == "Localizar":
        if request.form.get('cod_loja') == "":
            # wait = input(f"Código de Loja vazio {request.form.get('cod_loja')}.")
            flash('Atenção! O código da loja deve ser digitado. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DA LOJA
            codigo_loja = int(request.form.get('cod_loja'))
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM lojas WHERE id_loja = ?", (codigo_loja,))
            dados = cursor.fetchall()
            # db.commit()
            tamanho_dados = len(dados)
            cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""
            #wait = input(f"Na função mantem_lojas O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca da loja")
            if tamanho_dados != 0:
                mensagem = ""
                for loj in dados:
                    cod_loja = str(loj[0]).zfill(5)
                    nome_loja = loj[1]
                    cnpj_loja = loj[2]
                    atividade_loja = loj[3]
                    contato_loja = loj[4]
                    fone_loja = loj[5]
                    email_loja = loj[6]
                    cidade_loja = loj[7]
                    uf_loja = loj[8]

                    ####################################################################################################
                    # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
                    db = None
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM lojas")
                    dados = cursor.fetchall()
                    #wait = input(f"Dados da tabela Lojas: cidade da loja: {cidade_loja}.")
                    return render_template('lojas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo, cod_loja = int(cod_loja), nome_loja=nome_loja, cnpj_loja=cnpj_loja,
                    atividade_loja=atividade_loja, contato_loja=contato_loja, fone_loja=fone_loja, email_loja=email_loja, cidade_loja=cidade_loja, uf_loja=uf_loja, dados_lojas=dados, lista_estados=lista_estados)
            else:
                # wait = input("Loja não encontrada")
                flash('Loja não encontrada. Verifique!', category="warning")
                #mensagem = "Atenção! Loja não encontrada. Verifique!"
                mensagem = ""
                # return redirect(url_for("login"))
                #return render_template('lojas.html', mens=mensagem, cod_usu_ativo = cod_usu_ativo, nome_usu_ativo = nome_usu_ativo)

    ####################################################################################################################
    # ALTERAR UM USUÁRIO
    elif botao_acionado == "Alterar":
        if request.form.get('cod_loja') == "":
            # wait = input(f"Código de Loja vazio {request.form.get('cod_loja')}.")
            flash('Atenção! O código da loja deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DA LOJA
            codigo_loja = int(request.form.get('cod_loja'))
            # IDENTIFICA OS CAMPOS DIGITADOS
            nome_loja = request.form.get('nome_loja')
            cnpj_loja = request.form.get('cnpj_loja')
            atividade_loja = request.form.get('atividade_loja')
            contato_loja = request.form.get('contato_loja')
            fone_loja = request.form.get('fone_loja')
            email_loja = request.form.get('email_loja')
            cidade_loja = request.form.get('cidade_loja')
            # TRAZ O VALOR DA LISTA ESTADOS
            uf_loja = request.form.get('estados')

            ############################################################################################################
            # ALTERAR UMA LOJA
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE lojas SET nome_loja = ?, cnpj_loja = ?, atividade_loja = ?, contato_loja = ?, fone_loja = ?, email_loja = ?, \
                           cidade_loja = ?, uf_loja = ? \
                           WHERE id_loja = ?", (nome_loja, cnpj_loja, atividade_loja, contato_loja, fone_loja, email_loja, cidade_loja,
                           uf_loja, codigo_loja,))
            db.commit()
            flash('Registro alterado com sucesso!', category="warning")

    # INCLUIR UMA LOJA
    elif botao_acionado == "Incluir":
        ################################################################################################################
        # INCLUIR UMA LOJA - TESTA SE JÁ É CADASTRADO
        if request.form.get('cod_loja') == "":
            # wait = input(f"Código de Loja vazio {request.form.get('cod_loja')}.")
            flash('Atenção! O código da loja deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DA LOJA
            codigo_loja = int(request.form.get('cod_loja'))

            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM lojas WHERE id_loja = ?", (codigo_loja,))
            dados = cursor.fetchall()
            # db.commit()
            tamanho_dados = len(dados)
            #wait = input(f"Na função mantem_usuarios O tamanho_dados de Incluir é {tamanho_dados}. Fazendo a busca do usuário")
            if tamanho_dados != 0:
                flash('Atenção! Loja já cadastrada. Verifique!', category="warning")
                #mensagem = "Atenção! Loja já cadastrada. Verifique!"
            else:
                # IDENTIFICA OS CAMPOS DIGITADOS
                codigo_loja = int(request.form.get('cod_loja'))
                nome_loja = request.form.get('nome_loja')
                cnpj_loja = request.form.get('cnpj_loja')
                atividade_loja = request.form.get('atividade_loja')
                contato_loja = request.form.get('contato_loja')
                fone_loja = request.form.get('fone_loja')
                email_loja = request.form.get('email_loja')
                cidade_loja = request.form.get('cidade_loja')
                # TRAZ O VALOR DO CAMPO UF_LOJA - NÃO EXISTE ESTE CAMPO NO FORM
                # uf_loja = request.form.get('uf_loja')
                # TRAZ O VALOR DA LISTA ESTADOS
                uf_loja = request.form.get('estados')

                db = None
                db = get_db()
                cursor = db.cursor()
                dados_grava = (codigo_loja, nome_loja, cnpj_loja, atividade_loja, contato_loja, fone_loja, email_loja, cidade_loja, uf_loja)
                cursor.execute("INSERT INTO lojas (id_loja, nome_loja, cnpj_loja, atividade_loja, contato_loja, fone_loja, email_loja, \
                               cidade_loja, uf_loja) \
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", dados_grava)
                db.commit()
                flash('Registro incluído com sucesso!', category="warning")

    ####################################################################################################################
    # EXCLUIR UMA LOJA
    elif botao_acionado == "Excluir":
        if request.form.get('cod_loja') == "":
            # wait = input(f"Código de Loja vazio {request.form.get('cod_loja')}.")
            flash('Atenção! O código da loja deve ser digitado. Verifique!', category="warning")
        else:
            # ESTA MENSAGEM VEM DO INPUT mensagem_excluir - oculto no form LOJAS
            mensagem = request.form.get('mensagem_excluir')
            # wait = input(f"Mensagem {mensagem}.")
            if mensagem == "Sim":
                # IDENTIFICA O CÓDIGO DA LOJA
                codigo_loja = int(request.form.get('cod_loja'))

                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM lojas WHERE id_loja = ?", (codigo_loja,))
                dados = cursor.fetchall()
                db.commit()
                flash('Registro excluído com sucesso!', category="warning")
            else:
                flash('Exclusão cancelada!', category="warning")

    ####################################################################################################################
    # GERA ARQUIV EXCEL/TX/PDF
    elif botao_acionado == "Excel/TXT":
        db = None
        db = get_db()
        cursor = db.cursor()

        if request.form.get('cod_loja') == "":
            codigo_loja = 0
            cursor.execute("SELECT * FROM lojas")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DA LOJA
            codigo_loja = int(request.form.get('cod_loja'))
            cursor.execute("SELECT * FROM lojas WHERE id_loja = ?", (codigo_loja,))

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO TXT
        nome_arq_TXT = "lojas" + ".txt"
        arq_TXT = "static\\arquivos_txt\\" + nome_arq_TXT
        if (os.path.exists(arq_TXT)):
            arquivo = open(arq_TXT, 'w')
        else:
            arquivo = open(arq_TXT, 'x')

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO MS-Excel
        nome_arq_XLSX = "lojas" + ".xlsx"
        arq_XLSX = "static\\arquivos_xlsx\\" + nome_arq_XLSX

        ################################################################################################################
        ## FAZ A LEITURA DA BASE DE DADOS
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        atividade_loja: str
        cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""
        if tamanho_dados != 0:
            #wait = input("Loja encontrada")
            mensagem = ""
            tit1 = "SGEA-Sistema Gerenciador de Escritório de Arquitetura" + "\n"
            tit2 = "Relação de Lojas Cadastradas" + "\n"
            tit3 = "-----------------------------------------------------" + "\n"
            arquivo.write(tit1 + tit2 + tit3)

            for loj in dados:
                cod_loja = loj[0]
                nome_loja = loj[1]
                cnpj_loja = loj[2]
                atividade_loja = loj[3]
                contato_loja = loj[4]
                fone_loja = loj[5]
                email_loja = loj[6]
                cidade_loja = loj[7]
                uf_loja = loj[8]

                cod_loja = str(loj[0]).zfill(5)
                cod_loja_grava = cod_loja.zfill(5)
                #wait = input(f"Código de Loja do arquivo {loj[0]}.")
                nome_loja = nome_loja.upper()
                nome_loja = "{0:<80}".format(nome_loja)
                #wait = input(f"Nome de Loja {loj[1]}.")
                cnpj_loja = cnpj_loja.strip()
                if len(cnpj_loja) < 19:
                    cnpj_loja = "{0:<19}".format(cnpj_loja)
                #wait = input(f"Cnpj da Loja {loj[2]}.")
                atividade_loja = atividade_loja.strip().upper()
                atividade_loja = "{0:<30}".format(atividade_loja)
                #wait = input(f"Atividade de Loja {atividade_loja}.")
                contato_loja = contato_loja.strip()
                contato_loja = "{0:<50}".format(contato_loja)
                fone_loja = fone_loja.strip()
                if len(fone_loja) < 15:
                    fone_loja = "{0:<15}".format(fone_loja)
                #wait = input(f"Fone da Loja {loj[3]}.")
                email_loja = email_loja.strip()
                if len(email_loja) < 50:
                    email_loja = "{0:<50}".format(email_loja)
                #wait = input(f"Email da Loja {loj[4]}.")
                cidade_loja = cidade_loja.strip()
                if len(cidade_loja) < 80:
                    cidade_loja = "{0:<80}".format(cidade_loja)
                #wait = input(f"Cidade da Loja {loj[5]}.")
                uf_loja = uf_loja.strip()
                #wait = input(f"UF da Loja {loj[6]}.")
                linha_grava = cod_loja + nome_loja + cnpj_loja + atividade_loja + contato_loja + fone_loja + email_loja + cidade_loja + uf_loja + "\n"
                linha_grava = ("ID: " + cod_loja + "\n"
                               "Nome: " + nome_loja + "\n"
                               "CNPJ: " + cnpj_loja + "\n"
                               "Atividade: " + atividade_loja + "\n"
                               "Contato: " + contato_loja + "\n"
                               "Fone: " + fone_loja + "\n"
                               "Email: " + email_loja + "\n"
                               "Cidade: " + cidade_loja + "\n"
                               "UF: " + uf_loja + "\n" + "\n")
                #wait = input(f"Linha grava {linha_grava}.")
                arquivo.write(linha_grava)

            arquivo.close()

            ############################################################################################################
            ## 1-GERA UM df =: DATAFRAME COM O SQL GERADO - USANDO PANDAS
            df = pd.DataFrame(dados)

            ############################################################################################################
            ## O CABEÇALHO DAS COLUNAS PODE SER CRIADO DE DUAS MANEIRAS:
            ## 1- ATRIBUI A columns OS TÍTULOS DAS COLUNAS DO BD SQL PARA USAR COMO CABEÇALHO NO EXCEL
            ##    AS COLUNAS SÃO GERADAS NO MOMENTO DA GERAÇÃO DO SQL NO con
            # columns = [desc[0] for desc in con.description]
            # df = pd.DataFrame(list(sqlquery), columns=columns)
            # df.to_excel(arq_XLS, sheet_name="Lojas", index=False, startcol=0, startrow=0)

            ############################################################################################################
            ## 2- ATRIBUI A VARIÁVEL alias OS CABEÇALHOS DAS COLUNAS
            ##    NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias
            ##    SE NÃO USAR O alias O CABEÇALHO SERÁ 0,1,2,3,4,5

            ############################################################################################################
            ## VAMOS USAR O MÉTODO with... PODE GERAR UMA OU VÁRIAS  PLANILHAS NO MESMO ARQUIVO
            ## NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias index=False
            ## NESTE CASO VAMOS CRIAR UM ARQUIVO XLSX COM 1 PLANILHA - Lojas
            alias = ["ID_LOJA", "NOME_LOJA", "CNPJ_LOJA", "ATIVIDADE_LOJA", "CONTATO_LOJA", "FONE_LOJA", "EMAIL_LOJA", "CIDADE_LOJA", "UF_LOJA"]
            with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                df.to_excel(ew, sheet_name="Lojas", index=False, header=alias)

            ############################################################################################################
            ## PODEMOS APENDAR UM DATAFRAME DENTRO DE OUTRO PARA GRAVAR EM UMA PLANILHA
            ## APENDA O DATA FRAME df1 NO DATA FRAME df
            # df1 = pd.DataFrame(sqlquery)
            # df3 = df1.append(df1, ignore_index=False, sort=False)
            ############################################################################################################
            ## PODEMOS INCLUIR UMA NOVA PLANILHA DENTRO DO ARQUIVO JÁ GERADO
            ## CRIAMOS A PLANILHA Vendas2 COM O df3 QUE APENDOU O df1
            # with pd.ExcelWriter(arq_XLS1, engine="openpyxl", mode="a") as ew:
            # df3.to_excel(ew, sheet_name="Vendas2", index=False, header=alias)
            cursor.close()
            flash("Arquivo (Excel) - lojas.xlsx na pasta /static/arquivos_xlsx e Arquivo (TXT) - lojas.txt na pasta /static/arquivos_txt  => gerados com sucesso!", category="warning")

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM lojas")
    dados = cursor.fetchall()
    cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""
    default_estados = "PR"
    mensagem = ""
    return render_template('lojas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo, cod_loja = cod_loja, nome_loja=nome_loja, cnpj_loja=cnpj_loja,
    atividade_loja=atividade_loja, contato_loja=contato_loja, fone_loja=fone_loja, email_loja=email_loja, cidade_loja=cidade_loja, uf_loja=uf_loja, dados_lojas=dados, lista_estados=lista_estados,
    default_estados=default_estados)


########################################################################################################################
# ROTA PARA EDITAR A LOJA SELECIONADO NA TABLE
@app.route('/edita_loja/<int:record_id>, <cod_usu_ativo>, <nome_usu_ativo>')
def edita_loja(record_id, cod_usu_ativo, nome_usu_ativo):

    codigo_loja = record_id
    #wait = input(f"Na função edita_loja - O código da Loja selecionado é {codigo_loja}.")
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    #wait = input(f"Na função edita_usuario - O código do Usuário ativo lido é {cod_usu_ativo}.")
    #wait = input(f"Na função edita_usuario - O Nome do Usuário ativo lido é {nome_usu_ativo}.")
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM lojas WHERE id_loja = ?", (codigo_loja,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    #wait = input(f"Na função edita_loja - tamanho_dados para a loja selecioonada é {tamanho_dados}.")
    cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""
    if tamanho_dados != 0:
        for loja in dados:
            cod_loja = str(loja[0]).zfill(5)
            nome_loja = loja[1]
            cnpj_loja = loja[2]
            atividade_loja = loja[3]
            contato_loja = loja[4]
            fone_loja = loja[5]
            email_loja = loja[6]
            cidade_loja = loja[7]
            uf_loja = loja[8]
    #wait = input(f"Na função edita_loja - o código da loja de dados é {cod_loja}.")
    #wait = input(f"Na função edita_loja - o nome da loja de dados é {nome_loja}.")
    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM lojas")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    #wait = input(f"Na função edita_loja - tamanho_dados para a todas as lojas é {tamanho_dados}.")
    mensagem = ""
    return render_template('lojas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_loja=cod_loja, nome_loja=nome_loja, cnpj_loja=cnpj_loja,
                           atividade_loja=atividade_loja, contato_loja=contato_loja, fone_loja=fone_loja, email_loja=email_loja, cidade_loja=cidade_loja,
                           uf_loja=uf_loja, dados_lojas=dados, lista_estados=lista_estados)


########################################################################################################################
# ROTA PARA EDITAR A LOJA SELECIONADO NA TABLE
@app.route('/filtra_loja/<atividade_loja>, <cod_usu_ativo>, <nome_usu_ativo>')
def filtra_loja(atividade_loja, cod_usu_ativo, nome_usu_ativo):

    ativ_loja = atividade_loja.strip()
    #wait = input(f"Na função filtra_loja - A atividade da Loja selecionado é {atividade_loja}.")
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    #wait = input(f"Na função edita_usuario - O código do Usuário ativo lido é {cod_usu_ativo}.")
    #wait = input(f"Na função edita_usuario - O Nome do Usuário ativo lido é {nome_usu_ativo}.")
    cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""

    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM lojas WHERE atividade_loja = ?", (ativ_loja,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    #wait = input(f"Na função filtra_loja - tamanho_dados para a atividade selecionada é {tamanho_dados}.")
    mensagem = ""
    return render_template('lojas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_loja=cod_loja, nome_loja=nome_loja, cnpj_loja=cnpj_loja,
                           atividade_loja=atividade_loja, contato_loja=contato_loja, fone_loja=fone_loja, email_loja=email_loja, cidade_loja=cidade_loja,
                           uf_loja=uf_loja, dados_lojas=dados, lista_estados=lista_estados)


########################################################################################################################
# Rota para Manutenção de Cadastro Geral de Atividades e Tipos
@app.route('/mantem_tipos', methods=['GET', 'POST'])
def mantem_tipos():

    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_busca_tipo')
    #wait = input(f"O botão de lojas acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()
    cadastrode = request.form.get('titulo_cadastro')[0:30].strip()
    #wait = input(f"Na função mantem_loja - Usuário ativo é {cod_usu_ativo} e nome do usuário ativo é {nome_usu_ativo}.")

    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE TIPOS E ATIVIDADES
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
    if cadastrode=="Atividade":
        tab_tipo="atividade"
        codigo_tipo = "id_atividade"
    elif cadastrode=="Tipo de Cliente":
        tab_tipo="tipo_cliente"
        codigo_tipo = "id_tipo_cliente"
    elif cadastrode=="Tipo de Projeto":
        tab_tipo="tipo_projeto"
        codigo_tipo = "id_tipo_projeto"
    elif cadastrode=="Tipo de Despesa":
        tab_tipo="tipo_despesa"
        codigo_tipo = "id_tipo_despesa"
    elif cadastrode=="Tipo de Situacao":
        tab_tipo="tipo_situacao"
        codigo_tipo = "id_tipo_situacao"

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE TIPOS E ATIVIDADES
    if botao_acionado == "Limpar":
        db = None
        db = get_db()
        cursor = db.cursor()
        sqlquery = "SELECT * FROM " + tab_tipo
        cursor.execute(sqlquery)
        dados = cursor.fetchall()
        mensagem = ""
        id_atividade=nome_atividade=id_tipo_cliente=tipo_cliente=id_tipo_projeto=tipo_projeto=id_tipo_despesa=tipo_despesa=id_tipo_situacao=tipo_situacao=""
        return render_template('tipos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                               nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, id_atividade=id_atividade, nome_atividade=nome_atividade,
                               id_tipo_cliente=id_tipo_cliente, tipo_cliente=tipo_cliente, id_tipo_projeto=id_tipo_projeto, tipo_projeto=tipo_projeto,
                               id_tipo_despesa=id_tipo_despesa, tipo_despesa=tipo_despesa, id_tipo_situacao=id_tipo_situacao, tipo_situacao=tipo_situacao,
                               cadastrode=cadastrode, dados_tipos=dados)

    ####################################################################################################################
    # LOCALIZA UMA ATIVIDADE OU TIPO
    elif botao_acionado == "Localizar":
        if request.form.get('cod_tipo') == "":
            #wait = input(f"Código de Tipo vazio {request.form.get('cod_tipo')}.")
            flash('Atenção! O código deve ser digitado. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO TIPO DIGITADO
            codigo_tipo = int(request.form.get('cod_tipo'))
            #wait = input(f"No botão Localizar em mantem_tipos Código digitado foi {request.form.get('cod_tipo')}.")
            db = None
            db = get_db()
            cursor = db.cursor()
            if cadastrode == "Atividade":
                tab_tipo = "atividade"
                cursor.execute("SELECT * FROM atividade WHERE id_atividade = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Cliente":
                tab_tipo = "tipo_cliente"
                cursor.execute("SELECT * FROM tipo_cliente WHERE id_tipo_cliente = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Projeto":
                tab_tipo = "tipo_projeto"
                cursor.execute("SELECT * FROM tipo_projeto WHERE id_tipo_projeto = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Despesa":
                tab_tipo = "tipo_despesa"
                cursor.execute("SELECT * FROM tipo_despesa WHERE id_tipo_despesa = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Situacao":
                tab_tipo = "tipo_situacao"
                cursor.execute("SELECT * FROM tipo_situacao WHERE id_tipo_situacao = ?", (codigo_tipo,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            #wait = input(f"No botão Localizar em mantem_tipos a variável cadastrode é {cadastrode}.")
            mensagem = ""
            id_atividade=nome_atividade=id_tipo_cliente=tipo_cliente=id_tipo_projeto=tipo_projeto=id_tipo_despesa=tipo_despesa=id_tipo_situacao=tipo_situacao=""
            #wait = input(f"No botão Localizar em mantem_tipos a leitura da base de {cadastrode} é {tamanho_dados}")
            #wait = input(f"No botão Localizar em mantem_tipos o nome da tabela sendo usada é {tab_tipo}")
            if tamanho_dados != 0:
                for tip in dados:
                    if cadastrode == "Atividade":
                        id_atividade = str(tip[0]).zfill(5)
                        nome_atividade = tip[1]
                    elif cadastrode == "Tipo de Cliente":
                        id_tipo_cliente = str(tip[0]).zfill(5)
                        tipo_cliente = tip[1]
                    elif cadastrode == "Tipo de Projeto":
                        id_tipo_projeto = str(tip[0]).zfill(5)
                        tipo_projeto = tip[1]
                    elif cadastrode == "Tipo de Despesa":
                        id_tipo_despesa = str(tip[0]).zfill(5)
                        tipo_despesa = tip[1]
                    elif cadastrode == "Tipo de Situacao":
                        id_tipo_situacao = str(tip[0]).zfill(5)
                        tipo_situacao = tip[1]
                ########################################################################################################
                # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
                db = None
                db = get_db()
                cursor = db.cursor()
                sqlquery = "SELECT * FROM " + tab_tipo
                cursor.execute(sqlquery)
                dados = cursor.fetchall()
                tamanho_dados = len(dados)
                #wait = input(f"No botão Localizar após localizar o registro em mantem_tipos a leitura de toda a base de {tab_tipo} é {tamanho_dados}")
                mensagem = ""
                return render_template('tipos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                                       nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, id_atividade=id_atividade, nome_atividade=nome_atividade,
                                       id_tipo_cliente=id_tipo_cliente, tipo_cliente=tipo_cliente, id_tipo_projeto=id_tipo_projeto, tipo_projeto=tipo_projeto,
                                       id_tipo_despesa=id_tipo_despesa, tipo_despesa=tipo_despesa, id_tipo_situacao=id_tipo_situacao, tipo_situacao=tipo_situacao,
                                       cadastrode=cadastrode, dados_tipos=dados)
            else:
                flash('Tipo ou Atividade não encontrado. Verifique!', category="warning")
                mensagem = ""

    ####################################################################################################################
    # ALTERAR UM TIPO - NÃO PRONTO
    elif botao_acionado == "Alterar":
        if request.form.get('cod_tipo') == "":
            #wait = input(f"Código de Atividade ou Tipo vazio {request.form.get('cod_loja')}.")
            flash('Atenção! O código deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DA ATIVIDADE OU TIPO DIGITADOS
            codigo_tipo = int(request.form.get('cod_tipo'))
            nome_tipo = request.form.get('nome_tipo')
            ############################################################################################################
            # ALTERAR UMA ATIVIDADE OU TIPO
            db = None
            db = get_db()
            cursor = db.cursor()
            if cadastrode == "Atividade":
                cursor.execute("UPDATE atividade SET nome_atividade = ? WHERE id_atividade = ?", (nome_tipo, codigo_tipo,))
            elif cadastrode == "Tipo de Cliente":
                cursor.execute("UPDATE tipo_cliente SET tipo_cliente = ? WHERE id_tipo_cliente = ?", (nome_tipo, codigo_tipo,))
            elif cadastrode == "Tipo de Projeto":
                cursor.execute("UPDATE tipo_projeto SET tipo_projeto = ? WHERE id_tipo_projeto = ?", (nome_tipo, codigo_tipo,))
            elif cadastrode == "Tipo de Despesa":
                cursor.execute("UPDATE tipo_despesa SET tipo_despesa = ? WHERE id_tipo_despesa = ?", (nome_tipo, codigo_tipo,))
            elif cadastrode == "Tipo de Situacao":
                cursor.execute("UPDATE tipo_situacao SET tipo_situacao = ? WHERE id_tipo_situacao = ?", (nome_tipo, codigo_tipo,))
            dados = cursor.fetchall()
            db.commit()
            flash('Registro alterado com sucesso!', category="warning")

    # INCLUIR UMA ATIVIDADE OU TIPO
    elif botao_acionado == "Incluir":
        ################################################################################################################
        # INCLUIR UMA LOJA - TESTA SE JÁ É CADASTRADO
        if request.form.get('cod_tipo') == "" or request.form.get('nome_tipo') == "":
            flash('Atenção! O código e o nome devem ser digitados. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO TIPO
            codigo_tipo = int(request.form.get('cod_tipo'))
            nome_tipo = request.form.get('nome_tipo')
            db = None
            db = get_db()
            cursor = db.cursor()
            if cadastrode == "Atividade":
                cursor.execute("SELECT * FROM atividade WHERE id_atividade = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Cliente":
                cursor.execute("SELECT * FROM tipo_cliente WHERE id_tipo_cliente = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Projeto":
                cursor.execute("SELECT * FROM tipo_projeto WHERE id_tipo_projeto = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Despesa":
                cursor.execute("SELECT * FROM tipo_despesa WHERE id_tipo_despesa = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Situacao":
                cursor.execute("SELECT * FROM tipo_situacao WHERE id_tipo_situacao = ?", (codigo_tipo,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            #wait = input(f"Na função mantem_tipos O tamanho_dados de Incluir é {tamanho_dados}. Fazendo a busca do tipo ou atividade")
            if tamanho_dados != 0:
                flash('Atenção! Código já cadastrado. Verifique!', category="warning")
            else:
                # IDENTIFICA OS CAMPOS DIGITADOS
                codigo_tipo = int(request.form.get('cod_tipo'))
                nome_tipo = request.form.get('nome_tipo')
                dados_grava = (codigo_tipo, nome_tipo)
                #wait = input(f"Na função mantem_tipos o dados_grava na inclusão é {dados_grava}. Fazendo a inclusão de uma atividade")
                db = None
                db = get_db()
                cursor = db.cursor()
                if cadastrode == "Atividade":
                    cursor.execute("INSERT INTO atividade (id_atividade, nome_atividade)  VALUES (?, ?);", dados_grava)
                elif cadastrode == "Tipo de Cliente":
                    cursor.execute("INSERT INTO tipo_cliente (id_tipo_cliente, tipo_cliente)  VALUES (?, ?);", dados_grava)
                elif cadastrode == "Tipo de Projeto":
                    cursor.execute("INSERT INTO tipo_projeto (id_tipo_projeto, tipo_projeto)  VALUES (?, ?);", dados_grava)
                elif cadastrode == "Tipo de Despesa":
                    cursor.execute("INSERT INTO tipo_despesa (id_tipo_despesa, tipo_despesa)  VALUES (?, ?);", dados_grava)
                elif cadastrode == "Tipo de Situacao":
                    cursor.execute("INSERT INTO tipo_situacao (id_tipo_situacao, tipo_situacao)  VALUES (?, ?);", dados_grava)
                db.commit()
                flash('Registro incluído com sucesso!', category="warning")

    ####################################################################################################################
    # EXCLUIR UMA ATIVIDADE OU UM TIPO
    elif botao_acionado == "Excluir":
        if request.form.get('cod_tipo') == "":
            # wait = input(f"Código de Atividade ou Tipo vazio {request.form.get('cod_tipo')}.")
            flash('Atenção! O código da atividade ou o tipo deve ser digitado. Verifique!', category="warning")
        else:
            # ESTA MENSAGEM VEM DO INPUT mensagem_excluir - oculto no form TIPOS
            mensagem = request.form.get('mensagem_excluir')
            #wait = input(f"Mensagem {mensagem}.")
            if mensagem == "Sim":
                # IDENTIFICA O CÓDIGO DA ATIVIDADE OU TIPO
                codigo_tipo = int(request.form.get('cod_tipo'))
                db = None
                db = get_db()
                cursor = db.cursor()
                if cadastrode == "Atividade":
                    cursor.execute("DELETE FROM atividade WHERE id_atividade = ?", (codigo_tipo,))
                elif cadastrode == "Tipo de Cliente":
                    cursor.execute("DELETE FROM tipo_cliente WHERE id_tipo_cliente = ?", (codigo_tipo,))
                elif cadastrode == "Tipo de Projeto":
                    cursor.execute("DELETE FROM tipo_projeto WHERE id_tipo_projeto = ?", (codigo_tipo,))
                elif cadastrode == "Tipo de Despesa":
                    cursor.execute("DELETE FROM tipo_despesa WHERE id_tipo_despesa = ?", (codigo_tipo,))
                elif cadastrode == "Tipo de Situacao":
                    cursor.execute("DELETE FROM tipo_situacao WHERE id_tipo_situacao = ?", (codigo_tipo,))
                dados = cursor.fetchall()
                db.commit()
                flash('Registro excluído com sucesso!', category="warning")
            else:
                flash('Exclusão cancelada!', category="warning")



    ####################################################################################################################
    # GERA ARQUIVO EXCEL/TX/PDF
    elif botao_acionado == "Excel/TXT":
        db = None
        db = get_db()
        cursor = db.cursor()
        if request.form.get('cod_tipo') == "":
            codigo_tipo = 0
            if cadastrode == "Atividade":
                nome_arq_TXT = "atividades" + ".txt"
                nome_arq_XLSX = "atividades" + ".xlsx"
                tit2 = "Relação de Atividades Cadastradas" + "\n"
                cursor.execute("SELECT * FROM atividade")
            elif cadastrode == "Tipo de Cliente":
                nome_arq_TXT = "tipocliente" + ".txt"
                nome_arq_XLSX = "tipocliente" + ".xlsx"
                tit2 = "Relação de Tipos de Clientes Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_cliente")
            elif cadastrode == "Tipo de Projeto":
                nome_arq_TXT = "tipoprojeto" + ".txt"
                nome_arq_XLSX = "tipoprojeto" + ".xlsx"
                tit2 = "Relação de Tipos de Projetos Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_projeto")
            elif cadastrode == "Tipo de Despesa":
                nome_arq_TXT = "tipodespesa" + ".txt"
                nome_arq_XLSX = "tipodespesa" + ".xlsx"
                tit2 = "Relação de Tipos de Despesas Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_despesa")
            elif cadastrode == "Tipo de Situacao":
                nome_arq_TXT = "tiposituacao" + ".txt"
                nome_arq_XLSX = "tiposituacao" + ".xlsx"
                tit2 = "Relação de Tipos de Situação Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_situacao")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DA ATIVIDADE OU TIPO
            codigo_tipo = int(request.form.get('cod_tipo'))
            tit1 = tit2 = tit3 = ""
            if cadastrode == "Atividade":
                nome_arq_TXT = "atividades" + ".txt"
                nome_arq_XLSX = "atividades" + ".xlsx"
                tit2 = "Relação de Atividades Cadastradas" + "\n"
                cursor.execute("SELECT * FROM atividade WHERE id_atividade = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Cliente":
                nome_arq_TXT = "tipocliente" + ".txt"
                nome_arq_XLSX = "tipocliente" + ".xlsx"
                tit2 = "Relação de Tipos de Clientes Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_cliente WHERE id_tipo_cliente = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Projeto":
                nome_arq_TXT = "tipoprojeto" + ".txt"
                nome_arq_XLSX = "tipoprojeto" + ".xlsx"
                tit2 = "Relação de Tipos de Projetos Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_projeto WHERE id_tipo_projeto = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Despesa":
                nome_arq_TXT = "tipodespesa" + ".txt"
                nome_arq_XLSX = "tipodespesa" + ".xlsx"
                tit2 = "Relação de Tipos de Despesas Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_despesa WHERE id_tipo_despesa = ?", (codigo_tipo,))
            elif cadastrode == "Tipo de Situacao":
                nome_arq_TXT = "tiposituacao" + ".txt"
                nome_arq_XLSX = "tiposituacao" + ".xlsx"
                tit2 = "Relação de Tipos de Situação Cadastrados" + "\n"
                cursor.execute("SELECT * FROM tipo_situacao WHERE id_tipo_situacao = ?", (codigo_tipo,))

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO TXT
        arq_TXT = "static\\arquivos_txt\\" + nome_arq_TXT
        if (os.path.exists(arq_TXT)):
            arquivo = open(arq_TXT, 'w')
        else:
            arquivo = open(arq_TXT, 'x')

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO MS-Excel
        arq_XLSX = "static\\arquivos_xlsx\\" + nome_arq_XLSX

        ################################################################################################################
        ## FAZ A LEITURA DA BASE DE DADOS
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        id_atividade = nome_atividade = id_tipo_cliente = tipo_cliente = id_tipo_projeto = tipo_projeto = id_tipo_despesa = tipo_despesa = id_tipo_situacao = tipo_situacao = ""
        if tamanho_dados != 0:
            mensagem = ""
            tit1 = "SGEA-Sistema Gerenciador de Escritório de Arquitetura" + "\n"
            tit3 = "-----------------------------------------------------" + "\n"
            arquivo.write(tit1 + tit2 + tit3)

            for tip in dados:
                cod_tipo = tip[0]
                nome_tipo = tip[1]
                cod_tipo = str(tip[0]).zfill(5)
                cod_tipo_grava = cod_tipo.zfill(5)
                nome_tipo = nome_tipo.upper()
                nome_tipo = "{0:<80}".format(nome_tipo)
                linha_grava = cod_tipo + nome_tipo + "\n"
                linha_grava = ("ID: " + cod_tipo + " - " + "Nome: " + nome_tipo + "\n")
                #wait = input(f"Linha grava {linha_grava}.")
                arquivo.write(linha_grava)

            arquivo.close()

            ############################################################################################################
            ## 1-GERA UM df =: DATAFRAME COM O SQL GERADO - USANDO PANDAS
            df = pd.DataFrame(dados)

            ############################################################################################################
            ## O CABEÇALHO DAS COLUNAS PODE SER CRIADO DE DUAS MANEIRAS:
            ## 1- ATRIBUI A columns OS TÍTULOS DAS COLUNAS DO BD SQL PARA USAR COMO CABEÇALHO NO EXCEL
            ##    AS COLUNAS SÃO GERADAS NO MOMENTO DA GERAÇÃO DO SQL NO con
            # columns = [desc[0] for desc in con.description]
            # df = pd.DataFrame(list(sqlquery), columns=columns)
            # df.to_excel(arq_XLS, sheet_name="Lojas", index=False, startcol=0, startrow=0)
            ############################################################################################################
            ## 2- ATRIBUI A VARIÁVEL alias OS CABEÇALHOS DAS COLUNAS
            ##    NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias
            ##    SE NÃO USAR O alias O CABEÇALHO SERÁ 0,1,2,3,4,5
            ########################################################################################
            ## VAMOS USAR O MÉTODO with... PODE GERAR UMA OU VÁRIAS  PLANILHAS NO MESMO ARQUIVO
            ## NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias index=False
            ## NESTE CASO VAMOS CRIAR UM ARQUIVO XLSX COM 1 PLANILHA - Lojas
            if cadastrode == "Atividade":
                alias = ["ID_ATIVIDADE", "NOME_ATIVIDADE"]
                with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                    df.to_excel(ew, sheet_name="Atividades", index=False, header=alias)
            elif cadastrode == "Tipo de Cliente":
                alias = ["ID_TIPO_CLIENTE", "TIPO_CLIENTE"]
                with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                    df.to_excel(ew, sheet_name="Tipo_Cliente", index=False, header=alias)
            elif cadastrode == "Tipo de Projeto":
                alias = ["ID_TIPO_PROJETO", "TIPO_PROJETO"]
                with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                    df.to_excel(ew, sheet_name="Tipo_Projeto", index=False, header=alias)
            elif cadastrode == "Tipo de Despesa":
                alias = ["ID_TIPO_DESPESA", "TIPO_DESPESA"]
                with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                    df.to_excel(ew, sheet_name="Tipo_Despesa", index=False, header=alias)
            elif cadastrode == "Tipo de Situacao":
                alias = ["ID_TIPO_SITUACAO", "TIPO_SITUACAO"]
                with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                    df.to_excel(ew, sheet_name="Tipo_Situacao", index=False, header=alias)

            ############################################################################################################
            ## PODEMOS APENDAR UM DATAFRAME DENTRO DE OUTRO PARA GRAVAR EM UMA PLANILHA
            ## APENDA O DATA FRAME df1 NO DATA FRAME df
            # df1 = pd.DataFrame(sqlquery)
            # df3 = df1.append(df1, ignore_index=False, sort=False)
            ############################################################################################################
            ## PODEMOS INCLUIR UMA NOVA PLANILHA DENTRO DO ARQUIVO JÁ GERADO
            ## CRIAMOS A PLANILHA Vendas2 COM O df3 QUE APENDOU O df1
            # with pd.ExcelWriter(arq_XLS1, engine="openpyxl", mode="a") as ew:
            # df3.to_excel(ew, sheet_name="Vendas2", index=False, header=alias)
            cursor.close()
            flash("Arquivo (Excel) - Lojas.xlsx na pasta /static/arquivos_xlsx e Arquivo (TXT) - Lojas.txt na pasta /static/arquivos_txt  => gerados com sucesso!", category="warning")

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA DE ATIVIDADES OU TIPOS PARA LISTAR NO FORM TIPOS
    db = None
    db = get_db()
    cursor = db.cursor()
    if cadastrode == "Atividade":
        cursor.execute("SELECT * FROM atividade")
    elif cadastrode == "Tipo de Cliente":
        cursor.execute("SELECT * FROM tipo_cliente")
    elif cadastrode == "Tipo de Projeto":
        cursor.execute("SELECT * FROM tipo_projeto")
    elif cadastrode == "Tipo de Despesa":
        cursor.execute("SELECT * FROM tipo_despesa")
    elif cadastrode == "Tipo de Situacao":
        cursor.execute("SELECT * FROM tipo_situacao")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    mensagem = ""
    id_atividade=nome_atividade=id_tipo_cliente=tipo_cliente=id_tipo_projeto=tipo_projeto=id_tipo_despesa=tipo_despesa=id_tipo_situacao=tipo_situacao= ""
    #wait = input(f"Na função mantem_titulos o botão Localizar em mantem_tipos a leitura da base de {cadastrode} é {tamanho_dados}")
    #wait = input(f"Na função mantem_titulos o botão Localizar em mantem_tipos o nome da tabela sendo usada é {tab_tipo}")
    return render_template('tipos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                           nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, id_atividade=id_atividade,
                           nome_atividade=nome_atividade, id_tipo_cliente=id_tipo_cliente, tipo_cliente=tipo_cliente,
                           id_tipo_projeto=id_tipo_projeto, tipo_projeto=tipo_projeto, id_tipo_despesa=id_tipo_despesa, tipo_despesa=tipo_despesa,
                           id_tipo_situacao=id_tipo_situacao, tipo_situacao=tipo_situacao, cadastrode=cadastrode, dados_tipos=dados)


########################################################################################################################
# ROTA PARA EDITAR UMA ATIVIDADE OU TIPOS ELECIONADO NA TABLE
@app.route('/edita_tipo/<int:record_id>, <cod_usu_ativo>, <nome_usu_ativo>, <cadastrode>')
def edita_tipo(record_id, cod_usu_ativo, nome_usu_ativo, cadastrode):

    codigo_tipo = record_id
    #wait = input(f"Na função edita_tipo - O código da Atividade ou Tipo selecionado é {codigo_tipo}.")
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    cadastrode = cadastrode
    #wait = input(f"Na função edita_usuario - O código do Usuário ativo lido é {cod_usu_ativo}.")
    #wait = input(f"Na função edita_usuario - O Nome do Usuário ativo lido é {nome_usu_ativo}.")

    db = None
    db = get_db()
    cursor = db.cursor()
    if cadastrode == "Atividade":
        cursor.execute("SELECT * FROM atividade WHERE id_atividade = ?", (codigo_tipo,))
    elif cadastrode == "Tipo de Cliente":
        cursor.execute("SELECT * FROM tipo_cliente WHERE id_tipo_cliente = ?", (codigo_tipo,))
    elif cadastrode == "Tipo de Projeto":
        cursor.execute("SELECT * FROM tipo_projeto WHERE id_tipo_projeto = ?", (codigo_tipo,))
    elif cadastrode == "Tipo de Despesa":
        cursor.execute("SELECT * FROM tipo_despesa WHERE id_tipo_despesa = ?", (codigo_tipo,))
    elif cadastrode == "Tipo de Situacao":
        cursor.execute("SELECT * FROM tipo_situacao WHERE id_tipo_situacao = ?", (codigo_tipo,))
    dados = cursor.fetchall()
    # db.commit()
    tamanho_dados = len(dados)
    #wait = input(f"Na função edita_tipo - tamanho_dados para a atividade ou tipo selecioonado é {tamanho_dados}.")
    mensagem = ""
    id_atividade = nome_atividade = id_tipo_cliente = tipo_cliente = id_tipo_projeto = tipo_projeto = id_tipo_despesa = tipo_despesa = id_tipo_situacao = tipo_situacao = ""
    if tamanho_dados != 0:
        mensagem = ""
        for tip in dados:
            if cadastrode == "Atividade":
                id_atividade = str(tip[0]).zfill(5)
                nome_atividade = tip[1]
            elif cadastrode == "Tipo de Cliente":
                id_tipo_cliente = str(tip[0]).zfill(5)
                tipo_cliente = tip[1]
            elif cadastrode == "Tipo de Projeto":
                id_tipo_projeto = str(tip[0]).zfill(5)
                tipo_projeto = tip[1]
            elif cadastrode == "Tipo de Despesa":
                id_tipo_despesa = str(tip[0]).zfill(5)
                tipo_despesa = tip[1]
            elif cadastrode == "Tipo de Situacao":
                id_tipo_situacao = str(tip[0]).zfill(5)
                tipo_situacao = tip[1]

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA USUÁRIOS PARA LISTAR NO FORM USUARIOS
    db = None
    db = get_db()
    cursor = db.cursor()
    if cadastrode == "Atividade":
        cursor.execute("SELECT * FROM atividade")
    elif cadastrode == "Tipo de Cliente":
        cursor.execute("SELECT * FROM tipo_cliente")
    elif cadastrode == "Tipo de Projeto":
        cursor.execute("SELECT * FROM tipo_projeto")
    elif cadastrode == "Tipo de Despesa":
        cursor.execute("SELECT * FROM tipo_despesa")
    elif cadastrode == "Tipo de Situacao":
        cursor.execute("SELECT * FROM tipo_situacao")
    dados = cursor.fetchall()
    mensagem = ""
    return render_template('tipos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu_ativo, id_atividade=id_atividade, nome_atividade=nome_atividade, id_tipo_cliente=id_tipo_cliente,
                           tipo_cliente=tipo_cliente, id_tipo_projeto=id_tipo_projeto, tipo_projeto=tipo_projeto, id_tipo_despesa=id_tipo_despesa,
                           tipo_despesa=tipo_despesa, id_tipo_situacao=id_tipo_situacao, tipo_situacao=tipo_situacao,
                           cadastrode=cadastrode, dados_tipos=dados)


########################################################################################################################
# Rota para Manutenção de Clientes
@app.route('/mantem_clientes', methods=['GET', 'POST'])
def mantem_clientes():

    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_busca_cliente')
    #wait = input(f"O botão de clientes acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()
    #wait = input(f"Na função mantem_loja - Usuário ativo é {cod_usu_ativo} e nome do usuário ativo é {nome_usu_ativo}.")
    ################################################################################################################
    # BUSCA OS TIPOS DE ATIVIDADES PARA LISTAR NO FORM CLIENTES
    lista_atividadecliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM atividade")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for ativ in dados:
            cod_ativ = str(ativ[0]).zfill(2)
            nome_ativ = ativ[1]
            lista_atividadecliente.append(cod_ativ + "-" + nome_ativ)
    default_atividade = "01"

    ####################################################################################################################
    # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM CLIENTES
    lista_tipocliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_cliente")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            cod_tip = str(tip[0]).zfill(2)
            nome_tip = tip[1]
            lista_tipocliente.append(cod_tip + "-" + nome_tip)
    default_tipocliente = "01"

    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE CLIENTES
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE CLIENTES
    if botao_acionado == "Limpar":
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA LOJAS PARA LISTAR NO FORM LOJAS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM clientes")
        dados = cursor.fetchall()
        cod_cliente=nome_cliente=razao_social_cliente=nome_fantasia_cliente=fone_cliente=email_cliente=cpf_cliente=cnpj_cliente=atividade_cliente=""
        tipo_cliente=contato_cliente=data_nasc_cont_cliente=cpf_contato_cliente=cidade_cliente=uf_cliente=endereco_cliente=cep_cliente=func_resp_cliente=""
        mensagem = ""
        default_atividade = "01"
        default_tipocliente = "01"
        default_estados = 'PR'
        #  TEM QUE COLOCAR A LISTA DE TIPO DE CLIENTES E DE ATIVIDADES
        return render_template('clientes.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                               cod_usuario=cod_usu_ativo, dados_clientes=dados, lista_atividadecliente=lista_atividadecliente, default_atividade=default_atividade,
                               lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente, lista_estados=lista_estados, default_estados=default_estados)

    ####################################################################################################################
    # LOCALIZA UM CLIENTE
    elif botao_acionado == "Localizar":
        if request.form.get('cod_cliente') == "":
            # wait = input(f"Código de Cliente vazio {request.form.get('cod_cliente')}.")
            flash('Atenção! O código do Cliente deve ser digitado. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO CLIENTE
            codigo_cliente = int(request.form.get('cod_cliente'))
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            cod_cliente = nome_cliente = razao_social_cliente = nome_fantasia_cliente = fone_cliente = email_cliente = cpf_cliente = cnpj_cliente = atividade_cliente = ""
            tipo_cliente = contato_cliente = data_nasc_cont_cliente = cpf_contato_cliente = cidade_cliente = uf_cliente = endereco_cliente = cep_cliente = func_resp_cliente = ""
            #wait = input(f"Na função mantem_cliente O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca de clientes")
            if tamanho_dados != 0:
                mensagem = ""
                for cli in dados:
                    cod_cliente = str(cli[0]).zfill(5)
                    nome_cliente = cli[1]
                    razao_social_cliente = cli[2]
                    nome_fantasia_cliente = cli[3]
                    fone_cliente = cli[4]
                    email_cliente = cli[5]
                    cpf_cliente = cli[6]
                    cnpj_cliente = cli[7]
                    tipo_cliente = cli[8]
                    atividade_cliente = cli[9]
                    contato_cliente = cli[10]
                    cpf_contato_cliente = cli[11]
                    data_nasc_cont_cliente = cli[12]
                    cidade_cliente = cli[13]
                    uf_cliente = cli[14]
                    endereco_cliente = cli[15]
                    cep_cliente = cli[16]
                    func_resp_cliente = cli[17]
                    ####################################################################################################
                    # BUSCA TODOS OS REGISTROS DA TABELA CLIENTES PARA LISTAR NO FORM CLIENTES
                    db = None
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM clientes")
                    dados = cursor.fetchall()
                    #wait = input(f"Dados da tabela Clientes: cidade do Cliente: {cidade_cliente}.")
                    return render_template('clientes.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                                           cod_usuario=cod_usu_ativo, cod_cliente=cod_cliente, nome_cliente=nome_cliente, razao_social_cliente=razao_social_cliente,
                                           nome_fantasia_cliente=nome_fantasia_cliente, fone_cliente=fone_cliente, email_cliente=email_cliente, cpf_cliente=cpf_cliente,
                                           cnpj_cliente=cnpj_cliente, tipo_cliente=tipo_cliente, atividade_cliente=atividade_cliente, contato_cliente=contato_cliente,
                                           cpf_contato_cliente=cpf_contato_cliente, data_nasc_cont_cliente=data_nasc_cont_cliente, cidade_cliente=cidade_cliente,
                                           uf_cliente=uf_cliente, endereco_cliente=endereco_cliente, cep_cliente=cep_cliente, func_resp_cliente=func_resp_cliente,
                                           lista_atividadecliente=lista_atividadecliente, lista_tipocliente=lista_tipocliente,lista_estados=lista_estados, dados_clientes=dados)
            else:
                # wait = input("Cliente não encontrado")
                flash('Cliente não encontrado. Verifique!', category="warning")
                #mensagem = "Atenção! Cliente não encontrado. Verifique!"
                mensagem = ""
                # return redirect(url_for("login"))
                #return render_template('clientes.html', mens=mensagem, cod_usu_ativo = cod_usu_ativo, nome_usu_ativo = nome_usu_ativo)

    ####################################################################################################################
    # ALTERAR UM CLIENTE
    elif botao_acionado == "Alterar":
        if request.form.get('cod_cliente') == "":
            # wait = input(f"Código do Cliente vazio {request.form.get('cod_cliente')}.")
            flash('Atenção! O código do cliente deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO CLIENTE
            codigo_cliente = int(request.form.get('cod_cliente'))
            # IDENTIFICA OS CAMPOS DIGITADOS
            nome_cliente = request.form.get('nome_cliente')
            razao_social_cliente = request.form.get('razao_cliente')
            nome_fantasia_cliente = request.form.get('fantasia_cliente')
            fone_cliente = request.form.get('fone_cliente')
            email_cliente = request.form.get('email_cliente')
            cpf_cliente = request.form.get('cpf_cliente')
            cnpj_cliente = request.form.get('cnpj_cliente')
            tipo_cliente = request.form.get('tipo_cliente')
            atividade_cliente = request.form.get('atividade_cliente')
            contato_cliente = request.form.get('contato_cliente')
            cpf_contato_cliente = request.form.get('cpf_contato_cliente')
            data_nasc_cont_cliente = request.form.get('dtnasc_cont_cliente')
            cidade_cliente = request.form.get('cidade_cliente')
            uf_cliente = request.form.get('estados')
            endereco_cliente = request.form.get('endereco_cliente')
            cep_cliente = request.form.get('cep_cliente')
            func_resp_cliente = request.form.get('func_resp_cliente')

            ############################################################################################################
            # ALTERAR UM CLIENTE
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE clientes SET nome_cliente = ?, razao_social_cliente = ?, nome_fantasia_cliente = ?, fone_cliente = ?, email_cliente = ?, \
                           cpf_cliente = ?, cnpj_cliente = ?, tipo_cliente = ?, atividade_cliente = ?, contato_cliente = ?, cpf_contato_cliente = ?, \
                           data_nasc_cont_cliente = ?, cidade_cliente = ?, uf_cliente = ?, endereco_cliente = ?, cep_cliente = ?, usuario_cliente = ? \
                           WHERE id_cliente = ?", (nome_cliente, razao_social_cliente, nome_fantasia_cliente, fone_cliente, email_cliente, cpf_cliente,
                           cnpj_cliente, tipo_cliente, atividade_cliente, contato_cliente, cpf_contato_cliente, data_nasc_cont_cliente, cidade_cliente,
                           uf_cliente, endereco_cliente, cep_cliente, func_resp_cliente, codigo_cliente,))
            db.commit()
            flash('Registro alterado com sucesso!', category="warning")

    ####################################################################################################################
    # INCLUIR UMA CLIENTE
    elif botao_acionado == "Incluir":
        ################################################################################################################
        # INCLUIR UM CLIENTE - TESTA SE JÁ É CADASTRADO
        if request.form.get('cod_cliente') == "":
            flash('Atenção! O código do cliente deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO CLIENTE
            codigo_cliente = int(request.form.get('cod_cliente'))

            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                flash('Atenção! Cliente já cadastrado. Verifique!', category="warning")
            else:
                # IDENTIFICA O CÓDIGO DO CLIENTE
                codigo_cliente = int(request.form.get('cod_cliente'))
                nome_cliente = request.form.get('nome_cliente')
                razao_social_cliente = request.form.get('razao_cliente')
                nome_fantasia_cliente = request.form.get('fantasia_cliente')
                fone_cliente = request.form.get('fone_cliente')
                email_cliente = request.form.get('email_cliente')
                cpf_cliente = request.form.get('cpf_cliente')
                cnpj_cliente = request.form.get('cnpj_cliente')
                tipo_cliente = request.form.get('tipo_cliente')
                atividade_cliente = request.form.get('atividade_cliente')
                contato_cliente = request.form.get('contato_cliente')
                cpf_contato_cliente = request.form.get('cpf_contato_cliente')
                data_nasc_cont_cliente = request.form.get('dtnasc_cont_cliente')
                cidade_cliente = request.form.get('cidade_cliente')
                uf_cliente = request.form.get('estados')
                endereco_cliente = request.form.get('endereco_cliente')
                cep_cliente = request.form.get('cep_cliente')
                func_resp_cliente = request.form.get('func_resp_cliente')
                db = None
                db = get_db()
                cursor = db.cursor()
                dados_grava = (codigo_cliente, nome_cliente, razao_social_cliente, nome_fantasia_cliente, fone_cliente, email_cliente, cpf_cliente,
                           cnpj_cliente, tipo_cliente, atividade_cliente, contato_cliente, cpf_contato_cliente, data_nasc_cont_cliente, cidade_cliente,
                           uf_cliente, endereco_cliente, cep_cliente, func_resp_cliente)
                cursor.execute("INSERT INTO clientes (id_cliente, nome_cliente, razao_social_cliente, nome_fantasia_cliente, fone_cliente, \
                                email_cliente, cpf_cliente, cnpj_cliente, tipo_cliente, atividade_cliente, contato_cliente, cpf_contato_cliente, \
                                data_nasc_cont_cliente, cidade_cliente, uf_cliente, endereco_cliente, cep_cliente, usuario_cliente) \
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", dados_grava)
                db.commit()
                flash('Registro incluído com sucesso!', category="warning")

    ####################################################################################################################
    # EXCLUIR UM CLIENTE
    elif botao_acionado == "Excluir":
        if request.form.get('cod_cliente') == "":
            flash('Atenção! O código do cliente deve ser digitado. Verifique!', category="warning")
        else:
            # ESTA MENSAGEM VEM DO INPUT mensagem_excluir - oculto no form CLIENTES
            mensagem = request.form.get('mensagem_excluir')
            #wait = input(f"Mensagem {mensagem}.")
            if mensagem == "Sim":
                # IDENTIFICA O CÓDIGO DO CLIENTE
                codigo_cliente = int(request.form.get('cod_cliente'))
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
                dados = cursor.fetchall()
                db.commit()
                flash('Registro excluído com sucesso!', category="warning")
            else:
                flash('Exclusão cancelada!', category="warning")

    ####################################################################################################################
    # GERA ARQUIVO EXCEL/TX/PDF
    elif botao_acionado == "Excel/TXT":
        db = None
        db = get_db()
        cursor = db.cursor()

        if request.form.get('cod_cliente') == "":
            codigo_cliente = 0
            cursor.execute("SELECT * FROM clientes")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO CLIENTE
            codigo_cliente = int(request.form.get('cod_cliente'))
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (codigo_cliente,))

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO TXT
        nome_arq_TXT = "clientes" + ".txt"
        arq_TXT = "static\\arquivos_txt\\" + nome_arq_TXT
        if (os.path.exists(arq_TXT)):
            arquivo = open(arq_TXT, 'w')
        else:
            arquivo = open(arq_TXT, 'x')

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO MS-Excel
        nome_arq_XLSX = "clientes" + ".xlsx"
        arq_XLSX = "static\\arquivos_xlsx\\" + nome_arq_XLSX

        ################################################################################################################
        ## FAZ A LEITURA DA BASE DE DADOS
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        cod_cliente = nome_cliente = razao_social_cliente = nome_fantasia_cliente = fone_cliente = email_cliente = cpf_cliente = cnpj_cliente = atividade_cliente = ""
        tipo_cliente = contato_cliente = data_nasc_cont_cliente = cpf_contato_cliente = cidade_cliente = uf_cliente = endereco_cliente = cep_cliente = func_resp_cliente = ""
        cod_loja = nome_loja = cnpj_loja = atividade_loja = contato_loja = fone_loja = email_loja = cidade_loja = uf_loja = ""
        if tamanho_dados != 0:
            mensagem = ""
            tit1 = "SGEA-Sistema Gerenciador de Escritório de Arquitetura" + "\n"
            tit2 = "Relação de Clientes Cadastrados" + "\n"
            tit3 = "-----------------------------------------------------" + "\n"
            arquivo.write(tit1 + tit2 + tit3)
            # wait = input(f"Na função mantem_cliente O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca de clientes")
            for cli in dados:
                cod_cliente = str(cli[0]).zfill(5)
                nome_cliente = cli[1]
                razao_social_cliente = cli[2]
                nome_fantasia_cliente = cli[3]
                fone_cliente = cli[4]
                email_cliente = cli[5]
                cpf_cliente = cli[6]
                cnpj_cliente = cli[7]
                tipo_cliente = cli[8]
                atividade_cliente = cli[9]
                contato_cliente = cli[10]
                cpf_contato_cliente = cli[11]
                data_nasc_cont_cliente = cli[12]
                cidade_cliente = cli[13]
                uf_cliente = cli[14]
                endereco_cliente = cli[15]
                cep_cliente = cli[16]
                func_resp_cliente = cli[17]

                cod_cliente = str(cli[0]).zfill(5)
                nome_cliente = "{0:<80}".format(nome_cliente).upper()
                razao_social_cliente = "{0:<80}".format(razao_social_cliente).upper()
                nome_fantasia_cliente = "{0:<80}".format(nome_fantasia_cliente).upper()
                fone_cliente = fone_cliente.strip()
                if len(fone_cliente) < 15:
                    fone_cliente = "{0:<15}".format(fone_cliente)
                email_cliente = email_cliente.strip()
                if len(email_cliente) < 50:
                    email_cliente = "{0:<50}".format(email_cliente)
                cpf_cliente = cpf_cliente.strip()
                if len(cpf_cliente) < 14:
                    cpf_cliente = "{0:<14}".format(cpf_cliente)
                cnpj_cliente = cnpj_cliente.strip()
                if len(cnpj_cliente) < 19:
                    cnpj_cliente = "{0:<19}".format(cnpj_cliente)
                tipo_cliente = "{0:<60}".format(tipo_cliente).upper()
                atividade_cliente = "{0:<60}".format(atividade_cliente).upper()
                contato_cliente = "{0:<50}".format(contato_cliente)
                cpf_contato_cliente = cpf_contato_cliente.strip()
                if len(cpf_contato_cliente) < 14:
                    cpf_contato_cliente = "{0:<14}".format(cpf_contato_cliente)
                data_nasc_cont_cliente = data_nasc_cont_cliente
                cidade_cliente = cidade_cliente.strip()
                if len(cidade_cliente) < 80:
                    cidade_cliente = "{0:<80}".format(cidade_cliente)
                uf_cliente = uf_cliente.strip()
                endereco_cliente = endereco_cliente.strip()
                cep_cliente = cep_cliente.strip()
                usuario_cliente = func_resp_cliente.strip()
                #linha_grava = cod_loja + nome_loja + cnpj_loja + atividade_loja + contato_loja + fone_loja + email_loja + cidade_loja + uf_loja + "\n"
                linha_grava = ("ID: " + cod_cliente + "\n"
                               "Nome: " + nome_cliente + "\n"
                               "Razão Social:" + razao_social_cliente + "\n" 
                               "Nome Fantasia:" + nome_fantasia_cliente + "\n"
                               "Fone:" + fone_cliente + "\n"
                               "Email:" + email_cliente + "\n"     
                               "CPF:" + cpf_cliente + "\n"
                               "CNPJ: " + cnpj_cliente + "\n"
                               "Tipo:" + tipo_cliente + "\n"
                               "Atividade: " + atividade_cliente + "\n"
                               "Contato: " + contato_cliente + "\n"
                               "CPF Contato: " + cpf_contato_cliente + "\n"
                               "Data nasc.Contato:" + data_nasc_cont_cliente + "\n"                                                       
                               "Cidade: " + cidade_cliente + "\n"
                               "UF: " + uf_cliente + "\n"
                               "Endereço: " + endereco_cliente + "\n"
                               "CEP: " + cep_cliente + "\n"
                               "Responsável: " + usuario_cliente + "\n" + "\n")
                #wait = input(f"Linha grava {linha_grava}.")
                arquivo.write(linha_grava)

            arquivo.close()

            ############################################################################################################
            ## 1-GERA UM df =: DATAFRAME COM O SQL GERADO - USANDO PANDAS
            df = pd.DataFrame(dados)

            ############################################################################################################
            ## O CABEÇALHO DAS COLUNAS PODE SER CRIADO DE DUAS MANEIRAS:
            ## 1- ATRIBUI A columns OS TÍTULOS DAS COLUNAS DO BD SQL PARA USAR COMO CABEÇALHO NO EXCEL
            ##    AS COLUNAS SÃO GERADAS NO MOMENTO DA GERAÇÃO DO SQL NO con
            # columns = [desc[0] for desc in con.description]
            # df = pd.DataFrame(list(sqlquery), columns=columns)
            # df.to_excel(arq_XLS, sheet_name="Lojas", index=False, startcol=0, startrow=0)
            ############################################################################################################
            ## 2- ATRIBUI A VARIÁVEL alias OS CABEÇALHOS DAS COLUNAS
            ##    NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias
            ##    SE NÃO USAR O alias O CABEÇALHO SERÁ 0,1,2,3,4,5
            ############################################################################################################
            ## VAMOS USAR O MÉTODO with... PODE GERAR UMA OU VÁRIAS  PLANILHAS NO MESMO ARQUIVO
            ## NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias index=False
            ## NESTE CASO VAMOS CRIAR UM ARQUIVO XLSX COM 1 PLANILHA - Lojas
            alias = ["ID_CLIENTE", "NOME_CLIENTE", "RAZÃO SOCIAL", "NOME FANTASIA", "FONE", "EMAIL", "CPF", "CNPJ",
                     "TIPO", "ATIVIDADE", "CONTATO", "CPF_CONTATO", "DATA_NASC_CONTATO", "CIDADE", "UF", "ENDEREÇO", "CEP", "RESPONSÁVEL"]
            with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                df.to_excel(ew, sheet_name="Clientes", index=False, header=alias)

            ############################################################################################################
            ## PODEMOS APENDAR UM DATAFRAME DENTRO DE OUTRO PARA GRAVAR EM UMA PLANILHA
            ## APENDA O DATA FRAME df1 NO DATA FRAME df
            # df1 = pd.DataFrame(sqlquery)
            # df3 = df1.append(df1, ignore_index=False, sort=False)
            ############################################################################################################
            ## PODEMOS INCLUIR UMA NOVA PLANILHA DENTRO DO ARQUIVO JÁ GERADO
            ## CRIAMOS A PLANILHA Vendas2 COM O df3 QUE APENDOU O df1
            # with pd.ExcelWriter(arq_XLS1, engine="openpyxl", mode="a") as ew:
            # df3.to_excel(ew, sheet_name="Vendas2", index=False, header=alias)
            cursor.close()
            flash("Arquivo (Excel) - clientes.xlsx na pasta /static/arquivos_xlsx e Arquivo (TXT) - clientes.txt na pasta /static/arquivos_txt  => gerados com sucesso!", category="warning")

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA CLIENTE PARA LISTAR NO FORM CLIENTES
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    cod_cliente = nome_cliente = razao_social_cliente = nome_fantasia_cliente = fone_cliente = email_cliente = cpf_cliente = cnpj_cliente = atividade_cliente = ""
    tipo_cliente = contato_cliente = data_nasc_cont_cliente = cpf_contato_cliente = cidade_cliente = uf_cliente = endereco_cliente = cep_cliente = func_resp_cliente = ""
    mensagem = ""
    default_atividade = "01"
    default_tipocliente = "01"
    default_estados = "PR"
    return render_template('clientes.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu_ativo, cod_cliente=cod_cliente, nome_cliente=nome_cliente,
                           razao_social_cliente=razao_social_cliente, nome_fantasia_cliente=nome_fantasia_cliente, fone_cliente=fone_cliente,
                           email_cliente=email_cliente, cpf_cliente=cpf_cliente, cnpj_cliente=cnpj_cliente, tipo_cliente=tipo_cliente, atividade_cliente=atividade_cliente,
                           contato_cliente=contato_cliente, cpf_contato_cliente=cpf_contato_cliente, data_nasc_cont_cliente=data_nasc_cont_cliente, cidade_cliente=cidade_cliente,
                           uf_cliente=uf_cliente, endereco_cliente=endereco_cliente, cep_cliente=cep_cliente, func_resp_cliente=func_resp_cliente, lista_atividadecliente=lista_atividadecliente,
                           lista_tipocliente=lista_tipocliente, default_atividade=default_atividade, default_tipocliente=default_tipocliente, lista_estados=lista_estados,
                           default_estados=default_estados, dados_clientes=dados)


########################################################################################################################
# ROTA PARA EDITAR UM CLIENTE SELECIONADO NA TABLE
@app.route('/edita_cliente/<int:record_id>, <cod_usu_ativo>, <nome_usu_ativo>')
def edita_cliente(record_id, cod_usu_ativo, nome_usu_ativo):

    codigo_cliente = record_id
    #wait = input(f"Na função edita_loja - O código do cliente selecionado é {codigo_cliente}.")
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    cod_cliente = nome_cliente = razao_social_cliente = nome_fantasia_cliente = fone_cliente = email_cliente = cpf_cliente = cnpj_cliente = atividade_cliente = ""
    tipo_cliente = contato_cliente = data_nasc_cont_cliente = cpf_contato_cliente = cidade_cliente = uf_cliente = endereco_cliente = cep_cliente = func_resp_cliente = ""
    # wait = input(f"Na função mantem_cliente O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca de clientes")
    if tamanho_dados != 0:
        mensagem = ""
        for cli in dados:
            cod_cliente = str(cli[0]).zfill(5)
            nome_cliente = cli[1]
            razao_social_cliente = cli[2]
            nome_fantasia_cliente = cli[3]
            fone_cliente = cli[4]
            email_cliente = cli[5]
            cpf_cliente = cli[6]
            cnpj_cliente = cli[7]
            tipo_cliente = cli[8]
            atividade_cliente = cli[9]
            contato_cliente = cli[10]
            cpf_contato_cliente = cli[11]
            data_nasc_cont_cliente = cli[12]
            cidade_cliente = cli[13]
            uf_cliente = cli[14]
            endereco_cliente = cli[15]
            cep_cliente = cli[16]
            func_resp_cliente = cli[17]

    ####################################################################################################################
    # BUSCA OS TIPOS DE ATIVIDADES PARA LISTAR NO FORM CLIENTES
    lista_atividadecliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM atividade")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for ativ in dados:
            cod_ativ = str(ativ[0]).zfill(2)
            nome_ativ = ativ[1]
            lista_atividadecliente.append(cod_ativ + "-" + nome_ativ)
    default_atividade = "01"

    ####################################################################################################################
    # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM CLIENTES
    lista_tipocliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_cliente")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            cod_tip = str(tip[0]).zfill(2)
            nome_tip = tip[1]
            lista_tipocliente.append(cod_tip + "-" + nome_tip)
    default_tipocliente = "01"

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA CLIENTES PARA LISTAR NO FORM CLIENTES
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    mensagem = ""
    return render_template('clientes.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu_ativo, cod_cliente=cod_cliente, nome_cliente=nome_cliente,
                           razao_social_cliente=razao_social_cliente,
                           nome_fantasia_cliente=nome_fantasia_cliente, fone_cliente=fone_cliente,
                           email_cliente=email_cliente, cpf_cliente=cpf_cliente,
                           cnpj_cliente=cnpj_cliente, tipo_cliente=tipo_cliente, atividade_cliente=atividade_cliente,
                           contato_cliente=contato_cliente, cpf_contato_cliente=cpf_contato_cliente,
                           data_nasc_cont_cliente=data_nasc_cont_cliente, cidade_cliente=cidade_cliente,
                           uf_cliente=uf_cliente, endereco_cliente=endereco_cliente, cep_cliente=cep_cliente,
                           func_resp_cliente=func_resp_cliente, lista_atividadecliente=lista_atividadecliente, lista_tipocliente=lista_tipocliente,
                           lista_estados=lista_estados,dados_clientes=dados)


########################################################################################################################
# ROTA PARA FILTRAR UM CLIENTE SELECIONADO NA TABLE
@app.route('/filtra_cliente/<atividade_cliente>, <cod_usu_ativo>, <nome_usu_ativo>')
def filtra_cliente(atividade_cliente, cod_usu_ativo, nome_usu_ativo):

    ativ_cliente = atividade_cliente.strip()
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    cod_cliente = nome_cliente = razao_social_cliente = nome_fantasia_cliente = fone_cliente = email_cliente = cpf_cliente = cnpj_cliente = atividade_cliente = ""
    tipo_cliente = contato_cliente = data_nasc_cont_cliente = cpf_contato_cliente = cidade_cliente = uf_cliente = endereco_cliente = cep_cliente = func_resp_cliente = ""
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes WHERE atividade_cliente = ?", (ativ_cliente,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    mensagem = ""
    return render_template('clientes.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu_ativo, cod_cliente=cod_cliente, nome_cliente=nome_cliente,
                           razao_social_cliente=razao_social_cliente,
                           nome_fantasia_cliente=nome_fantasia_cliente, fone_cliente=fone_cliente,
                           email_cliente=email_cliente, cpf_cliente=cpf_cliente,
                           cnpj_cliente=cnpj_cliente, tipo_cliente=tipo_cliente, atividade_cliente=atividade_cliente,
                           contato_cliente=contato_cliente,
                           cpf_contato_cliente=cpf_contato_cliente, data_nasc_cont_cliente=data_nasc_cont_cliente,
                           cidade_cliente=cidade_cliente,
                           uf_cliente=uf_cliente, endereco_cliente=endereco_cliente, cep_cliente=cep_cliente,
                           func_resp_cliente=func_resp_cliente, dados_clientes=dados)


########################################################################################################################
# Rota para Manutenção de Projetos
@app.route('/mantem_projetos', methods=['GET', 'POST'])
def mantem_projetos():

    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_busca_projeto')
    #wait = input(f"O botão de projetos acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()
    #wait = input(f"Na função mantem_loja - Usuário ativo é {cod_usu_ativo} e nome do usuário ativo é {nome_usu_ativo}.")
    ####################################################################################################################
    # BUSCA OS TIPOS DE PROJETOS PARA LISTAR NO FORM PROJETOS
    lista_tipoprojeto = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_projeto")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            idtipo_projeto = str(tip[0]).zfill(2)
            tipo_projeto = tip[1]
            lista_tipoprojeto.append(idtipo_projeto + "-" + tipo_projeto)
    ################################################################################################################
    # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS
    lista_tipocliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_cliente")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            cod_tip = str(tip[0]).zfill(2)
            nome_tip = tip[1]
            lista_tipocliente.append(cod_tip+"-"+nome_tip)
    ################################################################################################################
    # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS
    lista_clientes = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for cli in dados:
            cod_cli = str(cli[0]).zfill(2)
            nome_cli = cli[1]
            lista_clientes.append(cod_cli + "-" + nome_cli)
    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE PROJETOS
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE PROJETOS
    if botao_acionado == "Limpar":
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM projetos")
        dados = cursor.fetchall()
        cod_projeto = nome_projeto = desc_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = cidade_projeto = uf_projeto = endereco_projeto = cep_projeto = ""
        data_contato_projeto = data_inicio_projeto = data_fim_projeto = usuario_projeto = prazo_projeto = estudo_preliminar_inicio = estudo_preliminar_fim = anteprojeto_inicio = ""
        anteprojeto_fim = projeto_legal_inicio = projeto_legal_fim = projeto_executivo_inicio = projeto_executivo_fim = viabilidade_andamento = viabilidade_prazo = ""
        mensagem = ""
        default_tipoprojeto = "01"
        default_clientes = "01"
        default_tipocliente = "01"
        default_estados = "PR"
        return render_template('projetos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                               cod_usuario=cod_usu_ativo, dados_projetos=dados, lista_tipoprojeto=lista_tipoprojeto, default_tipoprojeto=default_tipoprojeto,
                               lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente, lista_clientes=lista_clientes,
                               default_clientes=default_clientes, lista_estados=lista_estados, default_estados=default_estados)

    ####################################################################################################################
    # LOCALIZA UM PROJETO
    elif botao_acionado == "Localizar":
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO PROJETO
            codigo_projeto = int(request.form.get('cod_projeto'))
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos WHERE id_projeto = ?", (codigo_projeto,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            cod_projeto = nome_projeto = desc_projeto = cidade_projeto = endereco_projeto = cep_projeto = data_contato_projeto = data_inicio_projeto = data_fim_projeto = ""
            usuario_projeto = prazo_projeto = estudo_preliminar_inicio = estudo_preliminar_fim = anteprojeto_inicio = anteprojeto_fim = projeto_legal_inicio = projeto_legal_fim = ""
            projeto_executivo_inicio = projeto_executivo_fim = viabilidade_andamento = viabilidade_prazo = ""
            if tamanho_dados != 0:
                mensagem = ""
                for proj in dados:
                    cod_projeto = str(proj[0]).zfill(5)
                    nome_projeto = proj[1]
                    desc_projeto = proj[2]
                    id_tipo_projeto = str(proj[3]).zfill(2)
                    id_cliente = str(proj[4]).zfill(2)
                    id_tipo_cliente = str(proj[5]).zfill(2)
                    nome_cliente = proj[6]
                    cidade_projeto = proj[7]
                    uf_projeto = proj[8]
                    endereco_projeto = proj[10]
                    cep_projeto = proj[10]
                    data_contato_projeto = proj[11]
                    data_inicio_projeto = proj[12]
                    data_fim_projeto = proj[13]
                    usuario_projeto = proj[14]
                    prazo_projeto = proj[15]
                    estudo_preliminar_inicio = proj[16]
                    estudo_preliminar_fim = proj[17]
                    anteprojeto_inicio = proj[18]
                    anteprojeto_fim = proj[19]
                    projeto_legal_inicio = proj[20]
                    projeto_legal_fim = proj[21]
                    projeto_executivo_inicio = proj[22]
                    projeto_executivo_fim = proj[23]
                    viabilidade_andamento = proj[24]
                    viabilidade_prazo = proj[25]
                    ####################################################################################################
                    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
                    db = None
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM projetos")
                    dados = cursor.fetchall()
                    return render_template('projetos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                                           cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto, nome_projeto=nome_projeto, desc_projeto=desc_projeto,
                                           id_tipo_projeto=id_tipo_projeto, id_cliente=id_cliente, id_tipo_cliente=id_tipo_cliente,nome_cliente=nome_cliente,
                                           cidade_projeto=cidade_projeto, uf_projeto=uf_projeto, endereco_projeto=endereco_projeto, cep_projeto=cep_projeto,
                                           data_contato_projeto=data_contato_projeto, data_inicio_projeto=data_inicio_projeto, data_fim_projeto=data_fim_projeto,
                                           usuario_projeto=usuario_projeto, prazo_projeto=prazo_projeto, estudo_preliminar_inicio=estudo_preliminar_inicio,
                                           estudo_preliminar_fim=estudo_preliminar_fim, anteprojeto_inicio=anteprojeto_inicio, anteprojeto_fim=anteprojeto_fim,
                                           projeto_legal_inicio=projeto_legal_inicio, projeto_legal_fim=projeto_legal_fim, projeto_executivo_inicio=projeto_executivo_inicio,
                                           projeto_executivo_fim=projeto_executivo_fim, viabilidade_andamento=viabilidade_andamento, viabilidade_prazo=viabilidade_prazo,
                                           dados_projetos=dados, lista_tipoprojeto=lista_tipoprojeto, lista_tipocliente=lista_tipocliente, lista_clientes=lista_clientes, lista_estados=lista_estados)
            else:
                # wait = input("Projeto não encontrado")
                flash('Projeto não encontrado. Verifique!', category="warning")
                mensagem = ""

    ####################################################################################################################
    # ALTERAR UM PROJETO
    elif botao_acionado == "Alterar":
        if request.form.get('cod_projeto') == "":
            # wait = input(f"Código do Cliente vazio {request.form.get('cod_cliente')}.")
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO PROJETO
            codigo_projeto = int(request.form.get('cod_projeto'))
            # IDENTIFICA OS CAMPOS DIGITADOS
            nome_projeto = request.form.get('nome_projeto')
            desc_projeto = request.form.get('desc_projeto')
            # LISTAS
            id_tipo_projeto = int(request.form.get('tipo_projeto'))
            id_cliente = int(request.form.get('cliente_projeto'))
            id_tipo_cliente = int(request.form.get('tipo_cliente'))
            cidade_projeto = request.form.get('cidade_projeto')
            uf_projeto = request.form.get('estados')
            endereco_projeto = request.form.get('endereco_projeto')
            cep_projeto = request.form.get('cep_projeto')
            data_contato_projeto = request.form.get('data_contato')
            data_inicio_projeto = request.form.get('data_inicio')
            data_fim_projeto = request.form.get('data_fim')
            usuario_projeto = request.form.get('usuario_projeto')
            prazo_projeto = request.form.get('prazo_projeto')
            estudo_preliminar_inicio = request.form.get('est_preliminar_ini')
            estudo_preliminar_fim = request.form.get('est_preliminar_fim')
            anteprojeto_inicio = request.form.get('anteprojeto_ini')
            anteprojeto_fim = request.form.get('anteprojeto_fim')
            projeto_legal_inicio = request.form.get('projetolegal_ini')
            projeto_legal_fim = request.form.get('projetolegal_fim')
            projeto_executivo_inicio = request.form.get('projetoexecutivo_ini')
            projeto_executivo_fim = request.form.get('projetoexecutivo_fim')
            viabilidade_andamento = request.form.get('viabilidade_andamento')
            viabilidade_prazo = request.form.get('viabilidade_prazo')
            ################################################################################################################
            # BUSCA O NOME DO CLIENTE PARA LISTAR NO FORM PROJETOS
            codigo_cliente = int(request.form.get('cliente_projeto'))
            nome_cliente = ""
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT nome_cliente FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for proj in dados:
                    nome_cliente = proj[0]
            ############################################################################################################
            # ALTERAR UM PROJETO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE projetos SET nome_projeto = ?, desc_projeto = ?, id_tipo_projeto = ?, id_cliente = ?, id_tipo_cliente = ?, \
                           nome_cliente = ?, cidade_projeto = ?, uf_projeto = ?, endereco_projeto = ?, cep_projeto = ?, data_contato_projeto = ?, \
                           data_inicio_projeto = ?, data_fim_projeto = ?, usuario_projeto = ?, prazo_projeto = ?, estudo_preliminar_inicio = ?, \
                           estudo_preliminar_fim = ?, anteprojeto_inicio = ?, anteprojeto_fim  = ?, projeto_legal_inicio = ?, projeto_legal_fim = ?, \
                           projeto_executivo_inicio = ?, projeto_executivo_fim = ?, viabilidade_andamento = ?, viabilidade_prazo = ? \
                           WHERE id_projeto = ?", (nome_projeto, desc_projeto, id_tipo_projeto, id_cliente, id_tipo_cliente, nome_cliente,
                           cidade_projeto, uf_projeto, endereco_projeto, cep_projeto, data_contato_projeto, data_inicio_projeto, data_fim_projeto,
                           usuario_projeto, prazo_projeto, estudo_preliminar_inicio, estudo_preliminar_fim, anteprojeto_inicio, anteprojeto_fim,
                           projeto_legal_inicio, projeto_legal_fim, projeto_executivo_inicio, projeto_executivo_fim, viabilidade_andamento,
                           viabilidade_prazo, codigo_projeto,))
            db.commit()
            flash('Registro alterado com sucesso!', category="warning")

    ####################################################################################################################
    # INCLUIR UM PROJETO
    elif botao_acionado == "Incluir":
        ################################################################################################################
        # INCLUIR UM PROJETO - TESTA SE JÁ É CADASTRADO
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO PROJETO
            codigo_projeto = int(request.form.get('cod_projeto'))
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos WHERE id_projeto = ?", (codigo_projeto,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                flash('Atenção! Projeto já cadastrado. Verifique!', category="warning")
            else:
                nome_projeto = request.form.get('nome_projeto')
                desc_projeto = request.form.get('desc_projeto')
                id_tipo_projeto = int(request.form.get('tipo_projeto'))
                id_cliente = int(request.form.get('cliente_projeto'))
                id_tipo_cliente = int(request.form.get('tipo_cliente'))
                cidade_projeto = request.form.get('cidade_projeto')
                uf_projeto = request.form.get('estados')
                endereco_projeto = request.form.get('endereco_projeto')
                cep_projeto = request.form.get('cep_projeto')
                data_contato_projeto = request.form.get('data_contato')
                data_inicio_projeto = request.form.get('data_inicio')
                data_fim_projeto = request.form.get('data_fim')
                usuario_projeto = request.form.get('usuario_projeto')
                prazo_projeto = request.form.get('prazo_projeto')
                estudo_preliminar_inicio = request.form.get('est_preliminar_ini')
                estudo_preliminar_fim = request.form.get('est_preliminar_fim')
                anteprojeto_inicio = request.form.get('anteprojeto_ini')
                anteprojeto_fim = request.form.get('anteprojeto_fim')
                projeto_legal_inicio = request.form.get('projetolegal_ini')
                projeto_legal_fim = request.form.get('projetolegal_fim')
                projeto_executivo_inicio = request.form.get('projetoexecutivo_ini')
                projeto_executivo_fim = request.form.get('projetoexecutivo_fim')
                viabilidade_andamento = request.form.get('viabilidade_andamento')
                viabilidade_prazo = request.form.get('viabilidade_prazo')
                ################################################################################################################
                # BUSCA O NOME DO CLIENTES PARA LISTAR NO FORM PROJETOS
                codigo_cliente = int(request.form.get('cliente_projeto'))
                nome_cliente = ""
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT nome_cliente  FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
                dados = cursor.fetchall()
                tamanho_dados = len(dados)
                if tamanho_dados != 0:
                    for proj in dados:
                        nome_cliente  = proj[0]
                ########################################################################################################
                db = None
                db = get_db()
                cursor = db.cursor()
                dados_grava = (codigo_projeto, nome_projeto, desc_projeto, id_tipo_projeto, id_cliente, id_tipo_cliente, nome_cliente, cidade_projeto,
                           uf_projeto, endereco_projeto, cep_projeto, data_contato_projeto, data_inicio_projeto, data_fim_projeto, usuario_projeto,
                           prazo_projeto, estudo_preliminar_inicio, estudo_preliminar_fim, anteprojeto_inicio, anteprojeto_fim, projeto_legal_inicio,
                           projeto_legal_fim, projeto_executivo_inicio, projeto_executivo_fim, viabilidade_andamento, viabilidade_prazo)
                cursor.execute("INSERT INTO projetos (id_projeto, nome_projeto, desc_projeto, id_tipo_projeto, id_cliente, id_tipo_cliente, \
                           nome_cliente, cidade_projeto, uf_projeto, endereco_projeto, cep_projeto, data_contato_projeto, data_inicio_projeto, \
                           data_fim_projeto, usuario_projeto, prazo_projeto, estudo_preliminar_inicio, estudo_preliminar_fim, anteprojeto_inicio, \
                           anteprojeto_fim, projeto_legal_inicio, projeto_legal_fim, projeto_executivo_inicio, projeto_executivo_fim, \
                           viabilidade_andamento, viabilidade_prazo)  \
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", dados_grava)
                db.commit()
                ########################################################################################################
                # CRIA A PASTA DO PROJETO
                nome_pasta = "P" + str(codigo_projeto).zfill(5)
                caminho_base = "static/projetos"
                caminho_completo = os.path.join(caminho_base, nome_pasta)
                #wait = input(f"Nome do caminho pra criar a pasta {caminho_base}.")
                try:
                    # Cria o diretório, se não existir, e não lança erro
                    os.makedirs(caminho_completo, exist_ok=True)
                except Exception as e:
                    flash('Ocorreu um erro ao criar a pasta do Projeto!', category="warning")

                flash('Registro incluído com sucesso!', category="warning")

    ####################################################################################################################
    # EXCLUIR UM PROJETO
    elif botao_acionado == "Excluir":
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            # ESTA MENSAGEM VEM DO INPUT mensagem_excluir - oculto no form PROJETOS
            mensagem = request.form.get('mensagem_excluir')
            #wait = input(f"Mensagem {mensagem}.")
            if mensagem == "Sim":
                # IDENTIFICA O CÓDIGO DO PROJETO
                codigo_projeto = int(request.form.get('cod_projeto'))
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM projetos WHERE id_projeto = ?", (codigo_projeto,))
                dados = cursor.fetchall()
                db.commit()
                ############################################################################################################
                # EXCLUIR A PASTA DO PROJETO EXCLUÍDO
                nome_pasta = "P" + str(codigo_projeto).zfill(5)
                caminho_base = "static/projetos/"
                caminho_completo = os.path.join(caminho_base, nome_pasta)
                #wait = input(f"Nome do caminho pra excluir a pasta {caminho_completo}.")
                try:
                    # Exclui o diretório, se existir, e não lança erro
                    #os.rmdir(caminho_completo) - remove se estiver vazio
                    #os.removedirs(caminho_completo) - remove todos os diretórios - porém, a partir de static
                    shutil.rmtree(caminho_completo)
                except Exception as e:
                    wait = input(f"Ocorreu o erro {e} ao excluir a pasta {caminho_completo}.")

                    flash(f"Ocorreu um erro {e} ao excluir a pasta do Projeto!.", category="warning")

                flash('Registro excluído com sucesso!', category="warning")
            else:
                flash('Exclusão cancelada!', category="warning")

    ####################################################################################################################
    # GERA ARQUIVO EXCEL/TX/PDF
    elif botao_acionado == "Excel/TXT":
        db = None
        db = get_db()
        cursor = db.cursor()

        if request.form.get('cod_projeto') == "":
            codigo_projeto = 0
            cursor.execute("SELECT * FROM projetos")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO PROJETO
            codigo_projeto = int(request.form.get('cod_projeto'))
            cursor.execute("SELECT * FROM projetos WHERE id_projeto = ?", (codigo_projeto,))

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO TXT
        nome_arq_TXT = "projetos" + ".txt"
        arq_TXT = "static\\arquivos_txt\\" + nome_arq_TXT
        if (os.path.exists(arq_TXT)):
            arquivo = open(arq_TXT, 'w')
        else:
            arquivo = open(arq_TXT, 'x')

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO MS-Excel
        nome_arq_XLSX = "projetos" + ".xlsx"
        arq_XLSX = "static\\arquivos_xlsx\\" + nome_arq_XLSX

        ################################################################################################################
        ## FAZ A LEITURA DA BASE DE DADOS
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        cod_projeto = nome_projeto = desc_projeto = cidade_projeto = endereco_projeto = cep_projeto = data_contato_projeto = data_inicio_projeto = data_fim_projeto = ""
        usuario_projeto = prazo_projeto = estudo_preliminar_inicio = estudo_preliminar_fim = anteprojeto_inicio = anteprojeto_fim = projeto_legal_inicio = projeto_legal_fim = ""
        projeto_executivo_inicio = projeto_executivo_fim = viabilidade_andamento = viabilidade_prazo = ""
        if tamanho_dados != 0:
            mensagem = ""
            tit1 = "SGEA-Sistema Gerenciador de Escritório de Arquitetura" + "\n"
            tit2 = "Relação de Projetos Cadastrados" + "\n"
            tit3 = "-----------------------------------------------------" + "\n"
            arquivo.write(tit1 + tit2 + tit3)
            # wait = input(f"Na função mantem_projetos O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca de projetos")
            for proj in dados:
                cod_projeto = str(proj[0]).zfill(5)
                nome_projeto = "{0:<80}".format(proj[1]).upper()
                desc_projeto = "{0:<80}".format(proj[2]).upper()
                id_tipo_projeto = str(proj[3]).zfill(2)
                id_cliente = str(proj[4]).zfill(2)
                id_tipo_cliente = str(proj[5]).zfill(2)
                nome_cliente = "{0:<80}".format(proj[6]).upper()
                cidade_projeto = "{0:<80}".format(proj[7]).upper()
                uf_projeto = proj[8].strip()
                endereco_projeto = "{0:<80}".format(proj[9]).upper()
                cep_projeto = proj[10].strip()
                data_contato_projeto = proj[11]
                data_inicio_projeto = proj[12]
                data_fim_projeto = proj[13]
                usuario_projeto = "{0:<50}".format(proj[14])
                prazo_projeto = proj[15]
                estudo_preliminar_inicio = proj[16]
                estudo_preliminar_fim = proj[17]
                anteprojeto_inicio = proj[18]
                anteprojeto_fim = proj[19]
                projeto_legal_inicio = proj[20]
                projeto_legal_fim = proj[21]
                projeto_executivo_inicio = proj[22]
                projeto_executivo_fim = proj[23]
                viabilidade_andamento = proj[24]
                viabilidade_prazo = proj[25]
                linha_grava = ("ID                       :" + cod_projeto + "\n"
                               "Nome                     :" + nome_projeto + "\n"
                               "Descrição                :" + desc_projeto + "\n" 
                               "Tipo                     :" + id_tipo_projeto + "\n"
                               "Cliente                  :" + id_cliente + "\n"
                               "Tipo Cliente             :" + id_tipo_cliente + "\n"     
                               "Nome Cliente             :" + nome_cliente + "\n"
                               "Cidade                   :" + cidade_projeto + "\n"
                               "UF                       :" + uf_projeto + "\n"
                               "Endereço                 :" + endereco_projeto + "\n"
                               "CEP                      :" + cep_projeto + "\n"
                               "Data do contato          :" + data_contato_projeto + "\n"
                               "Data início              :" + data_inicio_projeto + "\n"                                                       
                               "Data fim                 :" + data_fim_projeto + "\n"
                               "Responsável              :" + usuario_projeto + "\n"
                               "Prazo                    :" + prazo_projeto + "\n"
                               "Estudo Preliminar-início :" + estudo_preliminar_inicio + "\n"
                               "Estudo Preliminar-fim    :" + estudo_preliminar_fim + "\n"
                               "Anteprojeto-início       :" + anteprojeto_inicio + "\n"
                               "Anteprojeto-fim          :" + anteprojeto_fim + "\n"
                               "Projeto Legal-início     :" + projeto_legal_inicio + "\n"
                               "Projeto Legal-fim        :" + projeto_legal_fim + "\n"
                               "Projeto Executivo-início :" + projeto_executivo_inicio + "\n"
                               "Projeto Executivo-fim    :" + projeto_executivo_fim + "\n"
                               "Viabilidade-andamento    :" + viabilidade_andamento + "\n"
                               "Viabilidade-prazo        :" + viabilidade_prazo + "\n" + "\n")
                arquivo.write(linha_grava)

            arquivo.close()

            ############################################################################################################
            ## 1-GERA UM df =: DATAFRAME COM O SQL GERADO - USANDO PANDAS
            df = pd.DataFrame(dados)

            ############################################################################################################
            ## O CABEÇALHO DAS COLUNAS PODE SER CRIADO DE DUAS MANEIRAS:
            ## 1- ATRIBUI A columns OS TÍTULOS DAS COLUNAS DO BD SQL PARA USAR COMO CABEÇALHO NO EXCEL
            ##    AS COLUNAS SÃO GERADAS NO MOMENTO DA GERAÇÃO DO SQL NO con
            # columns = [desc[0] for desc in con.description]
            # df = pd.DataFrame(list(sqlquery), columns=columns)
            # df.to_excel(arq_XLS, sheet_name="Lojas", index=False, startcol=0, startrow=0)
            ############################################################################################################
            ## 2- ATRIBUI A VARIÁVEL alias OS CABEÇALHOS DAS COLUNAS
            ##    NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias
            ##    SE NÃO USAR O alias O CABEÇALHO SERÁ 0,1,2,3,4,5
            ############################################################################################################
            ## VAMOS USAR O MÉTODO with... PODE GERAR UMA OU VÁRIAS  PLANILHAS NO MESMO ARQUIVO
            ## NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias index=False
            ## NESTE CASO VAMOS CRIAR UM ARQUIVO XLSX COM 1 PLANILHA - Lojas
            alias = ["ID_PROJETO", "NOME_PROJETO", "DESCRIÇÃO", "TIPO PROJETO", "ID_CLIENTE", "TIPO CLIENTE", "NOME CLIENTE", "CIDADE",
                     "UF", "ENDEREÇO", "CEP", "DATA CONTATO", "DATA INÍCIO", "DATA FIM", "RESPONSÁVEL", "PRAZO", "ESTUDO PRELIMINAR-INÍCIO",
                     "ESTUDO PRELIMINAR-FIM", "ANTEPROJETO-INICIO", "ANTEPROJETO-FIM", "PROJETO LEGAL-INICIO", "PROJETO LEGAL-FIM",
                     "PROJETO EXECUTIVO-INICIO", "PROJETO EXECUTIVO-FIM", "VIABILIDADE-ANDAMENTO", "VIABILIDADE-PRAZO"]
            with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                df.to_excel(ew, sheet_name="Projetos", index=False, header=alias)

            ############################################################################################################
            ## PODEMOS APENDAR UM DATAFRAME DENTRO DE OUTRO PARA GRAVAR EM UMA PLANILHA
            ## APENDA O DATA FRAME df1 NO DATA FRAME df
            # df1 = pd.DataFrame(sqlquery)
            # df3 = df1.append(df1, ignore_index=False, sort=False)
            ############################################################################################################
            ## PODEMOS INCLUIR UMA NOVA PLANILHA DENTRO DO ARQUIVO JÁ GERADO
            ## CRIAMOS A PLANILHA Vendas2 COM O df3 QUE APENDOU O df1
            # with pd.ExcelWriter(arq_XLS1, engine="openpyxl", mode="a") as ew:
            # df3.to_excel(ew, sheet_name="Vendas2", index=False, header=alias)
            cursor.close()
            flash("Arquivo (Excel) - projetos.xlsx na pasta /static/arquivos_xlsx e Arquivo (TXT) - projetos.txt na pasta /static/arquivos_txt  => gerados com sucesso!", category="warning")

    ####################################################################################################################
    # UPLOAD DE ARQUIVOS
    elif botao_acionado == "Upload":
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            codigo_projeto = int(request.form.get('cod_projeto'))
            #wait = input(f"Código do projeto é {codigo_projeto}.")
            ############################################################################################################
            # IDENTIFICA A PASTA DO PROJETO
            nome_pasta = "P" + str(codigo_projeto).zfill(5)
            caminho_base = "static/projetos/"
            caminho_completo = os.path.join(caminho_base, nome_pasta)
            #wait = input(f"Nome do caminho da pasta de upload é {caminho_completo}.")
            try:
                # Cria o diretório, se não existir, e não lança erro
                os.makedirs(caminho_completo, exist_ok=True)
            except Exception as e:
                flash('Ocorreu um erro ao criar a pasta do Projeto!', category="warning")
            UPLOAD_FOLDER = os.path.join(caminho_base, nome_pasta)
            ############################################################################################################
            # PEGA O NOME DO ARQUIVO QUE FOI SELECIONADO
            file = request.files['upload']
            ############################################################################################################
            # VERIFICA SE O ARQUIVO ESTÁ A SER FEITO O UPLOAD ESTÁ NO FORM
            if 'upload' not in request.files:
                flash('Atenção! Nenhum arquivo selecionado!', category="warning")
            ############################################################################################################
            # SE O USUÁRIO NÃO SELECIONAR UM ARQUIVO O NAVEGADOR ENVIA UM CAMPO VAZIO
            if file.filename == "":
                flash('Atenção! Nenhum arquivo selecionado!', category="warning")
            ############################################################################################################
            # VERIFICA SE O ARQUIVO ESTÁ NOS ARQUIVOS PERMITIDOS PARA UPLOAD - FUNÇÃO QUE DEFINE
            if file and allowed_file(file.filename):
                ########################################################################################################
                # FAZ A CARGA DO ARQUIVO UTILIZANDO O MÉTODO secure_filename
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                flash('Atenção! Arquivo carregado com sucesso!', category="warning")
            else:
                flash('Atenção! Extensão de arquivo não permitida!', category="warning")

    ####################################################################################################################
    # DOWNLOAD DE  ARQUIVOS
    elif botao_acionado == "Download":
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            codigo_projeto = int(request.form.get('cod_projeto'))
            #wait = input(f"Código do projeto é {codigo_projeto}.")
            ###########################################################################################################
            # IDENTIFICA A PASTA DO PROJETO
            nome_pasta = "P" + str(codigo_projeto).zfill(5)
            caminho_base = "static/projetos/"
            caminho_completo = os.path.join(caminho_base, nome_pasta)
            #wait = input(f"Nome do caminho da pasta de upload é {caminho_completo}.")
            UPLOAD_FOLDER = os.path.join(caminho_base, nome_pasta)
            ############################################################################################################
            # PEGA O NOME DO ARQUIVO QUE FOI SELECIONADO
            file = request.files['upload']
            ############################################################################################################
            # VERIFICA SE O ARQUIVO ESTÁ A SER FEITO O UPLOAD ESTÁ NO FORM
            if 'upload' not in request.files:
                flash('Atenção! Nenhum arquivo selecionado!', category="warning")
            ############################################################################################################
            # SE O USUÁRIO NÃO SELECIONAR UM ARQUIVO O NAVEGADOR ENVIA UM CAMPO VAZIO
            if file.filename == "":
                flash('Atenção! Nenhum arquivo selecionado!', category="warning")
            #wait = input(f"Nome do caminho selecionado para leitura é {file.filename}.")
            #ext = file.filename[-4:]
            #wait = input(f"Extensão do arquivo selecionado é {ext}.")
            ############################################################################################################
            # VERIFICA SE O ARQUIVO ESTÁ NOS ARQUIVOS PERMITIDOS PARA UPLOAD - FUNÇÃO QUE DEFINE
            if file and allowed_file(file.filename):
                return send_from_directory(UPLOAD_FOLDER, file.filename, as_attachment=True)

    ####################################################################################################################
    # VISUALIZAR ARQUIVOS
    elif botao_acionado == "Visualizar":
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            codigo_projeto = int(request.form.get('cod_projeto'))
            #wait = input(f"Código do projeto é {codigo_projeto}.")
            ############################################################################################################
            # IDENTIFICA A PASTA DO PROJETO
            nome_pasta = "P" + str(codigo_projeto).zfill(5)
            caminho_base = "static/projetos/"
            caminho_completo = os.path.join(caminho_base, nome_pasta)
            #wait = input(f"Nome do caminho da pasta de upload é {caminho_completo}.")
            UPLOAD_FOLDER = os.path.join(caminho_base, nome_pasta)
            ############################################################################################################
            # PEGA O NOME DO ARQUIVO QUE FOI SELECIONADO
            file = request.files['upload']
            ############################################################################################################
            # VERIFICA SE O ARQUIVO ESTÁ A SER FEITO O UPLOAD ESTÁ NO FORM
            if 'upload' not in request.files:
                flash('Atenção! Nenhum arquivo selecionado!', category="warning")
            ############################################################################################################
            # SE O USUÁRIO NÃO SELECIONAR UM ARQUIVO O NAVEGADOR ENVIA UM CAMPO VAZIO
            if file.filename == "":
                flash('Atenção! Nenhum arquivo selecionado!', category="warning")
                #wait = input(f"Nome do caminho selecionado para leitura é {file.filename}.")
            ############################################################################################################
            # VERIFICA SE O ARQUIVO ESTÁ NOS ARQUIVOS PERMITIDOS PARA UPLOAD - FUNÇÃO QUE DEFINE
            if file and allowed_file(file.filename):
                ext = file.filename[-4:]
                # wait = input(f"Extensão do arquivo selecionado é {ext}.")
                if ext == ".txt":
                    return send_from_directory(UPLOAD_FOLDER, file.filename, as_attachment=False)
                elif ext == ".pdf":
                    # as_attachment=False para exibir no navegador
                    return send_from_directory(UPLOAD_FOLDER, file.filename,  as_attachment=False)
                elif ext == ".png" or ext == ".jpg" or ext == ".jpe" or ext == ".gif":
                    return send_from_directory(UPLOAD_FOLDER, file.filename, as_attachment=False)
                ########################################################################################################
                # FAZ A CARGA DO ARQUIVO UTILIZANDO O MÉTODO secure_filename
                # filename = secure_filename(file.filename)
                # file.save(os.path.join(UPLOAD_FOLDER, filename))
                flash('Atenção! Arquivo carregado com sucesso!', category="warning")
            else:
                flash('Atenção! Extensão de arquivo não permitida!', category="warning")

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projetos")
    dados = cursor.fetchall()
    cod_projeto = nome_projeto = desc_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = cidade_projeto = uf_projeto = endereco_projeto = cep_projeto =  ""
    data_contato_projeto = data_inicio_projeto = data_fim_projeto = usuario_projeto = prazo_projeto = estudo_preliminar_inicio = estudo_preliminar_fim = anteprojeto_inicio = ""
    anteprojeto_fim = projeto_legal_inicio = projeto_legal_fim = projeto_executivo_inicio = projeto_executivo_fim = viabilidade_andamento = viabilidade_prazo = ""
    mensagem = ""
    default_tipoprojeto = "01"
    default_clientes = "01"
    default_tipocliente = "01"
    default_estados = "PR"
    return render_template('projetos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto, nome_projeto=nome_projeto, desc_projeto=desc_projeto,
                           id_tipo_projeto=id_tipo_projeto, id_cliente=id_cliente, id_tipo_cliente=id_tipo_cliente, nome_cliente=nome_cliente,
                           cidade_projeto=cidade_projeto, uf_projeto=uf_projeto, endereco_projeto=endereco_projeto, cep_projeto=cep_projeto,
                           data_contato_projeto=data_contato_projeto, data_inicio_projeto=data_inicio_projeto, data_fim_projeto=data_fim_projeto,
                           usuario_projeto=usuario_projeto, prazo_projeto=prazo_projeto, estudo_preliminar_inicio=estudo_preliminar_inicio,
                           estudo_preliminar_fim=estudo_preliminar_fim, anteprojeto_inicio=anteprojeto_inicio, anteprojeto_fim=anteprojeto_fim,
                           projeto_legal_inicio=projeto_legal_inicio, projeto_legal_fim=projeto_legal_fim, projeto_executivo_inicio=projeto_executivo_inicio,
                           projeto_executivo_fim=projeto_executivo_fim, viabilidade_andamento=viabilidade_andamento, viabilidade_prazo=viabilidade_prazo,
                           lista_tipoprojeto=lista_tipoprojeto, default_tipoprojeto=default_tipoprojeto, lista_tipocliente=lista_tipocliente,
                           default_tipocliente=default_tipocliente, lista_clientes=lista_clientes, default_clientes=default_clientes, lista_estados=lista_estados,
                           default_estados=default_estados, dados_projetos=dados)

########################################################################################################################
# ROTA PARA EDITAR UM PROJETO SELECIONADO NA TABLE
@app.route('/edita_projeto/<int:record_id>, <cod_usu_ativo>, <nome_usu_ativo>')
def edita_projeto(record_id, cod_usu_ativo, nome_usu_ativo):

    codigo_projeto = record_id
    #wait = input(f"Na função edita_loja - O código do cliente selecionado é {codigo_cliente}.")
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()

    # BUSCA OS TIPOS DE PROJETOS PARA LISTAR NO FORM PROJETOS
    lista_tipoprojeto = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_projeto")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            idtipo_projeto = str(tip[0]).zfill(2)
            tipo_projeto = tip[1]
            lista_tipoprojeto.append(idtipo_projeto + "-" + tipo_projeto)
    ####################################################################################################################
    # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS
    lista_tipocliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_cliente")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            cod_tip = str(tip[0]).zfill(2)
            nome_tip = tip[1]
            lista_tipocliente.append(cod_tip+"-"+nome_tip)
    ####################################################################################################################
    # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS
    lista_clientes = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for cli in dados:
            cod_cli = str(cli[0]).zfill(2)
            nome_cli = cli[1]
            lista_clientes.append(cod_cli + "-" + nome_cli)

    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projetos WHERE id_projeto = ?", (codigo_projeto,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    cod_projeto = nome_projeto = desc_projeto = cidade_projeto = endereco_projeto = cep_projeto = data_contato_projeto = data_inicio_projeto = data_fim_projeto = ""
    usuario_projeto = prazo_projeto = estudo_preliminar_inicio = estudo_preliminar_fim = anteprojeto_inicio = anteprojeto_fim = projeto_legal_inicio = projeto_legal_fim = ""
    projeto_executivo_inicio = projeto_executivo_fim = viabilidade_andamento = viabilidade_prazo = ""
    if tamanho_dados != 0:
        mensagem = ""
        for proj in dados:
            cod_projeto = str(proj[0]).zfill(5)
            nome_projeto = proj[1]
            desc_projeto = proj[2]
            id_tipo_projeto = str(proj[3]).zfill(2)
            id_cliente = str(proj[4]).zfill(2)
            id_tipo_cliente = str(proj[5]).zfill(2)
            nome_cliente = proj[6]
            cidade_projeto = proj[7]
            uf_projeto = proj[8]
            endereco_projeto = proj[10]
            cep_projeto = proj[10]
            data_contato_projeto = proj[11]
            data_inicio_projeto = proj[12]
            data_fim_projeto = proj[13]
            usuario_projeto = proj[14]
            prazo_projeto = proj[15]
            estudo_preliminar_inicio = proj[16]
            estudo_preliminar_fim = proj[17]
            anteprojeto_inicio = proj[18]
            anteprojeto_fim = proj[19]
            projeto_legal_inicio = proj[20]
            projeto_legal_fim = proj[21]
            projeto_executivo_inicio = proj[22]
            projeto_executivo_fim = proj[23]
            viabilidade_andamento = proj[24]
            viabilidade_prazo = proj[25]
            ############################################################################################################
            # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos")
            dados = cursor.fetchall()
            return render_template('projetos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                                   nome_usu_ativo=nome_usu_ativo,
                                   cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto, nome_projeto=nome_projeto,
                                   desc_projeto=desc_projeto,
                                   id_tipo_projeto=id_tipo_projeto, id_cliente=id_cliente,
                                   id_tipo_cliente=id_tipo_cliente, nome_cliente=nome_cliente,
                                   cidade_projeto=cidade_projeto, uf_projeto=uf_projeto,
                                   endereco_projeto=endereco_projeto, cep_projeto=cep_projeto,
                                   data_contato_projeto=data_contato_projeto, data_inicio_projeto=data_inicio_projeto,
                                   data_fim_projeto=data_fim_projeto, usuario_projeto=usuario_projeto, prazo_projeto=prazo_projeto,
                                   estudo_preliminar_inicio=estudo_preliminar_inicio, estudo_preliminar_fim=estudo_preliminar_fim,
                                   anteprojeto_inicio=anteprojeto_inicio, anteprojeto_fim=anteprojeto_fim, projeto_legal_inicio=projeto_legal_inicio, projeto_legal_fim=projeto_legal_fim,
                                   projeto_executivo_inicio=projeto_executivo_inicio, projeto_executivo_fim=projeto_executivo_fim,
                                   viabilidade_andamento=viabilidade_andamento, viabilidade_prazo=viabilidade_prazo, dados_projetos=dados,
                                   lista_tipoprojeto=lista_tipoprojeto, lista_clientes=lista_clientes, lista_tipocliente=lista_tipocliente, lista_estados=lista_estados)

    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projetos")
    dados = cursor.fetchall()
    cod_projeto = nome_projeto = desc_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = cidade_projeto = uf_projeto = endereco_projeto = cep_projeto =  ""
    data_contato_projeto = data_inicio_projeto = data_fim_projeto = usuario_projeto = prazo_projeto = estudo_preliminar_inicio = estudo_preliminar_fim = anteprojeto_inicio = ""
    anteprojeto_fim = projeto_legal_inicio = projeto_legal_fim = projeto_executivo_inicio = projeto_executivo_fim = viabilidade_andamento = viabilidade_prazo = ""
    mensagem = ""
    default_tipoprojeto = "01"
    default_clientes = "01"
    default_tipocliente = "01"
    default_estados = "PR"
    return render_template('projetos.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                           cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto, nome_projeto=nome_projeto, desc_projeto=desc_projeto,
                           id_tipo_projeto=id_tipo_projeto, id_cliente=id_cliente, id_tipo_cliente=id_tipo_cliente, nome_cliente=nome_cliente,
                           cidade_projeto=cidade_projeto, uf_projeto=uf_projeto, endereco_projeto=endereco_projeto, cep_projeto=cep_projeto,
                           data_contato_projeto=data_contato_projeto, data_inicio_projeto=data_inicio_projeto, data_fim_projeto=data_fim_projeto,
                           usuario_projeto=usuario_projeto, prazo_projeto=prazo_projeto, estudo_preliminar_inicio=estudo_preliminar_inicio,
                           estudo_preliminar_fim=estudo_preliminar_fim, anteprojeto_inicio=anteprojeto_inicio, anteprojeto_fim=anteprojeto_fim,
                           projeto_legal_inicio=projeto_legal_inicio, projeto_legal_fim=projeto_legal_fim, projeto_executivo_inicio=projeto_executivo_inicio,
                           projeto_executivo_fim=projeto_executivo_fim, viabilidade_andamento=viabilidade_andamento, viabilidade_prazo=viabilidade_prazo,
                           lista_tipoprojeto=lista_tipoprojeto, default_tipoprojeto=default_tipoprojeto, lista_tipocliente=lista_tipocliente,
                           default_tipocliente=default_tipocliente, lista_clientes=lista_clientes, default_clientes=default_clientes, lista_estados=lista_estados,
                           default_estados=default_estados, dados_projetos=dados)


########################################################################################################################
# Rota para Manutenção de Tarefas de Projetos
@app.route('/mantem_tarefas', methods=['GET', 'POST'])
def mantem_tarefas():
    ####################################################################################################################
    # IDENTIFICA O BOTÃO QUE SOFREU ACTION
    botao_acionado = request.form.get('bt_busca_tarefa')
    #wait = input(f"O botão de tarefas de projetos acionado foi  {botao_acionado}.")

    ####################################################################################################################
    # IDENTIFICA O USUÁRIO ATIVO
    cod_usu_ativo = request.form.get('usuario_ativo')[:5]
    nome_usu_ativo = request.form.get('usuario_ativo')[8:60].strip()
    #wait = input(f"Na função mantem_loja - Usuário ativo é {cod_usu_ativo} e nome do usuário ativo é {nome_usu_ativo}.")
    ####################################################################################################################
    # BUSCA OS TIPOS DE PROJETOS PARA LISTAR NO FORM PROJETOS
    lista_tipoprojeto = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_projeto")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            idtipo_projeto = str(tip[0]).zfill(2)
            tipo_projeto = tip[1]
            lista_tipoprojeto.append(idtipo_projeto + "-" + tipo_projeto)
    default_tipoprojeto = "01"
    ################################################################################################################
    # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS
    lista_tipocliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_cliente")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            cod_tip = str(tip[0]).zfill(2)
            nome_tip = tip[1]
            lista_tipocliente.append(cod_tip+"-"+nome_tip)
    default_tipocliente = "01"
    ################################################################################################################
    # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS
    lista_clientes = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for cli in dados:
            cod_cli = str(cli[0]).zfill(2)
            nome_cli = cli[1]
            lista_clientes.append(cod_cli + "-" + nome_cli)
    default_clientes = "01"
    ####################################################################################################################
    # SAIR DA TELA DE MANUTENÇÃO DE TAREFAS DE PROJETOS
    if botao_acionado == "Sair":
        mensagem = ""
        return render_template('principal.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo)

    ####################################################################################################################
    # LIMPAR OS CAMPOS DA TELA DE MANUTENÇÃO DE TAREFAS DE PROJETOS
    if botao_acionado == "Limpar":
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM projetos")
        dados_projetos = cursor.fetchall()
        cod_projeto = nome_projeto = nome_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = ""
        cod_tarefa = desc_tarefa = tarefa_prazo = tarefa_inicio = tarefa_fim = ""
        ################################################################################################################
        # BUSCA TODOS OS REGISTROS DA TABELA DE TAREFAS DE PROJETOS PARA LISTAR NO FORM PROJETOS
        db = None
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM projetos_tarefas order by id_projeto, id_tarefa")
        dados_tarefas = cursor.fetchall()
        mensagem = ""
        default_tipoprojeto = "01"
        default_clientes = "01"
        default_tipocliente = "01"
        return render_template('projetos_tarefas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                               cod_usuario=cod_usu_ativo, dados_projetos=dados_projetos, dados_tarefas=dados_tarefas, lista_tipoprojeto=lista_tipoprojeto,
                               default_tipoprojeto=default_tipoprojeto, lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente,
                               lista_clientes=lista_clientes, default_clientes=default_clientes)

    ####################################################################################################################
    # LOCALIZA UMA TAREFA DE UM PROJETO
    elif botao_acionado == "Localizar":
        if request.form.get('cod_projeto') == "":
            flash('Atenção! O código do Projeto deve ser digitado. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO PROJETO E DA TAREFA
            codigo_projeto = int(request.form.get('cod_projeto'))
            ################################################################################################################
            # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS DO PROJETO SELECIONADO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos WHERE id_projeto = ?", (codigo_projeto,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            cod_projeto = nome_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = ""
            if tamanho_dados != 0:
                for proj in dados:
                    cod_projeto = str(proj[0]).zfill(5)
                    nome_projeto = proj[1]
                    id_tipo_projeto = str(proj[3]).zfill(2)
                    id_cliente = str(proj[4]).zfill(2)
                    id_tipo_cliente = str(proj[5]).zfill(2)
                    nome_cliente = proj[6]
                    ########################################################################################################
                    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS_TAREFAS ASSOCIADAS AO PROJETO DIGITADO
                    db = None
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM projetos_tarefas WHERE id_projeto = ? order by id_projeto, id_tarefa", (codigo_projeto,))
                    dados_tarefas = cursor.fetchall()
                    tamanho_dados = len(dados)
                    #wait = input(f"Na função mantem_tarefas - Tamanho dados na busca em projetos_tarefas deste projeto é {tamanho_dados}.")
                    ####################################################################################################
                    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
                    db = None
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM projetos")
                    dados_projetos = cursor.fetchall()
                    ####################################################################################################
                    # LIMPA OS CAMPOS DAS TAREFAS - SÓ VAI PREENCHER APÓS SELECIONAR UMA TAREFA
                    cod_tarefa = desc_tarefa = tarefa_prazo = tarefa_inicio = tarefa_fim = ""
                    mensagem = ""
                    return render_template('projetos_tarefas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo, nome_usu_ativo=nome_usu_ativo,
                                       cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto, nome_projeto=nome_projeto, id_tipo_projeto=id_tipo_projeto,
                                       id_cliente=id_cliente, id_tipo_cliente=id_tipo_cliente,nome_cliente=nome_cliente, cod_tarefa=cod_tarefa, desc_tarefa=desc_tarefa,
                                       tarefa_prazo=tarefa_prazo, tarefa_inicio=tarefa_inicio, tarefa_fim=tarefa_fim, dados_projetos=dados_projetos, dados_tarefas=dados_tarefas,
                                       lista_tipoprojeto=lista_tipoprojeto, lista_clientes=lista_clientes, lista_tipocliente=lista_tipocliente)
            else:
                # wait = input("Projeto não encontrado")
                flash('Projeto não encontrado. Verifique!', category="warning")

    ####################################################################################################################
    # ALTERAR UMA TAREFA DE PROJETO
    elif botao_acionado == "Alterar":
        if request.form.get('cod_projeto') == "" or request.form.get('cod_tarefa') == "":
            flash('Atenção! O código do Projeto e da Tarefa devem ser digitados. Verifique!', category="warning")
        else:
            # IDENTIFICA O CÓDIGO DO PROJETO E DA TAREFA
            codigo_projeto = int(request.form.get('cod_projeto'))
            nome_projeto = request.form.get('nome_projeto')
            id_tipo_projeto = int(request.form.get('tipo_projeto'))
            id_cliente = int(request.form.get('cliente_projeto'))
            id_tipo_cliente = int(request.form.get('tipo_cliente'))
            codigo_tarefa = int(request.form.get('cod_tarefa'))
            desc_tarefa = request.form.get('desc_tarefa')
            tarefa_prazo = request.form.get('tarefa_prazo')
            tarefa_inicio = request.form.get('tarefa_inicio')
            tarefa_fim = request.form.get('tarefa_fim')
            ############################################################################################################
            # BUSCA O NOME DO CLIENTES PARA LISTAR NO FORM PROJETOS
            codigo_cliente = int(request.form.get('cliente_projeto'))
            nome_cliente = ""
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT nome_cliente FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for proj in dados:
                    nome_cliente = proj[0]
            ############################################################################################################
            # ALTERAR UMA TAREFA DE UM PROJETO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE projetos_tarefas SET nome_projeto = ?, id_tipo_projeto = ?, id_cliente = ?, id_tipo_cliente = ?, \
                           nome_cliente = ?, desc_tarefa = ?, tarefa_prazo = ?, tarefa_inicio = ?, tarefa_fim = ? \
                           WHERE id_projeto = ? and id_tarefa = ?", (nome_projeto, id_tipo_projeto, id_cliente, id_tipo_cliente,
                           nome_cliente, desc_tarefa, tarefa_prazo, tarefa_inicio, tarefa_fim, codigo_projeto, codigo_tarefa))
            db.commit()
            flash('Registro alterado com sucesso!', category="warning")

    ####################################################################################################################
    # INCLUIR UMA TAREFA DE UM PROJETO
    elif botao_acionado == "Incluir":
        ################################################################################################################
        # INCLUIR UMA TAREFA DE UM PROJETO - TESTA SE JÁ É CADASTRADA
        if request.form.get('cod_projeto') == "" or request.form.get('cod_tarefa') == "":
            flash('Atenção! O código do Projeto e da Tarefa devem ser digitados. Verifique!', category="warning")
        else:
            ################################################################################################################
            # IDENTIFICA O CÓDIGO DA TAREFA E DO PROJETO
            codigo_projeto = int(request.form.get('cod_projeto'))
            codigo_tarefa = int(request.form.get('cod_tarefa'))
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos_tarefas WHERE id_projeto = ? and id_tarefa = ? order by id_projeto, id_tarefa", (codigo_projeto, codigo_tarefa))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                flash('Atenção! Tarefa já cadastrada para este Projeto já cadastrado. Verifique!', category="warning")
            else:
                # IDENTIFICA O CÓDIGO DO PROJETO E DA TAREFA
                codigo_projeto = int(request.form.get('cod_projeto'))
                nome_projeto = request.form.get('nome_projeto')
                id_tipo_projeto = int(request.form.get('tipo_projeto'))
                id_cliente = int(request.form.get('cliente_projeto'))
                id_tipo_cliente = int(request.form.get('tipo_cliente'))
                codigo_tarefa = int(request.form.get('cod_tarefa'))
                desc_tarefa = request.form.get('desc_tarefa')
                tarefa_prazo = request.form.get('tarefa_prazo')
                tarefa_inicio = request.form.get('tarefa_inicio')
                tarefa_fim = request.form.get('tarefa_fim')
                ################################################################################################################
                # BUSCA O NOME DO CLIENTES PARA LISTAR NO FORM PROJETOS
                codigo_cliente = int(request.form.get('cliente_projeto'))
                nome_cliente = ""
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT nome_cliente  FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
                dados = cursor.fetchall()
                tamanho_dados = len(dados)
                if tamanho_dados != 0:
                    for proj in dados:
                        nome_cliente = proj[0]
                db = None
                db = get_db()
                cursor = db.cursor()
                dados_grava = (codigo_projeto, nome_projeto, id_tipo_projeto, id_cliente, id_tipo_cliente, nome_cliente,
                           codigo_tarefa, desc_tarefa, tarefa_prazo, tarefa_inicio, tarefa_fim)
                #wait = input(f"Em mantem_tarefa opção incluir uma tarefa dados_grava é {dados_grava}.")
                cursor.execute("INSERT INTO projetos_tarefas (id_projeto, nome_projeto, id_tipo_projeto, id_cliente, id_tipo_cliente, \
                           nome_cliente, id_tarefa, desc_tarefa, tarefa_prazo, tarefa_inicio, tarefa_fim) \
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", dados_grava)
                db.commit()

    ####################################################################################################################
    # EXCLUIR UMA TAREFA DE UM  PROJETO
    elif botao_acionado == "Excluir":
        if request.form.get('cod_projeto') == "" or request.form.get('cod_tarefa') == "":
            flash('Atenção! O código do Projeto e da Tarefa devem ser digitados. Verifique!', category="warning")
        else:
            # ESTA MENSAGEM VEM DO INPUT mensagem_excluir - oculto no form PROJETOS
            mensagem = request.form.get('mensagem_excluir')
            if mensagem == "Sim":
                # IDENTIFICA O CÓDIGO DO PROJETO
                codigo_projeto = int(request.form.get('cod_projeto'))
                codigo_tarefa = int(request.form.get('cod_tarefa'))
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM projetos_tarefas WHERE id_projeto = ? and id_tarefa = ?", (codigo_projeto, codigo_tarefa))
                dados = cursor.fetchall()
                db.commit()
                flash('Registro excluído com sucesso!', category="warning")
            else:
                flash('Exclusão cancelada!', category="warning")

    ####################################################################################################################
    # GERA ARQUIVO EXCEL/TX/PDF
    elif botao_acionado == "Excel/TXT":
        db = None
        db = get_db()
        cursor = db.cursor()
        if request.form.get('cod_projeto') == "":
            codigo_projeto = 0
            cursor.execute("SELECT * FROM projetos_tarefas order by id_projeto, id_tarefa")
        else:
            ############################################################################################################
            # IDENTIFICA O CÓDIGO DO PROJETO
            codigo_projeto = int(request.form.get('cod_projeto'))
            cursor.execute("SELECT * FROM projetos_tarefas WHERE id_projeto = ? order by id_projeto, id_tarefa", (codigo_projeto,))
        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO TXT
        nome_arq_TXT = "projetos_tarefas" + ".txt"
        arq_TXT = "static\\arquivos_txt\\" + nome_arq_TXT
        if (os.path.exists(arq_TXT)):
            arquivo = open(arq_TXT, 'w')
        else:
            arquivo = open(arq_TXT, 'x')

        ################################################################################################################
        ## DEFINE O NOME DO ARQUIVO MS-Excel
        nome_arq_XLSX = "projetos_tarefas" + ".xlsx"
        arq_XLSX = "static\\arquivos_xlsx\\" + nome_arq_XLSX

        ################################################################################################################
        ## FAZ A LEITURA DA BASE DE DADOS
        dados = cursor.fetchall()
        tamanho_dados = len(dados)
        cod_projeto = nome_projeto =  id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = ""
        id_tarefa = desc_tarefa = tarefa_prazo = tarefa_inicio = arefa_fim = ""
        if tamanho_dados != 0:
            mensagem = ""
            tit1 = "SGEA-Sistema Gerenciador de Escritório de Arquitetura" + "\n"
            tit2 = "Relação de Tarefas de Projetos Cadastrados" + "\n"
            tit3 = "-----------------------------------------------------" + "\n"
            arquivo.write(tit1 + tit2 + tit3)
            # wait = input(f"Na função mantem_projetos O tamanho_dados de Localizar é {tamanho_dados}. Fazendo a busca de projetos")
            for proj in dados:
                cod_projeto = str(proj[0]).zfill(5)
                nome_projeto = "{0:<80}".format(proj[1]).upper()
                id_tipo_projeto = str(proj[2]).zfill(5)
                id_cliente = str(proj[3]).zfill(5)
                id_tipo_cliente = str(proj[4]).zfill(5)
                nome_cliente = "{0:<80}".format(proj[5]).upper()
                id_tarefa = str(proj[6]).zfill(5)
                desc_tarefa = "{0:<80}".format(proj[7]).upper()
                tarefa_prazo = "{0:<50}".format(proj[8]).upper()
                tarefa_inicio = proj[9]
                tarefa_fim = proj[10]
                linha_grava = ("ID Projeto               :" + cod_projeto + "\n"
                               "Nome Projeto             :" + nome_projeto + "\n"
                               "Tipo                     :" + id_tipo_projeto + "\n"
                               "Cliente                  :" + id_cliente + "\n"
                               "Tipo Cliente             :" + id_tipo_cliente + "\n"     
                               "Nome Cliente             :" + nome_cliente + "\n"
                               "ID Tarefa                :" + id_tarefa + "\n"
                               "Descrição                :" + desc_tarefa + "\n"
                               "Prazo                    :" + tarefa_prazo + "\n"
                               "Início                   :" + tarefa_inicio + "\n"
                               "Fim                      :" + tarefa_fim + "\n" + "\n")
                arquivo.write(linha_grava)

            arquivo.close()

            ############################################################################################################
            ## 1-GERA UM df =: DATAFRAME COM O SQL GERADO - USANDO PANDAS
            df = pd.DataFrame(dados)

            ############################################################################################################
            ## O CABEÇALHO DAS COLUNAS PODE SER CRIADO DE DUAS MANEIRAS:
            ## 1- ATRIBUI A columns OS TÍTULOS DAS COLUNAS DO BD SQL PARA USAR COMO CABEÇALHO NO EXCEL
            ##    AS COLUNAS SÃO GERADAS NO MOMENTO DA GERAÇÃO DO SQL NO con
            # columns = [desc[0] for desc in con.description]
            # df = pd.DataFrame(list(sqlquery), columns=columns)
            # df.to_excel(arq_XLS, sheet_name="Lojas", index=False, startcol=0, startrow=0)
            ############################################################################################################
            ## 2- ATRIBUI A VARIÁVEL alias OS CABEÇALHOS DAS COLUNAS
            ##    NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias
            ##    SE NÃO USAR O alias O CABEÇALHO SERÁ 0,1,2,3,4,5
            ############################################################################################################
            ## VAMOS USAR O MÉTODO with... PODE GERAR UMA OU VÁRIAS  PLANILHAS NO MESMO ARQUIVO
            ## NO MOMENTO DA GERAÇÃO DA PLANILHA COM O MÉTODO with O header=alias index=False
            ## NESTE CASO VAMOS CRIAR UM ARQUIVO XLSX COM 1 PLANILHA - Lojas
            alias = ["ID_PROJETO", "NOME_PROJETO", "TIPO PROJETO", "ID_CLIENTE", "TIPO CLIENTE", "NOME CLIENTE",
                     "ID_TAREFA", "DESCRIÇÃO", "PRAZO", "DATA INÍCIO", "DATA FIM"]
            with pd.ExcelWriter(arq_XLSX, engine="xlsxwriter") as ew:
                df.to_excel(ew, sheet_name="Projetos_Tarefas", index=False, header=alias)

            ############################################################################################################
            ## PODEMOS APENDAR UM DATAFRAME DENTRO DE OUTRO PARA GRAVAR EM UMA PLANILHA
            ## APENDA O DATA FRAME df1 NO DATA FRAME df
            # df1 = pd.DataFrame(sqlquery)
            # df3 = df1.append(df1, ignore_index=False, sort=False)
            ############################################################################################################
            ## PODEMOS INCLUIR UMA NOVA PLANILHA DENTRO DO ARQUIVO JÁ GERADO
            ## CRIAMOS A PLANILHA Vendas2 COM O df3 QUE APENDOU O df1
            # with pd.ExcelWriter(arq_XLS1, engine="openpyxl", mode="a") as ew:
            # df3.to_excel(ew, sheet_name="Vendas2", index=False, header=alias)
            cursor.close()
            flash("Arquivo (Excel) - projetos_tarefas.xlsx na pasta /static/arquivos_xlsx e Arquivo (TXT) - projetos_tarefas.txt na pasta /static/arquivos_txt  => gerados com sucesso!", category="warning")

    ####################################################################################################################
    # EDITA UMA TAREFA
    elif botao_acionado == "Editar_Tarefa":
        if request.form.get('cod_projeto') == "" or request.form.get('cod_tarefa') == "":
            flash('Atenção! O código do Projeto e da Tarefa devem ser digitados. Verifique!', category="warning")
        else:
            ############################################################################################################
            # IDENTIFICA OS DADOS DO PROJETO NA TABELA PROJETOS QUE FORAM TRAZIDOS NO MOMENTO DA SELEÇÃO DO
            # PROJETO E SERÃO SERÃO GRAVADOS NA TABELA DE PROJETOS_TAREFAS
            codigo_projeto = int(request.form.get('cod_projeto'))
            codigo_tarefa = int(request.form.get('cod_tarefa'))
            nome_projeto = request.form.get('nome_projeto')
            id_tipo_projeto = request.form.get('tipo_projeto')
            id_cliente = request.form.get('cliente_projeto')
            id_tipo_cliente = request.form.get('tipo_cliente')
            #wait = input(f"Na função Localizar_tarefa - O código do Projeto é {codigo_projeto} e o código da tarefa é {codigo_tarefa}.")
            ####################################################################################################################
            # BUSCA OS TIPOS DE PROJETOS PARA LISTAR NO FORM PROJETOS_TAREFAS
            lista_tipoprojeto = ['']
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tipo_projeto")
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for tip in dados:
                    idtipo_projeto = str(tip[0]).zfill(2)
                    tipo_projeto = tip[1]
                    lista_tipoprojeto.append(idtipo_projeto + "-" + tipo_projeto)
            ####################################################################################################################
            # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS_TAREFAS
            lista_tipocliente = ['']
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM tipo_cliente")
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for tip in dados:
                    cod_tip = str(tip[0]).zfill(2)
                    nome_tip = tip[1]
                    lista_tipocliente.append(cod_tip+"-"+nome_tip)
            ####################################################################################################################
            # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS_TAREFAS
            lista_clientes = ['']
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM clientes")
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for cli in dados:
                    cod_cli = str(cli[0]).zfill(2)
                    nome_cli = cli[1]
                    lista_clientes.append(cod_cli + "-" + nome_cli)
            ################################################################################################################
            # BUSCA O NOME DO CLIENTE PARA ATUALIZAR NA TABELA PROJETOS_TAREFAS
            codigo_cliente = int(request.form.get('cliente_projeto'))
            nome_cliente = ""
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT nome_cliente FROM clientes WHERE id_cliente = ?", (codigo_cliente,))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for proj in dados:
                    nome_cliente = proj[0]
            ############################################################################################################
            # BUSCA TODOS OS REGISTROS DA TAREFA DIGITADA DA TABELA PROJETOS_TAREFAS ASSOCIADAS AO PROJETO DIGITADO
            cod_projeto = cod_tarefa = desc_tarefa = tarefa_prazo = tarefa_inicio = tarefa_fim = ""
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos_tarefas WHERE id_projeto = ? and id_tarefa = ?", (codigo_projeto, codigo_tarefa))
            dados = cursor.fetchall()
            tamanho_dados = len(dados)
            if tamanho_dados != 0:
                for proj in dados:
                    cod_projeto = str(proj[0]).zfill(5)
                    # nome_projeto = proj[1]
                    # id_tipo_projeto = str(proj[2]).zfill(2)
                    # id_cliente = str(proj[3]).zfill(2)
                    # id_tipo_cliente = str(proj[4]).zfill(2)
                    # nome_cliente = proj[5]
                    cod_tarefa = str(proj[6]).zfill(5)
                    desc_tarefa = proj[7]
                    tarefa_prazo = proj[8]
                    tarefa_inicio = proj[9]
                    tarefa_fim = proj[10]
                # wait = input(f"Na função mantem_tarefas - Tamanho dados na busca em projetos_tarefas deste projeto é {tamanho_dados}.")
                ####################################################################################################
                # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT * FROM projetos")
                dados_projetos = cursor.fetchall()
                ########################################################################################################
                # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS_TAREFAS ASSOCIADAS AO PROJETO DIGITADO
                db = None
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT * FROM projetos_tarefas WHERE id_projeto = ? order by id_projeto, id_tarefa",
                               (codigo_projeto,))
                dados_tarefas = cursor.fetchall()
                tamanho_dados = len(dados)
                ####################################################################################################
                mensagem = ""
                return render_template('projetos_tarefas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                                       nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto,
                                       nome_projeto=nome_projeto, id_tipo_projeto=id_tipo_projeto, id_cliente=id_cliente,
                                       id_tipo_cliente=id_tipo_cliente, nome_cliente=nome_cliente, cod_tarefa=cod_tarefa,
                                       desc_tarefa=desc_tarefa, tarefa_prazo=tarefa_prazo, tarefa_inicio=tarefa_inicio,
                                       tarefa_fim=tarefa_fim, dados_projetos=dados_projetos, dados_tarefas=dados_tarefas,
                                       lista_tipoprojeto=lista_tipoprojeto, lista_clientes=lista_clientes, lista_tipocliente=lista_tipocliente)
            else:
                # wait = input("Projeto não encontrado")
                flash('Projeto e;ou Tarefa não encontrados. Verifique!', category="warning")


    ####################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS_TAREFAS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projetos")
    dados_projetos = cursor.fetchall()
    cod_projeto = nome_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = ""
    cod_tarefa = desc_tarefa = tarefa_prazo = tarefa_inicio = tarefa_fim = ""
    ################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA DE TAREFAS DE PROJETOS PARA LISTAR NO FORM PROJETOS
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projetos_tarefas order by id_projeto, id_tarefa")
    dados_tarefas = cursor.fetchall()
    mensagem = ""
    default_tipoprojeto = "01"
    default_clientes = "01"
    default_tipocliente = "01"
    mensagem = ""
    return render_template('projetos_tarefas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                           nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, dados_projetos=dados_projetos,
                           dados_tarefas=dados_tarefas, lista_tipoprojeto=lista_tipoprojeto, default_tipoprojeto=default_tipoprojeto,
                           lista_tipocliente=lista_tipocliente, default_tipocliente=default_tipocliente,
                           lista_clientes=lista_clientes, default_clientes=default_clientes)


########################################################################################################################
# ROTA PARA EDITAR UM PROJETO SELECIONADO NA TABELA DE PROJETOS DO FORM PROJETOS_TAREFAS
@app.route('/edita_projetotarefa/<int:record_id>, <cod_usu_ativo>, <nome_usu_ativo>')
def edita_projetotarefa(record_id, cod_usu_ativo, nome_usu_ativo):
    codigo_projeto = record_id
    cod_usu_ativo = cod_usu_ativo
    nome_usu_ativo = nome_usu_ativo.strip()
    ####################################################################################################################
    # BUSCA OS TIPOS DE PROJETOS PARA LISTAR NO FORM PROJETOS_TAREFAS
    lista_tipoprojeto = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_projeto")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            idtipo_projeto = str(tip[0]).zfill(2)
            tipo_projeto = tip[1]
            lista_tipoprojeto.append(idtipo_projeto + "-" + tipo_projeto)
    ####################################################################################################################
    # BUSCA OS TIPOS DE CLIENTES PARA LISTAR NO FORM PROJETOS_TAREFAS
    lista_tipocliente = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tipo_cliente")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for tip in dados:
            cod_tip = str(tip[0]).zfill(2)
            nome_tip = tip[1]
            lista_tipocliente.append(cod_tip+"-"+nome_tip)
    ####################################################################################################################
    # BUSCA OS CLIENTES PARA LISTAR NO FORM PROJETOS_TAREFAS
    lista_clientes = ['']
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    if tamanho_dados != 0:
        for cli in dados:
            cod_cli = str(cli[0]).zfill(2)
            nome_cli = cli[1]
            lista_clientes.append(cod_cli + "-" + nome_cli)
    ################################################################################################################
    # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS DO PROJETO SELECIONADO
    db = None
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM projetos WHERE id_projeto = ?", (codigo_projeto,))
    dados = cursor.fetchall()
    tamanho_dados = len(dados)
    cod_projeto = nome_projeto = id_tipo_projeto = id_cliente = id_tipo_cliente = nome_cliente = ""
    if tamanho_dados != 0:
        for proj in dados:
            cod_projeto = str(proj[0]).zfill(5)
            nome_projeto = proj[1]
            id_tipo_projeto = str(proj[3]).zfill(2)
            id_cliente = str(proj[4]).zfill(2)
            id_tipo_cliente = str(proj[5]).zfill(2)
            nome_cliente = proj[6]
            # wait = input(f"Em edita_tarefa id_tipo_projeto é  {id_tipo_projeto}.")
            # wait = input(f"Em edita_tarefa id_cliente é  {id_cliente}.")
            # wait = input(f"Em edita_tarefa id_tipo_cliente é  {id_tipo_cliente}.")
            ########################################################################################################
            # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS_TAREFAS ASSOCIADAS AO PROJETO DIGITADO
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos_tarefas WHERE id_projeto = ? order by id_projeto, id_tarefa", (codigo_projeto,))
            dados_tarefas = cursor.fetchall()
            tamanho_dados = len(dados)
            # wait = input(f"Na função mantem_tarefas - Tamanho dados na busca em projetos_tarefas deste projeto é {tamanho_dados}.")
            ####################################################################################################
            # BUSCA TODOS OS REGISTROS DA TABELA PROJETOS PARA LISTAR NO FORM PROJETOS
            db = None
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM projetos")
            dados_projetos = cursor.fetchall()
            ####################################################################################################
            # LIMPA OS CAMPOS DAS TAREFAS - SÓ VAI PREENCHER PÓS SELECINARUMA TAREFA
            cod_tarefa = desc_tarefa = tarefa_prazo = tarefa_inicio = tarefa_fim = ""
            mensagem = ""
            return render_template('projetos_tarefas.html', mens=mensagem, cod_usu_ativo=cod_usu_ativo,
                                   nome_usu_ativo=nome_usu_ativo, cod_usuario=cod_usu_ativo, cod_projeto=cod_projeto,
                                   nome_projeto=nome_projeto, id_tipo_projeto=id_tipo_projeto, id_cliente=id_cliente,
                                   id_tipo_cliente=id_tipo_cliente, nome_cliente=nome_cliente, cod_tarefa=cod_tarefa,
                                   desc_tarefa=desc_tarefa, tarefa_prazo=tarefa_prazo, tarefa_inicio=tarefa_inicio,
                                   tarefa_fim=tarefa_fim, dados_projetos=dados_projetos, dados_tarefas=dados_tarefas,
                                   lista_tipoprojeto=lista_tipoprojeto, lista_clientes=lista_clientes, lista_tipocliente=lista_tipocliente)


########################################################################################################################
# INCIAR A APLICAÇÃO FLASK - Este if vai executar o código de programa abaixo
# Se não tiver este if, não vai rodar no servidor.
if __name__ == '__main__':
    app.run(debug=True)
