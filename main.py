"""
Simulador de Controle de Concorrência usando Protocolo de Timestamps
Implementação conforme especificação do trabalho de Banco de Dados

FUNCIONAMENTO:
- Recebe uma História Inicial (HI) com operações de transações
- Aplica o Protocolo de Timestamps para controle de concorrência
- Gera a História Final (HF) com as operações que foram executadas
- Aborta transações quando necessário e permite reinício com novo timestamp
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TipoOperacao(Enum):
    """Tipos de operações suportadas no escalonador"""
    LEITURA = "r"   # Operação de leitura (read)
    ESCRITA = "w"   # Operação de escrita (write)
    COMMIT = "c"    # Operação de commit


@dataclass
class Operacao:
    """
    Representa uma operação individual na história
    
    Atributos:
        id_transacao: Identificador da transação (ex: 1 para T1)
        tipo_op: Tipo da operação (LEITURA, ESCRITA ou COMMIT)
        item_dado: Nome do item de dado (ex: 'x', 'y') - None para commit
    """
    id_transacao: int
    tipo_op: TipoOperacao
    item_dado: Optional[str] = None  # None para operações de commit
    
    def __str__(self):
        """Retorna representação em string da operação (ex: r1(x), w2(y), c3)"""
        if self.tipo_op == TipoOperacao.COMMIT:
            return f"c{self.id_transacao}"
        else:
            return f"{self.tipo_op.value}{self.id_transacao}({self.item_dado})"


class ItemDado:
    """
    Representa um item de dado com seus timestamps de controle
    
    Atributos:
        nome: Identificador do item (ex: 'x', 'y', 'z')
        rts: Read Timestamp - timestamp da última leitura bem-sucedida
        wts: Write Timestamp - timestamp da última escrita bem-sucedida
        valor: Valor armazenado (simulado, não usado na lógica)
    """
    def __init__(self, nome: str):
        self.nome = nome
        self.rts = 0  # Read Timestamp - inicialmente 0
        self.wts = 0  # Write Timestamp - inicialmente 0
        self.valor = None  # Valor simulado do dado
    
    def __str__(self):
        """Retorna string com o estado do item (ex: x[RTS=2, WTS=1])"""
        return f"{self.nome}[RTS={self.rts}, WTS={self.wts}]"


class Transacao:
    """
    Representa uma transação no sistema
    
    Atributos:
        id: Identificador da transação
        timestamp: Timestamp atribuído quando a transação inicia
        operacoes_na_hf: Lista de operações que foram adicionadas à HF
        abortada: Flag indicando se a transação foi abortada
        confirmada: Flag indicando se a transação foi confirmada (commit)
    """
    def __init__(self, id_transacao: int, timestamp: int):
        self.id = id_transacao
        self.timestamp = timestamp
        self.operacoes_na_hf: List[Operacao] = []
        self.abortada = False
        self.confirmada = False
    
    def __str__(self):
        """Retorna string com informações da transação (ex: T1(TS=3))"""
        return f"T{self.id}(TS={self.timestamp})"


class EscalonadorTimestamp:
    """
    Escalonador baseado no Protocolo de Timestamps
    
    Gerencia a execução de operações seguindo as regras:
    - Para LEITURA: TS(Ti) >= WTS(X) para executar
    - Para ESCRITA: TS(Ti) >= RTS(X) E TS(Ti) >= WTS(X) para executar
    - Se não pode executar, aborta a transação
    """
    
    def __init__(self):
        """Inicializa o escalonador com estruturas vazias"""
        self.transacoes: Dict[int, Transacao] = {}  # Transações ativas
        self.itens_dados: Dict[str, ItemDado] = {}  # Itens de dados do BD
        self.timestamp_atual = 0  # Contador de timestamps
        self.hf: List[Operacao] = []  # História Final (HF)
        self.transacoes_abortadas: List[int] = []  # Rastreamento de abortos
        
    def obter_ou_criar_item_dado(self, nome: str) -> ItemDado:
        """
        Obtém um item de dado existente ou cria um novo
        
        Args:
            nome: Nome do item de dado (ex: 'x', 'y', 'z')
            
        Returns:
            ItemDado correspondente ao nome
        """
        if nome not in self.itens_dados:
            self.itens_dados[nome] = ItemDado(nome)
        return self.itens_dados[nome]
    
    def obter_ou_criar_transacao(self, id_transacao: int) -> Transacao:
        """
        Obtém uma transação existente ou cria uma nova com timestamp atual
        
        O timestamp é atribuído na PRIMEIRA operação da transação.
        Se a transação foi abortada anteriormente, recebe um novo timestamp.
        
        Args:
            id_transacao: ID da transação (ex: 1 para T1)
            
        Returns:
            Transacao correspondente ao ID
        """
        if id_transacao not in self.transacoes:
            # Incrementa timestamp global e atribui à nova transação
            self.timestamp_atual += 1
            self.transacoes[id_transacao] = Transacao(id_transacao, self.timestamp_atual)
            print(f"  → Nova transação T{id_transacao} criada com TS={self.timestamp_atual}")
        return self.transacoes[id_transacao]
    
    def processar_leitura(self, operacao: Operacao) -> bool:
        """
        Processa operação de LEITURA seguindo o protocolo de timestamps
        
        REGRA: TS(Ti) < WTS(X)? 
            - SIM: Abortar Ti (tentando ler valor muito antigo)
            - NÃO: Executar e atualizar RTS(X) = max(RTS(X), TS(Ti))
        
        Args:
            operacao: Operação de leitura a ser processada
            
        Returns:
            True se a operação pode ser executada
            False se a transação deve ser abortada
        """
        transacao = self.obter_ou_criar_transacao(operacao.id_transacao)
        item_dado = self.obter_ou_criar_item_dado(operacao.item_dado)
        
        ts = transacao.timestamp
        
        print(f"  → Verificando {operacao}: TS(T{transacao.id})={ts}, {item_dado}")
        
        # REGRA DE LEITURA: TS(Ti) < WTS(X) => Abortar
        # Significa que a transação tenta ler um valor que já foi sobrescrito
        # por uma transação mais recente
        if ts < item_dado.wts:
            print(f"  ✗ ABORTAR: TS({ts}) < WTS({item_dado.wts}) - Leitura muito antiga!")
            return False
        
        # Pode executar a leitura
        # Atualiza RTS(X) para o máximo entre o valor atual e o TS da transação
        if ts > item_dado.rts:
            item_dado.rts = ts
            print(f"  ✓ Executar: RTS({item_dado.nome}) atualizado para {item_dado.rts}")
        else:
            print(f"  ✓ Executar: RTS({item_dado.nome}) mantido em {item_dado.rts}")
        
        return True
    
    def processar_escrita(self, operacao: Operacao) -> bool:
        """
        Processa operação de ESCRITA seguindo o protocolo de timestamps
        
        REGRAS:
        1. TS(Ti) < RTS(X)? Abortar (tentando escrever valor que já foi lido por transação mais nova)
        2. TS(Ti) < WTS(X)? Abortar (tentando escrever valor muito antigo)
        3. Caso contrário: Executar e atualizar WTS(X) = TS(Ti)
        
        Args:
            operacao: Operação de escrita a ser processada
            
        Returns:
            True se a operação pode ser executada
            False se a transação deve ser abortada
        """
        transacao = self.obter_ou_criar_transacao(operacao.id_transacao)
        item_dado = self.obter_ou_criar_item_dado(operacao.item_dado)
        
        ts = transacao.timestamp
        
        print(f"  → Verificando {operacao}: TS(T{transacao.id})={ts}, {item_dado}")
        
        # REGRA 1 DE ESCRITA: TS(Ti) < RTS(X) => Abortar
        # Significa que uma transação mais recente já leu o valor antigo
        # Se permitir esta escrita, violaria a ordem de serialização
        if ts < item_dado.rts:
            print(f"  ✗ ABORTAR: TS({ts}) < RTS({item_dado.rts}) - Escrita muito antiga!")
            return False
        
        # REGRA 2 DE ESCRITA: TS(Ti) < WTS(X) => Abortar
        # Significa que uma transação mais recente já escreveu neste item
        # Esta escrita seria sobrescrita, então deve ser abortada
        if ts < item_dado.wts:
            print(f"  ✗ ABORTAR: TS({ts}) < WTS({item_dado.wts}) - Escrita muito antiga!")
            return False
        
        # Pode executar a escrita
        # Atualiza WTS(X) com o timestamp da transação
        item_dado.wts = ts
        print(f"  ✓ Executar: WTS({item_dado.nome}) atualizado para {item_dado.wts}")
        
        return True
    
    def abortar_transacao(self, id_transacao: int):
        """
        Aborta uma transação e remove todas suas operações da História Final (HF)
        
        Quando uma transação é abortada:
        1. Remove todas suas operações já adicionadas à HF
        2. Marca a transação como abortada
        3. Remove a transação do dicionário (permite reinício com novo TS)
        4. Registra o aborto para estatísticas
        
        Args:
            id_transacao: ID da transação a ser abortada
        """
        transacao = self.transacoes[id_transacao]
        
        print(f"\n  ⚠️  ABORTANDO T{id_transacao}...")
        
        # Encontrar todas as operações desta transação que já estão na HF
        operacoes_para_remover = [op for op in self.hf if op.id_transacao == id_transacao]
        
        if operacoes_para_remover:
            print(f"  → Removendo {len(operacoes_para_remover)} operação(ões) de T{id_transacao} da HF:")
            for op in operacoes_para_remover:
                print(f"    - {op}")
                self.hf.remove(op)
        
        # Marcar transação como abortada
        transacao.abortada = True
        transacao.operacoes_na_hf.clear()
        
        # Remover a transação do dicionário para que possa ser reiniciada
        # com um novo timestamp quando aparecer novamente na HI
        del self.transacoes[id_transacao]
        self.transacoes_abortadas.append(id_transacao)
        
        print(f"  → T{id_transacao} será reiniciada posteriormente com novo timestamp\n")
    
    def processar_commit(self, operacao: Operacao) -> bool:
        """
        Processa operação de COMMIT
        
        Marca a transação como confirmada. Todas as suas operações
        já executadas são permanentemente adicionadas à HF.
        
        Args:
            operacao: Operação de commit
            
        Returns:
            True (commit sempre pode ser executado se chegou até aqui)
        """
        transacao = self.obter_ou_criar_transacao(operacao.id_transacao)
        
        print(f"  → Commit de T{transacao.id}")
        transacao.confirmada = True
        print(f"  ✓ T{transacao.id} confirmada com sucesso")
        
        return True
    
    def escalonar_operacao(self, operacao: Operacao) -> bool:
        """
        Escalona (tenta executar) uma operação da História Inicial
        
        Fluxo:
        1. Verifica se a transação já foi abortada
        2. Aplica as regras do protocolo de timestamps
        3. Se pode executar: adiciona à HF
        4. Se não pode executar: aborta a transação
        
        Args:
            operacao: Operação a ser escalonada
            
        Returns:
            True se a operação foi executada
            False se a transação foi abortada
        """
        print(f"\n📌 Processando operação: {operacao}")
        
        # Verificar se a transação já foi abortada (não processar operações de transação morta)
        transacao = self.transacoes.get(operacao.id_transacao)
        if transacao and transacao.abortada:
            print(f"  → T{operacao.id_transacao} já foi abortada, ignorando operação")
            return False
        
        pode_executar = False
        
        # Aplicar regras específicas de cada tipo de operação
        if operacao.tipo_op == TipoOperacao.LEITURA:
            pode_executar = self.processar_leitura(operacao)
        elif operacao.tipo_op == TipoOperacao.ESCRITA:
            pode_executar = self.processar_escrita(operacao)
        elif operacao.tipo_op == TipoOperacao.COMMIT:
            pode_executar = self.processar_commit(operacao)
        
        if pode_executar:
            # Operação aceita: adicionar à História Final
            self.hf.append(operacao)
            transacao = self.transacoes[operacao.id_transacao]
            transacao.operacoes_na_hf.append(operacao)
            print(f"  ➕ Adicionado à HF: {operacao}")
            return True
        else:
            # Operação rejeitada: abortar toda a transação
            self.abortar_transacao(operacao.id_transacao)
            return False
    
    def executar_historia(self, hi: List[Operacao]):
        """
        Executa a História Inicial (HI) completa, operação por operação
        
        Para cada operação na HI:
        - Tenta escalonar a operação
        - Exibe o estado atual do sistema
        - Continua até processar todas as operações
        
        Args:
            hi: Lista de operações da História Inicial
        """
        print("="*70)
        print("INICIANDO EXECUÇÃO DA HISTÓRIA INICIAL (HI)")
        print("="*70)
        
        # Processar cada operação sequencialmente
        for i, operacao in enumerate(hi, 1):
            print(f"\n{'─'*70}")
            print(f"Passo {i}/{len(hi)}")
            self.escalonar_operacao(operacao)
            self.imprimir_estado_atual()
        
        print("\n" + "="*70)
        print("EXECUÇÃO COMPLETA")
        print("="*70)
    
    def imprimir_estado_atual(self):
        """
        Imprime o estado atual do sistema:
        - História Final até o momento
        - Estado dos itens de dados (RTS e WTS)
        """
        print(f"\n  📊 Estado atual:")
        print(f"  HF até agora: {' '.join(str(op) for op in self.hf) if self.hf else '(vazia)'}")
        
        if self.itens_dados:
            print(f"  Itens de dados:")
            for nome, item in sorted(self.itens_dados.items()):
                print(f"    {item}")
    
    def imprimir_historia_final(self):
        """
        Imprime um relatório completo da execução:
        - Sequência final de operações (HF)
        - Estado final dos itens de dados
        - Status das transações
        - Estatísticas de abortos
        """
        print("\n" + "="*70)
        print("HISTÓRIA FINAL (HF)")
        print("="*70)
        
        if not self.hf:
            print("HF está vazia!")
            return
        
        # Exibir sequência de operações que foram executadas
        print("\nSequência de operações executadas:")
        for i, op in enumerate(self.hf, 1):
            print(f"  {i:2d}. {op}")
        
        # Exibir estado final de cada item de dado
        print("\n" + "-"*70)
        print("Estado final dos itens de dados:")
        for nome, item in sorted(self.itens_dados.items()):
            print(f"  {item}")
        
        # Exibir informações sobre as transações
        print("\n" + "-"*70)
        print("Transações:")
        for tid, trans in sorted(self.transacoes.items()):
            status = "COMMITTED" if trans.confirmada else "ACTIVE"
            print(f"  T{tid}: TS={trans.timestamp}, Status={status}")
        
        # Exibir estatísticas de abortos
        if self.transacoes_abortadas:
            contagem_abortos = {}
            for tid in self.transacoes_abortadas:
                contagem_abortos[tid] = contagem_abortos.get(tid, 0) + 1
            
            print("\n" + "-"*70)
            print("Transações abortadas (total de abortos por transação):")
            for tid, count in sorted(contagem_abortos.items()):
                print(f"  T{tid}: {count} aborto(s)")


def analisar_operacao(texto_op: str) -> Operacao:
    """
    Analisa uma string de operação e converte para objeto Operacao
    
    Formatos aceitos:
    - Leitura: r1(x), r2(y), etc.
    - Escrita: w1(x), w3(z), etc.
    - Commit: c1, c2, c3, etc.
    
    Args:
        texto_op: String representando a operação
        
    Returns:
        Objeto Operacao correspondente
        
    Exemplos:
        >>> analisar_operacao("r1(x)")
        Operacao(id_transacao=1, tipo_op=TipoOperacao.LEITURA, item_dado='x')
        
        >>> analisar_operacao("w2(y)")
        Operacao(id_transacao=2, tipo_op=TipoOperacao.ESCRITA, item_dado='y')
        
        >>> analisar_operacao("c3")
        Operacao(id_transacao=3, tipo_op=TipoOperacao.COMMIT, item_dado=None)
    """
    texto_op = texto_op.strip().lower()
    
    # Verificar se é operação de commit (formato: c1, c2, etc.)
    if texto_op[0] == 'c':
        tid = int(texto_op[1:])
        return Operacao(tid, TipoOperacao.COMMIT)
    
    # Determinar tipo de operação: leitura (r) ou escrita (w)
    tipo_op = TipoOperacao.LEITURA if texto_op[0] == 'r' else TipoOperacao.ESCRITA
    
    # Extrair ID da transação e nome do item de dado
    # Formato: r1(x) -> tid=1, item_dado='x'
    abre_parentese = texto_op.index('(')
    tid = int(texto_op[1:abre_parentese])
    item_dado = texto_op[abre_parentese+1:-1]
    
    return Operacao(tid, tipo_op, item_dado)


def executar_cenario(nome: str, hi_strings: List[str]):
    """
    Executa um cenário de teste específico
    
    Args:
        nome: Nome descritivo do cenário
        hi_strings: Lista de strings representando operações da HI
    """
    print("\n" + "="*70)
    print(f"CENÁRIO: {nome}")
    print("="*70)
    print("\nHistória Inicial (HI):")
    print("  " + " ".join(hi_strings))
    
    # Converter strings em objetos Operacao
    hi = [analisar_operacao(op_str) for op_str in hi_strings]
    
    # Criar escalonador e executar história
    escalonador = EscalonadorTimestamp()
    escalonador.executar_historia(hi)
    
    # Exibir resultado final
    escalonador.imprimir_historia_final()
    
    print("\n" + "="*70)
    print("CENÁRIO CONCLUÍDO")
    print("="*70 + "\n")
    input("Pressione ENTER para continuar...\n")


def main():
    """
    Função principal - executa todos os cenários de teste
    """
    print("\n" + "="*70)
    print("SIMULADOR DE CONTROLE DE CONCORRÊNCIA")
    print("Protocolo de Timestamps")
    print("="*70)
    print("\nEste programa demonstra o funcionamento do Protocolo de Timestamps")
    print("para controle de concorrência em bancos de dados.")
    print("\nSerão executados vários cenários de teste.")
    print("="*70)
    
    # ==========================================================================
    # CENÁRIO 1: Execução serial simples (sem conflitos)
    # ==========================================================================
    executar_cenario(
        "Execução Serial Simples",
        [
            "r1(x)",    # T1 lê X
            "w1(x)",    # T1 escreve X
            "c1",       # T1 commita
            "r2(x)",    # T2 lê X
            "c2"        # T2 commita
        ]
    )
    
    # ==========================================================================
    # CENÁRIO 2: Conflito de leitura/escrita - T1 abortada
    # ==========================================================================
    executar_cenario(
        "Conflito Leitura/Escrita - T1 Abortada",
        [
            "r1(y)",    # T1 lê Y
            "r2(y)",    # T2 lê Y
            "w1(y)",    # T1 tenta escrever Y - ABORTA! (TS(1) < RTS(2))
            "c2",       # T2 commita
            "c1"        # T1 reiniciada, commita
        ]
    )
    
    # ==========================================================================
    # CENÁRIO 3: Conflito de escrita - T2 abortada por T3
    # ==========================================================================
    executar_cenario(
        "Conflito de Escrita - T2 Abortada",
        [
            "w1(z)",    # T1 escreve Z
            "r2(z)",    # T2 lê Z
            "w3(z)",    # T3 escreve Z
            "w2(z)",    # T2 tenta escrever Z - ABORTA! (TS(2) < WTS(3))
            "w2(z)",    # T2 reiniciada, escreve Z
            "c1",       # T1 commita
            "c3",       # T3 commita
            "c2"        # T2 (reiniciada) commita
        ]
    )
    
    # ==========================================================================
    # CENÁRIO 4: Conflito complexo - T1 lê, T3 escreve, T1 tenta escrever
    # ==========================================================================
    executar_cenario(
        "Conflito Complexo - T1 Abortada por T3",
        [
            "r1(a)",    # T1 lê A
            "w3(a)",    # T3 escreve A
            "c3",       # T3 commita
            "w1(a)",    # T1 tenta escrever A - ABORTA! (TS(1) < WTS(3))
            "c1"        # T1 reiniciada, commita
        ]
    )
    
    # ==========================================================================
    # CENÁRIO 5: Múltiplos itens de dados
    # ==========================================================================
    executar_cenario(
        "Múltiplos Itens de Dados",
        [
            "w1(x)",    # T1 escreve X
            "r2(x)",    # T2 lê X
            "w1(y)",    # T1 escreve Y
            "r2(y)",    # T2 lê Y
            "w2(x)",    # T2 escreve X
            "w2(y)",    # T2 escreve Y
            "c1",       # T1 commita
            "c2"        # T2 commita
        ]
    )
    
    print("\n" + "="*70)
    print("TODOS OS CENÁRIOS FORAM EXECUTADOS COM SUCESSO!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
