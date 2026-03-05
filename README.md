# NEO Tracker

> 🇧🇷 [Versão em Português](#versão-em-português) | 🇬🇧 [English Version](#english-version)

---

## Versão em Português

Este programa exibe objetos do NEOCP, consulta alvos via NEOFIXER e gera efemérides para facilitar o trabalho de follow-up observacional de NEOs.

---

### Para usuários finais (versão executável)

#### 1. Instalar o Find_Orb

O NEO Tracker depende do Find_Orb (desenvolvido por Bill Gray / Project Pluto) para calcular órbitas e gerar efemérides. A instalação é feita em duas etapas:

**Passo 1 — Instalar o Find_Orb interativo**

Acesse https://www.projectpluto.com/find_con.htm, baixe a versão 64-bit para Windows (`find_c64.zip`) e descompacte em uma pasta de sua escolha (ex: `C:\find_orb`).

> Este passo é obrigatório mesmo que você não vá usar o Find_Orb interativo. O `fo64.exe` depende dos arquivos de configuração instalados nessa etapa.

**Passo 2 — Baixar o fo64.exe**

Acesse https://www.projectpluto.com/devel/fo64.exe e salve o arquivo `fo64.exe` dentro da mesma pasta do Passo 1 (ex: `C:\find_orb\fo64.exe`).

#### 2. Configurar o `config.ini`

Crie ou edite o arquivo `config.ini` no mesmo diretório do executável:

```ini
[Paths]
find_orb_path = C:\find_orb
```

Substitua `C:\find_orb` pelo caminho onde se encontra o `fo64.exe`.

#### 3. Executar

Baixe o executável `NEO_Tracker.exe` e execute diretamente. Nenhuma instalação adicional é necessária.

---

### Para desenvolvedores (código fonte)

#### Pré-requisitos

- Python 3.9 ou superior
- Find_Orb instalado conforme descrito acima

#### Instalação de dependências Python

```bash
python -m pip install requests pandas
```

#### Configuração do `config.ini`

```ini
[Paths]
find_orb_path = C:\find_orb
```

O caminho também pode ser informado via linha de comando:

```bash
python NEO_Tracker.py --find_orb_path "C:\find_orb"
```

#### Execução

```bash
python NEO_Tracker.py
```

---

### Opções do menu

- **NEOCP**: visualiza candidatos a NEO diretamente do Minor Planet Center.
- **NEOFIXER**: consulta e lista alvos prioritários via NEOFIXER (Universidade do Arizona).
- **Help**: abre o manual do usuário.
- **About**: informações sobre o aplicativo.
- **Quit**: encerra a aplicação.

Use o botão **Submit** para gerar as efemérides e **Reset** para limpar os campos.

---

## English Version

This program displays NEOCP objects, queries targets via NEOFIXER, and generates ephemerides to support NEO observational follow-up work.

---

### For end users (executable version)

#### 1. Install Find_Orb

NEO Tracker depends on Find_Orb (developed by Bill Gray / Project Pluto) to compute orbits and generate ephemerides. Installation is done in two steps:

**Step 1 — Install interactive Find_Orb**

Go to https://www.projectpluto.com/find_con.htm, download the 64-bit Windows version (`find_c64.zip`), and unzip it to a folder of your choice (e.g. `C:\find_orb`).

> This step is required even if you do not intend to use interactive Find_Orb. The `fo64.exe` executable depends on configuration files installed in this step.

**Step 2 — Download fo64.exe**

Go to https://www.projectpluto.com/devel/fo64.exe and save `fo64.exe` inside the same folder from Step 1 (e.g. `C:\find_orb\fo64.exe`).

#### 2. Configure `config.ini`

Create or edit the `config.ini` file in the same directory as the executable:

```ini
[Paths]
find_orb_path = C:\find_orb
```

Replace `C:\find_orb` with the path where `fo64.exe` is located.

#### 3. Run

Download `NEO_Tracker.exe` and run it directly. No additional installation required.

---

### For developers (source code)

#### Prerequisites

- Python 3.9 or higher
- Find_Orb installed as described above

#### Installing Python dependencies

```bash
python -m pip install requests pandas
```

#### Configuring `config.ini`

```ini
[Paths]
find_orb_path = C:\find_orb
```

The path can also be provided via command line:

```bash
python NEO_Tracker.py --find_orb_path "C:\find_orb"
```

#### Running

```bash
python NEO_Tracker.py
```

---

### Menu options

- **NEOCP**: displays NEO candidates directly from the Minor Planet Center.
- **NEOFIXER**: queries and lists priority targets via NEOFIXER (University of Arizona).
- **Help**: opens the user manual.
- **About**: application information.
- **Quit**: exits the application.

Use the **Submit** button to generate ephemerides and **Reset** to clear the fields.
