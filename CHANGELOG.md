# 📝 Changelog - Sistema de Gerenciamento de Pagamentos

## [2.1.0] - 2026-02-01

### 🎉 Recursos Principais - Comprovantes e Filtros

Esta versão adiciona duas funcionalidades muito solicitadas: gestão de comprovantes e sistema de filtros avançado.

### ✨ Novos Recursos

#### 📎 Sistema de Comprovantes
- **Adicionado**: Campo `comprovante` para vincular arquivos aos pagamentos
- **Funcionalidade**: Copiar e renomear automaticamente arquivos de comprovante
- **Nomenclatura**: Arquivos salvos como `[ID]_[BENEFICIARIO]_[VALOR].[ext]`
- **Pasta**: Todos comprovantes em `comprovantes/` (criada automaticamente)
- **Tipos**: Suporta qualquer tipo de arquivo (PDF, JPG, PNG, DOC, etc.)
- **Integração**: Disponível em `pagto novo` e `pagto editar`
- **Visualização**: Ícone 📎 nos relatórios indica presença de comprovante

**Exemplo de uso:**
```bash
pagto novo
# ... preencher dados ...
Caminho do comprovante (opcional): /home/user/recibo.pdf
✓ Comprovante salvo: 1_Fazenda_Silva_5000.pdf
```

#### 🔍 Sistema de Filtros Avançado
- **Adicionado**: Filtros por linha de comando em formato `campo:valor`
- **Sintaxe**: `pagto [comando] campo1:valor1 campo2:valor2 ...`
- **Comandos suportados**: `todos`, `categoria`, `deletados`
- **Múltiplos filtros**: Combinação com lógica AND
- **Busca parcial**: Campos de texto fazem busca case-insensitive

**Campos filtráveis:**
- `categoria` - Busca exata ou parcial
- `beneficiario` - Busca parcial case-insensitive
- `conta` - Busca parcial
- `devendo` / `devendo_para` - Busca parcial
- `pendente` - s/n, sim/não, 1/0, true/false
- `data` / `data_pagamento` - Busca parcial ou exata
- `valor` - Suporta operadores numéricos
- `id` - Busca exata

**Filtros numéricos de valor:**
- `valor:>100` - Maior que 100
- `valor:<500` - Menor que 500
- `valor:>=1000` - Maior ou igual a 1000
- `valor:<=250` - Menor ou igual a 250
- `valor:150.50` - Valor exato

**Exemplos de uso:**
```bash
# Filtro simples
pagto todos categoria:TRATOR

# Múltiplos filtros
pagto todos categoria:TRATOR pendente:n valor:>1000

# Filtro em agregação
pagto categoria conta:Nubank pendente:s
```

### 🔧 Melhorias

#### Interface do Usuário
- **Melhorado**: Tabelas agora mostram ícone 📎 para comprovantes
- **Adicionado**: Indicador de filtros aplicados nos relatórios
- **Adicionado**: Contador de registros encontrados
- **Melhorado**: Largura das colunas ajustada para nova coluna "Comp"

#### Gerenciamento de Arquivos
- **Adicionado**: Método `_copiar_comprovante()` para gestão de arquivos
- **Adicionado**: Método `_garantir_pasta_comprovantes()` para criar pasta
- **Adicionado**: Limpeza automática de nomes de arquivo (remove caracteres especiais)
- **Adicionado**: Arredondamento de valor para nomenclatura

#### Sistema de Filtros
- **Adicionado**: Método `_aplicar_filtros()` com lógica de filtragem
- **Adicionado**: Função `parsear_filtros()` para linha de comando
- **Adicionado**: Suporte a operadores de comparação numérica
- **Adicionado**: Mapeamento flexível de nomes de campos

#### Entrada de Dados
- **Adicionado**: Função `solicitar_comprovante()` com validação
- **Melhorado**: Validação de existência de arquivo
- **Melhorado**: Remoção automática de aspas do caminho

### 📚 Documentação

#### Novos Arquivos
- **COMPROVANTES_E_FILTROS.md**: Guia completo dos novos recursos

#### Arquivos Atualizados
- **README.md**: Atualizado com comprovantes e filtros
- **CHANGELOG.md**: Este arquivo
- **Ajuda do programa**: Exemplos de filtros adicionados

### 🔄 Mudanças na Estrutura de Dados

#### Campo Adicionado
```
comprovante - String, nome do arquivo de comprovante, opcional, padrão ""
```

#### Formato CSV Anterior (v2.0)
```csv
id,categoria,beneficiario,data_pagamento,conta,valor,devendo_para,pendente,deletado
```

#### Formato CSV Novo (v2.1)
```csv
id,categoria,beneficiario,data_pagamento,conta,valor,devendo_para,pendente,deletado,comprovante
```

### ⚠️ Breaking Changes

**Nenhum!** A v2.1 é 100% compatível com dados da v2.0 através de migração automática.

### 🐛 Correções

- **Corrigido**: Migração agora verifica também campo `comprovante`
- **Melhorado**: Tratamento de erros ao copiar arquivos
- **Melhorado**: Validação de caminhos de arquivo

### 🔒 Segurança

- **Adicionado**: Validação de existência de arquivo antes de copiar
- **Adicionado**: Limpeza de caracteres especiais em nomes de arquivo
- **Melhorado**: Tratamento de exceções em operações de arquivo

### 📊 Compatibilidade

- **Python**: 3.6+
- **Sistemas**: Linux, macOS, Windows
- **Dados**: 100% compatível com v2.0 e v1.0
- **Migração**: Automática e não destrutiva

### 🎯 Novos Casos de Uso

1. **Arquivo Digital Organizado**
   - Anexar todos comprovantes aos pagamentos
   - Organização automática com nomenclatura padronizada
   
2. **Auditoria e Compliance**
   - Rastreabilidade completa com comprovantes
   - Fácil localização de documentos por ID
   
3. **Análises Específicas**
   - Filtrar gastos por categoria e valor
   - Identificar pagamentos pendentes de fornecedor específico
   - Análise de gastos acima de threshold
   
4. **Gestão de Pendências**
   - Listar todos pendentes com filtros
   - Acompanhar pendências por fornecedor

### 📈 Estatísticas

- **Linhas de código adicionadas**: ~300
- **Novos métodos**: 4
- **Novos comandos**: Nenhum (filtros adicionados aos existentes)
- **Campos adicionados**: 1 (comprovante)
- **Compatibilidade retroativa**: 100%

---

## [2.0.0] - 2026-02-01

### 🎉 Versão Principal - Grandes Mudanças

Esta é uma atualização significativa que adiciona controle completo sobre os pagamentos com sistema de IDs, edição e exclusão lógica.

### ✨ Novos Recursos

#### Sistema de IDs Únicos
- **Adicionado**: Campo `id` para cada pagamento
- **Característica**: IDs são sequenciais, únicos e permanentes
- **Comportamento**: Mesmo pagamentos deletados mantêm seus IDs (nunca reutilizados)
- **Geração**: Automática ao criar novo pagamento
- **Migração**: IDs são gerados automaticamente para pagamentos antigos

#### Status de Pagamento Pendente
- **Adicionado**: Campo `pendente` para marcar pagamentos não efetivados
- **Uso**: Ideal para pagamentos agendados ou recorrentes
- **Visualização**: Indicador visual "⏳ Pend." vs "✓ Pago" no relatório
- **Padrão**: Novos pagamentos são marcados como "não pendente" por padrão

#### Sistema de Soft Delete
- **Adicionado**: Campo `deletado` para marcar registros removidos
- **Comportamento**: Pagamentos deletados não aparecem em relatórios normais
- **Preservação**: Dados deletados permanecem no arquivo para auditoria
- **Recuperação**: Possível visualizar deletados com comando específico

#### Novos Comandos

**`pagto delete [id]`**
- Marca um pagamento como deletado
- Solicita confirmação antes de deletar
- Mostra resumo do pagamento antes de deletar
- Não permite deletar registros já deletados

**`pagto deletados`**
- Lista todos os pagamentos marcados como deletados
- Mostra tabela formatada com totais
- Útil para auditoria e histórico

**`pagto editar [id]`**
- Permite editar qualquer campo de um pagamento
- Mostra valores atuais entre colchetes
- Pressionar ENTER mantém valor atual
- Não permite editar pagamentos deletados
- Não permite alterar o ID

### 🔧 Melhorias

#### Interface do Usuário
- **Melhorado**: Comando `pagto todos` agora mostra ID na primeira coluna
- **Melhorado**: Adicionada coluna "Status" mostrando se está pago ou pendente
- **Melhorado**: Formatação da tabela ajustada para novos campos
- **Melhorado**: Mensagens de sucesso agora mostram o ID do registro

#### Sistema de Entrada de Dados
- **Melhorado**: Funções de input agora suportam valores atuais (para edição)
- **Adicionado**: Nova função `solicitar_pendente()` para status
- **Melhorado**: Validação mantida em todas as entradas

#### Gerenciamento de Dados
- **Adicionado**: Método `_gerar_novo_id()` para IDs únicos
- **Adicionado**: Método `_listar_todos_incluindo_deletados()` para operações internas
- **Adicionado**: Método `buscar_por_id()` para localizar registros
- **Adicionado**: Método `marcar_como_deletado()` para soft delete
- **Adicionado**: Método `atualizar_pagamento()` para edições
- **Adicionado**: Método `listar_deletados()` para visualização
- **Adicionado**: Método `_reescrever_arquivo()` para atualizações

#### Migração Automática
- **Adicionado**: Método `_migrar_dados_antigos()` para compatibilidade
- **Comportamento**: Detecta automaticamente arquivos v1.0
- **Ação**: Adiciona novos campos preservando dados existentes
- **Geração**: Cria IDs sequenciais para registros migrados
- **Execução**: Transparente na primeira execução

### 📚 Documentação

#### Novos Arquivos
- **ATUALIZACAO.md**: Guia completo de atualização da v1.0 para v2.0
- **CHANGELOG.md**: Este arquivo

#### Arquivos Atualizados
- **README.md**: Atualizado com novos comandos e recursos
- **GUIA_RAPIDO.md**: Atualizado com exemplos dos novos comandos

### 🔄 Mudanças na Estrutura de Dados

#### Campos Adicionados
```
id          - String, identificador único, obrigatório
pendente    - String "0" ou "1", padrão "0"
deletado    - String "0" ou "1", padrão "0"
```

#### Formato CSV Anterior (v1.0)
```csv
categoria,beneficiario,data_pagamento,conta,valor,devendo_para
```

#### Formato CSV Novo (v2.0)
```csv
id,categoria,beneficiario,data_pagamento,conta,valor,devendo_para,pendente,deletado
```

### ⚠️ Breaking Changes

**Nenhum!** A v2.0 é 100% compatível com dados da v1.0 através de migração automática.

### 🐛 Correções

- **Corrigido**: Tratamento de campos ausentes em dados migrados
- **Corrigido**: Validação de valores vazios em campos opcionais
- **Melhorado**: Mensagens de erro mais descritivas

### 🔒 Segurança

- **Adicionado**: Validação de ID antes de operações críticas
- **Adicionado**: Confirmação obrigatória antes de deletar
- **Melhorado**: Validação de tipo de dados em todas as entradas

### 📊 Compatibilidade

- **Python**: 3.6+
- **Sistemas**: Linux, macOS, Windows
- **Dados**: 100% compatível com v1.0
- **Migração**: Automática e não destrutiva

### 🎯 Casos de Uso Novos

1. **Pagamentos Recorrentes**
   - Criar pagamento como pendente
   - Editar para marcar como pago quando efetivado
   
2. **Correção de Erros**
   - Usar `pagto editar [id]` para corrigir valores
   
3. **Auditoria**
   - Manter histórico de deletados para análise
   
4. **Organização**
   - Usar IDs para referência rápida
   - Deletar duplicatas mantendo histórico

### 📈 Estatísticas

- **Linhas de código adicionadas**: ~500
- **Novos métodos**: 8
- **Novos comandos**: 3
- **Campos adicionados**: 3
- **Compatibilidade retroativa**: 100%

---

## [1.0.0] - 2026-01-XX

### 🎉 Versão Inicial

#### Recursos Principais

**Comandos Básicos**
- `pagto novo` - Registrar novos pagamentos
- `pagto todos` - Listar todos os pagamentos
- `pagto categoria` - Agregação por categoria

#### Campos de Dados
- categoria (obrigatório)
- beneficiario (obrigatório)
- data_pagamento (padrão: hoje)
- conta (obrigatório)
- valor (obrigatório, float)
- devendo_para (opcional)

#### Funcionalidades
- ✅ Validação de entrada de dados
- ✅ Formatação de moeda em Real (R$)
- ✅ Armazenamento em CSV
- ✅ Totais automáticos
- ✅ Interface de linha de comando
- ✅ Mensagens de erro amigáveis

---

## 🔮 Roadmap Futuro

### Possíveis Melhorias para v2.1+

- [ ] Restaurar pagamentos deletados
- [ ] Filtros por data/categoria/conta
- [ ] Exportação para PDF
- [ ] Gráficos em linha de comando
- [ ] Importação de extratos bancários
- [ ] Categorias personalizadas
- [ ] Multi-usuário
- [ ] Sincronização em nuvem
- [ ] Modo interativo (TUI)
- [ ] API REST

### Sugestões da Comunidade

Sugestões e contribuições são bem-vindas! Abra uma issue ou pull request.

---

**Desenvolvido com ❤️ para facilitar o controle financeiro pessoal**
