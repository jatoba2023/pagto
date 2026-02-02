# 📎 Guia de Comprovantes e Filtros - pagto v2.1

## 🆕 Novidades da v2.1

### 1. 📎 Sistema de Comprovantes
Agora você pode anexar comprovantes (recibos, notas fiscais, etc.) aos seus pagamentos!

### 2. 🔍 Sistema de Filtros Avançado
Filtre relatórios por qualquer campo usando sintaxe simples na linha de comando.

---

## 📎 Comprovantes

### Como Funciona

Quando você registra ou edita um pagamento, pode fornecer o caminho de um arquivo (PDF, imagem, etc.) que será:
1. **Copiado** para a pasta `comprovantes/`
2. **Renomeado** automaticamente no formato: `[ID]_[BENEFICIARIO]_[VALOR].[extensão]`
3. **Vinculado** ao pagamento no registro

### Adicionando Comprovante ao Criar Pagamento

```bash
$ pagto novo

Categoria: TRATOR
Beneficiário: Fazenda Silva
Data: 01/02/2026
Conta: Dinheiro
Valor: 5000.00
Devendo para: 
Pagamento pendente? (s/n): n
Caminho do comprovante (opcional): /home/user/Downloads/recibo_fazenda.pdf

✓ Pagamento registrado com sucesso! (ID: 1)
✓ Comprovante salvo: 1_Fazenda_Silva_5000.pdf
```

### Adicionando Comprovante ao Editar

```bash
$ pagto editar 1

=== EDITAR PAGAMENTO (ID: 1) ===

📎 Comprovante atual: 1_Fazenda_Silva_5000.pdf

Categoria [TRATOR]: 
Beneficiário [Fazenda Silva]: 
...
Atualizar comprovante? (s/n) [Não]: s
Caminho do comprovante (opcional): /home/user/novo_recibo.pdf

✓ Pagamento ID 1 atualizado com sucesso!
✓ Comprovante atualizado!
```

### Visualizando Comprovantes nos Relatórios

Pagamentos com comprovante exibem o ícone 📎:

```bash
$ pagto todos

ID    Data         Categoria          Beneficiário       Valor         Comp
------------------------------------------------------------------------
1     01/02/2026   TRATOR            Fazenda Silva      R$ 5.000,00   📎
2     02/02/2026   Alimentação       Supermercado       R$ 350,00     
```

### Localização dos Comprovantes

Todos os comprovantes ficam na pasta `comprovantes/` no mesmo diretório do programa:

```
/seu/diretorio/
├── pagto.py
├── pagamentos.csv
└── comprovantes/
    ├── 1_Fazenda_Silva_5000.pdf
    ├── 2_Supermercado_ABC_350.jpg
    └── 3_Mecanica_Joao_1201.pdf
```

### Formato do Nome do Arquivo

**Padrão**: `[ID]_[BENEFICIARIO]_[VALOR_ARREDONDADO].[extensão]`

Exemplos:
- `1_Fazenda_Silva_5000.pdf`
- `2_Supermercado_ABC_350.jpg`
- `10_João_da_Silva_1234.png`

**Regras de nomenclatura:**
- Caracteres especiais são removidos
- Espaços virados em underscores (_)
- Valor é arredondado para inteiro
- Extensão original é mantida

### Tipos de Arquivo Suportados

Qualquer tipo de arquivo pode ser usado como comprovante:
- 📄 PDFs
- 🖼️ Imagens (JPG, PNG, etc.)
- 📝 Documentos (DOC, TXT, etc.)
- 📊 Planilhas (XLS, CSV, etc.)

---

## 🔍 Sistema de Filtros

### Sintaxe Básica

```bash
pagto [comando] campo1:valor1 campo2:valor2 ...
```

### Comandos que Aceitam Filtros

✅ `pagto todos`  
✅ `pagto categoria`  
✅ `pagto deletados`

❌ `pagto novo` - Não aceita filtros (é para criar)  
❌ `pagto delete [id]` - Requer ID específico  
❌ `pagto editar [id]` - Requer ID específico

### Campos Disponíveis para Filtro

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `categoria` | Categoria do pagamento | `categoria:TRATOR` |
| `beneficiario` | Nome do beneficiário | `beneficiario:Silva` |
| `conta` | Conta utilizada | `conta:Nubank` |
| `devendo` ou `devendo_para` | Devendo para | `devendo:João` |
| `pendente` | Status pendente | `pendente:s` ou `pendente:n` |
| `data` ou `data_pagamento` | Data | `data:01/02/2026` |
| `valor` | Valor do pagamento | `valor:>100` |
| `id` | ID do pagamento | `id:5` |

### Exemplos de Uso

#### 1. Filtrar por Categoria

```bash
# Apenas pagamentos da categoria TRATOR
pagto todos categoria:TRATOR

# Agregado apenas de Alimentação
pagto categoria categoria:Alimentação
```

#### 2. Filtrar por Status Pendente

```bash
# Apenas pendentes
pagto todos pendente:s

# Apenas pagos
pagto todos pendente:n
pagto todos pendente:false
pagto todos pendente:0
```

Aceita: `s`, `sim`, `1`, `true`, `yes` (para sim) ou `n`, `não`, `0`, `false`, `no` (para não)

#### 3. Filtrar por Valor

```bash
# Valores maiores que 100
pagto todos valor:>100

# Valores menores que 500
pagto todos valor:<500

# Valores maiores ou iguais a 1000
pagto todos valor:>=1000

# Valores menores ou iguais a 250
pagto todos valor:<=250

# Valor exato
pagto todos valor:150.50
```

#### 4. Filtrar por Beneficiário (busca parcial)

```bash
# Beneficiários que contêm "silva"
pagto todos beneficiario:silva

# Beneficiários que contêm "super"
pagto todos beneficiario:super
```

A busca é **case-insensitive** e **parcial** (procura em qualquer parte do texto).

#### 5. Filtrar por Conta

```bash
# Pagamentos do Nubank
pagto todos conta:Nubank

# Pagamentos em Dinheiro
pagto todos conta:Dinheiro
```

#### 6. Múltiplos Filtros Combinados

```bash
# TRATOR E pendentes
pagto todos categoria:TRATOR pendente:s

# Nubank E valores acima de 100
pagto todos conta:Nubank valor:>100

# Alimentação E Supermercado E pagos
pagto todos categoria:Alimentação beneficiario:supermercado pendente:n

# Deletados da categoria TRATOR
pagto deletados categoria:TRATOR
```

### Como os Filtros Funcionam

**Lógica AND**: Quando você usa múltiplos filtros, **TODOS** devem corresponder.

Exemplo:
```bash
pagto todos categoria:TRATOR valor:>1000
```
Mostrará apenas pagamentos que são:
- DA categoria TRATOR **E**
- COM valor maior que 1000

### Exemplos Práticos Completos

#### Cenário 1: Auditoria de Gastos com Trator

```bash
# Ver todos os gastos com TRATOR
pagto todos categoria:TRATOR

# Ver total por categoria (apenas TRATOR)
pagto categoria categoria:TRATOR

# Ver apenas os caros (acima de R$ 1.000)
pagto todos categoria:TRATOR valor:>1000
```

#### Cenário 2: Pagamentos Pendentes

```bash
# Listar todos pendentes
pagto todos pendente:s

# Pendentes do Nubank
pagto todos pendente:s conta:Nubank

# Total de pendentes por categoria
pagto categoria pendente:s
```

#### Cenário 3: Análise de Fornecedor

```bash
# Todos pagamentos para "Silva"
pagto todos beneficiario:Silva

# Total pago para fornecedores com "Silva"
pagto categoria beneficiario:Silva

# Pagamentos deletados de "Silva"
pagto deletados beneficiario:Silva
```

#### Cenário 4: Análise Temporal

```bash
# Pagamentos de uma data específica
pagto todos data:01/02/2026

# Combinar com categoria
pagto todos data:01/02/2026 categoria:Alimentação
```

### Saída com Filtros

Quando filtros são aplicados, o sistema mostra:

```bash
$ pagto todos categoria:TRATOR pendente:s

=== FILTROS APLICADOS: {'categoria': 'TRATOR', 'pendente': 's'} ===

=== TODOS OS PAGAMENTOS ===

ID    Data         Categoria    ...
----------------------------------
5     15/02/2026   TRATOR       ...

Registros encontrados: 1
```

---

## 💡 Dicas e Melhores Práticas

### Comprovantes

1. **Organize antes**: Mantenha seus comprovantes em uma pasta temporária
2. **Use nomes descritivos**: Facilita encontrar antes de importar
3. **Backup**: A pasta `comprovantes/` deve ser incluída nos backups
4. **Formato**: PDFs são ideais para armazenamento de longo prazo

### Filtros

1. **Teste incremental**: Comece com um filtro, depois adicione mais
2. **Case insensitive**: Não se preocupe com maiúsculas/minúsculas
3. **Busca parcial**: Para texto, a busca encontra em qualquer parte
4. **Aspas**: Use aspas se o valor tiver espaços: `beneficiario:"João Silva"`

---

## 🐛 Solução de Problemas

### Comprovante não foi copiado

**Problema**: Mensagem de erro ao tentar copiar comprovante

**Soluções**:
```bash
# Verifique se o arquivo existe
ls -la /caminho/do/arquivo

# Verifique permissões
chmod +r /caminho/do/arquivo

# Use caminho absoluto
/home/user/documentos/recibo.pdf
```

### Filtro não funciona

**Problema**: Filtro não retorna resultados esperados

**Soluções**:
```bash
# Verifique a sintaxe (campo:valor)
pagto todos categoria:TRATOR    # ✓ Correto
pagto todos categoria TRATOR    # ✗ Errado

# Verifique o nome exato do campo
pagto todos categoria:trator    # Busca case-insensitive funciona!

# Para valor, use sintaxe correta
pagto todos valor:>100          # ✓ Correto
pagto todos valor:maior que 100 # ✗ Errado
```

### Pasta comprovantes não criada

**Problema**: Pasta `comprovantes/` não existe

**Solução**: A pasta é criada automaticamente ao executar qualquer comando. Se não existir:
```bash
mkdir comprovantes
```

---

## 📊 Exemplos de Fluxo de Trabalho

### Fluxo 1: Registro Completo com Comprovante

```bash
# 1. Registrar pagamento
pagto novo
# ... preencher dados ...
# Comprovante: /home/user/Downloads/recibo.pdf

# 2. Verificar se foi salvo
ls comprovantes/

# 3. Ver no relatório
pagto todos
```

### Fluxo 2: Análise Mensal

```bash
# 1. Ver todos de fevereiro
pagto todos data:02/2026    # Se suportar busca parcial em data

# 2. Ver apenas categoria específica
pagto categoria categoria:TRATOR

# 3. Ver pendentes para pagar
pagto todos pendente:s
```

### Fluxo 3: Auditoria de Fornecedor

```bash
# 1. Listar todos pagamentos do fornecedor
pagto todos beneficiario:FazendaSilva

# 2. Ver total por categoria
pagto categoria beneficiario:FazendaSilva

# 3. Verificar se há deletados
pagto deletados beneficiario:FazendaSilva
```

---

## 🎯 Resumo Rápido

### Comprovantes
- ✅ Adicione ao criar: `pagto novo` → preencher caminho
- ✅ Atualize ao editar: `pagto editar [id]` → atualizar comprovante
- ✅ Identifique pelo 📎 nos relatórios
- ✅ Encontre em `comprovantes/[ID]_[BENEFICIARIO]_[VALOR].[ext]`

### Filtros
- ✅ Sintaxe: `campo:valor`
- ✅ Múltiplos: `campo1:valor1 campo2:valor2`
- ✅ Valores: `>`, `<`, `>=`, `<=`, `valor_exato`
- ✅ Texto: busca parcial case-insensitive
- ✅ Pendente: `s`/`n`, `sim`/`não`, `1`/`0`, `true`/`false`

---

**Aproveite os novos recursos para ter controle total dos seus pagamentos! 🚀**
