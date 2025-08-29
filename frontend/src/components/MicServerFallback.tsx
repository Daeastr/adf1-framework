// frontend/src/components/MicServerFallback.tsx
import { useRef, useState } from "react";

export function MicServerFallback({
  apiUrl,
  token,
  conversationId,
  sender,
}: {
  apiUrl: string;
  token: string;
  conversationId: string;
  sender: "user1" | "user2";
}) {
  const [recording, setRecording] = useState(false);
  const recRef = useRef<MediaRecorder | null>(null);
  const chunks = useRef<BlobPart[]>([]);

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mr.ondataavailable = (e) => chunks.current.push(e.data);
    mr.onstop = async () => {
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      chunks.current = [];
      const form = new FormData();
      form.append("conversation_id", conversationId);
      form.append("sender", sender);
      form.append("audio", blob, "speech.webm");
      const res = await fetch(`${apiUrl}/speech`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) {
        const msg = await res.text();
        console.warn("Server STT error:", msg); // 501 expected until enabled
      }
    };
    mr.start();
    recRef.current = mr;
    setRecording(true);
  };

  const stop = () => {
    recRef.current?.stop();
    setRecording(false);
  };

  return (
    <div className="flex gap-2">
      {!recording ? (
        <button onClick={start}>🎙️ Record (server)</button>
      ) : (
        <button onClick={stop}>⏹ Stop</button>
      )}
    </div>
  );
}
