#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Pagamentos
Aplicação de linha de comando para registrar e consultar pagamentos
"""

import os
import sys
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from pathlib import Path


# Configuração de diretórios
CONFIG_DIR = os.path.expanduser("~/.pagto")
DB_PATH = os.path.join(CONFIG_DIR, "pagamentos.db")
COMPROVANTES_DIR = os.path.join(CONFIG_DIR, "comprovantes")


class Pagamento:
    """Classe para representar um pagamento"""
    
    def __init__(self, categoria: str, beneficiario: str, conta: str, 
                 valor: float, data_pagamento: str = None, devendo_para: str = "",
                 id_pagamento: int = None, pendente: bool = False, deletado: bool = False,
                 comprovante: str = "", observacao: str = ""):
        self.id = id_pagamento
        self.categoria = categoria
        self.beneficiario = beneficiario
        self.data_pagamento = data_pagamento or datetime.now().strftime("%d/%m/%Y")
        self.conta = conta
        self.valor = valor
        self.devendo_para = devendo_para
        self.pendente = pendente
        self.deletado = deletado
        self.comprovante = comprovante
        self.observacao = observacao
    
    def to_dict(self) -> Dict:
        """Converte o pagamento para dicionário"""
        return {
            'id': self.id,
            'categoria': self.categoria,
            'beneficiario': self.beneficiario,
            'data_pagamento': self.data_pagamento,
            'conta': self.conta,
            'valor': self.valor,
            'devendo_para': self.devendo_para,
            'pendente': 1 if self.pendente else 0,
            'deletado': 1 if self.deletado else 0,
            'comprovante': self.comprovante,
            'observacao': self.observacao
        }


class GerenciadorPagamentos:
    """Classe para gerenciar os pagamentos com SQLite"""
    
    def __init__(self):
        self._garantir_diretorios()
        self._garantir_banco()
        self._migrar_csv_se_necessario()
    
    def _garantir_diretorios(self):
        """Garante que os diretórios necessários existem"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(COMPROVANTES_DIR, exist_ok=True)
    
    def _garantir_banco(self):
        """Cria o banco de dados e tabelas se não existirem"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                beneficiario TEXT NOT NULL,
                data_pagamento TEXT NOT NULL,
                conta TEXT NOT NULL,
                valor REAL NOT NULL,
                devendo_para TEXT,
                pendente INTEGER DEFAULT 0,
                deletado INTEGER DEFAULT 0,
                comprovante TEXT,
                observacao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Verifica se precisa adicionar coluna observacao (migração de versões antigas)
        cursor.execute("PRAGMA table_info(pagamentos)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'observacao' not in colunas:
            cursor.execute('ALTER TABLE pagamentos ADD COLUMN observacao TEXT')
        
        conn.commit()
        conn.close()
    
    def _migrar_csv_se_necessario(self):
        """Migra dados de CSV antigo se existir"""
        csv_path = os.path.join(os.getcwd(), 'pagamentos.csv')
        
        if not os.path.exists(csv_path):
            return
        
        print("\n🔄 Detectado arquivo CSV antigo. Migrando para SQLite...")
        
        try:
            import csv
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Verifica se já tem dados
            cursor.execute("SELECT COUNT(*) FROM pagamentos")
            if cursor.fetchone()[0] > 0:
                print("⚠ Banco já contém dados. Migração cancelada.")
                conn.close()
                return
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                migrados = 0
                
                for row in reader:
                    cursor.execute('''
                        INSERT INTO pagamentos 
                        (categoria, beneficiario, data_pagamento, conta, valor, 
                         devendo_para, pendente, deletado, comprovante, observacao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('categoria', ''),
                        row.get('beneficiario', ''),
                        row.get('data_pagamento', ''),
                        row.get('conta', ''),
                        float(row.get('valor', 0)),
                        row.get('devendo_para', ''),
                        int(row.get('pendente', 0)),
                        int(row.get('deletado', 0)),
                        row.get('comprovante', ''),
                        row.get('observacao', '')
                    ))
                    migrados += 1
            
            conn.commit()
            conn.close()
            
            print(f"✓ {migrados} registros migrados com sucesso!")
            print(f"✓ Banco de dados criado em: {DB_PATH}")
            print(f"⚠ Você pode fazer backup e remover o arquivo CSV antigo: {csv_path}\n")
            
        except Exception as e:
            print(f"✗ Erro na migração: {e}")
    
    def _copiar_comprovante(self, caminho_origem: str, id_pagamento: int, beneficiario: str, valor: float) -> str:
        """Copia o comprovante para a pasta e retorna o novo nome"""
        if not caminho_origem or not os.path.exists(caminho_origem):
            return ""
        
        # Pega a extensão do arquivo
        _, extensao = os.path.splitext(caminho_origem)
        
        # Limpa o nome do beneficiário (remove caracteres especiais)
        beneficiario_limpo = "".join(c for c in beneficiario if c.isalnum() or c in (' ', '-', '_')).strip()
        beneficiario_limpo = beneficiario_limpo.replace(' ', '_')[:30]  # Limita tamanho
        
        # Valor arredondado
        valor_arredondado = int(round(valor))
        
        # Monta o novo nome: ID_BENEFICIARIO_VALOR.extensao
        novo_nome = f"{id_pagamento}_{beneficiario_limpo}_{valor_arredondado}{extensao}"
        caminho_destino = os.path.join(COMPROVANTES_DIR, novo_nome)
        
        # Copia o arquivo
        import shutil
        try:
            shutil.copy2(caminho_origem, caminho_destino)
            return novo_nome
        except Exception as e:
            print(f"  ⚠ Erro ao copiar comprovante: {e}")
            return ""
    
    def _aplicar_filtros_sql(self, filtros: Dict[str, str]) -> Tuple[str, List]:
        """Gera cláusula WHERE e parâmetros para filtros SQL"""
        if not filtros:
            return "", []
        
        condicoes = []
        parametros = []
        
        # Mapeamento de campos
        mapeamento = {
            'categoria': 'categoria',
            'beneficiario': 'beneficiario',
            'conta': 'conta',
            'devendo': 'devendo_para',
            'devendo_para': 'devendo_para',
            'pendente': 'pendente',
            'data': 'data_pagamento',
            'data_pagamento': 'data_pagamento',
            'id': 'id',
            'valor': 'valor',
            'comprovante': 'comprovante',
            'observacao': 'observacao'
        }
        
        for campo, valor_filtro in filtros.items():
            campo_lower = campo.lower()
            campo_real = mapeamento.get(campo_lower, campo_lower)
            valor_filtro_lower = valor_filtro.lower()
            
            if campo_real == 'pendente':
                valor_esperado = 1 if valor_filtro_lower in ['s', 'sim', '1', 'true', 'yes'] else 0
                condicoes.append(f"{campo_real} = ?")
                parametros.append(valor_esperado)
            
            elif campo_real == 'valor':
                if valor_filtro_lower.startswith('>='):
                    condicoes.append(f"{campo_real} >= ?")
                    parametros.append(float(valor_filtro_lower[2:]))
                elif valor_filtro_lower.startswith('<='):
                    condicoes.append(f"{campo_real} <= ?")
                    parametros.append(float(valor_filtro_lower[2:]))
                elif valor_filtro_lower.startswith('>'):
                    condicoes.append(f"{campo_real} > ?")
                    parametros.append(float(valor_filtro_lower[1:]))
                elif valor_filtro_lower.startswith('<'):
                    condicoes.append(f"{campo_real} < ?")
                    parametros.append(float(valor_filtro_lower[1:]))
                else:
                    condicoes.append(f"{campo_real} = ?")
                    parametros.append(float(valor_filtro_lower))
            
            elif campo_real == 'id':
                condicoes.append(f"{campo_real} = ?")
                parametros.append(int(valor_filtro))
            
            else:
                # Busca parcial case-insensitive
                condicoes.append(f"LOWER({campo_real}) LIKE ?")
                parametros.append(f"%{valor_filtro_lower}%")
        
        where_clause = " AND ".join(condicoes)
        return where_clause, parametros
    
    def _parsear_ordenacao(self, sort_value: str) -> str:
        """Parseia o valor de ordenação e retorna cláusula ORDER BY"""
        if not sort_value:
            return "data_pagamento ASC, id ASC"  # Padrão: data ascendente
        
        # Remove prefixo - se houver (indica descendente)
        descendente = sort_value.startswith('-')
        campo = sort_value[1:] if descendente else sort_value
        
        # Mapeamento de campos
        mapeamento = {
            'data': 'data_pagamento',
            'valor': 'valor',
            'categoria': 'categoria',
            'beneficiario': 'beneficiario',
            'conta': 'conta',
            'id': 'id'
        }
        
        campo_sql = mapeamento.get(campo.lower(), 'data_pagamento')
        direcao = 'DESC' if descendente else 'ASC'
        
        return f"{campo_sql} {direcao}, id ASC"
    
    def adicionar_pagamento(self, pagamento: Pagamento, caminho_comprovante: str = None) -> Optional[int]:
        """Adiciona um novo pagamento ao banco"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pagamentos 
            (categoria, beneficiario, data_pagamento, conta, valor, 
             devendo_para, pendente, deletado, comprovante, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pagamento.categoria,
            pagamento.beneficiario,
            pagamento.data_pagamento,
            pagamento.conta,
            pagamento.valor,
            pagamento.devendo_para,
            1 if pagamento.pendente else 0,
            1 if pagamento.deletado else 0,
            pagamento.comprovante,
            pagamento.observacao
        ))
        
        pagamento_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Copia o comprovante se fornecido
        if caminho_comprovante:
            nome_comprovante = self._copiar_comprovante(
                caminho_comprovante,
                pagamento_id,
                pagamento.beneficiario,
                pagamento.valor
            )
            if nome_comprovante:
                # Atualiza o registro com o nome do comprovante
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE pagamentos SET comprovante = ? WHERE id = ?",
                             (nome_comprovante, pagamento_id))
                conn.commit()
                conn.close()
        
        msg = f"\n✓ Pagamento registrado com sucesso! (ID: {pagamento_id})"
        if caminho_comprovante and nome_comprovante:
            msg += f"\n✓ Comprovante salvo: {nome_comprovante}"
        print(msg)
        
        return pagamento_id
    
    def listar_todos(self, incluir_deletados: bool = False, filtros: Dict[str, str] = None,
                    ordenacao: str = None) -> List[Dict]:
        """Lista todos os pagamentos"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Monta a query base
        query = "SELECT * FROM pagamentos"
        parametros = []
        
        # Adiciona condição de deletados
        condicoes = []
        if not incluir_deletados:
            condicoes.append("deletado = 0")
        
        # Aplica filtros
        if filtros:
            # Remove 'sort' dos filtros se estiver presente
            filtros_limpos = {k: v for k, v in filtros.items() if k.lower() != 'sort'}
            if filtros_limpos:
                where_filtros, params_filtros = self._aplicar_filtros_sql(filtros_limpos)
                if where_filtros:
                    condicoes.append(where_filtros)
                    parametros.extend(params_filtros)
        
        # Adiciona WHERE se houver condições
        if condicoes:
            query += " WHERE " + " AND ".join(condicoes)
        
        # Adiciona ordenação
        order_by = self._parsear_ordenacao(ordenacao)
        query += f" ORDER BY {order_by}"
        
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        conn.close()
        
        # Converte para lista de dicionários
        return [dict(row) for row in resultados]
    
    def listar_deletados(self, filtros: Dict[str, str] = None, ordenacao: str = None) -> List[Dict]:
        """Lista apenas os pagamentos deletados"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM pagamentos WHERE deletado = 1"
        parametros = []
        
        # Aplica filtros
        if filtros:
            filtros_limpos = {k: v for k, v in filtros.items() if k.lower() != 'sort'}
            if filtros_limpos:
                where_filtros, params_filtros = self._aplicar_filtros_sql(filtros_limpos)
                if where_filtros:
                    query += " AND " + where_filtros
                    parametros.extend(params_filtros)
        
        # Adiciona ordenação
        order_by = self._parsear_ordenacao(ordenacao)
        query += f" ORDER BY {order_by}"
        
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in resultados]
    
    def buscar_por_id(self, id_busca: int) -> Optional[Dict]:
        """Busca um pagamento por ID"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pagamentos WHERE id = ?", (id_busca,))
        resultado = cursor.fetchone()
        conn.close()
        
        return dict(resultado) if resultado else None
    
    def marcar_como_deletado(self, id_pagamento: int) -> bool:
        """Marca um pagamento como deletado"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE pagamentos SET deletado = 1 WHERE id = ?", (id_pagamento,))
        linhas_afetadas = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return linhas_afetadas > 0
    
    def atualizar_pagamento(self, id_pagamento: int, dados_atualizados: Dict,
                          caminho_comprovante: str = None) -> bool:
        """Atualiza um pagamento existente"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Se há novo comprovante, copia e atualiza
        if caminho_comprovante:
            beneficiario = dados_atualizados.get('beneficiario')
            valor = dados_atualizados.get('valor', 0)
            
            # Se beneficiario ou valor não estão nos dados atualizados, busca do banco
            if not beneficiario or not valor:
                cursor.execute("SELECT beneficiario, valor FROM pagamentos WHERE id = ?",
                             (id_pagamento,))
                row = cursor.fetchone()
                if row:
                    beneficiario = beneficiario or row[0]
                    valor = valor or row[1]
            
            nome_comprovante = self._copiar_comprovante(
                caminho_comprovante,
                id_pagamento,
                beneficiario,
                float(valor)
            )
            if nome_comprovante:
                dados_atualizados['comprovante'] = nome_comprovante
        
        # Monta a query de atualização
        campos = []
        valores = []
        
        for campo, valor in dados_atualizados.items():
            if campo != 'id':  # Não permite alterar o ID
                campos.append(f"{campo} = ?")
                valores.append(valor)
        
        if not campos:
            conn.close()
            return False
        
        valores.append(id_pagamento)
        query = f"UPDATE pagamentos SET {', '.join(campos)} WHERE id = ?"
        
        cursor.execute(query, valores)
        linhas_afetadas = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return linhas_afetadas > 0
    
    def agregrar_por_categoria(self, filtros: Dict[str, str] = None) -> Dict[str, float]:
        """Agrega os valores por categoria"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = "SELECT categoria, SUM(valor) as total FROM pagamentos WHERE deletado = 0"
        parametros = []
        
        # Aplica filtros
        if filtros:
            filtros_limpos = {k: v for k, v in filtros.items() if k.lower() != 'sort'}
            if filtros_limpos:
                where_filtros, params_filtros = self._aplicar_filtros_sql(filtros_limpos)
                if where_filtros:
                    query += " AND " + where_filtros
                    parametros.extend(params_filtros)
        
        query += " GROUP BY categoria ORDER BY categoria"
        
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        conn.close()
        
        return {row[0]: row[1] for row in resultados}


def formatar_moeda(valor: float) -> str:
    """Formata um valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def solicitar_input(prompt: str, obrigatorio: bool = False, default: str = None, valor_atual: str = None, permite_limpar: bool = False) -> str:
    """Solicita input do usuário com validação"""
    # Se há valor atual, mostra entre colchetes
    if valor_atual:
        if permite_limpar:
            prompt_completo = f"{prompt} [{valor_atual}] (LIMPAR para apagar): "
        else:
            prompt_completo = f"{prompt} [{valor_atual}]: "
    elif default:
        prompt_completo = f"{prompt} [{default}]: "
    else:
        prompt_completo = f"{prompt}: "
    
    while True:
        valor = input(prompt_completo).strip()
        
        # Se digitou LIMPAR (case-insensitive), retorna string vazia
        if permite_limpar and valor.upper() == "LIMPAR":
            return ""
        
        if valor:
            return valor
        elif valor_atual:
            return valor_atual
        elif default is not None:
            return default
        elif not obrigatorio:
            return ""
        else:
            print("  ⚠ Este campo é obrigatório. Por favor, preencha.")


def solicitar_valor(valor_atual: str = None) -> float:
    """Solicita um valor monetário do usuário"""
    prompt = f"Valor (R$) [{valor_atual}]: " if valor_atual else "Valor (R$): "
    
    while True:
        try:
            valor_str = input(prompt).strip()
            
            # Se não digitou nada e tem valor atual, mantém o atual
            if not valor_str and valor_atual:
                return float(valor_atual.replace(",", "."))
            
            valor_str = valor_str.replace(",", ".")
            valor = float(valor_str)
            if valor < 0:
                print("  ⚠ O valor não pode ser negativo.")
                continue
            return valor
        except ValueError:
            if not valor_str and not valor_atual:
                print("  ⚠ Valor inválido. Use números (ex: 150.50 ou 150,50)")
            elif not valor_str:
                return float(valor_atual.replace(",", "."))


def solicitar_data(valor_atual: str = None) -> str:
    """Solicita uma data do usuário ou usa a data atual"""
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    if valor_atual:
        data = input(f"Data do pagamento (dd/mm/aaaa) [{valor_atual}]: ").strip()
    else:
        data = input(f"Data do pagamento (dd/mm/aaaa) [hoje: {hoje}]: ").strip()
    
    if not data:
        return valor_atual if valor_atual else hoje
    
    # Validação básica de formato
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return data
    except ValueError:
        valor_padrao = valor_atual if valor_atual else hoje
        print(f"  ⚠ Data inválida. Usando: {valor_padrao}")
        return valor_padrao


def solicitar_pendente(valor_atual: str = None) -> bool:
    """Solicita se o pagamento está pendente"""
    atual_texto = "Sim" if valor_atual == "1" else "Não" if valor_atual == "0" else None
    
    if atual_texto:
        resposta = input(f"Pagamento pendente? (s/n) [{atual_texto}]: ").strip().lower()
    else:
        resposta = input("Pagamento pendente? (s/n) [Não]: ").strip().lower()
    
    if not resposta:
        return valor_atual == "1" if valor_atual else False
    
    return resposta in ['s', 'sim', 'yes', 'y']


def solicitar_comprovante() -> str:
    """Solicita o caminho do comprovante (opcional)"""
    caminho = input("Caminho do comprovante (opcional): ").strip()
    
    if not caminho:
        return ""
    
    # Remove aspas se houver
    caminho = caminho.strip('"').strip("'")
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho):
        print(f"  ⚠ Arquivo não encontrado: {caminho}")
        return ""
    
    # Verifica se é um arquivo
    if not os.path.isfile(caminho):
        print(f"  ⚠ O caminho não aponta para um arquivo: {caminho}")
        return ""
    
    return caminho


def parsear_filtros(args: List[str]) -> Tuple[Dict[str, str], str]:
    """
    Parseia filtros da linha de comando no formato campo:valor
    Retorna: (filtros_dict, ordenacao)
    Exemplo: categoria:TRATOR pendente:S sort:-data
    """
    filtros = {}
    ordenacao = None
    
    for arg in args:
        if ':' in arg:
            campo, valor = arg.split(':', 1)
            campo = campo.strip()
            valor = valor.strip()
            
            if campo.lower() == 'sort':
                ordenacao = valor
            else:
                filtros[campo] = valor
    
    return filtros, ordenacao


def comando_novo():
    """Executa o comando 'pagto novo'"""
    print("\n=== NOVO PAGAMENTO ===\n")
    
    categoria = solicitar_input("Categoria", obrigatorio=True)
    beneficiario = solicitar_input("Beneficiário", obrigatorio=True)
    data_pagamento = solicitar_data()
    conta = solicitar_input("Conta", obrigatorio=True)
    valor = solicitar_valor()
    devendo_para = solicitar_input("Devendo para (opcional)", obrigatorio=False)
    pendente = solicitar_pendente()
    comprovante = solicitar_comprovante()
    observacao = solicitar_input("Observação (opcional)", obrigatorio=False)
    
    pagamento = Pagamento(
        categoria=categoria,
        beneficiario=beneficiario,
        data_pagamento=data_pagamento,
        conta=conta,
        valor=valor,
        devendo_para=devendo_para,
        pendente=pendente,
        observacao=observacao
    )
    
    gerenciador = GerenciadorPagamentos()
    gerenciador.adicionar_pagamento(pagamento, caminho_comprovante=comprovante)


def comando_todos(filtros: Dict[str, str] = None, ordenacao: str = None):
    """Executa o comando 'pagto todos'"""
    gerenciador = GerenciadorPagamentos()
    pagamentos = gerenciador.listar_todos(filtros=filtros, ordenacao=ordenacao)
    
    if not pagamentos:
        if filtros:
            print("\nNenhum pagamento encontrado com os filtros aplicados.")
            print(f"Filtros: {filtros}")
        else:
            print("\nNenhum pagamento registrado ainda.")
        return
    
    # Mostra filtros aplicados
    if filtros:
        print(f"\n=== FILTROS APLICADOS: {filtros} ===")
    if ordenacao:
        print(f"=== ORDENAÇÃO: {ordenacao} ===")
    
    print("\n=== TODOS OS PAGAMENTOS ===\n")
    
    # Cabeçalho da tabela
    print(f"{'ID':<5} {'Data':<12} {'Categoria':<18} {'Beneficiário':<20} {'Valor':>13} {'Status':<8} {'📎':<3} {'Obs':<3}")
    print("-" * 95)
    
    total = 0.0
    for pag in pagamentos:
        try:
            valor = float(pag['valor'])
            total += valor
        except (ValueError, KeyError, TypeError):
            valor = 0.0
        
        # Status do pagamento
        status = "⏳ Pend." if pag.get('pendente') == 1 else "✓ Pago"
        
        # Indicador de comprovante
        comp_icon = "📎" if pag.get('comprovante') else ""
        
        # Indicador de observação
        obs_icon = "📝" if pag.get('observacao') else ""
        
        print(f"{pag.get('id', 0):<5} "
              f"{pag.get('data_pagamento', ''):<12} "
              f"{pag.get('categoria', '')[:17]:<18} "
              f"{pag.get('beneficiario', '')[:19]:<20} "
              f"{formatar_moeda(valor):>13} "
              f"{status:<8} "
              f"{comp_icon:<3} "
              f"{obs_icon:<3}")
    
    print("-" * 95)
    print(f"{'TOTAL:':<50} {formatar_moeda(total):>13}")
    print(f"\nRegistros encontrados: {len(pagamentos)}\n")


def comando_categoria(filtros: Dict[str, str] = None, ordenacao: str = None):
    """Executa o comando 'pagto categoria'"""
    gerenciador = GerenciadorPagamentos()
    categorias = gerenciador.agregrar_por_categoria(filtros=filtros)
    
    if not categorias:
        if filtros:
            print("\nNenhum pagamento encontrado com os filtros aplicados.")
            print(f"Filtros: {filtros}")
        else:
            print("\nNenhum pagamento registrado ainda.")
        return
    
    # Mostra filtros aplicados
    if filtros:
        print(f"\n=== FILTROS APLICADOS: {filtros} ===\n")
    
    print("\n=== PAGAMENTOS POR CATEGORIA ===\n")
    
    # Cabeçalho
    print(f"{'Categoria':<30} {'Total':>20}")
    print("-" * 52)
    
    # Ordena por categoria
    total_geral = 0.0
    for categoria in sorted(categorias.keys()):
        valor = categorias[categoria]
        total_geral += valor
        print(f"{categoria[:29]:<30} {formatar_moeda(valor):>20}")
    
    print("-" * 52)
    print(f"{'TOTAL GERAL:':<30} {formatar_moeda(total_geral):>20}\n")


def comando_delete(id_pagamento: str):
    """Executa o comando 'pagto delete [id]'"""
    try:
        id_int = int(id_pagamento)
    except ValueError:
        print(f"\n✗ ID inválido: {id_pagamento}")
        return
    
    gerenciador = GerenciadorPagamentos()
    
    # Verifica se o pagamento existe
    pagamento = gerenciador.buscar_por_id(id_int)
    
    if not pagamento:
        print(f"\n✗ Pagamento com ID {id_pagamento} não encontrado.")
        return
    
    # Verifica se já está deletado
    if pagamento.get('deletado') == 1:
        print(f"\n⚠ Pagamento ID {id_pagamento} já está deletado.")
        return
    
    # Mostra os dados do pagamento
    print(f"\n=== DELETAR PAGAMENTO ===\n")
    print(f"ID: {pagamento.get('id')}")
    print(f"Categoria: {pagamento.get('categoria')}")
    print(f"Beneficiário: {pagamento.get('beneficiario')}")
    print(f"Valor: {formatar_moeda(float(pagamento.get('valor', 0)))}")
    print(f"Data: {pagamento.get('data_pagamento')}")
    
    # Confirmação
    confirmacao = input("\nDeseja realmente deletar este pagamento? (s/n): ").strip().lower()
    
    if confirmacao in ['s', 'sim', 'yes', 'y']:
        if gerenciador.marcar_como_deletado(id_int):
            print(f"\n✓ Pagamento ID {id_pagamento} deletado com sucesso!")
        else:
            print(f"\n✗ Erro ao deletar pagamento.")
    else:
        print("\n✗ Operação cancelada.")


def comando_deletados(filtros: Dict[str, str] = None, ordenacao: str = None):
    """Executa o comando 'pagto deletados'"""
    gerenciador = GerenciadorPagamentos()
    pagamentos = gerenciador.listar_deletados(filtros=filtros, ordenacao=ordenacao)
    
    if not pagamentos:
        if filtros:
            print("\nNenhum pagamento deletado encontrado com os filtros aplicados.")
            print(f"Filtros: {filtros}")
        else:
            print("\nNenhum pagamento deletado encontrado.")
        return
    
    # Mostra filtros aplicados
    if filtros:
        print(f"\n=== FILTROS APLICADOS: {filtros} ===")
    if ordenacao:
        print(f"=== ORDENAÇÃO: {ordenacao} ===")
    
    print("\n=== PAGAMENTOS DELETADOS ===\n")
    
    # Cabeçalho da tabela  
    print(f"{'ID':<5} {'Data':<12} {'Categoria':<18} {'Beneficiário':<20} {'Valor':>13} {'📎':<3} {'📝':<3}")
    print("-" * 85)
    
    total = 0.0
    for pag in pagamentos:
        try:
            valor = float(pag['valor'])
            total += valor
        except (ValueError, KeyError, TypeError):
            valor = 0.0
        
        # Indicador de comprovante
        comp_icon = "📎" if pag.get('comprovante') else ""
        
        # Indicador de observação
        obs_icon = "📝" if pag.get('observacao') else ""
        
        print(f"{pag.get('id', 0):<5} "
              f"{pag.get('data_pagamento', ''):<12} "
              f"{pag.get('categoria', '')[:17]:<18} "
              f"{pag.get('beneficiario', '')[:19]:<20} "
              f"{formatar_moeda(valor):>13} "
              f"{comp_icon:<3} "
              f"{obs_icon:<3}")
    
    print("-" * 85)
    print(f"{'TOTAL:':<50} {formatar_moeda(total):>13}")
    print(f"\nRegistros encontrados: {len(pagamentos)}\n")


def comando_editar(id_pagamento: str):
    """Executa o comando 'pagto editar [id]'"""
    try:
        id_int = int(id_pagamento)
    except ValueError:
        print(f"\n✗ ID inválido: {id_pagamento}")
        return
    
    gerenciador = GerenciadorPagamentos()
    
    # Verifica se o pagamento existe
    pagamento = gerenciador.buscar_por_id(id_int)
    
    if not pagamento:
        print(f"\n✗ Pagamento com ID {id_pagamento} não encontrado.")
        return
    
    # Verifica se está deletado
    if pagamento.get('deletado') == 1:
        print(f"\n✗ Não é possível editar um pagamento deletado.")
        return
    
    print(f"\n=== EDITAR PAGAMENTO (ID: {id_pagamento}) ===\n")
    print("Pressione ENTER para manter o valor atual")
    print("Digite LIMPAR para apagar o campo\n")
    
    # Mostra comprovante atual se existir
    if pagamento.get('comprovante'):
        print(f"📎 Comprovante atual: {pagamento.get('comprovante')}")
    
    # Mostra observação atual se existir
    if pagamento.get('observacao'):
        print(f"📝 Observação atual: {pagamento.get('observacao')}\n")
    
    # Solicita novos valores (mostrando os atuais)
    categoria = solicitar_input("Categoria", obrigatorio=True, valor_atual=pagamento.get('categoria'))
    beneficiario = solicitar_input("Beneficiário", obrigatorio=True, valor_atual=pagamento.get('beneficiario'))
    data_pagamento = solicitar_data(valor_atual=pagamento.get('data_pagamento'))
    conta = solicitar_input("Conta", obrigatorio=True, valor_atual=pagamento.get('conta'))
    valor = solicitar_valor(valor_atual=str(pagamento.get('valor')))
    devendo_para = solicitar_input("Devendo para", obrigatorio=False, valor_atual=pagamento.get('devendo_para'), permite_limpar=True)
    pendente = solicitar_pendente(valor_atual=str(pagamento.get('pendente')))
    observacao = solicitar_input("Observação", obrigatorio=False, valor_atual=pagamento.get('observacao'), permite_limpar=True)
    
    # Pergunta sobre comprovante
    comprovante = None
    if pagamento.get('comprovante'):
        atualizar_comprovante = input("Atualizar comprovante? (s/n) [Não]: ").strip().lower()
        if atualizar_comprovante in ['s', 'sim', 'yes', 'y']:
            comprovante = solicitar_comprovante()
    else:
        print("Adicionar comprovante:")
        comprovante = solicitar_comprovante()
    
    # Monta o dicionário com os dados atualizados
    dados_atualizados = {
        'categoria': categoria,
        'beneficiario': beneficiario,
        'data_pagamento': data_pagamento,
        'conta': conta,
        'valor': valor,
        'devendo_para': devendo_para,
        'pendente': 1 if pendente else 0,
        'observacao': observacao
    }
    
    # Atualiza o pagamento
    if gerenciador.atualizar_pagamento(id_int, dados_atualizados, caminho_comprovante=comprovante):
        print(f"\n✓ Pagamento ID {id_pagamento} atualizado com sucesso!")
        if comprovante:
            print(f"✓ Comprovante atualizado!")
    else:
        print(f"\n✗ Erro ao atualizar pagamento.")


def mostrar_ajuda():
    """Mostra a ajuda do programa"""
    print(f"""
=== SISTEMA DE GERENCIAMENTO DE PAGAMENTOS ===

📁 Banco de dados: {DB_PATH}
📎 Comprovantes: {COMPROVANTES_DIR}

Comandos disponíveis:

  pagto novo              - Registra um novo pagamento (com comprovante e observação)
  pagto todos             - Lista todos os pagamentos em formato tabular
  pagto categoria         - Mostra total agregado por categoria
  pagto delete [id]       - Marca um pagamento como deletado
  pagto deletados         - Lista todos os pagamentos deletados
  pagto editar [id]       - Edita um pagamento existente
  pagto ajuda             - Mostra esta mensagem de ajuda

Filtros (aplicáveis em todos, categoria e deletados):
  Use o formato campo:valor para filtrar resultados
  
  Campos disponíveis:
    categoria, beneficiario, conta, devendo, pendente, data, valor, id, observacao
  
  Exemplos de filtros:
    categoria:TRATOR           - Filtra por categoria
    pendente:s                 - Mostra apenas pendentes
    valor:>100                 - Valores maiores que 100
    beneficiario:silva         - Beneficiários que contêm "silva"

Ordenação (aplicável em todos e deletados):
  Use sort:campo ou sort:-campo para ordenar resultados
  
  Campos de ordenação:
    data, valor, categoria, beneficiario, conta, id
  
  Exemplos:
    sort:data                  - Ordena por data ascendente (padrão)
    sort:-data                 - Ordena por data descendente
    sort:valor                 - Ordena por valor ascendente
    sort:-valor                - Ordena por valor descendente

Edição de campos:
  Durante a edição, use a palavra LIMPAR para apagar um campo opcional
  Exemplo: ao editar "Devendo para", digite LIMPAR para remover o valor

Exemplos de uso completo:

  # Comandos básicos
  pagto novo
  pagto todos
  pagto categoria
  pagto delete 5
  pagto editar 3
  
  # Com filtros
  pagto todos categoria:Alimentação pendente:s
  pagto categoria conta:Nubank
  pagto todos valor:>100 beneficiario:supermercado
  
  # Com ordenação
  pagto todos sort:-data                    # Mais recentes primeiro
  pagto todos sort:valor                     # Menor valor primeiro
  pagto todos categoria:TRATOR sort:-valor   # TRATOR, maior valor primeiro
  pagto deletados sort:-data                 # Deletados mais recentes primeiro

Ícones nos relatórios:
  📎 = Pagamento possui comprovante anexado
  📝 = Pagamento possui observação
  ⏳ = Pagamento pendente
  ✓ = Pagamento concluído
""")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Erro: Comando não especificado.")
        mostrar_ajuda()
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    # Parseia filtros e ordenação dos argumentos restantes
    filtros, ordenacao = parsear_filtros(sys.argv[2:]) if len(sys.argv) > 2 else ({}, None)
    
    if comando == "novo":
        comando_novo()
    elif comando == "todos":
        comando_todos(filtros=filtros if filtros else None, ordenacao=ordenacao)
    elif comando == "categoria":
        comando_categoria(filtros=filtros if filtros else None, ordenacao=ordenacao)
    elif comando == "delete":
        # Para delete, o segundo argumento é o ID, não um filtro
        if len(sys.argv) < 3 or ':' in sys.argv[2]:
            print("Erro: ID do pagamento não especificado.")
            print("Uso: pagto delete [id]")
            sys.exit(1)
        comando_delete(sys.argv[2])
    elif comando == "deletados":
        comando_deletados(filtros=filtros if filtros else None, ordenacao=ordenacao)
    elif comando == "editar":
        # Para editar, o segundo argumento é o ID, não um filtro
        if len(sys.argv) < 3 or ':' in sys.argv[2]:
            print("Erro: ID do pagamento não especificado.")
            print("Uso: pagto editar [id]")
            sys.exit(1)
        comando_editar(sys.argv[2])
    elif comando in ["ajuda", "help", "-h", "--help"]:
        mostrar_ajuda()
    else:
        print(f"Erro: Comando '{comando}' não reconhecido.")
        mostrar_ajuda()
        sys.exit(1)


if __name__ == "__main__":
    main()
