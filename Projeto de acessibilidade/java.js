const recognition = new webkitSpeechRecognition();
const synth = window.speechSynthesis; // Para o retorno de voz (TTS)

recognition.onresult = async (event) => {
    const textoProfessor = event.results[0][0].transcript;
    console.log("Ouvido:", textoProfessor);

    // 1. Envia para o seu servidor Flask (IA)
    const response = await fetch('http://localhost:5000/traduzir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: textoProfessor })
    });

    const dados = await response.json();

    if (dados.comando) {
        // 2. Executa no GeoGebra
        ggbApplet.evalCommand(dados.comando); 

        // 3. RETORNO DE VOZ: O "Espelho Auditivo"
        const confirmacao = new SpeechSynthesisUtterance("Comando executado: " + textoProfessor); 
        synth.speak(confirmacao);
    }
};
