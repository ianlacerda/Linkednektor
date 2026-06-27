# 🔗 Linkednektor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Latest-green?logo=playwright&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey?logo=sqlite&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**Automação inteligente e ultra-resiliente para envio de convites de conexão no LinkedIn com comportamento humano simulado e controle total via interface gráfica.**

[Funcionalidades](#-funcionalidades) •
[Instalação](#-instalação) •
[Como Usar](#-como-usar) •
[Arquitetura](#-arquitetura) •
[Segurança e GitHub](#-segurança-e-github)

</div>

---

## 📋 Sobre o Projeto

O **Linkednektor** é uma ferramenta de automação desktop desenvolvida em Python para profissionais de recrutamento, marketing e vendas. O programa automatiza o fluxo de busca de pessoas no LinkedIn, aplicação de filtros regionais/cargos e envio de convites de conexão de forma extremamente natural, simulando o comportamento de um usuário real e registrando os contatos para evitar interações duplicadas.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🔍 **Busca por Palavras-chave** | Pesquisa automática por cargos, competências ou qualquer termo de busca. |
| 📍 **Filtro de Localidade** | Aplica o filtro geográfico nativo do LinkedIn. |
| 🏢 **Filtro "Contratando Já"** | Filtra perfis que possuem vagas ativas e o selo "Hiring". |
| 💾 **Sessão Persistente** | Salva os cookies e o perfil do navegador Playwright localmente para que você só precise fazer login uma vez. |
| 💾 **Banco de Dados SQLite3** | Registra perfis processados (`sent` ou `already_connected`) em um banco local (`linkednektor.db`). O bot pula automaticamente contatos já abordados. |
| ⏸️ **Controles de Pausa/Retomada** | Botão de Pausar e Retomar na interface gráfica com interrupção e retomada imediata (thread-safe). |
| 📱 **Suporte a Layout Responsivo** | Detecta elementos tanto na versão desktop quanto mobile-responsiva do LinkedIn (tratando botões do tipo `<a>` e wrappers complexos do `Topcard`). |
| 🚫 **Filtro de Conexões Mútuas** | Ignora links de conexões em comum listados abaixo do card principal na pesquisa. |
| 📸 **Debug Dumps Automáticos** | Em caso de erro na página de busca ou perfil, o bot salva um screenshot (`.png`) e o código-fonte (`.html`) na pasta `debug_dumps/` e gera links clicáveis no terminal. |
| 🧹 **Limpar Histórico** | Botão na interface do usuário para limpar o banco de dados de histórico com diálogo de confirmação. |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior instalado.
- Google Chrome instalado.
- Gerenciador de pacotes `pip` instalado.

### Passo a Passo

1. **Crie um diretório e acesse-o:**
   ```bash
   cd Linkednektor
   ```

2. **Crie e ative um ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   # No Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install playwright
   ```

4. **Instale os binários de navegador do Playwright:**
   ```bash
   playwright install chromium
   ```

5. **Inicie o programa:**
   ```bash
   python main.py
   ```

---

## 🖥️ Como Usar

1. Execute `python main.py` para abrir a interface gráfica.
2. Insira o termo de busca (ex: `Design Recruiter`).
3. (Opcional) Digite a cidade para filtragem regional.
4. Selecione a quantidade de páginas do LinkedIn a pesquisar.
5. Se desejar, marque **Contratando já** e insira o cargo da vaga.
6. Clique em **🚀 Iniciar Buscas**.
7. Na primeira execução, o navegador abrirá para que você faça login manualmente. Uma vez logado, o bot salvará a sessão.
8. Para reiniciar os testes ou limpar contatos antigos, clique no botão **🧹 Limpar Histórico** na interface gráfica.

---

## 🔒 Segurança e GitHub

### 1. Repositório Privado (Acesso por Senha)
Para garantir que o código de automação e dados internos permaneçam protegidos, **crie o repositório como PRIVADO no GitHub**. 
* Apenas usuários convidados explicitamente por você terão acesso ao código.
* O acesso de leitura e escrita é protegido pelas credenciais do GitHub (Token de Acesso Pessoal ou chaves SSH).

### 2. Proteção de Dados Sensíveis
O projeto inclui um arquivo `.gitignore` configurado para **nunca** subir arquivos locais com dados pessoais ou de sessão para o GitHub:
* 🔴 `linkednektor.db` (histórico de perfis contatados).
* 🔴 `linkednektor_profile/` (cookies de login e credenciais do LinkedIn no Chrome).
* 🔴 `debug_dumps/` (screenshots e páginas HTML de auditoria).

> [!WARNING]
> Nunca delete ou altere a pasta `linkednektor_profile/` no `.gitignore`. Ela contém suas credenciais ativas do LinkedIn.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
