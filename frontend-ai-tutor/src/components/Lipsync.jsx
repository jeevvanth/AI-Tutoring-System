import { useState } from 'react'

// const[MouthState,setMouthState]=useState("closed")

export function startLipSync(audioBuffer, setMouthState) {
  const audioCtx = new AudioContext();
  const source = audioCtx.createBufferSource();
  source.buffer = audioBuffer;

  const analyser = audioCtx.createAnalyser();
  source.connect(analyser);
  analyser.connect(audioCtx.destination);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);

  function animate() {
    analyser.getByteFrequencyData(dataArray);
    const volume = dataArray.reduce((a, b) => a + b) / dataArray.length;

    if (volume < 20) setMouthState("closed");
    else if (volume < 80) setMouthState("half");
    else setMouthState("open");

    requestAnimationFrame(animate);
  }

  animate();
  source.start();
}
