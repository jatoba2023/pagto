# 💰 Sistema de Gerenciamento de Pagamentos v2.1

Aplicação de linha de comando para registrar e consultar pagamentos de forma simples e eficiente.

## ✨ Novidades da v2.1

- 📎 **Comprovantes Anexados** - Vincule arquivos (PDFs, imagens) aos pagamentos
- 🔍 **Filtros Avançados** - Filtre relatórios por qualquer campo com sintaxe simples
- 🎯 **Busca por Valor** - Filtros numéricos (>, <, >=, <=)
- 📊 **Ícone de Comprovante** - Veja facilmente quais pagamentos têm comprovante (📎)

## ✨ Recursos da v2.0

- 🆔 **Sistema de IDs únicos** - Cada pagamento tem um identificador permanente
- ⏳ **Status Pendente** - Marque pagamentos que ainda não foram efetivados
- 🗑️ **Soft Delete** - Pagamentos deletados ficam ocultos mas podem ser recuperados
- ✏️ **Edição de Pagamentos** - Altere qualquer campo de registros existentes
- 📊 **IDs nos Relatórios** - Veja os IDs em todas as listagens para fácil referência
- 🔄 **Migração Automática** - Dados de versões antigas são migrados automaticamente

## 📋 Funcionalidades

- ✅ Registrar novos pagamentos com validação de dados
- 🆔 Sistema de IDs únicos e permanentes
- 📎 Anexar comprovantes (PDFs, imagens, etc.)
- 🔍 Filtrar por qualquer campo (categoria, valor, status, etc.)
- ⏳ Marcar pagamentos como pendentes ou pagos
- 📊 Listar todos os pagamentos em formato tabular com IDs e status
- 📈 Visualizar totais agregados por categoria
- 🗑️ Deletar pagamentos (soft delete - não remove do arquivo)
- 👁️ Visualizar pagamentos deletados separadamente
- ✏️ Editar qualquer campo de pagamentos existentes
- 💾 Armazenamento em arquivo CSV (fácil exportação para Excel)
- 🇧🇷 Formatação de valores em Real (R$)

## 🚀 Instalação

### Opção 1: Instalação Automática (Recomendado)

```bash
chmod +x instalar.sh
./instalar.sh
```

### Opção 2: Instalação Manual

```bash
# Torna o script executável
chmod +x pagto.py

# Cria um alias no seu .bashrc ou .zshrc
echo 'alias pagto="python3 /caminho/completo/para/pagto.py"' >> ~/.bashrc
source ~/.bashrc
```

### Opção 3: Uso Direto (Sem Instalação)

```bash
python3 pagto.py novo
python3 pagto.py todos
python3 pagto.py categoria
```

## 📖 Uso

### Registrar Novo Pagamento

```bash
pagto novo
```

O sistema solicitará os seguintes dados:

- **Categoria** (obrigatório): Ex: Alimentação, Transporte, Moradia
- **Beneficiário** (obrigatório): Ex: Supermercado ABC, João Silva
- **Data do pagamento** (opcional, padrão = hoje): Formato dd/mm/aaaa
- **Conta** (obrigatório): Ex: Nubank, Itaú, Dinheiro
- **Valor** (obrigatório): Ex: 150.50 ou 150,50
- **Devendo para** (opcional): Ex: Maria, Empresa XYZ
- **Pendente** (opcional, padrão = Não): s para sim, n para não

**Novo!** Cada pagamento recebe automaticamente um **ID único**.

### Listar Todos os Pagamentos

```bash
pagto todos
```

Exibe uma tabela formatada com todos os pagamentos (exceto deletados), mostrando ID, status e total geral.

**Exemplo de saída:**
```
=== TODOS OS PAGAMENTOS ===

ID    Data         Categoria          Beneficiário              Conta                 Valor Status   Devendo             
------------------------------------------------------------------------------------------------------------------------
1     01/02/2026   Alimentação        Supermercado XYZ          Nubank            R$ 234,50 ✓ Pago                       
3     01/02/2026   Transporte         Uber                      Itaú               R$ 45,50 ⏳ Pend.  João               
------------------------------------------------------------------------------------------------------------------------
TOTAL:                                                                                      R$ 280,00
```

### Deletar um Pagamento

```bash
pagto delete [id]
```

Marca um pagamento como deletado. Ele não aparecerá mais nos relatórios normais.

**Exemplo:**
```bash
pagto delete 3
```

### Visualizar Pagamentos Deletados

```bash
pagto deletados
```

Mostra todos os pagamentos que foram marcados como deletados.

### Editar um Pagamento

```bash
pagto editar [id]
```

Permite editar qualquer campo de um pagamento existente. Pressione ENTER para manter o valor atual.

**Exemplo:**
```bash
pagto editar 1

=== EDITAR PAGAMENTO (ID: 1) ===

Pressione ENTER para manter o valor atual

Categoria [Alimentação]: Mercado
Beneficiário [Supermercado XYZ]: 
Valor (R$) [234.5]: 250.00
...
```

### Visualizar por Categoria

```bash
pagto categoria
```

Mostra os valores totais agrupados por categoria (excluindo pagamentos deletados).

**Exemplo de saída:**
```
=== PAGAMENTOS POR CATEGORIA ===

Categoria                               Total
----------------------------------------------------
Alimentação                        R$ 1.234,50
Moradia                            R$ 2.500,00
Transporte                           R$ 450,00
----------------------------------------------------
TOTAL GERAL:                       R$ 4.184,50
```

### 🔍 Filtros Avançados

Você pode filtrar qualquer relatório usando a sintaxe `campo:valor`:

```bash
# Filtrar por categoria
pagto todos categoria:TRATOR

# Filtrar por status pendente
pagto todos pendente:s

# Filtrar por valor (maior que 100)
pagto todos valor:>100

# Múltiplos filtros combinados
pagto todos categoria:Alimentação pendente:n conta:Nubank

# Filtros em agregações
pagto categoria categoria:TRATOR valor:>1000
```

**Campos disponíveis para filtro:**
- `categoria` - Categoria do pagamento
- `beneficiario` - Nome do beneficiário (busca parcial)
- `conta` - Conta utilizada
- `devendo` - Devendo para
- `pendente` - Status (s/n, sim/não, 1/0)
- `valor` - Valor (suporta >, <, >=, <=)
- `data` - Data do pagamento
- `id` - ID do pagamento

Para mais detalhes, consulte `COMPROVANTES_E_FILTROS.md`.

## 📂 Estrutura de Dados

Os pagamentos são armazenados no arquivo `pagamentos.csv` com a seguinte estrutura:

```csv
id,categoria,beneficiario,data_pagamento,conta,valor,devendo_para,pendente,deletado,comprovante
1,Alimentação,Supermercado ABC,01/02/2026,Nubank,234.50,,0,0,
2,Transporte,Uber,01/02/2026,Itaú,45.50,,1,0,
3,TRATOR,Fazenda Silva,31/01/2026,Dinheiro,5000.00,Maria,0,0,3_Fazenda_Silva_5000.pdf
```

### Campos:
- **id**: Identificador único (gerado automaticamente, nunca reutilizado)
- **categoria**: Categoria do pagamento
- **beneficiario**: Quem recebeu o pagamento
- **data_pagamento**: Data no formato dd/mm/aaaa
- **conta**: Conta ou forma de pagamento
- **valor**: Valor numérico (use ponto como separador decimal)
- **devendo_para**: Pessoa/empresa a quem você deve (opcional)
- **pendente**: 1 = pendente, 0 = pago
- **deletado**: 1 = deletado, 0 = ativo
- **comprovante**: Nome do arquivo de comprovante (opcional)

### Pasta de Comprovantes

Os arquivos de comprovante ficam em `comprovantes/` com nomenclatura automática:
```
comprovantes/
├── 1_Supermercado_ABC_235.pdf
├── 3_Fazenda_Silva_5000.jpg
└── 5_Mecânica_João_1201.pdf
```

Formato: `[ID]_[BENEFICIARIO]_[VALOR_ARREDONDADO].[extensão]`

Este formato permite fácil importação em Excel, Google Sheets ou outras ferramentas.

## 🛠️ Requisitos

- Python 3.6 ou superior
- Bibliotecas padrão do Python (nenhuma dependência externa necessária)

## 💡 Dicas de Uso

1. **IDs Permanentes**: Anote os IDs de pagamentos recorrentes importantes para fácil edição

2. **Status Pendente**: Use para pagamentos agendados ou parcelamentos futuros
   ```bash
   pagto novo
   # Marque como pendente: s
   
   # Quando pagar, edite:
   pagto editar [id]
   # Pendente: n
   ```

3. **Categorias Consistentes**: Use sempre as mesmas categorias para facilitar a análise

4. **Soft Delete**: Pagamentos deletados ficam ocultos mas mantêm o histórico
   ```bash
   pagto delete [id]      # Esconde do relatório
   pagto deletados        # Ver histórico de deletados
   ```

5. **Backup Regular**: Faça backup do arquivo `pagamentos.csv` regularmente
   ```bash
   cp pagamentos.csv pagamentos_backup_$(date +%Y%m%d).csv
   ```

6. **Exportação**: O arquivo CSV pode ser aberto diretamente no Excel ou Google Sheets

7. **Edição Rápida**: Use IDs para editar rapidamente
   ```bash
   pagto todos            # Veja o ID
   pagto editar 5         # Edite diretamente
   ```

8. **Múltiplas Contas**: Use o campo "conta" para separar pagamentos de diferentes contas bancárias

## 🔄 Migração da v1.0

Se você já usa a versão antiga do pagto:

1. **Faça backup** dos seus dados:
   ```bash
   cp pagamentos.csv pagamentos_backup.csv
   ```

2. **Substitua** o arquivo `pagto.py` pela nova versão

3. **Execute** qualquer comando - a migração é automática:
   ```bash
   pagto todos
   ```

Os IDs serão gerados automaticamente para seus pagamentos existentes!

Para mais detalhes, consulte o arquivo `ATUALIZACAO.md`.

## 🔧 Solução de Problemas

### Erro: "comando não encontrado"
- Verifique se o script está executável: `chmod +x pagto.py`
- Verifique se o diretório está no PATH

### Erro de permissão
- Use `python3 pagto.py` ao invés de `./pagto.py`
- Verifique as permissões do arquivo

### Dados não aparecem
- Certifique-se de que o arquivo `pagamentos.csv` está no mesmo diretório de onde você executa o comando

## 📝 Exemplos Práticos

### Exemplo 1: Registro Completo
```bash
$ pagto novo

=== NOVO PAGAMENTO ===

Categoria: Alimentação
Beneficiário: Restaurante Bom Sabor
Data do pagamento (dd/mm/aaaa) [hoje: 01/02/2026]: 
Conta: Cartão Itaú
Valor (R$): 85,50
Devendo para (opcional): 

✓ Pagamento registrado com sucesso!
```

### Exemplo 2: Pagamento Parcelado com Dívida
```bash
$ pagto novo

=== NOVO PAGAMENTO ===

Categoria: Eletrônicos
Beneficiário: Loja Tech
Data do pagamento (dd/mm/aaaa) [hoje: 01/02/2026]: 15/01/2026
Conta: Nubank
Valor (R$): 500
Devendo para (opcional): Carlos

✓ Pagamento registrado com sucesso!
```

## 📄 Licença

Este projeto é de código aberto e pode ser usado livremente.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas!

---

**Desenvolvido com ❤️ para facilitar o controle financeiro pessoal**
