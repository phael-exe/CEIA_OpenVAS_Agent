# Documentação para Diagramação do Projeto OpenVAS Agent

Este documento detalha a arquitetura e o funcionamento do projeto OpenVAS Agent, com foco nas classes, funções, agentes e seus fluxos de entrada e saída, para auxiliar na criação de diagramas.

---

## 1. Visão Geral do Projeto (`main.py`)

O `main.py` é o ponto de entrada da aplicação, orquestrando os agentes e o fluxo de trabalho usando LangGraph. Ele inicializa o LLM, define o grafo de estados e gerencia a interação principal com o usuário.

### Fluxo Principal

1.  **Inicialização**: Carrega variáveis de ambiente, inicializa o LLM (`ChatOpenAI`).
2.  **Construção do Grafo**: Define os nós (`TaskCreator`, `ResultAnalyzer`, `supervisor`) e as arestas condicionais que governam a transição entre eles.
3.  **Loop de Interação**: Entra em um loop onde o usuário insere uma query. A query é passada para o grafo, que a processa e retorna um resultado.

### Componentes Principais:

*   **LLM**: `ChatOpenAI` (modelo definido por `OPENAI_MODEL_ID` no `.env`).
*   **Grafo de Estados**: `StateGraph` com `AgentState`.
*   **Nós do Grafo**:
    *   `TaskCreator`: Cria e inicia tarefas no OpenVAS.
    *   `ResultAnalyzer`: Busca e analisa resultados de scans do OpenVAS.
    *   `supervisor`: Roteia a execução para o agente apropriado ou finaliza.

### Entradas e Saídas Esperadas:

*   **Entrada**: `query` (string) do usuário via `input()`.
*   **Saída**: `final_message.content` (string) do grafo, exibido para o usuário.

---

## 2. Estado do Agente (`src/state.py`)

Define a estrutura de dados que representa o estado compartilhado entre os agentes no grafo.

### Classe: `AgentState`

*   **Descrição**: Um `TypedDict` que armazena as mensagens da conversa.
*   **Atributos**:
    *   `messages`: `Annotated[Sequence[BaseMessage], operator.add]`
        *   **Tipo**: Uma sequência de objetos `BaseMessage` (do `langchain_core.messages`).
        *   **Propósito**: Acumula o histórico de mensagens (Human, AI, Tool) ao longo da execução do grafo.
        *   **Entrada**: Novas mensagens são adicionadas a esta sequência por cada nó do grafo.
        *   **Saída**: O estado atualizado, incluindo as novas mensagens, é passado para o próximo nó.

---

## 3. Agente Supervisor (`src/agents/supervisor.py`)

Responsável por rotear a requisição do usuário para o agente correto (`TaskCreator` ou `ResultAnalyzer`) ou finalizar o processo.

### Classe: `Route`

*   **Descrição**: Modelo Pydantic para a decisão de roteamento do supervisor.
*   **Atributos**:
    *   `next`: `Literal["TaskCreator", "ResultAnalyzer"]`
        *   **Propósito**: Indica qual será o próximo nó a ser executado no grafo.

### Função: `create_supervisor_chain(llm: ChatOpenAI)`

*   **Descrição**: Constrói a cadeia de decisão do supervisor usando um LLM.
*   **Entrada**:
    *   `llm`: Uma instância de `ChatOpenAI`.
*   **Processamento**:
    *   Define um `system_prompt_supervisor` que instrui o LLM sobre as regras de roteamento.
    *   Cria um `ChatPromptTemplate` com o prompt do sistema e um `MessagesPlaceholder` para o histórico de mensagens.
    *   Configura o LLM para retornar uma saída estruturada (`Route`).
*   **Saída**: Uma cadeia LangChain que, quando invocada, retorna um objeto `Route` indicando o próximo passo.

### Função: `router_function(state: AgentState, supervisor_chain)`

*   **Descrição**: Função de roteamento condicional usada pelo LangGraph. Decide o próximo passo com base no estado atual.
*   **Entrada**:
    *   `state`: O estado atual do agente (`AgentState`).
    *   `supervisor_chain`: A cadeia de decisão do supervisor criada por `create_supervisor_chain`.
*   **Processamento**:
    *   Verifica se a última mensagem no `state['messages']` é um `ToolMessage`.
        *   **Se sim**: Significa que uma ferramenta foi executada e o trabalho do agente está completo. Retorna `"FINISH"`.
        *   **Se não**: Invoca a `supervisor_chain` com o estado atual para obter a decisão de roteamento do LLM.
*   **Saída**: Uma string (`"TaskCreator"`, `"ResultAnalyzer"`, ou `"FINISH"`) que determina a próxima transição no grafo.

---

## 4. Agente Criador de Tarefas (`src/agents/task_creator.py`)

Responsável por interagir com as ferramentas do OpenVAS para criar e iniciar novas tarefas de scan.

### Ferramenta: `create_openvas_task(question: str)`

*   **Descrição**: Uma ferramenta decorada com `@tool` que encapsula a lógica de criação e início de uma tarefa OpenVAS.
*   **Entrada**:
    *   `question`: Uma string (geralmente a query original do usuário, embora não diretamente usada pela ferramenta, é um requisito do `tool_node`).
*   **Processamento**:
    *   Instancia `GVMWorkflow` (de `src/tools/gvm_workflow.py`).
    *   Chama o método `run()` do `GVMWorkflow`, que interage com o usuário para obter detalhes da tarefa (nome, alvo, etc.) e executa as operações no OpenVAS.
*   **Saída**: Uma string indicando o sucesso ou falha da execução da ferramenta, incluindo o resultado do `GVMWorkflow.run()`.

### Função: `create_task_creator_node()`

*   **Descrição**: Cria um nó para o grafo que executa a ferramenta `create_openvas_task`.
*   **Entrada**: Nenhuma.
*   **Saída**: Um `functools.partial` que, quando invocado, executa `tool_node` com `create_openvas_task` como a ferramenta a ser rodada.

### Função: `tool_node(state: AgentState, tool_to_run: callable)`

*   **Descrição**: Função genérica para executar qualquer ferramenta dentro de um nó do grafo.
*   **Entrada**:
    *   `state`: O estado atual do agente (`AgentState`).
    *   `tool_to_run`: A função da ferramenta a ser executada (e.g., `create_openvas_task`).
*   **Processamento**:
    *   Extrai a última mensagem do estado para usar como entrada para a ferramenta (embora `create_openvas_task` não a use diretamente, é um padrão para ferramentas).
    *   Invoca a `tool_to_run` com a entrada.
*   **Saída**: Um dicionário `{"messages": [ToolMessage(...)]}` contendo o resultado da execução da ferramenta encapsulado em um `ToolMessage`.

---

## 5. Agente Analisador de Resultados (`src/agents/result_analyzer.py`)

Responsável por buscar e analisar os resultados de scans de vulnerabilidade do OpenVAS.

### Ferramenta: `get_openvas_results(question: str)`

*   **Descrição**: Uma ferramenta decorada com `@tool` que busca e formata os resultados de um scan OpenVAS.
*   **Entrada**:
    *   `question`: Uma string (geralmente a query original do usuário).
*   **Processamento**:
    *   Instancia `ResultManager` (de `src/tools/gvm_results.py`).
    *   Chama `result_manager.result()` para obter os resultados brutos do OpenVAS (XML).
    *   Cria uma mensagem para o LLM (`SystemMessage` e `HumanMessage`) com o contexto dos resultados e a pergunta do usuário.
    *   Chama `get_response_from_openai` para que o LLM analise e formate os resultados.
*   **Saída**: Uma string contendo a análise dos resultados do OpenVAS formatada pelo LLM, ou uma mensagem de erro.

### Função: `get_response_from_openai(message: list[BaseMessage])`

*   **Descrição**: Função auxiliar para invocar o LLM (`ChatOpenAI`) e obter uma resposta.
*   **Entrada**:
    *   `message`: Uma lista de objetos `BaseMessage` (histórico da conversa/prompt).
*   **Saída**: A resposta do LLM (`BaseMessage`).

### Função: `create_result_analyzer_node()`

*   **Descrição**: Cria um nó para o grafo que executa a ferramenta `get_openvas_results`.
*   **Entrada**: Nenhuma.
*   **Saída**: Um `functools.partial` que, quando invocado, executa `tool_node` com `get_openvas_results` como a ferramenta a ser rodada.

### Função: `tool_node(state: AgentState, tool_to_run: callable)`

*   **Descrição**: (Mesma função genérica que em `task_creator.py`) Função genérica para executar qualquer ferramenta dentro de um nó do grafo.
*   **Entrada**:
    *   `state`: O estado atual do agente (`AgentState`).
    *   `tool_to_run`: A função da ferramenta a ser executada (e.g., `get_openvas_results`).
*   **Processamento**:
    *   Extrai a última mensagem do estado para usar como entrada para a ferramenta.
    *   Invoca a `tool_to_run` com a entrada.
*   **Saída**: Um dicionário `{"messages": [ToolMessage(...)]}` contendo o resultado da execução da ferramenta encapsulado em um `ToolMessage`.

---

## 6. Ferramentas de Workflow GVM (`src/tools/gvm_workflow.py`)

Conjunto de classes para gerenciar a conexão, autenticação, alvos, configurações, scanners e tarefas no OpenVAS (GVM).

### Classe: `ConnectionManager`

*   **Descrição**: Gerencia a conexão com o socket Unix do GVM.
*   **Métodos**:
    *   `connect()`:
        *   **Entrada**: Nenhuma (usa `self.path`).
        *   **Saída**: Uma instância de `GMP` (Greenbone Management Protocol).

### Classe: `AuthenticationManager`

*   **Descrição**: Gerencia a autenticação no GVM.
*   **Métodos**:
    *   `authenticate(gmp)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
        *   **Saída**: Nenhuma (autentica a sessão `gmp`).

### Classe: `TargetManager`

*   **Descrição**: Gerencia a criação e seleção de alvos de scan.
*   **Métodos**:
    *   `create_target(gmp)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
            *   **Interação com Usuário**: Solicita `target_name` e `target_host` via `input()`.
            *   **Interação com Usuário**: Solicita a escolha de uma lista de portas via `input()`.
        *   **Saída**: O ID do alvo recém-criado (string).
    *   `get_port_lists(gmp)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
        *   **Saída**: Um dicionário `{nome_lista: id_lista}` das listas de portas disponíveis.
    *   `get_target_id(gmp)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
            *   **Interação com Usuário**: Pergunta se deseja criar um novo alvo (`yes/no`).
            *   **Interação com Usuário**: Se não, solicita o nome exato de um alvo existente.
        *   **Saída**: O ID do alvo selecionado ou recém-criado (string).

### Classe: `ConfigManager`

*   **Descrição**: Gerencia a obtenção de IDs de configuração de scan.
*   **Métodos**:
    *   `get_config_id(gmp)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
        *   **Saída**: O ID da configuração de scan "Full and fast" (string).

### Classe: `ScannerManager`

*   **Descrição**: Gerencia a obtenção de IDs de scanner.
*   **Métodos**:
    *   `get_scanner_id(gmp)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
        *   **Saída**: O ID do scanner "OpenVAS Default" (string).

### Classe: `TaskCreator`

*   **Descrição**: Cria tarefas de scan no GVM.
*   **Métodos**:
    *   `create_task(gmp, name, config_id, target_id, scanner_id)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
            *   `name`: Nome da tarefa (string).
            *   `config_id`: ID da configuração de scan (string).
            *   `target_id`: ID do alvo (string).
            *   `scanner_id`: ID do scanner (string).
        *   **Saída**: O objeto da tarefa criada (XML ElementTree).

### Classe: `TaskManager`

*   **Descrição**: Orquestra a preparação e criação de tarefas.
*   **Métodos**:
    *   `prepare_task(gmp, task_name)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
            *   `task_name`: Nome da tarefa (string).
        *   **Processamento**: Utiliza `TargetManager`, `ConfigManager`, `ScannerManager` para obter os IDs necessários e então chama `TaskCreator.create_task`.
        *   **Saída**: O objeto da tarefa criada (XML ElementTree).

### Classe: `TaskStarter`

*   **Descrição**: Inicia tarefas existentes no GVM.
*   **Métodos**:
    *   `start_task(gmp, task_name)`:
        *   **Entrada**:
            *   `gmp`: Uma instância de `GMP`.
            *   `task_name`: Nome da tarefa a ser iniciada (string).
        *   **Saída**: O objeto de resposta da operação de início da tarefa (XML ElementTree).

### Classe: `GVMWorkflow`

*   **Descrição**: Classe principal que orquestra todo o fluxo de criação e início de uma tarefa OpenVAS.
*   **Métodos**:
    *   `run()`:
        *   **Entrada**: Nenhuma.
        *   **Processamento**:
            *   Estabelece conexão e autentica.
            *   **Interação com Usuário**: Solicita o nome da tarefa via `input()`.
            *   Chama `task_manager.prepare_task` para criar a tarefa.
            *   Chama `task_starter.start_task` para iniciar a tarefa.
        *   **Saída**: Imprime mensagens de sucesso/erro no console.

---

## 7. Ferramentas de Resultados GVM (`src/tools/gvm_results.py`)

Gerencia a obtenção e processamento de resultados de scans do OpenVAS.

### Classe: `ResultManager`

*   **Descrição**: Gerencia a busca de resultados de scans do OpenVAS.
*   **Métodos**:
    *   `result()`:
        *   **Entrada**: Nenhuma.
        *   **Processamento**:
            *   Autentica no GVM.
            *   **Interação com Usuário**: Solicita o nome da tarefa para buscar resultados via `input()`.
            *   Verifica o status da tarefa.
            *   Busca os resultados do scan usando `gmp.get_results`.
            *   Converte o XML dos resultados para string.
        *   **Saída**: Uma string XML contendo os resultados do scan, ou `None` se a tarefa não for encontrada/concluída ou ocorrer um erro.

---

## 8. Arte ASCII (`src/art/art.py`)

Módulo para exibir arte ASCII no início da aplicação.

### Função: `art_generation(texto, font='standard')`

*   **Descrição**: Gera arte ASCII a partir de um texto usando a biblioteca `pyfiglet`.
*   **Entrada**:
    *   `texto`: A string a ser convertida em arte ASCII.
    *   `font`: A fonte `pyfiglet` a ser usada (padrão: 'standard').
*   **Saída**: Uma string contendo a arte ASCII gerada.

### Função: `art_main()`

*   **Descrição**: Função principal para exibir a arte ASCII e uma descrição do projeto no console.
*   **Entrada**: Nenhuma.
*   **Saída**: Imprime a arte ASCII colorida e a descrição do projeto no console.

---

## 9. Fluxo de Execução da Aplicação

O fluxo da aplicação é orquestrado pelo `main.py` usando o LangGraph, que gerencia a interação entre o usuário e os agentes.

### 9.1. Início da Aplicação

1.  **`main.py` é executado.**
2.  **`art_main()`** (de `src/art/art.py`) é chamada.
    *   **Entrada**: Nenhuma.
    *   **Processamento**: Gera e imprime a arte ASCII "OPENVAS AGENT" e uma descrição do projeto no console.
    *   **Saída**: Exibição visual no console.

### 9.2. Loop de Interação Principal

1.  O programa entra em um loop infinito (`while True`).
2.  **Entrada do Usuário**: O usuário é solicitado a digitar uma `query` via `input()`.
    *   **Entrada Esperada**: Uma string contendo a intenção do usuário (e.g., "criar um scan", "analisar resultados").
    *   **Saída**: A string digitada pelo usuário.
3.  **Verificação de Saída**: Se a `query` for "q", "exit", "quit" ou "sair", o loop é encerrado.
4.  **Inicialização do Estado**: Um `initial_state` é criado com a `query` do usuário como uma `HumanMessage`.
5.  **Invocação do Grafo**: O `graph.invoke(initial_state)` é chamado. Este é o coração do fluxo.

### 9.3. Fluxo Dentro do Grafo (LangGraph)

O grafo, definido em `main.py`, segue a seguinte lógica:

1.  **Ponto de Entrada: `supervisor`**.
    *   O nó `supervisor` é o primeiro a ser ativado.
    *   Ele chama a função `router_function` (de `src/agents/supervisor.py`).
    *   **Entrada para `router_function`**: O `AgentState` atual (contendo a `HumanMessage` inicial do usuário).
    *   **Processamento em `router_function`**:
        *   Verifica se a última mensagem é um `ToolMessage`. No início, não é.
        *   Invoca a `supervisor_chain` (uma cadeia LangChain que usa o LLM).
        *   **Entrada para `supervisor_chain`**: O `AgentState` (especificamente as mensagens).
        *   **Processamento na `supervisor_chain`**: O LLM analisa a `query` do usuário e decide o próximo passo com base nas regras definidas no `system_prompt_supervisor`.
        *   **Saída da `supervisor_chain`**: Um objeto `Route` com o atributo `next` sendo `"TaskCreator"`, `"ResultAnalyzer"`, ou `"FINISH"`.
    *   **Saída de `router_function`**: A string de roteamento (`"TaskCreator"`, `"ResultAnalyzer"`, ou `"FINISH"`).

2.  **Roteamento Condicional**:
    *   **Se `router_function` retorna `"TaskCreator"`**:
        *   O controle é passado para o nó `TaskCreator`.
        *   O nó `TaskCreator` executa a função `tool_node` (de `src/agents/task_creator.py`) com a ferramenta `create_openvas_task`.
        *   **Entrada para `create_openvas_task`**: A `query` original do usuário.
        *   **Processamento em `create_openvas_task`**:
            *   Instancia `GVMWorkflow` (de `src/tools/gvm_workflow.py`).
            *   Chama `workflow.run()`.
            *   **Interação com Usuário (dentro de `GVMWorkflow.run()`):**
                *   Solicita "Type a name for the task: "
                *   Solicita "Do you want to create a new target? (yes/no): "
                *   Se "yes":
                    *   Solicita "Type a name for the target: "
                    *   Solicita "Type a host for the target: "
                    *   Exibe "Available Port Lists:" e solicita "Enter the number of the port list you want to use: "
                *   Se "no":
                    *   Exibe "Existing Targets:" e solicita "Type the exact name of the target you want to use: "
            *   **Saída de `create_openvas_task`**: Uma string de sucesso/erro da execução da ferramenta.
        *   **Saída do nó `TaskCreator`**: Um `ToolMessage` contendo o resultado da execução da ferramenta.
        *   **Próximo passo**: O controle retorna para o nó `supervisor`.

    *   **Se `router_function` retorna `"ResultAnalyzer"`**:
        *   O controle é passado para o nó `ResultAnalyzer`.
        *   O nó `ResultAnalyzer` executa a função `tool_node` (de `src/agents/result_analyzer.py`) com a ferramenta `get_openvas_results`.
        *   **Entrada para `get_openvas_results`**: A `query` original do usuário.
        *   **Processamento em `get_openvas_results`**:
            *   Instancia `ResultManager` (de `src/tools/gvm_results.py`).
            *   Chama `result_manager.result()`.
            *   **Interação com Usuário (dentro de `ResultManager.result()`):**
                *   Solicita "Type a word or the task name: "
            *   **Saída de `result_manager.result()`**: Uma string XML com os resultados do OpenVAS ou `None`.
            *   Chama `get_response_from_openai` para que o LLM analise e formate os resultados.
            *   **Entrada para `get_response_from_openai`**: `SystemMessage` com o template de vulnerabilidade e `HumanMessage` com os resultados XML e a `question` do usuário.
            *   **Saída de `get_response_from_openai`**: A análise formatada do LLM.
        *   **Saída do nó `ResultAnalyzer`**: Um `ToolMessage` contendo a análise formatada.
        *   **Próximo passo**: O controle retorna para o nó `supervisor`.

    *   **Se `router_function` retorna `"FINISH"`**:
        *   O grafo termina a execução.

3.  **Retorno ao Supervisor (após execução de `TaskCreator` ou `ResultAnalyzer`)**:
    *   Quando o controle retorna ao `supervisor` após a execução de um agente, a última mensagem no `AgentState` será um `ToolMessage`.
    *   A `router_function` é chamada novamente.
    *   **Processamento em `router_function`**: Detecta o `ToolMessage` e retorna `"FINISH"`.
    *   **Saída de `router_function`**: `"FINISH"`.
    *   O grafo termina a execução.

### 9.4. Saída Final da Aplicação

1.  Após o grafo terminar (`graph.invoke` retorna), o `final_state` é obtido.
2.  A `final_message` é extraída do `final_state['messages'][-1]`.
3.  O `final_message.content` é impresso para o usuário.
    *   **Saída Esperada**: Uma string contendo o resultado final da operação (sucesso da criação da tarefa, análise de vulnerabilidades, ou uma mensagem de erro/informação).

---