#!/bin/bash
# Script de instalação do pagto

echo "=== Instalando pagto ==="

# Torna o script executável
chmod +x pagto.py

# Cria um link simbólico em /usr/local/bin (requer sudo)
# Ou copia para ~/.local/bin (não requer sudo)

if [ -w "/usr/local/bin" ]; then
    # Se temos permissão de escrita em /usr/local/bin
    ln -sf "$(pwd)/pagto.py" /usr/local/bin/pagto
    echo "✓ Comando 'pagto' instalado em /usr/local/bin"
else
    # Caso contrário, instala em ~/.local/bin
    mkdir -p ~/.local/bin
    ln -sf "$(pwd)/pagto.py" ~/.local/bin/pagto
    echo "✓ Comando 'pagto' instalado em ~/.local/bin"
    echo ""
    echo "Certifique-se de que ~/.local/bin está no seu PATH."
    echo "Adicione esta linha ao seu ~/.bashrc ou ~/.zshrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
fi

echo ""
echo "Instalação concluída! Agora você pode usar:"
echo "  pagto novo"
echo "  pagto todos"
echo "  pagto categoria"
