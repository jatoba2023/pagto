# 🔄 Guia de Atualização - pagto v2.0

## 📋 O que mudou na versão 2.0?

### ✨ Novas Funcionalidades

1. **Sistema de IDs únicos** - Cada pagamento agora tem um ID único e permanente
2. **Status Pendente** - Marque pagamentos que ainda não foram efetivados
3. **Soft Delete** - Pagamentos deletados são marcados, mas não removidos do arquivo
4. **Edição de Pagamentos** - Altere qualquer campo de um pagamento existente
5. **Visualização de Deletados** - Veja todos os registros deletados

### 🆕 Novos Comandos

```bash
pagto delete [id]      # Marca um pagamento como deletado
pagto deletados        # Lista todos os pagamentos deletados
pagto editar [id]      # Edita um pagamento existente
```

### 🔧 Campos Adicionados

- **id**: Identificador único do pagamento (gerado automaticamente)
- **pendente**: Indica se o pagamento está pendente (sim/não)
- **deletado**: Marca se o pagamento foi deletado (interno)

---

## 📦 Como Atualizar

### Opção 1: Atualização Automática (Recomendado)

Se você já tem a versão antiga instalada:

```bash
# 1. Faça backup dos seus dados
cp pagamentos.csv pagamentos_backup.csv

# 2. Baixe a nova versão do pagto.py

# 3. Substitua o arquivo antigo
cp pagto.py /caminho/da/instalacao/pagto.py

# 4. Execute qualquer comando para ativar a migração automática
python3 pagto.py todos
```

**A migração é automática!** O sistema detecta arquivos antigos e adiciona os novos campos automaticamente.

### Opção 2: Instalação Limpa

Se preferir começar do zero:

```bash
# 1. Salve seus dados antigos (se desejar)
cp pagamentos.csv pagamentos_old.csv

# 2. Remova a instalação antiga
rm /usr/local/bin/pagto  # ou ~/.local/bin/pagto

# 3. Instale a nova versão
chmod +x instalar.sh
./instalar.sh

# 4. (Opcional) Importe dados antigos
# O novo sistema reconhecerá o formato antigo automaticamente
```

---

## 🔄 Migração de Dados

### Automática

Ao executar qualquer comando pela primeira vez com a nova versão, o sistema:

1. ✅ Detecta se o arquivo tem formato antigo
2. ✅ Adiciona os novos campos automaticamente
3. ✅ Gera IDs únicos para registros existentes
4. ✅ Marca todos como "não pendente" e "não deletado"
5. ✅ Preserva todos os dados originais

**Você não precisa fazer nada!**

### Verificação Pós-Migração

```bash
# Execute para ver se a migração funcionou
python3 pagto.py todos

# Deve mostrar seus pagamentos antigos com IDs
```

### Estrutura do Arquivo Migrado

**Antes (v1.0):**
```csv
categoria,beneficiario,data_pagamento,conta,valor,devendo_para
Alimentação,Mercado,01/02/2026,Nubank,350.50,
```

**Depois (v2.0):**
```csv
id,categoria,beneficiario,data_pagamento,conta,valor,devendo_para,pendente,deletado
1,Alimentação,Mercado,01/02/2026,Nubank,350.50,,0,0
```

---

## 🎯 Novos Recursos em Ação

### 1. Criar Pagamento com Status Pendente

```bash
$ pagto novo

Categoria: Conta de Luz
Beneficiário: CEMIG
Data: 15/02/2026
Conta: Nubank
Valor: 250.00
Devendo para: 
Pagamento pendente? (s/n) [Não]: s

✓ Pagamento registrado com sucesso! (ID: 5)
```

### 2. Listar com IDs e Status

```bash
$ pagto todos

ID    Data         Categoria          Beneficiário            Status
----------------------------------------------------------------
1     01/02/2026   Alimentação        Supermercado XYZ        ✓ Pago
5     15/02/2026   Conta de Luz       CEMIG                   ⏳ Pend.
```

### 3. Deletar um Pagamento

```bash
$ pagto delete 5

=== DELETAR PAGAMENTO ===

ID: 5
Categoria: Conta de Luz
Beneficiário: CEMIG
Valor: R$ 250,00
Data: 15/02/2026

Deseja realmente deletar este pagamento? (s/n): s

✓ Pagamento ID 5 deletado com sucesso!
```

### 4. Ver Pagamentos Deletados

```bash
$ pagto deletados

=== PAGAMENTOS DELETADOS ===

ID    Data         Categoria          Beneficiário            Valor
------------------------------------------------------------------
5     15/02/2026   Conta de Luz       CEMIG                   R$ 250,00
```

### 5. Editar um Pagamento

```bash
$ pagto editar 1

=== EDITAR PAGAMENTO (ID: 1) ===

Pressione ENTER para manter o valor atual

Categoria [Alimentação]: Mercado
Beneficiário [Supermercado XYZ]: 
Data do pagamento [01/02/2026]: 02/02/2026
Conta [Nubank]: 
Valor (R$) [350.5]: 400.00
Devendo para: 
Pagamento pendente? (s/n) [Não]: 

✓ Pagamento ID 1 atualizado com sucesso!
```

---

## ⚠️ Avisos Importantes

### Backup é Essencial
Antes de atualizar, **SEMPRE** faça backup:
```bash
cp pagamentos.csv pagamentos_backup_$(date +%Y%m%d).csv
```

### IDs são Permanentes
- Uma vez gerado, um ID nunca é reutilizado
- Mesmo pagamentos deletados mantêm seu ID
- IDs são sequenciais e únicos

### Pagamentos Deletados
- Não aparecem em relatórios normais
- Não são contabilizados nos totais
- Podem ser visualizados com `pagto deletados`
- Não podem ser editados
- Ocupam espaço no arquivo (soft delete)

### Compatibilidade
- ✅ Arquivos da v1.0 são **100% compatíveis**
- ✅ Migração é **automática e segura**
- ✅ Dados antigos são **preservados**
- ⚠️ Após migrar, não use a v1.0 novamente

---

## 🐛 Solução de Problemas

### Erro: "Campos não encontrados"
```bash
# Solução: Force a recriação do arquivo
mv pagamentos.csv pagamentos_old.csv
python3 pagto.py novo
# Depois importe manualmente se necessário
```

### IDs Duplicados
```bash
# Não deve acontecer, mas se ocorrer:
# 1. Faça backup
cp pagamentos.csv pagamentos_problema.csv

# 2. Delete o arquivo e reimporte
rm pagamentos.csv
# Reimporte seus dados manualmente ou use backup
```

### Dados Não Aparecem Após Atualização
```bash
# Verifique se o arquivo foi migrado corretamente
head -n 2 pagamentos.csv

# Deve mostrar:
# id,categoria,beneficiario,data_pagamento,conta,valor,devendo_para,pendente,deletado
# 1,Alimentação,Mercado,...
```

---

## 📊 Comparação de Versões

| Recurso | v1.0 | v2.0 |
|---------|------|------|
| Registrar pagamentos | ✅ | ✅ |
| Listar todos | ✅ | ✅ + IDs + Status |
| Agregação por categoria | ✅ | ✅ |
| Sistema de IDs | ❌ | ✅ |
| Status pendente | ❌ | ✅ |
| Deletar pagamentos | ❌ | ✅ |
| Ver deletados | ❌ | ✅ |
| Editar pagamentos | ❌ | ✅ |
| Migração automática | - | ✅ |

---

## 🎉 Próximos Passos

1. ✅ Faça backup dos dados
2. ✅ Atualize para v2.0
3. ✅ Execute `pagto todos` para verificar migração
4. ✅ Teste os novos comandos
5. ✅ Aproveite os novos recursos!

---

## 💡 Dicas de Uso

### Marque Pagamentos Recorrentes como Pendentes
```bash
# Crie o pagamento futuro como pendente
pagto novo
# Categoria: Internet
# Pendente: s

# Quando pagar, edite e marque como pago
pagto editar [id]
# Pendente: n
```

### Use IDs para Referência Rápida
```bash
# Anote os IDs importantes
pagto todos | grep "Aluguel"  # Veja o ID
pagto editar [id]             # Edite direto pelo ID
```

### Mantenha Histórico com Soft Delete
```bash
# Não perca o histórico - apenas delete
pagto delete [id]

# Depois consulte quando precisar
pagto deletados
```

---

**Atualização concluída! Aproveite os novos recursos! 🚀**
