import { useEffect, useRef, useState } from "react";
import { apiPost } from "../lib/api";

declare global {
  interface Window {
    webkitSpeechRecognition?: any;
    SpeechRecognition?: any;
  }
}

export function MicCapture({ conversationId, sender, token, lang = "en-US" }) {
  const [recording, setRecording] = useState(false);
  const [text, setText] = useState("");
  const recRef = useRef<any>(null);

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    const rec = new SR();
    rec.lang = lang;
    rec.interimResults = true;
    rec.continuous = true;
    rec.onresult = (e: any) => {
      let combined = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        combined += e.results[i][0].transcript;
      }
      setText(combined.trim());
    };
    rec.onend = () => setRecording(false);
    recRef.current = rec;
  }, [lang]);

  const start = () => { setText(""); setRecording(true); recRef.current?.start(); };
  const stop  = () => { recRef.current?.stop(); };
  const send  = async () => {
    if (!text) return;
    await apiPost("/message", { text, sender, conversation_id: conversationId }, token);
    setText("");
  };

  const supported = Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);

  return (
    <div>
      {!supported && <div>Speech recognition not supported</div>}
      {!recording ? <button onClick={start}>🎙️ Start</button> : <button onClick={stop}>⏹ Stop</button>}
      <button onClick={send} disabled={!text}>Send</button>
      <textarea value={text} onChange={(e) => setText(e.target.value)} />
    </div>
  );
}
