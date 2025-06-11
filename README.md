# NEO Tracker

Este programa exibe objetos do NEOCP, consulta alvos via NEOFIXER e gera efemérides para facilitar o trabalho de follow up.

## Instalação de dependências

Recomenda-se o uso de um ambiente virtual. Instale os pacotes necessários com:

```bash
pip install requests pandas
```

## Configuração do `config.ini`

Crie ou edite o arquivo `config.ini` no mesmo diretório do script contendo:

```ini
[Paths]
find_orb_path = C:\\Caminho\\Para\\find_orb
```

Substitua `C:\\Caminho\\Para\\find_orb` pelo caminho onde se encontra o executável `fo64.exe` do `find_orb`. Esse caminho também pode ser informado via linha de comando com a opção `--find_orb_path`.

## Execução

Execute a aplicação com:

```bash
python NEO_Tracker.py
```

Opcionalmente especifique o caminho do `find_orb`:

```bash
python NEO_Tracker.py --find_orb_path "C:\\Caminho\\Para\\find_orb"
```

## Opções do menu

O menu principal da aplicação oferece:

- **NEOCP**: visualiza candidatos a NEO.
- **NEOFIXER**: executa o NEOFIXER e lista alvos disponíveis.
- **Help**: abre o manual do usuário.
- **About**: informações sobre o aplicativo.
- **Quit**: encerra a aplicação.

Use o botão **Submit** para gerar as efemérides e **Reset** para limpar os campos.
