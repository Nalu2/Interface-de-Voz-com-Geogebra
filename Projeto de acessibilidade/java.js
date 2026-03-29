recognition.onresult = async function(event) {
  for (let i = event.resultIndex; i < event.results.length; i++) {
    if (event.results[i].isFinal) {
      const falaProfessor = event.results[i][0].transcript.trim();
      output.textContent = "Processando: " + falaProfessor;

      // ENVIANDO PARA A IA TRADUZIR
      const comandoGGB = await traduzirComIA(falaProfessor);
      
      if (comandoGGB) {
        ggbApplet.evalCommand(comandoGGB); // Executa no GeoGebra
        falarFeedback("Comando executado: " + falaProfessor); // Feedback Auditivo [cite: 33]
      }
    }
  }
};

// Função que simula a chamada para a IA
async function traduzirComIA(texto) {
  try {
    // Aqui você chamaria seu backend (Python/Node) que contém a chave da API
    // O Prompt deve instruir a IA a retornar APENAS o comando GGBScript 
    const response = await fetch('/api/traduzir', {
      method: 'POST',
      body: JSON.stringify({ prompt: texto }),
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    return data.comando; // Ex: "Círculo((0,0), 3)"
  } catch (e) {
    console.error("Erro na tradução da IA", e);
    return null;
  }
}

// Função de Acessibilidade: O sistema fala com o docente [cite: 33]
function falarFeedback(mensagem) {
  const synth = window.speechSynthesis;
  const utterThis = new SpeechSynthesisUtterance(mensagem);
  utterThis.lang = 'pt-BR';
  synth.speak(utterThis);
}