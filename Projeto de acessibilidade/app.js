var applet = new GGBApplet(
    { appName: "graphing", width: 820, height: 500, showAlgebraInput: true, showToolBar: false },
    true
);
window.addEventListener('load', () => applet.inject('ggb-element'));

const btn    = document.getElementById('start-btn');
const status = document.getElementById('status');
const liveEl = document.getElementById('transcricao-ao-vivo');
const lista  = document.getElementById('historico-lista');

function falar(msg) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(msg);
    u.lang = 'pt-BR';
    window.speechSynthesis.speak(u);
}

function setStatus(msg, tipo = '') {
    status.textContent = msg;
    status.className = tipo;
}

function addHistorico(txt, ok = true) {
    const li = document.createElement('li');
    li.textContent = txt;
    if (!ok) li.classList.add('erro-item');
    lista.prepend(li);
}

function resetBtn() {
    btn.textContent = '🎤 Iniciar Comando de Voz';
    btn.classList.remove('ouvindo');
}

function iniciarReconhecimento() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { setStatus('Use o Chrome.', 'erro'); return; }

    const rec = new SR();
    rec.lang = 'pt-BR';
    rec.continuous = false;
    rec.interimResults = true;

    rec.onstart = () => {
        setStatus('Ouvindo...');
        btn.textContent = '⏹️ Ouvindo...';
        btn.classList.add('ouvindo');
        liveEl.textContent = '...';
    };

    rec.onresult = (e) => {
        const t = e.results[0][0].transcript;
        liveEl.textContent = t;
        if (e.results[0].isFinal) processarComando(t);
    };

    rec.onerror = (e) => {
        setStatus('Erro: ' + e.error, 'erro');
        falar('Erro no microfone.');
        resetBtn();
    };

    rec.onend = resetBtn;
    rec.start();
}

async function processarComando(texto) {
    setStatus('IA interpretando...');
    try {
        const response = await fetch('http://127.0.0.1:5000/traduzir', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texto })
        });
        if (!response.ok) throw new Error('Status ' + response.status);
        const data = await response.json();

        if (data.comando) {
            ggbApplet.evalCommand(data.comando);
            setStatus('Executado: ' + data.comando, 'ok');
            falar('Feito! ' + texto);
            addHistorico('"' + texto + '" → ' + data.comando);
        } else {
            setStatus(data.erro || 'Não reconhecido.', 'erro');
            falar('Não consegui converter esse comando. Tente de outro jeito.');
            addHistorico('"' + texto + '" — não reconhecido', false);
        }
    } catch (err) {
        setStatus('Erro de conexão. Flask está rodando?', 'erro');
        falar('Erro de conexão com o servidor.');
        addHistorico('Erro de servidor: "' + texto + '"', false);
    }
}

btn.addEventListener('click', iniciarReconhecimento);