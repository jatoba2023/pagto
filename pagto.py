#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Pagamentos
Aplicação de linha de comando para registrar e consultar pagamentos
"""

import os
import sys
import csv
from datetime import datetime
from typing import List, Dict
from collections import defaultdict


class Pagamento:
    """Classe para representar um pagamento"""
    
    def __init__(self, categoria: str, beneficiario: str, conta: str, 
                 valor: float, data_pagamento: str = None, devendo_para: str = "",
                 id_pagamento: str = None, pendente: bool = False, deletado: bool = False,
                 comprovante: str = ""):
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
    
    def to_dict(self) -> Dict:
        """Converte o pagamento para dicionário"""
        return {
            'id': self.id,
            'categoria': self.categoria,
            'beneficiario': self.beneficiario,
            'data_pagamento': self.data_pagamento,
            'conta': self.conta,
            'valor': str(self.valor),
            'devendo_para': self.devendo_para,
            'pendente': '1' if self.pendente else '0',
            'deletado': '1' if self.deletado else '0',
            'comprovante': self.comprovante
        }


class GerenciadorPagamentos:
    """Classe para gerenciar os pagamentos"""
    
    ARQUIVO_DADOS = 'pagamentos.csv'
    PASTA_COMPROVANTES = 'comprovantes'
    CAMPOS = ['id', 'categoria', 'beneficiario', 'data_pagamento', 'conta', 'valor', 'devendo_para', 'pendente', 'deletado', 'comprovante']
    
    def __init__(self):
        self._garantir_arquivo_existe()
        self._garantir_pasta_comprovantes()
        self._migrar_dados_antigos()
    
    def _garantir_arquivo_existe(self):
        """Garante que o arquivo CSV existe com os cabeçalhos corretos"""
        if not os.path.exists(self.ARQUIVO_DADOS):
            with open(self.ARQUIVO_DADOS, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.CAMPOS)
                writer.writeheader()
    
    def _garantir_pasta_comprovantes(self):
        """Garante que a pasta de comprovantes existe"""
        if not os.path.exists(self.PASTA_COMPROVANTES):
            os.makedirs(self.PASTA_COMPROVANTES)
    
    def _migrar_dados_antigos(self):
        """Migra dados de versões antigas para incluir novos campos"""
        try:
            with open(self.ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                campos_atuais = reader.fieldnames
                
                # Se não tem o campo 'id' ou 'comprovante', precisa migrar
                if campos_atuais and ('id' not in campos_atuais or 'comprovante' not in campos_atuais):
                    dados = list(reader)
                    
                    # Fecha o arquivo e reescreve com novos campos
                    with open(self.ARQUIVO_DADOS, 'w', newline='', encoding='utf-8') as fw:
                        writer = csv.DictWriter(fw, fieldnames=self.CAMPOS)
                        writer.writeheader()
                        
                        for idx, row in enumerate(dados, start=1):
                            if 'id' not in row or not row.get('id'):
                                row['id'] = str(idx)
                            row['pendente'] = row.get('pendente', '0')
                            row['deletado'] = row.get('deletado', '0')
                            row['comprovante'] = row.get('comprovante', '')
                            # Garante que todos os campos existem
                            for campo in self.CAMPOS:
                                if campo not in row:
                                    row[campo] = ''
                            writer.writerow(row)
        except FileNotFoundError:
            pass
    
    def _gerar_novo_id(self) -> str:
        """Gera um novo ID único"""
        pagamentos = self._listar_todos_incluindo_deletados()
        if not pagamentos:
            return "1"
        
        ids_existentes = [int(p.get('id', 0)) for p in pagamentos if p.get('id', '').isdigit()]
        return str(max(ids_existentes) + 1) if ids_existentes else "1"
    
    def _copiar_comprovante(self, caminho_origem: str, id_pagamento: str, beneficiario: str, valor: float) -> str:
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
        caminho_destino = os.path.join(self.PASTA_COMPROVANTES, novo_nome)
        
        # Copia o arquivo
        import shutil
        try:
            shutil.copy2(caminho_origem, caminho_destino)
            return novo_nome
        except Exception as e:
            print(f"  ⚠ Erro ao copiar comprovante: {e}")
            return ""
    
    def _listar_todos_incluindo_deletados(self) -> List[Dict]:
        """Lista TODOS os pagamentos, incluindo deletados"""
        pagamentos = []
        try:
            with open(self.ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pagamentos.append(row)
        except FileNotFoundError:
            pass
        return pagamentos
    
    def _aplicar_filtros(self, pagamentos: List[Dict], filtros: Dict[str, str]) -> List[Dict]:
        """Aplica filtros aos pagamentos"""
        if not filtros:
            return pagamentos
        
        pagamentos_filtrados = []
        for pag in pagamentos:
            incluir = True
            for campo, valor_filtro in filtros.items():
                campo_lower = campo.lower()
                valor_filtro_lower = valor_filtro.lower()
                
                # Mapeia campos para os nomes reais no CSV
                mapeamento_campos = {
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
                    'comprovante': 'comprovante'
                }
                
                campo_real = mapeamento_campos.get(campo_lower, campo_lower)
                
                if campo_real not in pag:
                    continue
                
                valor_campo = str(pag.get(campo_real, '')).lower()
                
                # Tratamento especial para campo pendente
                if campo_real == 'pendente':
                    # Aceita: s, sim, 1, true, n, nao, não, 0, false
                    valor_esperado = '1' if valor_filtro_lower in ['s', 'sim', '1', 'true', 'yes'] else '0'
                    if valor_campo != valor_esperado:
                        incluir = False
                        break
                # Tratamento especial para valor (permite filtros numéricos)
                elif campo_real == 'valor':
                    try:
                        valor_pag = float(pag.get(campo_real, 0))
                        # Suporta: >100, <50, >=200, <=300, 150
                        if valor_filtro_lower.startswith('>='):
                            if not valor_pag >= float(valor_filtro_lower[2:]):
                                incluir = False
                                break
                        elif valor_filtro_lower.startswith('<='):
                            if not valor_pag <= float(valor_filtro_lower[2:]):
                                incluir = False
                                break
                        elif valor_filtro_lower.startswith('>'):
                            if not valor_pag > float(valor_filtro_lower[1:]):
                                incluir = False
                                break
                        elif valor_filtro_lower.startswith('<'):
                            if not valor_pag < float(valor_filtro_lower[1:]):
                                incluir = False
                                break
                        else:
                            if abs(valor_pag - float(valor_filtro_lower)) > 0.01:
                                incluir = False
                                break
                    except ValueError:
                        incluir = False
                        break
                # Para outros campos, faz busca parcial (contains)
                else:
                    if valor_filtro_lower not in valor_campo:
                        incluir = False
                        break
            
            if incluir:
                pagamentos_filtrados.append(pag)
        
        return pagamentos_filtrados
    
    def adicionar_pagamento(self, pagamento: Pagamento, caminho_comprovante: str = None):
        """Adiciona um novo pagamento ao arquivo"""
        # Gera ID se não fornecido
        if not pagamento.id:
            pagamento.id = self._gerar_novo_id()
        
        # Copia o comprovante se fornecido
        if caminho_comprovante:
            nome_comprovante = self._copiar_comprovante(
                caminho_comprovante, 
                pagamento.id, 
                pagamento.beneficiario, 
                pagamento.valor
            )
            pagamento.comprovante = nome_comprovante
        
        with open(self.ARQUIVO_DADOS, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.CAMPOS)
            writer.writerow(pagamento.to_dict())
        
        msg = f"\n✓ Pagamento registrado com sucesso! (ID: {pagamento.id})"
        if pagamento.comprovante:
            msg += f"\n✓ Comprovante salvo: {pagamento.comprovante}"
        print(msg)
    
    def listar_todos(self, incluir_deletados: bool = False, filtros: Dict[str, str] = None) -> List[Dict]:
        """Lista todos os pagamentos (excluindo deletados por padrão)"""
        pagamentos = self._listar_todos_incluindo_deletados()
        
        if not incluir_deletados:
            pagamentos = [p for p in pagamentos if p.get('deletado', '0') != '1']
        
        # Aplica filtros se fornecidos
        if filtros:
            pagamentos = self._aplicar_filtros(pagamentos, filtros)
        
        return pagamentos
    
    def listar_deletados(self, filtros: Dict[str, str] = None) -> List[Dict]:
        """Lista apenas os pagamentos deletados"""
        pagamentos = self._listar_todos_incluindo_deletados()
        deletados = [p for p in pagamentos if p.get('deletado', '0') == '1']
        
        # Aplica filtros se fornecidos
        if filtros:
            deletados = self._aplicar_filtros(deletados, filtros)
        
        return deletados
    
    def buscar_por_id(self, id_busca: str) -> Dict:
        """Busca um pagamento por ID"""
        pagamentos = self._listar_todos_incluindo_deletados()
        for pag in pagamentos:
            if pag.get('id') == id_busca:
                return pag
        return None
    
    def marcar_como_deletado(self, id_pagamento: str) -> bool:
        """Marca um pagamento como deletado"""
        pagamentos = self._listar_todos_incluindo_deletados()
        encontrado = False
        
        for pag in pagamentos:
            if pag.get('id') == id_pagamento:
                pag['deletado'] = '1'
                encontrado = True
                break
        
        if encontrado:
            self._reescrever_arquivo(pagamentos)
        
        return encontrado
    
    def atualizar_pagamento(self, id_pagamento: str, dados_atualizados: Dict, caminho_comprovante: str = None) -> bool:
        """Atualiza um pagamento existente"""
        pagamentos = self._listar_todos_incluindo_deletados()
        encontrado = False
        
        for pag in pagamentos:
            if pag.get('id') == id_pagamento:
                # Se há novo comprovante, copia e atualiza
                if caminho_comprovante:
                    try:
                        valor = float(dados_atualizados.get('valor', pag.get('valor', 0)))
                    except ValueError:
                        valor = 0
                    
                    nome_comprovante = self._copiar_comprovante(
                        caminho_comprovante,
                        id_pagamento,
                        dados_atualizados.get('beneficiario', pag.get('beneficiario', '')),
                        valor
                    )
                    if nome_comprovante:
                        dados_atualizados['comprovante'] = nome_comprovante
                
                # Atualiza apenas os campos fornecidos
                for campo, valor in dados_atualizados.items():
                    if campo in self.CAMPOS and campo != 'id':  # Não permite alterar o ID
                        pag[campo] = valor
                encontrado = True
                break
        
        if encontrado:
            self._reescrever_arquivo(pagamentos)
        
        return encontrado
    
    def _reescrever_arquivo(self, pagamentos: List[Dict]):
        """Reescreve o arquivo CSV com os dados atualizados"""
        with open(self.ARQUIVO_DADOS, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.CAMPOS)
            writer.writeheader()
            for pag in pagamentos:
                # Garante que todos os campos existem
                for campo in self.CAMPOS:
                    if campo not in pag:
                        pag[campo] = ''
                writer.writerow(pag)
    
    def agregrar_por_categoria(self, filtros: Dict[str, str] = None) -> Dict[str, float]:
        """Agrega os valores por categoria (excluindo deletados)"""
        categorias = defaultdict(float)
        pagamentos = self.listar_todos(incluir_deletados=False, filtros=filtros)
        
        for pag in pagamentos:
            try:
                valor = float(pag['valor'])
                categorias[pag['categoria']] += valor
            except (ValueError, KeyError):
                continue
        
        return dict(categorias)


def formatar_moeda(valor: float) -> str:
    """Formata um valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def solicitar_input(prompt: str, obrigatorio: bool = False, default: str = None, valor_atual: str = None) -> str:
    """Solicita input do usuário com validação"""
    # Se há valor atual, mostra entre colchetes
    if valor_atual:
        prompt_completo = f"{prompt} [{valor_atual}]: "
    elif default:
        prompt_completo = f"{prompt} [{default}]: "
    else:
        prompt_completo = f"{prompt}: "
    
    while True:
        valor = input(prompt_completo).strip()
        
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


def parsear_filtros(args: List[str]) -> Dict[str, str]:
    """
    Parseia filtros da linha de comando no formato campo:valor
    Exemplo: categoria:TRATOR pendente:S valor:>100
    """
    filtros = {}
    for arg in args:
        if ':' in arg:
            campo, valor = arg.split(':', 1)
            filtros[campo.strip()] = valor.strip()
    return filtros


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
    
    pagamento = Pagamento(
        categoria=categoria,
        beneficiario=beneficiario,
        data_pagamento=data_pagamento,
        conta=conta,
        valor=valor,
        devendo_para=devendo_para,
        pendente=pendente
    )
    
    gerenciador = GerenciadorPagamentos()
    gerenciador.adicionar_pagamento(pagamento, caminho_comprovante=comprovante)


def comando_todos(filtros: Dict[str, str] = None):
    """Executa o comando 'pagto todos'"""
    gerenciador = GerenciadorPagamentos()
    pagamentos = gerenciador.listar_todos(filtros=filtros)
    
    if not pagamentos:
        if filtros:
            print("\nNenhum pagamento encontrado com os filtros aplicados.")
            print(f"Filtros: {filtros}")
        else:
            print("\nNenhum pagamento registrado ainda.")
        return
    
    # Mostra filtros aplicados
    if filtros:
        print(f"\n=== FILTROS APLICADOS: {filtros} ===\n")
    
    print("\n=== TODOS OS PAGAMENTOS ===\n")
    
    # Cabeçalho da tabela
    print(f"{'ID':<5} {'Data':<12} {'Categoria':<18} {'Beneficiário':<23} {'Conta':<15} {'Valor':>15} {'Status':<8} {'Comp':<4} {'Devendo':<15}")
    print("-" * 135)
    
    total = 0.0
    for pag in pagamentos:
        try:
            valor = float(pag['valor'])
            total += valor
        except (ValueError, KeyError):
            valor = 0.0
        
        # Status do pagamento
        status = "⏳ Pend." if pag.get('pendente', '0') == '1' else "✓ Pago"
        
        # Indicador de comprovante
        comp_icon = "📎" if pag.get('comprovante', '') else ""
        
        print(f"{pag.get('id', 'N/A'):<5} "
              f"{pag.get('data_pagamento', ''):<12} "
              f"{pag.get('categoria', '')[:17]:<18} "
              f"{pag.get('beneficiario', '')[:22]:<23} "
              f"{pag.get('conta', '')[:14]:<15} "
              f"{formatar_moeda(valor):>15} "
              f"{status:<8} "
              f"{comp_icon:<4} "
              f"{pag.get('devendo_para', '')[:14]:<15}")
    
    print("-" * 135)
    print(f"{'TOTAL:':<95} {formatar_moeda(total):>15}")
    print(f"\nRegistros encontrados: {len(pagamentos)}\n")


def comando_categoria(filtros: Dict[str, str] = None):
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
    gerenciador = GerenciadorPagamentos()
    
    # Verifica se o pagamento existe
    pagamento = gerenciador.buscar_por_id(id_pagamento)
    
    if not pagamento:
        print(f"\n✗ Pagamento com ID {id_pagamento} não encontrado.")
        return
    
    # Verifica se já está deletado
    if pagamento.get('deletado', '0') == '1':
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
        if gerenciador.marcar_como_deletado(id_pagamento):
            print(f"\n✓ Pagamento ID {id_pagamento} deletado com sucesso!")
        else:
            print(f"\n✗ Erro ao deletar pagamento.")
    else:
        print("\n✗ Operação cancelada.")


def comando_deletados(filtros: Dict[str, str] = None):
    """Executa o comando 'pagto deletados'"""
    gerenciador = GerenciadorPagamentos()
    pagamentos = gerenciador.listar_deletados(filtros=filtros)
    
    if not pagamentos:
        if filtros:
            print("\nNenhum pagamento deletado encontrado com os filtros aplicados.")
            print(f"Filtros: {filtros}")
        else:
            print("\nNenhum pagamento deletado encontrado.")
        return
    
    # Mostra filtros aplicados
    if filtros:
        print(f"\n=== FILTROS APLICADOS: {filtros} ===\n")
    
    print("\n=== PAGAMENTOS DELETADOS ===\n")
    
    # Cabeçalho da tabela
    print(f"{'ID':<5} {'Data':<12} {'Categoria':<18} {'Beneficiário':<23} {'Conta':<15} {'Valor':>15} {'Comp':<4} {'Devendo':<15}")
    print("-" * 125)
    
    total = 0.0
    for pag in pagamentos:
        try:
            valor = float(pag['valor'])
            total += valor
        except (ValueError, KeyError):
            valor = 0.0
        
        # Indicador de comprovante
        comp_icon = "📎" if pag.get('comprovante', '') else ""
        
        print(f"{pag.get('id', 'N/A'):<5} "
              f"{pag.get('data_pagamento', ''):<12} "
              f"{pag.get('categoria', '')[:17]:<18} "
              f"{pag.get('beneficiario', '')[:22]:<23} "
              f"{pag.get('conta', '')[:14]:<15} "
              f"{formatar_moeda(valor):>15} "
              f"{comp_icon:<4} "
              f"{pag.get('devendo_para', '')[:14]:<15}")
    
    print("-" * 125)
    print(f"{'TOTAL:':<88} {formatar_moeda(total):>15}")
    print(f"\nRegistros encontrados: {len(pagamentos)}\n")


def comando_editar(id_pagamento: str):
    """Executa o comando 'pagto editar [id]'"""
    gerenciador = GerenciadorPagamentos()
    
    # Verifica se o pagamento existe
    pagamento = gerenciador.buscar_por_id(id_pagamento)
    
    if not pagamento:
        print(f"\n✗ Pagamento com ID {id_pagamento} não encontrado.")
        return
    
    # Verifica se está deletado
    if pagamento.get('deletado', '0') == '1':
        print(f"\n✗ Não é possível editar um pagamento deletado.")
        return
    
    print(f"\n=== EDITAR PAGAMENTO (ID: {id_pagamento}) ===\n")
    print("Pressione ENTER para manter o valor atual\n")
    
    # Mostra comprovante atual se existir
    if pagamento.get('comprovante'):
        print(f"📎 Comprovante atual: {pagamento.get('comprovante')}\n")
    
    # Solicita novos valores (mostrando os atuais)
    categoria = solicitar_input("Categoria", obrigatorio=True, valor_atual=pagamento.get('categoria'))
    beneficiario = solicitar_input("Beneficiário", obrigatorio=True, valor_atual=pagamento.get('beneficiario'))
    data_pagamento = solicitar_data(valor_atual=pagamento.get('data_pagamento'))
    conta = solicitar_input("Conta", obrigatorio=True, valor_atual=pagamento.get('conta'))
    valor = solicitar_valor(valor_atual=pagamento.get('valor'))
    devendo_para = solicitar_input("Devendo para (opcional)", obrigatorio=False, valor_atual=pagamento.get('devendo_para'))
    pendente = solicitar_pendente(valor_atual=pagamento.get('pendente'))
    
    # Pergunta sobre comprovante
    if pagamento.get('comprovante'):
        atualizar_comprovante = input("Atualizar comprovante? (s/n) [Não]: ").strip().lower()
        if atualizar_comprovante in ['s', 'sim', 'yes', 'y']:
            comprovante = solicitar_comprovante()
        else:
            comprovante = None
    else:
        print("Adicionar comprovante:")
        comprovante = solicitar_comprovante()
    
    # Monta o dicionário com os dados atualizados
    dados_atualizados = {
        'categoria': categoria,
        'beneficiario': beneficiario,
        'data_pagamento': data_pagamento,
        'conta': conta,
        'valor': str(valor),
        'devendo_para': devendo_para,
        'pendente': '1' if pendente else '0'
    }
    
    # Atualiza o pagamento
    if gerenciador.atualizar_pagamento(id_pagamento, dados_atualizados, caminho_comprovante=comprovante):
        print(f"\n✓ Pagamento ID {id_pagamento} atualizado com sucesso!")
        if comprovante:
            print(f"✓ Comprovante atualizado!")
    else:
        print(f"\n✗ Erro ao atualizar pagamento.")


def mostrar_ajuda():
    """Mostra a ajuda do programa"""
    print("""
=== SISTEMA DE GERENCIAMENTO DE PAGAMENTOS ===

Comandos disponíveis:

  pagto novo              - Registra um novo pagamento (com opção de comprovante)
  pagto todos             - Lista todos os pagamentos em formato tabular
  pagto categoria         - Mostra total agregado por categoria
  pagto delete [id]       - Marca um pagamento como deletado
  pagto deletados         - Lista todos os pagamentos deletados
  pagto editar [id]       - Edita um pagamento existente
  pagto ajuda             - Mostra esta mensagem de ajuda

Filtros (aplicáveis em todos, categoria e deletados):
  Use o formato campo:valor para filtrar resultados
  
  Campos disponíveis:
    categoria, beneficiario, conta, devendo, pendente, data, valor, id
  
  Exemplos de filtros:
    categoria:TRATOR           - Filtra por categoria exata
    pendente:s                 - Mostra apenas pendentes
    pendente:n                 - Mostra apenas pagos
    valor:>100                 - Valores maiores que 100
    valor:<=500                - Valores menores ou iguais a 500
    conta:Nubank               - Pagamentos da conta Nubank
    beneficiario:maria         - Beneficiários que contêm "maria"

Exemplos de uso:

  # Comandos básicos
  python pagto.py novo
  python pagto.py todos
  python pagto.py categoria
  python pagto.py delete 5
  python pagto.py deletados
  python pagto.py editar 3
  
  # Com filtros
  python pagto.py todos categoria:Alimentação pendente:s
  python pagto.py categoria conta:Nubank
  python pagto.py todos valor:>100 beneficiario:supermercado
  python pagto.py deletados categoria:TRATOR

Comprovantes:
  📎 = Indica que o pagamento possui comprovante anexado
  Os comprovantes são salvos na pasta 'comprovantes/' com nomenclatura:
  [ID]_[BENEFICIARIO]_[VALOR].[extensão]
""")


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Erro: Comando não especificado.")
        mostrar_ajuda()
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    # Parseia filtros dos argumentos restantes (formato campo:valor)
    filtros = parsear_filtros(sys.argv[2:]) if len(sys.argv) > 2 else {}
    
    if comando == "novo":
        comando_novo()
    elif comando == "todos":
        comando_todos(filtros=filtros if filtros else None)
    elif comando == "categoria":
        comando_categoria(filtros=filtros if filtros else None)
    elif comando == "delete":
        # Para delete, o segundo argumento é o ID, não um filtro
        if len(sys.argv) < 3 or ':' in sys.argv[2]:
            print("Erro: ID do pagamento não especificado.")
            print("Uso: pagto delete [id]")
            sys.exit(1)
        comando_delete(sys.argv[2])
    elif comando == "deletados":
        comando_deletados(filtros=filtros if filtros else None)
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
