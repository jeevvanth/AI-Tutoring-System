import { useState } from "react";
import "./App.css";
import { startLipSync } from "./components/Lipsync";
import { Mic } from "lucide-react";

function App() {
  const [mouth, setMouth] = useState("closed");
  // const [transcribedText,SetTranscribed]=useState("")

  async function handleMicClick() {
    try {
      let texts=""
      let answer=""
      const sttResp = await fetch("http://127.0.0.1:8001/transcribe", {
        method: "GET",
      });
      const { text } = await sttResp.json();
      console.log("text:", text);
      texts=text;

      console.log("Transcribed Text",texts)

      //  Query RAG
      const ragResp = await fetch("http://127.0.0.1:8002/response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: texts }),
      });
      // console.log("response",ragResp.json());
      const { response } = await ragResp.json();
      console.log("RAG answer:", response);
      answer=response;


      
      const ttsResp = await fetch("http://127.0.0.1:8000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: answer }),
      });

      
      const arrayBuffer = await ttsResp.arrayBuffer();
      const audioCtx = new AudioContext();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
      startLipSync(audioBuffer, setMouth);

    } catch (err) {
      console.error("Error in mic flow:", err);
    }
  }

  return (
    <>
    <button
  onClick={handleMicClick}
  className="group relative mb-6 p-6 rounded-full bg-gradient-to-r from-pink-500 to-red-500 text-white shadow-lg hover:shadow-2xl transform hover:scale-110 transition-all duration-300"
>
  <a href="#" onClick={(e) => e.preventDefault()}>
    <Mic className="h-8 w-8 group-hover:animate-pulse" />
  </a>
  {/* Glow ring effect */}
  <span className="absolute inset-0 rounded-full border-4 border-pink-400 opacity-50 group-hover:animate-ping"></span>
</button>

    <div className="flex flex-col items-center justify-center min-h-screen">
      
      <img
        src={`/moscot_mouth_${mouth}.png`}
        alt="Mascot"
        className="w-24 h-auto mx-auto"
      />
    </div>
    </> 
  );
}

export default App;
