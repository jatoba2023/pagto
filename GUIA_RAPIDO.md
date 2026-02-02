# 🚀 Guia de Início Rápido - pagto

## Instalação em 3 Passos

### 1. Baixe os arquivos
Você receberá:
- `pagto.py` - Aplicação principal
- `instalar.sh` - Script de instalação
- `README.md` - Documentação completa

### 2. Instale o comando

**Linux/Mac:**
```bash
chmod +x instalar.sh
./instalar.sh
```

**Ou adicione um alias:**
```bash
echo 'alias pagto="python3 /caminho/para/pagto.py"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
```bash
# Use diretamente:
python pagto.py novo
python pagto.py todos
python pagto.py categoria
```

### 3. Comece a usar!

```bash
pagto novo      # Registrar pagamento
pagto todos     # Ver todos
pagto categoria # Ver por categoria
```

## 📝 Exemplo de Uso Completo

### Passo 1: Registrar seus primeiros pagamentos

```bash
$ pagto novo

=== NOVO PAGAMENTO ===

Categoria: Alimentação
Beneficiário: Supermercado Extra
Data do pagamento (dd/mm/aaaa) [hoje: 01/02/2026]: 
Conta: Nubank
Valor (R$): 350,00
Devendo para (opcional): 

✓ Pagamento registrado com sucesso!
```

### Passo 2: Registrar mais pagamentos

```bash
$ pagto novo

Categoria: Transporte
Beneficiário: Uber
Conta: Itaú
Valor (R$): 45.50
```

```bash
$ pagto novo

Categoria: Lazer
Beneficiário: Cinema
Conta: Dinheiro
Valor (R$): 80
Devendo para (opcional): Maria
```

### Passo 3: Ver todos os pagamentos

```bash
$ pagto todos

=== TODOS OS PAGAMENTOS ===

Data         Categoria            Beneficiário              Conta                     Valor Devendo             
------------------------------------------------------------------------------------------------------------------------
01/02/2026   Alimentação          Supermercado Extra        Nubank                R$ 350,00                     
01/02/2026   Transporte           Uber                      Itaú                   R$ 45,50                     
01/02/2026   Lazer                Cinema                    Dinheiro               R$ 80,00 Maria               
------------------------------------------------------------------------------------------------------------------------
TOTAL:                                                                                        R$ 475,50
```

### Passo 4: Ver totais por categoria

```bash
$ pagto categoria

=== PAGAMENTOS POR CATEGORIA ===

Categoria                                     Total
----------------------------------------------------
Alimentação                               R$ 350,00
Lazer                                      R$ 80,00
Transporte                                 R$ 45,50
----------------------------------------------------
TOTAL GERAL:                              R$ 475,50
```

## 💡 Dicas Importantes

### Categorias Recomendadas
- Alimentação
- Transporte
- Moradia
- Saúde
- Lazer
- Educação
- Vestuário
- Outros

### Boas Práticas
1. **Use categorias consistentes** - sempre a mesma grafia
2. **Registre imediatamente** - não deixe acumular
3. **Faça backup** do arquivo `pagamentos.csv`
4. **Revise mensalmente** com `pagto categoria`

### Exportar para Excel
O arquivo `pagamentos.csv` pode ser aberto diretamente no Excel ou Google Sheets!

1. Abra o Excel/Sheets
2. Arquivo → Abrir → Selecione `pagamentos.csv`
3. Pronto! Você pode criar gráficos e análises

## 🔧 Comandos Úteis

```bash
# Ver ajuda
pagto ajuda

# Ver onde está o arquivo de dados
ls -la pagamentos.csv

# Fazer backup
cp pagamentos.csv pagamentos_backup_$(date +%Y%m%d).csv

# Limpar todos os dados (CUIDADO!)
rm pagamentos.csv
```

## ❓ Perguntas Frequentes

**P: Onde ficam salvos os dados?**
R: No arquivo `pagamentos.csv` no mesmo diretório onde você executa o comando.

**P: Posso editar o CSV manualmente?**
R: Sim! Abra com Excel ou editor de texto, mas mantenha o formato.

**P: Perdi meus dados, como recuperar?**
R: Se não fez backup, infelizmente não há como recuperar. Faça backups regulares!

**P: Posso usar em várias máquinas?**
R: Sim! Coloque o `pagamentos.csv` em um serviço de nuvem (Dropbox, Google Drive) e aponte o caminho no código.

**P: Como remover um pagamento errado?**
R: Abra o arquivo `pagamentos.csv` e delete a linha correspondente.

## 🎯 Próximos Passos

1. Configure categorias que fazem sentido para você
2. Registre todos os pagamentos do mês
3. No fim do mês, use `pagto categoria` para ver onde gastou mais
4. Ajuste seus gastos baseado na análise

---

**Pronto para começar a ter controle total das suas finanças!** 💪
