// Cenários de teste
const cenarios = {
    'serial': {
        nome: 'Execução Serial Simples',
        operacoes: ['r1(x)', 'w1(x)', 'c1', 'r2(x)', 'c2']
    },
    'conflito_leitura': {
        nome: 'Conflito Leitura/Escrita - T1 Abortada',
        operacoes: ['r1(y)', 'r2(y)', 'w1(y)', 'c2', 'c1']
    },
    'conflito_escrita': {
        nome: 'Conflito de Escrita - T2 Abortada',
        operacoes: ['w1(z)', 'r2(z)', 'w3(z)', 'w2(z)', 'w2(z)', 'c1', 'c3', 'c2']
    },
    'conflito_complexo': {
        nome: 'Conflito Complexo - T1 Abortada por T3',
        operacoes: ['r1(a)', 'w3(a)', 'c3', 'w1(a)', 'c1']
    },
    'multiplos_itens': {
        nome: 'Múltiplos Itens de Dados',
        operacoes: ['w1(x)', 'r2(x)', 'w1(y)', 'r2(y)', 'w2(x)', 'w2(y)', 'c1', 'c2']
    }
};

// Estado da simulação
let estadoAtual = {
    transacoes: {},
    itens_dados: {},
    hf: [],
    hi: [],
    passo_atual: 0,
    timestamp_atual: 0,
    transacoes_abortadas: []
};

let autoPlay = false;
let autoInterval = null;

// Inicializar select com cenários
function inicializarCenarios() {
    const select = document.getElementById('scenarioSelect');
    for (const [key, cenario] of Object.entries(cenarios)) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = cenario.nome;
        select.appendChild(option);
    }
}

// Toggle da seção de entrada personalizada
function toggleCustomInput() {
    const content = document.getElementById('customInputContent');
    const icon = document.getElementById('toggleIcon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.textContent = '▼';
    } else {
        content.style.display = 'none';
        icon.textContent = '▶';
    }
}

// Adicionar cenário personalizado
function adicionarCenarioPersonalizado() {
    const nome = document.getElementById('customName').value.trim();
    const operacoesTexto = document.getElementById('customOperations').value.trim();

    if (!nome) {
        adicionarMensagem('Por favor, digite um nome para o cenário', 'warning');
        return;
    }

    if (!operacoesTexto) {
        adicionarMensagem('Por favor, digite as operações', 'warning');
        return;
    }

    // Processar operações (separar por vírgula ou espaço)
    const operacoes = operacoesTexto
        .split(/[,\s]+/)
        .map(op => op.trim())
        .filter(op => op.length > 0);

    if (operacoes.length === 0) {
        adicionarMensagem('Nenhuma operação válida encontrada', 'warning');
        return;
    }

    // Validar operações
    const operacoesInvalidas = [];
    for (const op of operacoes) {
        if (!validarOperacao(op)) {
            operacoesInvalidas.push(op);
        }
    }

    if (operacoesInvalidas.length > 0) {
        adicionarMensagem(
            `Operações inválidas: ${operacoesInvalidas.join(', ')}. Use o formato correto (ex: r1(x), w2(y), c3)`,
            'error'
        );
        return;
    }

    // Adicionar ao objeto de cenários
    const chave = 'custom_' + Date.now();
    cenarios[chave] = {
        nome: nome,
        operacoes: operacoes
    };

    // Adicionar ao select
    const select = document.getElementById('scenarioSelect');
    const option = document.createElement('option');
    option.value = chave;
    option.textContent = `${nome} (Personalizado)`;
    select.appendChild(option);
    select.value = chave;

    // Limpar campos
    document.getElementById('customName').value = '';
    document.getElementById('customOperations').value = '';

    adicionarMensagem(`Cenário "${nome}" adicionado com sucesso! ${operacoes.length} operação(ões).`, 'success');
}

// Validar operação
function validarOperacao(op) {
    op = op.toLowerCase().trim();
    
    // Validar commit: c1, c2, c3, etc.
    if (/^c\d+$/.test(op)) {
        return true;
    }
    
    // Validar leitura/escrita: r1(x), w2(y), etc.
    if (/^[rw]\d+\([a-z]+\)$/.test(op)) {
        return true;
    }
    
    return false;
}

// Abrir modal de exemplos
function abrirModalExemplos() {
    document.getElementById('examplesModal').classList.add('active');
}

// Fechar modal de exemplos
function fecharModalExemplos() {
    document.getElementById('examplesModal').classList.remove('active');
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('examplesModal');
    if (event.target === modal) {
        fecharModalExemplos();
    }
}

// Iniciar simulação
function iniciarSimulacao() {
    const cenarioKey = document.getElementById('scenarioSelect').value;
    if (!cenarioKey) {
        adicionarMensagem('Por favor, selecione um cenário', 'warning');
        return;
    }

    const cenario = cenarios[cenarioKey];
    estadoAtual = {
        transacoes: {},
        itens_dados: {},
        hf: [],
        hi: cenario.operacoes,
        passo_atual: 0,
        timestamp_atual: 0,
        transacoes_abortadas: []
    };

    document.getElementById('startBtn').disabled = true;
    document.getElementById('nextBtn').disabled = false;
    document.getElementById('autoBtn').disabled = false;
    document.getElementById('resetBtn').disabled = false;
    document.getElementById('stepInfo').style.display = 'block';
    
    atualizarInterface();
    adicionarMensagem(`Cenário "${cenario.nome}" carregado. Clique em "Próximo Passo" para começar.`, 'info');
}

// Próximo passo
function proximoPasso() {
    if (estadoAtual.passo_atual >= estadoAtual.hi.length) {
        adicionarMensagem('Simulação concluída!', 'success');
        document.getElementById('nextBtn').disabled = true;
        document.getElementById('autoBtn').disabled = true;
        return;
    }

    const operacao = estadoAtual.hi[estadoAtual.passo_atual];
    processarOperacao(operacao);
    estadoAtual.passo_atual++;
    
    atualizarInterface();

    if (estadoAtual.passo_atual >= estadoAtual.hi.length) {
        adicionarMensagem('✅ Todas as operações foram processadas!', 'success');
        document.getElementById('nextBtn').disabled = true;
        document.getElementById('autoBtn').disabled = true;
    }
}

// Executar automaticamente
function executarAutomatico() {
    if (autoPlay) {
        autoPlay = false;
        clearInterval(autoInterval);
        document.getElementById('autoBtn').textContent = '⚡ Auto';
        document.getElementById('nextBtn').disabled = false;
    } else {
        autoPlay = true;
        document.getElementById('autoBtn').textContent = '⏸️ Pausar';
        document.getElementById('nextBtn').disabled = true;
        
        autoInterval = setInterval(() => {
            if (estadoAtual.passo_atual >= estadoAtual.hi.length) {
                autoPlay = false;
                clearInterval(autoInterval);
                document.getElementById('autoBtn').textContent = '⚡ Auto';
                document.getElementById('autoBtn').disabled = true;
                return;
            }
            proximoPasso();
        }, 1500);
    }
}

// Processar operação
function processarOperacao(opStr) {
    const op = analisarOperacao(opStr);
    
    // Verificar se a transação foi abortada e ainda não foi reiniciada
    const transacaoExistente = estadoAtual.transacoes[op.id_transacao];
    if (transacaoExistente && transacaoExistente.status === 'abortada') {
        adicionarMensagem(`⏭️ Ignorando ${opStr} - T${op.id_transacao} foi abortada`, 'warning');
        return;
    }
    
    if (op.tipo === 'commit') {
        // Verificar se a transação existe e não foi abortada
        if (!estadoAtual.transacoes[op.id_transacao]) {
            adicionarMensagem(`⏭️ Ignorando ${opStr} - T${op.id_transacao} não existe ou foi abortada`, 'warning');
            return;
        }
        processarCommit(op);
    } else {
        const transacao = obterOuCriarTransacao(op.id_transacao);
        const item = obterOuCriarItemDado(op.item_dado);

        if (op.tipo === 'leitura') {
            processarLeitura(op, transacao, item);
        } else if (op.tipo === 'escrita') {
            processarEscrita(op, transacao, item);
        }
    }
}

// Analisar operação
function analisarOperacao(opStr) {
    opStr = opStr.trim().toLowerCase();
    
    if (opStr[0] === 'c') {
        return {
            tipo: 'commit',
            id_transacao: parseInt(opStr.substring(1)),
            string: opStr
        };
    }

    const tipo = opStr[0] === 'r' ? 'leitura' : 'escrita';
    const abreParentese = opStr.indexOf('(');
    const id_transacao = parseInt(opStr.substring(1, abreParentese));
    const item_dado = opStr.substring(abreParentese + 1, opStr.length - 1);

    return { tipo, id_transacao, item_dado, string: opStr };
}

// Obter ou criar transação
function obterOuCriarTransacao(id) {
    if (!estadoAtual.transacoes[id]) {
        estadoAtual.timestamp_atual++;
        estadoAtual.transacoes[id] = {
            id: id,
            timestamp: estadoAtual.timestamp_atual,
            status: 'ativa',
            operacoes: []
        };
        adicionarMensagem(`🆕 Nova transação T${id} criada com TS=${estadoAtual.timestamp_atual}`, 'info');
    }
    return estadoAtual.transacoes[id];
}

// Obter ou criar item de dado
function obterOuCriarItemDado(nome) {
    if (!estadoAtual.itens_dados[nome]) {
        estadoAtual.itens_dados[nome] = {
            nome: nome,
            rts: 0,
            wts: 0
        };
    }
    return estadoAtual.itens_dados[nome];
}

// Processar leitura
function processarLeitura(op, transacao, item) {
    adicionarMensagem(`🔍 Verificando ${op.string}: TS(T${transacao.id})=${transacao.timestamp}, RTS(${item.nome})=${item.rts}, WTS(${item.nome})=${item.wts}`, 'info');
    
    if (transacao.timestamp < item.wts) {
        adicionarMensagem(
            `❌ ABORTAR T${transacao.id}: TS(${transacao.timestamp}) < WTS(${item.wts}) - Leitura muito antiga!`,
            'error'
        );
        abortarTransacao(transacao.id);
        return;
    }

    if (transacao.timestamp > item.rts) {
        item.rts = transacao.timestamp;
        adicionarMensagem(
            `✅ ${op.string} executado: RTS(${item.nome}) atualizado para ${item.rts}`,
            'success'
        );
    } else {
        adicionarMensagem(
            `✅ ${op.string} executado: RTS(${item.nome}) mantido em ${item.rts}`,
            'success'
        );
    }

    estadoAtual.hf.push(op.string);
    transacao.operacoes.push(op.string);
}

// Processar escrita
function processarEscrita(op, transacao, item) {
    adicionarMensagem(`🔍 Verificando ${op.string}: TS(T${transacao.id})=${transacao.timestamp}, RTS(${item.nome})=${item.rts}, WTS(${item.nome})=${item.wts}`, 'info');
    
    if (transacao.timestamp < item.rts) {
        adicionarMensagem(
            `❌ ABORTAR T${transacao.id}: TS(${transacao.timestamp}) < RTS(${item.rts}) - Escrita muito antiga!`,
            'error'
        );
        abortarTransacao(transacao.id);
        return;
    }

    if (transacao.timestamp < item.wts) {
        adicionarMensagem(
            `❌ ABORTAR T${transacao.id}: TS(${transacao.timestamp}) < WTS(${item.wts}) - Escrita muito antiga!`,
            'error'
        );
        abortarTransacao(transacao.id);
        return;
    }

    item.wts = transacao.timestamp;
    adicionarMensagem(
        `✅ ${op.string} executado: WTS(${item.nome}) atualizado para ${item.wts}`,
        'success'
    );

    estadoAtual.hf.push(op.string);
    transacao.operacoes.push(op.string);
}

// Processar commit
function processarCommit(op) {
    const transacao = obterOuCriarTransacao(op.id_transacao);
    transacao.status = 'committed';
    estadoAtual.hf.push(op.string);
    adicionarMensagem(`✅ Commit de T${transacao.id} - Transação confirmada com sucesso!`, 'success');
}

// Abortar transação
function abortarTransacao(id) {
    const transacao = estadoAtual.transacoes[id];
    
    adicionarMensagem(`⚠️ T${id} será reiniciada posteriormente com novo timestamp`, 'warning');
    
    // Remover operações da HF
    const operacoesRemovidas = [];
    estadoAtual.hf = estadoAtual.hf.filter(opStr => {
        const op = analisarOperacao(opStr);
        if (op.id_transacao === id) {
            operacoesRemovidas.push(opStr);
            return false;
        }
        return true;
    });
    
    if (operacoesRemovidas.length > 0) {
        adicionarMensagem(`🔄 Removidas ${operacoesRemovidas.length} operação(ões) de T${id} da HF`, 'warning');
    }

    transacao.status = 'abortada';
    transacao.operacoes = [];
    delete estadoAtual.transacoes[id];
    estadoAtual.transacoes_abortadas.push(id);
    
    // Recalcular RTS e WTS dos itens de dados baseado no que está na HF
    recalcularTimestampsItensDados();
}

// Recalcular timestamps dos itens de dados baseado na HF atual
function recalcularTimestampsItensDados() {
    // Resetar todos os timestamps
    Object.values(estadoAtual.itens_dados).forEach(item => {
        item.rts = 0;
        item.wts = 0;
    });
    
    // Recalcular baseado nas operações que permanecem na HF
    estadoAtual.hf.forEach(opStr => {
        const op = analisarOperacao(opStr);
        if (op.tipo !== 'commit') {
            const item = estadoAtual.itens_dados[op.item_dado];
            const transacao = estadoAtual.transacoes[op.id_transacao];
            
            if (transacao) {
                if (op.tipo === 'leitura') {
                    item.rts = Math.max(item.rts, transacao.timestamp);
                } else if (op.tipo === 'escrita') {
                    item.wts = Math.max(item.wts, transacao.timestamp);
                }
            }
        }
    });
}

// Atualizar interface
function atualizarInterface() {
    // Atualizar progresso
    const progresso = (estadoAtual.passo_atual / estadoAtual.hi.length) * 100;
    document.getElementById('progressBar').style.width = progresso + '%';

    // Atualizar informações do passo
    document.getElementById('stepNumber').textContent = estadoAtual.passo_atual;
    document.getElementById('totalSteps').textContent = estadoAtual.hi.length;
    
    if (estadoAtual.passo_atual < estadoAtual.hi.length) {
        document.getElementById('currentOperation').textContent = estadoAtual.hi[estadoAtual.passo_atual];
    } else {
        document.getElementById('currentOperation').textContent = 'Concluído';
    }

    // Atualizar HF
    atualizarHF();

    // Atualizar itens de dados
    atualizarItensDados();

    // Atualizar transações
    atualizarTransacoes();

    // Atualizar HI
    atualizarHI();
}

// Atualizar HF
function atualizarHF() {
    const container = document.getElementById('hfTimeline');
    container.innerHTML = '';

    if (estadoAtual.hf.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Nenhuma operação executada ainda</p></div>';
        return;
    }

    estadoAtual.hf.forEach(op => {
        const div = document.createElement('div');
        div.className = 'hf-operation';
        div.textContent = op;
        container.appendChild(div);
    });
}

// Atualizar itens de dados
function atualizarItensDados() {
    const container = document.getElementById('dataItems');
    container.innerHTML = '';

    const itens = Object.values(estadoAtual.itens_dados);
    if (itens.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Nenhum item de dado acessado</p></div>';
        return;
    }

    itens.forEach(item => {
        const div = document.createElement('div');
        div.className = 'data-item';
        div.innerHTML = `
            <strong>${item.nome.toUpperCase()}</strong>
            <div>
                <span class="timestamp-badge">RTS: ${item.rts}</span>
                <span class="timestamp-badge">WTS: ${item.wts}</span>
            </div>
        `;
        container.appendChild(div);
    });
}

// Atualizar transações
function atualizarTransacoes() {
    const container = document.getElementById('transactions');
    container.innerHTML = '';

    const transacoes = Object.values(estadoAtual.transacoes);
    if (transacoes.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Nenhuma transação iniciada</p></div>';
        return;
    }

    transacoes.forEach(t => {
        const div = document.createElement('div');
        div.className = `transaction-item ${t.status}`;
        
        let statusClass = 'status-active';
        let statusText = 'ATIVA';
        if (t.status === 'committed') {
            statusClass = 'status-committed';
            statusText = 'COMMITTED';
        } else if (t.status === 'abortada') {
            statusClass = 'status-aborted';
            statusText = 'ABORTADA';
        }

        div.innerHTML = `
            <div>
                <strong>T${t.id}</strong>
                <span class="timestamp-badge">TS: ${t.timestamp}</span>
            </div>
            <span class="status-badge ${statusClass}">${statusText}</span>
        `;
        container.appendChild(div);
    });
}

// Atualizar HI
function atualizarHI() {
    const container = document.getElementById('initialHistory');
    container.innerHTML = '';

    if (estadoAtual.hi.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>Selecione um cenário para começar</p></div>';
        return;
    }

    const timeline = document.createElement('div');
    timeline.className = 'hf-timeline';
    
    estadoAtual.hi.forEach((op, index) => {
        const div = document.createElement('div');
        div.className = 'hf-operation';
        
        if (index < estadoAtual.passo_atual) {
            div.style.opacity = '0.5';
        } else if (index === estadoAtual.passo_atual) {
            div.style.background = '#48bb78';
        }
        
        div.textContent = op;
        timeline.appendChild(div);
    });

    container.appendChild(timeline);
}

// Adicionar mensagem
function adicionarMensagem(texto, tipo) {
    const container = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = `message ${tipo}`;
    div.textContent = texto;
    
    container.insertBefore(div, container.firstChild);

    // Limitar número de mensagens
    while (container.children.length > 8) {
        container.removeChild(container.lastChild);
    }
}

// Resetar simulação
function resetarSimulacao() {
    if (autoPlay) {
        autoPlay = false;
        clearInterval(autoInterval);
        document.getElementById('autoBtn').textContent = '⚡ Auto';
    }

    estadoAtual = {
        transacoes: {},
        itens_dados: {},
        hf: [],
        hi: [],
        passo_atual: 0,
        timestamp_atual: 0,
        transacoes_abortadas: []
    };

    document.getElementById('startBtn').disabled = false;
    document.getElementById('nextBtn').disabled = true;
    document.getElementById('autoBtn').disabled = true;
    document.getElementById('resetBtn').disabled = true;
    document.getElementById('stepInfo').style.display = 'none';
    document.getElementById('messages').innerHTML = '';
    document.getElementById('progressBar').style.width = '0%';

    atualizarInterface();
    adicionarMensagem('Simulação resetada. Selecione um novo cenário.', 'info');
}

// Inicializar ao carregar
window.onload = function() {
    inicializarCenarios();
};
