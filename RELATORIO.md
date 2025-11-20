# Relatório do Trabalho - Simulador de Controle de Concorrência

**Disciplina:** Banco de Dados  
**Tema:** Protocolo de Timestamps (Marcadores de Tempo)  
**Data:** Novembro de 2025

---

## 1. Descrição do Trabalho Realizado

Este trabalho implementa um **simulador de escalonador de transações** utilizando o **Protocolo de Timestamps** para controle de concorrência em bancos de dados. O simulador permite visualizar, passo a passo, como o escalonador decide se cada operação pode ser executada ou se a transação deve ser abortada.

---

## 2. Características Implementadas

### ✅ Características Implementadas

#### 2.1 Protocolo de Timestamps Completo
- **Atribuição de Timestamps:** Cada transação recebe um timestamp único na sua primeira operação
- **Controle de Leitura (Read):** Verifica se `TS(Ti) >= WTS(X)` antes de executar
- **Controle de Escrita (Write):** Verifica se `TS(Ti) >= RTS(X)` e `TS(Ti) >= WTS(X)` antes de executar
- **Atualização de RTS/WTS:** Atualiza os timestamps dos itens de dados após operações bem-sucedidas

#### 2.2 Gerenciamento de Transações
- **Criação automática** de transações ao encontrar primeira operação
- **Operações suportadas:** Leitura `r`, Escrita `w`, Commit `c`
- **Status das transações:** Ativa, Committed, Abortada
- **Rastreamento de operações** executadas por cada transação

#### 2.3 Tratamento de Abortos e Re-execução Automática
- **Detecção de conflitos:** Identifica quando operação viola regras do protocolo
- **Remoção da HF:** Remove todas as operações da transação abortada da História Final
- **Recálculo de timestamps:** Recalcula RTS e WTS dos itens de dados após aborto
- **Re-agendamento automático:** Operações da transação abortada são automaticamente adicionadas ao final da HI
- **Reinício com novo timestamp:** Transação é recriada com timestamp mais recente ao ser re-executada
- **Rastreamento de operações:** Sistema mantém mapa das operações originais de cada transação para garantir re-execução completa

#### 2.4 Interface Visual Interativa
- **História Inicial (HI):** Exibe a sequência de operações a serem processadas
- **História Final (HF):** Mostra operações que foram executadas com sucesso
- **Estado dos Dados:** Exibe RTS e WTS de cada item de dado
- **Estado das Transações:** Mostra timestamp e status de cada transação
- **Log de Mensagens:** Exibe detalhes do processamento de cada operação
- **Barra de Progresso:** Indica quantos passos foram executados

#### 2.5 Modos de Execução
- **Passo a Passo:** Executa uma operação por vez com botão "Próximo Passo"
- **Execução Automática:** Executa todas as operações automaticamente com intervalo de 1.5s
- **Pausa:** Permite pausar a execução automática
- **Reset:** Reinicia a simulação do zero

#### 2.6 Cenários Pré-Definidos
O simulador inclui 5 cenários de teste:
1. **Execução Serial Simples:** Sem conflitos
2. **Conflito Leitura/Escrita:** T1 é abortada
3. **Conflito de Escrita:** T2 é abortada por T3
4. **Conflito Complexo:** T1 tenta escrever após T3
5. **Múltiplos Itens de Dados:** Operações em X e Y

#### 2.7 Cenários Personalizados
- **Interface para criar cenários:** Usuário pode adicionar seus próprios cenários
- **Validação de operações:** Verifica se operações estão no formato correto
- **Exemplos integrados:** Modal com exemplos de como criar operações

### ❌ Características NÃO Implementadas

- **Persistência em banco de dados real:** Os dados são simulados em memória (conforme permitido na especificação)
- **Otimização Thomas Write Rule:** Não implementada (apenas protocolo básico)
- **Multiprogramação real:** É uma simulação visual, não há execução paralela real de threads
- **Recuperação de falhas:** Não trata falhas de sistema ou disco

---

## 3. Entrada de Dados

### 3.1 Formato das Operações

As operações seguem o formato padrão usado em aula:

#### Operação de Leitura
```
r<id_transacao>(<item_dado>)
Exemplos: r1(x), r2(y), r3(z)
```

#### Operação de Escrita
```
w<id_transacao>(<item_dado>)
Exemplos: w1(x), w2(y), w3(z)
```

#### Operação de Commit
```
c<id_transacao>
Exemplos: c1, c2, c3
```

### 3.2 Como Informar a História Inicial (HI)

**Opção 1: Cenários Pré-Definidos**
- Selecionar no dropdown "Selecione um Cenário"
- Clicar em "Iniciar Simulação"

**Opção 2: Cenário Personalizado**
- Preencher o campo "Nome do Cenário"
- Digitar as operações separadas por vírgula ou espaço
  - Exemplo: `r1(x), w1(x), r2(x), w2(x), c1, c2`
- Clicar em "Adicionar Cenário"
- Selecionar o cenário criado no dropdown
- Clicar em "Iniciar Simulação"

### 3.3 Validações

O sistema valida automaticamente:
- ✅ Formato correto das operações
- ✅ IDs de transações são números
- ✅ Itens de dados são letras minúsculas
- ❌ Rejeita operações malformadas com mensagem de erro

---

## 4. Saída de Dados

### 4.1 História Final (HF)

**Visualização em Timeline:**
- Sequência horizontal de operações executadas
- Mostra apenas operações que passaram no protocolo
- Operações de transações abortadas são removidas

**Exemplo de HF:**
```
r1(x) → w1(x) → r2(x) → c1 → w2(x) → c2
```

### 4.2 Estado dos Itens de Dados

Para cada item de dado (x, y, z, etc.), exibe:
- **RTS (Read Timestamp):** Timestamp da última leitura bem-sucedida
- **WTS (Write Timestamp):** Timestamp da última escrita bem-sucedida

**Exemplo:**
```
X: RTS=2, WTS=1
Y: RTS=3, WTS=3
```

### 4.3 Estado das Transações

Para cada transação, exibe:
- **ID da transação:** T1, T2, T3, etc.
- **Timestamp (TS):** Timestamp atribuído à transação
- **Status:** ATIVA, COMMITTED ou ABORTADA

**Exemplo:**
```
T1: TS=1, Status=COMMITTED
T2: TS=2, Status=ATIVA
```

### 4.4 Log de Mensagens

Mensagens detalhadas do processamento:

**Tipos de mensagens:**
- 🆕 **INFO (azul):** Criação de transação, carregamento de cenário
- 🔍 **INFO (azul):** Verificação de operação com valores de TS/RTS/WTS
- ✅ **SUCCESS (verde):** Operação executada com sucesso
- ❌ **ERROR (vermelho):** Operação rejeitada, transação abortada
- ⚠️ **WARNING (amarelo):** Transação será reiniciada, operações ignoradas

**Exemplo de sequência:**
```
🆕 Nova transação T1 criada com TS=1
🔍 Verificando r1(x): TS(T1)=1, RTS(x)=0, WTS(x)=0
✅ r1(x) executado: RTS(x) atualizado para 1
```

### 4.5 Informações de Progresso

- **Passo Atual:** Mostra qual operação está sendo processada (ex: "Passo 3/8")
- **Operação Atual:** Exibe a próxima operação a ser executada
- **Barra de Progresso:** Indicador visual de quantos % foi completado

---

## 5. Estruturas de Dados

### 5.1 Estado Global da Simulação

```javascript
estadoAtual = {
    transacoes: {},              // Mapa de transações ativas
    itens_dados: {},             // Mapa de itens de dados
    hf: [],                      // História Final (array de strings)
    hi: [],                      // História Inicial (array de strings)
    passo_atual: 0,              // Índice da operação atual
    timestamp_atual: 0,          // Contador global de timestamps
    transacoes_abortadas: []     // Lista de IDs de transações abortadas
}
```

### 5.2 Estrutura de Transação

```javascript
transacao = {
    id: number,                  // ID da transação (ex: 1 para T1)
    timestamp: number,           // TS atribuído à transação
    status: string,              // 'ativa', 'committed' ou 'abortada'
    operacoes: []                // Array de operações executadas
}
```

### 5.3 Estrutura de Item de Dado

```javascript
itemDado = {
    nome: string,                // Nome do item (ex: 'x', 'y', 'z')
    rts: number,                 // Read Timestamp
    wts: number                  // Write Timestamp
}
```

### 5.4 Estrutura de Operação

```javascript
operacao = {
    tipo: string,                // 'leitura', 'escrita' ou 'commit'
    id_transacao: number,        // ID da transação
    item_dado: string,           // Nome do item (null para commit)
    string: string               // Representação original (ex: 'r1(x)')
}
```

### 5.5 Estrutura de Cenário

```javascript
cenario = {
    nome: string,                // Nome descritivo do cenário
    operacoes: []                // Array de strings de operações
}
```

---

## 6. Algoritmo do Protocolo de Timestamps

### 6.1 Fluxo Principal

```
1. Receber operação da HI
2. Analisar operação (tipo, transação, item)
3. Obter ou criar transação (atribui TS na primeira vez)
4. Obter ou criar item de dado

5. Se for LEITURA:
   - TS(Ti) < WTS(X)? → ABORTAR
   - Senão → EXECUTAR e RTS(X) = max(RTS(X), TS(Ti))

6. Se for ESCRITA:
   - TS(Ti) < RTS(X)? → ABORTAR
   - TS(Ti) < WTS(X)? → ABORTAR
   - Senão → EXECUTAR e WTS(X) = TS(Ti)

7. Se for COMMIT:
   - Marcar transação como committed

8. Se EXECUTOU: adicionar à HF
9. Se ABORTOU: remover operações da HF e recalcular RTS/WTS
```

### 6.2 Regras do Protocolo Implementadas

#### Regra de Leitura (Read Rule)
```
SE TS(Ti) < WTS(X) ENTÃO
    ABORTAR Ti
SENÃO
    EXECUTAR ri(X)
    RTS(X) = max(RTS(X), TS(Ti))
FIM SE
```

#### Regra de Escrita (Write Rule)
```
SE TS(Ti) < RTS(X) ENTÃO
    ABORTAR Ti
SENÃO SE TS(Ti) < WTS(X) ENTÃO
    ABORTAR Ti
SENÃO
    EXECUTAR wi(X)
    WTS(X) = TS(Ti)
FIM SE
```

#### Procedimento de Aborto
```
1. Remover todas as operações de Ti da HF
2. Marcar Ti como abortada
3. Remover Ti do conjunto de transações ativas
4. Recalcular RTS e WTS de todos os itens baseado na HF atual
5. Ti poderá reiniciar com novo TS quando aparecer novamente na HI
```

---

## 7. Tecnologias Utilizadas

- **HTML5:** Estrutura da interface
- **CSS3:** Estilização e responsividade
- **JavaScript (ES6+):** Lógica do simulador
- **Nenhuma biblioteca externa:**

---

## 8. Como Executar

### 8.1 Requisitos
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Nenhuma instalação necessária

### 8.2 Passos para Execução
1. Abrir o arquivo `visualizador.html` no navegador
2. Selecionar um cenário ou criar um personalizado
3. Clicar em "Iniciar Simulação"
4. Usar "Próximo Passo" ou "⚡ Auto" para executar

### 8.3 Estrutura de Arquivos
```
Trabalho_Banco/
├── visualizador.html    # Interface principal
├── script.js            # Lógica do simulador
├── styles.css           # Estilização
├── main.py              # Versão Python (opcional)
└── RELATORIO.md         # Este relatório
```

---

## 9. Exemplos de Execução

### Exemplo 1: Execução Serial (Sem Conflitos)

**HI:** `r1(x), w1(x), c1, r2(x), c2`

**Processamento:**
1. `r1(x)` → T1 criada com TS=1, RTS(x)=1, executa
2. `w1(x)` → WTS(x)=1, executa
3. `c1` → T1 committed
4. `r2(x)` → T2 criada com TS=2, RTS(x)=2, executa
5. `c2` → T2 committed

**HF:** `r1(x) w1(x) c1 r2(x) c2`

### Exemplo 2: Conflito de Leitura/Escrita (Com Re-execução Automática)

**HI Inicial:** `r1(y), r2(y), w1(y), c2, c1`

**Processamento:**
1. `r1(y)` → T1 criada com TS=1, RTS(y)=1, executa
2. `r2(y)` → T2 criada com TS=2, RTS(y)=2, executa
3. `w1(y)` → ❌ ABORTAR: TS(1) < RTS(2), T1 abortada
   - Remove `r1(y)` da HF
   - Remove `w1(y)` e `c1` da HI (operações não processadas)
   - Adiciona `r1(y), w1(y), c1` ao final da HI
   - **Nova HI:** `r1(y), r2(y), w1(y), c2, c1, r1(y), w1(y), c1`
4. `c2` → T2 committed
5. `c1` → ⏭️ Ignorado (T1 não existe mais)
6. `r1(y)` → T1 recriada com TS=3, RTS(y)=3, executa
7. `w1(y)` → ✅ TS(3) >= RTS(3), WTS(y)=3, executa
8. `c1` → T1 committed

**HF Final:** `r2(y), c2, r1(y), w1(y), c1`

### Exemplo 3: Conflito de Escrita (Com Re-execução Automática)

**HI Inicial:** `w1(z), r2(z), w3(z), w2(z), c1, c3, c2`

**Processamento:**
1. `w1(z)` → T1 criada com TS=1, WTS(z)=1, executa
2. `r2(z)` → T2 criada com TS=2, RTS(z)=2, executa
3. `w3(z)` → T3 criada com TS=3, WTS(z)=3, executa
4. `w2(z)` → ❌ ABORTAR: TS(2) < WTS(3), T2 abortada
   - Remove `r2(z)` da HF
   - Remove `w2(z)` e `c2` da HI (operações não processadas)
   - Adiciona `r2(z), w2(z), c2` ao final da HI
   - **Nova HI:** `w1(z), r2(z), w3(z), w2(z), c1, c3, c2, r2(z), w2(z), c2`
5. `c1` → T1 committed
6. `c3` → T3 committed
7. `c2` → ⏭️ Ignorado (T2 não existe mais)
8. `r2(z)` → T2 recriada com TS=4, RTS(z)=4, executa
9. `w2(z)` → ✅ TS(4) >= RTS(4) e TS(4) >= WTS(3), WTS(z)=4, executa
10. `c2` → T2 committed

**HF Final:** `w1(z), w3(z), c1, c3, r2(z), w2(z), c2`

---

## 10. Conclusão

O simulador implementado atende completamente aos requisitos do trabalho, fornecendo uma visualização clara e interativa do funcionamento do Protocolo de Timestamps. A interface permite compreender:

- ✅ Como timestamps são atribuídos às transações
- ✅ Quando operações são aceitas ou rejeitadas
- ✅ Como abortos afetam a História Final
- ✅ Como transações são reiniciadas após aborto
- ✅ O estado dos itens de dados em cada momento

A implementação é didática, robusta e facilita o entendimento do protocolo de controle de concorrência por timestamps.

---

## 11. Referências

- Slides e material da disciplina de Banco de Dados
- SILBERSCHATZ, A.; KORTH, H. F.; SUDARSHAN, S. **Sistema de Banco de Dados**. 6ª ed.
- ELMASRI, R.; NAVATHE, S. B. **Sistemas de Banco de Dados**. 7ª ed.

---

**Trabalho desenvolvido por:** Lucas Schiochet 
**Data de entrega:** Novembro de 2025
