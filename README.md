# NEO Tracker — Ephemeris Calculator

**NEO Tracker** is a desktop application for calculating ephemerides and orbital elements of Near-Earth Objects (NEOs) and NEOCP candidates, using data from the Minor Planet Center and the Find_Orb orbital solver.

**NEO Tracker** é uma aplicação desktop para calcular efemérides e elementos orbitais de Near-Earth Objects (NEOs) e candidatos NEOCP, utilizando dados do Minor Planet Center e o solver orbital Find_Orb.

---

## Table of Contents / Índice

- 🇺🇸 [English](#english)
  - [For End Users — Installing the Executable](#for-end-users--installing-the-executable)
  - [Using the Application](#using-the-application)
  - [For Developers — Running from Source](#for-developers--running-from-source)
  - [Troubleshooting](#troubleshooting)
- 🇧🇷 [Português](#português)
  - [Para Usuários Finais — Instalando o Executável](#para-usuários-finais--instalando-o-executável)
  - [Usando o Programa](#usando-o-programa)
  - [Para Desenvolvedores — Rodando pelo Código-Fonte](#para-desenvolvedores--rodando-pelo-código-fonte)
  - [Solução de Problemas](#solução-de-problemas)

---

# English

## For End Users — Installing the Executable

You do **not** need Python installed. The `.exe` includes everything.  
You **do** need to install Find_Orb separately — it is the orbital solver that does the calculations.

---

### Step 1 — Install Find_Orb

Find_Orb is a free orbital solver by Bill Gray (Project Pluto). NEO Tracker uses its command-line version (`fo64.exe`).

**1.1 — Download the Find_Orb support files**

Go to: https://www.projectpluto.com/find_con.htm

Download the file **`find_c64.zip`** (look for the Windows 64-bit download link).  
Extract the ZIP to a folder of your choice, for example:

```
C:\find_c64\
```

> ⚠️ This step is mandatory even if you only plan to use NEO Tracker. The `fo64.exe` executable depends on configuration files that are inside this ZIP.

**1.2 — Download fo64.exe**

Go to: https://www.projectpluto.com/devel/fo64.exe

Save **`fo64.exe`** into the **same folder** where you extracted `find_c64.zip`:

```
C:\find_c64\fo64.exe
```

After this step your `find_c64` folder should contain `fo64.exe` plus several configuration files (`.json`, `.dat`, etc.).

---

### Step 2 — Download NEO Tracker

Go to the [Releases page](https://github.com/Anduin-source/NEOS_Tracker/releases) and download the latest release ZIP file.

Extract it to a folder of your choice, for example:

```
C:\NEO_Tracker\
```

The extracted folder should contain:

```
NEO_Tracker.exe
config.ini
```

---

### Step 3 — Configure config.ini

Open `config.ini` with Notepad (right-click → Open with → Notepad).

You will see:

```ini
[Paths]
find_orb_path = 
obs_code = X93
```

Edit `find_orb_path` to point to the folder where you installed Find_Orb in Step 1:

```ini
[Paths]
find_orb_path = C:\find_c64
obs_code = X93
```

> ℹ️ **obs_code** is your MPC observatory code (3 characters). The default `X93` is a valid code.  
> If you have your own MPC code, enter it here. You can look it up at:  
> https://minorplanetcenter.net/iau/lists/ObsCodes.html  
> The application will remember your code automatically after each successful calculation.

Save and close the file.

---

### Step 4 — Run the program

Double-click `NEO_Tracker.exe`.

The application will open and automatically load the current NEOCP candidate list from the Minor Planet Center. An internet connection is required.

---

## Using the Application

**Left panel — NEOCP Candidates**
- Loads automatically on startup, sorted by visual magnitude (brightest first)
- Double-click any row to fill the form automatically
- Click **↻ Refresh** to reload the list at any time

**Right panel — Form**
- Select object type: **NEO** (known numbered/named object) or **NEOCP** (unconfirmed candidate)
- Enter the object designation (e.g. `2021 PDC`), or double-click a row in the NEOCP panel
- Enter your observatory code (default: X93)
- Set the number of ephemeris steps (default: 10)
- Click **▶ Submit** or press **Ctrl+S**

**Results** appear in the lower right area:
- Orbital elements
- Ephemerides
- Raw observations (MPC OBS80 format)

**NEOFIXER** menu — loads follow-up targets from the University of Arizona NEOFIXER API filtered by your observatory.

---

## For Developers — Running from Source

**Requirements**
- Python 3.10 or higher (3.12 recommended)
- Find_Orb installed as described in Step 1 above

**Install dependencies**

```bash
pip install requests pandas
```

**Run**

```bash
python NEO_Tracker.py
```

Or specify the Find_Orb path directly:

```bash
python NEO_Tracker.py --find_orb_path "C:\find_c64"
```

**Build executable**

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --icon=neo_tracker.ico --name="NEO_Tracker" NEO_Tracker.py
```

The `.exe` will be generated in the `dist\` folder.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "fo64.exe not found" | Check that `find_orb_path` in `config.ini` points to the correct folder and that `fo64.exe` is inside it |
| "Object not found" | Check the designation. For NEOCP objects use the temporary designation (e.g. `P21Xvzq`), not a name |
| NEOCP panel shows "Failed to load" | Check your internet connection |
| Application opens and closes immediately | Open a terminal (`cmd`) and run `NEO_Tracker.exe` to see the error message |
| Antivirus blocks the .exe | False positive common with PyInstaller executables. Add an exception for `NEO_Tracker.exe` |

**Logs:** errors are recorded in `app.log` in the same folder as the executable.

**Support:** https://github.com/Anduin-source/NEOS_Tracker/issues

---

# Português

## Para Usuários Finais — Instalando o Executável

Você **não** precisa ter Python instalado. O `.exe` já inclui tudo.  
Você **precisa** instalar o Find_Orb separadamente — ele é o solver orbital que faz os cálculos.

---

### Passo 1 — Instalar o Find_Orb

O Find_Orb é um solver orbital gratuito desenvolvido por Bill Gray (Project Pluto). O NEO Tracker utiliza sua versão de linha de comando (`fo64.exe`).

**1.1 — Baixar os arquivos de suporte do Find_Orb**

Acesse: https://www.projectpluto.com/find_con.htm

Baixe o arquivo **`find_c64.zip`** (procure pelo link de download para Windows 64-bit).  
Extraia o ZIP para uma pasta de sua escolha, por exemplo:

```
C:\find_c64\
```

> ⚠️ Este passo é obrigatório mesmo que você não vá usar o Find_Orb diretamente. O `fo64.exe` depende de arquivos de configuração que estão dentro desse ZIP.

**1.2 — Baixar o fo64.exe**

Acesse: https://www.projectpluto.com/devel/fo64.exe

Salve o arquivo **`fo64.exe`** na **mesma pasta** onde você extraiu o `find_c64.zip`:

```
C:\find_c64\fo64.exe
```

Após este passo, sua pasta `find_c64` deve conter o `fo64.exe` mais vários arquivos de configuração (`.json`, `.dat`, etc.).

---

### Passo 2 — Baixar o NEO Tracker

Acesse a [página de Releases](https://github.com/Anduin-source/NEOS_Tracker/releases) e baixe o arquivo ZIP da versão mais recente.

Extraia para uma pasta de sua escolha, por exemplo:

```
C:\NEO_Tracker\
```

A pasta extraída deve conter:

```
NEO_Tracker.exe
config.ini
```

---

### Passo 3 — Configurar o config.ini

Abra o arquivo `config.ini` com o Bloco de Notas (clique com o botão direito → Abrir com → Bloco de Notas).

Você verá:

```ini
[Paths]
find_orb_path = 
obs_code = X93
```

Edite o campo `find_orb_path` para apontar para a pasta onde você instalou o Find_Orb no Passo 1:

```ini
[Paths]
find_orb_path = C:\find_c64
obs_code = X93
```

> ℹ️ **obs_code** é o seu código de observatório MPC (3 caracteres). O padrão `X93` é um código válido.  
> Se você tiver seu próprio código MPC, insira-o aqui. Você pode consultá-lo em:  
> https://minorplanetcenter.net/iau/lists/ObsCodes.html  
> O programa memoriza automaticamente o código utilizado após cada cálculo bem-sucedido.

Salve e feche o arquivo.

---

### Passo 4 — Executar o programa

Dê um duplo clique em `NEO_Tracker.exe`.

O programa abrirá e carregará automaticamente a lista atual de candidatos NEOCP do Minor Planet Center. É necessária conexão com a internet.

---

## Usando o Programa

**Painel esquerdo — Candidatos NEOCP**
- Carrega automaticamente ao abrir, ordenado por magnitude visual (mais brilhantes primeiro)
- Dê um duplo clique em qualquer linha para preencher o formulário automaticamente
- Clique em **↻ Refresh** para recarregar a lista a qualquer momento

**Painel direito — Formulário**
- Selecione o tipo de objeto: **NEO** (objeto conhecido) ou **NEOCP** (candidato não confirmado)
- Digite a designação do objeto (ex: `2021 PDC`), ou dê duplo clique no painel NEOCP
- Digite o código do observatório (padrão: X93)
- Defina o número de passos de efeméride (padrão: 10)
- Clique em **▶ Submit** ou pressione **Ctrl+S**

**Resultados** aparecem na área inferior direita:
- Elementos orbitais
- Efemérides
- Observações brutas (formato MPC OBS80)

**Menu NEOFIXER** — carrega alvos de seguimento da API NEOFIXER da Universidade do Arizona filtrados pelo seu observatório.

---

## Para Desenvolvedores — Rodando pelo Código-Fonte

**Requisitos**
- Python 3.10 ou superior (recomendado: 3.12)
- Find_Orb instalado conforme o Passo 1 acima

**Instalar dependências**

```bash
pip install requests pandas
```

**Executar**

```bash
python NEO_Tracker.py
```

Ou especificando o caminho do Find_Orb diretamente:

```bash
python NEO_Tracker.py --find_orb_path "C:\find_c64"
```

**Gerar executável**

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --icon=neo_tracker.ico --name="NEO_Tracker" NEO_Tracker.py
```

O `.exe` será gerado na pasta `dist\`.

---

## Solução de Problemas

| Problema | Solução |
|---|---|
| "fo64.exe not found" | Verifique se `find_orb_path` no `config.ini` aponta para a pasta correta e se o `fo64.exe` está dentro dela |
| "Object not found" | Verifique a designação. Para objetos NEOCP use a designação temporária (ex: `P21Xvzq`), não um nome |
| Painel NEOCP mostra "Failed to load" | Verifique sua conexão com a internet |
| Programa abre e fecha imediatamente | Abra um terminal (`cmd`) e execute `NEO_Tracker.exe` para ver a mensagem de erro |
| Antivírus bloqueia o .exe | Falso positivo comum em executáveis gerados pelo PyInstaller. Adicione uma exceção para o `NEO_Tracker.exe` |

**Logs:** erros são registrados no arquivo `app.log` na mesma pasta do executável.

**Suporte:** https://github.com/Anduin-source/NEOS_Tracker/issues

---

*Fontes de dados: Minor Planet Center · Find_Orb por Bill Gray (Project Pluto) · NEOFIXER pela Universidade do Arizona*
