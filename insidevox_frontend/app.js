"use strict";

const API_URL = "http://localhost:8000/comando";

let elementosAtuais = [];
let ggb = null;
let ouvindo = false;

const btnMicrofone   = document.getElementById("btn-microfone");
const btnLerTudo     = document.getElementById("btn-ler-tudo");
const elTranscricao  = document.getElementById("transcricao-ao-vivo");
const elStatus       = document.getElementById("status");
const elStatusDot    = document.getElementById("status-dot");
const elListaElem    = document.getElementById("lista-elementos");
const elContador     = document.getElementById("elementos-contador");
const elFeedback     = document.getElementById("feedback-texto");
const elHistorico    = document.getElementById("historico-lista");

// GeoGebra 
const ggbParams = {
  appName: "graphing",
  width: 820,
  height: 480,
  showToolBar: false,
  showAlgebraInput: false,
  showMenuBar: false,
  enableLabelDrags: false,
  enableShiftDragZoom: true,
  language: "pt",
  appletOnLoad(api) {
    ggb = api;
    falar("InsideVox pronto. Pressione espaço ou clique no botão para dar um comando.");
    setStatus("Aguardando comando...", "ok");
  },
};

window.addEventListener("load", () => {
  const applet = new GGBApplet(ggbParams, true);
  applet.inject("ggb-elemento");
});

// Reconhecimento de voz 
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
  alert("Use o Google Chrome para acessar o InsideVox.");
}

const reconhecimento = new SpeechRecognition();
reconhecimento.lang            = "pt-BR";
reconhecimento.continuous      = false;
reconhecimento.interimResults  = true;
reconhecimento.maxAlternatives = 1;

reconhecimento.onstart = () => {
  ouvindo = true;
  btnMicrofone.textContent = "";
  btnMicrofone.innerHTML = `
    <span class="btn-mic__icon" aria-hidden="true">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>
    </span>
    <span class="btn-mic__label">Parar</span>`;
  btnMicrofone.classList.add("ouvindo");
  btnMicrofone.setAttribute("aria-pressed", "true");
  elStatusDot.classList.add("ouvindo");
  elStatusDot.classList.remove("erro");
  setStatus("Ouvindo...", "");
  elTranscricao.textContent = "...";
};

reconhecimento.onend = () => {
  ouvindo = false;
  btnMicrofone.innerHTML = `
    <span class="btn-mic__icon" aria-hidden="true">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>
    </span>
    <span class="btn-mic__label">Comando de Voz</span>`;
  btnMicrofone.classList.remove("ouvindo");
  btnMicrofone.setAttribute("aria-pressed", "false");
  elStatusDot.classList.remove("ouvindo");
};

reconhecimento.onerror = (ev) => {
  const msg = ev.error === "not-allowed"
    ? "Permissão de microfone negada."
    : `Erro no microfone: ${ev.error}`;
  setStatus(msg, "erro");
  falar(msg);
};

reconhecimento.onresult = (evento) => {
  const resultado = evento.results[evento.results.length - 1];
  const texto     = resultado[0].transcript.trim();
  elTranscricao.textContent = texto;
  if (resultado.isFinal) processarComando(texto);
};

// Controles 
btnMicrofone.addEventListener("click", alternarMicrofone);
btnLerTudo.addEventListener("click", () => processarComando("ler tudo"));

document.addEventListener("keydown", (ev) => {
  if (ev.code === "Space" && document.activeElement === document.body) {
    ev.preventDefault();
    alternarMicrofone();
  }
});

function alternarMicrofone() {
  if (ouvindo) reconhecimento.stop();
  else { elTranscricao.textContent = "Aguardando..."; reconhecimento.start(); }
}

//  Processamento 
async function processarComando(texto) {
  if (!ggb) { falar("GeoGebra ainda carregando. Aguarde."); return; }

  setStatus("Processando...", "");
  setFeedback("Processando comando...", "");

  try {
    const resposta = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto, elementos_atuais: elementosAtuais }),
    });

    if (!resposta.ok) throw new Error(`Status ${resposta.status}`);
    const dados = await resposta.json();
    console.log("[InsideVox]", dados);
    tratarResposta(texto, dados);

  } catch (erro) {
    const msg = "Falha na conexão com o servidor.";
    console.error(erro);
    setStatus(msg, "erro");
    setFeedback(msg, "erro");
    falar(msg);
  }
}

// Tratamento por tipo 
function tratarResposta(textoOriginal, dados) {
  const { tipo, comandos_ggb, feedback, nome_elemento, tipo_elemento, descricao_elemento } = dados;

  switch (tipo) {

    case "novo_elemento": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento) {
        elementosAtuais.push({
          nome: nome_elemento,
          tipo: tipo_elemento || "elemento",
          descricao: descricao_elemento || `${tipo_elemento} ${nome_elemento}`,
        });
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }

    case "modificacao": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento && descricao_elemento) {
        const idx = elementosAtuais.findIndex((e) => e.nome === nome_elemento);
        if (idx !== -1) elementosAtuais[idx].descricao = descricao_elemento;
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }

    case "ler_tudo": {
      falar(feedback);
      setStatus("Lendo...", "ok");
      setFeedback(feedback, "ok");
      break;
    }

    case "limpar": {
      ggb.reset();
      elementosAtuais = [];
      atualizarListaElementos();
      falar(feedback);
      setStatus("Tela limpa.", "ok");
      setFeedback(feedback, "ok");
      break;
    }

    case "derivada": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento) {
        elementosAtuais.push({
          nome: nome_elemento,
          tipo: tipo_elemento || "derivada",
          descricao: descricao_elemento || `Derivada ${nome_elemento}`,
        });
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }
    
    case "integral_indefinida": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento) {
        elementosAtuais.push({
          nome: nome_elemento,
          tipo: tipo_elemento || "integral indefinida",
          descricao: descricao_elemento || `Integral ${nome_elemento}`,
        });
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }
    
    case "integral_definida": {
      // Integral definida retorna número — não cria elemento novo
      executarComandosGGB(comandos_ggb);
      const resultadoInt = dados.resultado_numero;
      const msgInt = resultadoInt !== null && resultadoInt !== undefined
        ? `${feedback} Valor: ${resultadoInt}`
        : feedback;
      falar(msgInt);
      setStatus(feedback, "ok");
      setFeedback(msgInt, "ok");
      break;
    }
    
    case "limite": {
      // Limite retorna número — não cria elemento novo
      executarComandosGGB(comandos_ggb);
      const resultadoLim = dados.resultado_numero;
      const msgLim = resultadoLim !== null && resultadoLim !== undefined
        ? `${feedback} Resultado: ${resultadoLim}`
        : feedback;
      falar(msgLim);
      setStatus(feedback, "ok");
      setFeedback(msgLim, "ok");
      break;
    }
    
    case "tangente": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento) {
        elementosAtuais.push({
          nome: nome_elemento,
          tipo: "reta tangente",
          descricao: descricao_elemento || `Reta tangente ${nome_elemento}`,
        });
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }
    
    case "area_entre_curvas": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento) {
        elementosAtuais.push({
          nome: nome_elemento,
          tipo: "área entre curvas",
          descricao: descricao_elemento || `Área ${nome_elemento}`,
        });
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }
    
    case "soma_riemann": {
      executarComandosGGB(comandos_ggb);
      if (nome_elemento) {
        elementosAtuais.push({
          nome: nome_elemento,
          tipo: "soma de Riemann",
          descricao: descricao_elemento || `Soma de Riemann ${nome_elemento}`,
        });
        atualizarListaElementos();
      }
      falar(feedback);
      setStatus(feedback, "ok");
      setFeedback(feedback, "ok");
      break;
    }

    default: {
      const msg = feedback || "Não entendi o comando.";
      falar(msg);
      setStatus(msg, "erro");
      setFeedback(msg, "erro");
    }
  }
}


function executarComandosGGB(comandos) {
  for (const cmd of comandos) {
    const ok = ggb.evalCommand(cmd);
    if (!ok) console.warn(`[GeoGebra] Falhou: ${cmd}`);
  }
}

const synth = window.speechSynthesis;

function falar(texto) {
  if (!texto) return;
  synth.cancel();
  const u = new SpeechSynthesisUtterance(texto);
  u.lang = "pt-BR";
  u.rate = 1.0;
  synth.speak(u);
}

function setStatus(mensagem, classe) {
  elStatus.textContent = mensagem;
  elStatusDot.className = "status-dot" + (classe === "erro" ? " erro" : "");
}

function setFeedback(mensagem, tipo) {
  elFeedback.innerHTML = "";
  const span = document.createElement("span");
  span.textContent = mensagem;
  if (tipo === "ok")   span.className = "feedback-ok";
  if (tipo === "erro") span.className = "feedback-erro";
  if (!tipo)           span.className = "feedback-placeholder";
  elFeedback.appendChild(span);
}

const TIPO_CONFIG = {
  "função":             { avatarClass: "funcao",    dotClass: "funcao"    },
  "parábola":           { avatarClass: "funcao",    dotClass: "funcao"    },
  "reta":               { avatarClass: "funcao",    dotClass: "funcao"    },
  "círculo":            { avatarClass: "circulo",   dotClass: "circulo"   },
  "elipse":             { avatarClass: "circulo",   dotClass: "circulo"   },
  "hipérbole":          { avatarClass: "circulo",   dotClass: "circulo"   },
  "cônica":             { avatarClass: "circulo",   dotClass: "circulo"   },
  "ponto":              { avatarClass: "ponto",     dotClass: "ponto"     },
  // Cálculo
  "derivada":           { avatarClass: "calculo",   dotClass: "calculo"   },
  "integral indefinida":{ avatarClass: "calculo",   dotClass: "calculo"   },
  "reta tangente":      { avatarClass: "tangente",  dotClass: "tangente"  },
  "área entre curvas":  { avatarClass: "area",      dotClass: "area"      },
  "soma de riemann":    { avatarClass: "area",      dotClass: "area"      },
};

function getTipoConfig(tipo) {
  const chave = (tipo || "").toLowerCase();
  return TIPO_CONFIG[chave] || { avatarClass: "default", dotClass: "default" };
}

function atualizarListaElementos() {
  elListaElem.innerHTML = "";

  if (elementosAtuais.length === 0) {
    const li = document.createElement("li");
    li.className = "elementos-vazio";
    li.textContent = "Nenhum elemento na tela";
    elListaElem.appendChild(li);
    elContador.textContent = "0 elementos carregados";
    return;
  }

  const n = elementosAtuais.length;
  elContador.textContent = `${n} elemento${n !== 1 ? "s" : ""} carregado${n !== 1 ? "s" : ""}`;

  for (const elem of elementosAtuais) {
    const { avatarClass, dotClass } = getTipoConfig(elem.tipo);

    const li = document.createElement("li");
    li.className = "elemento-card";
    li.setAttribute("tabindex", "0");
    li.setAttribute("role", "listitem");
    li.setAttribute("aria-label", elem.descricao || `${elem.tipo} ${elem.nome}`);

    li.innerHTML = `
      <div class="elemento-avatar elemento-avatar--${avatarClass}" aria-hidden="true">${elem.nome}</div>
      <div class="elemento-info">
        <div class="elemento-tipo">${(elem.tipo || "ELEMENTO").toUpperCase()}</div>
        <div class="elemento-expr">${elem.descricao || elem.nome}</div>
      </div>
      <span class="elemento-dot elemento-dot--${dotClass}" aria-hidden="true"></span>
    `;

    li.addEventListener("focus", () => falar(elem.descricao || `${elem.tipo} ${elem.nome}`));
    elListaElem.appendChild(li);
  }
}

atualizarListaElementos();