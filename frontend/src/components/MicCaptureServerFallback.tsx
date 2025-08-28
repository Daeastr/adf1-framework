import { useEffect, useRef, useState } from "react";

export function MicCaptureServerFallback({ conversationId, sender, token }) {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    chunksRef.current = [];

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunksRef.current.push(e.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const url = URL.createObjectURL(blob);
      setAudioURL(url);
    };

    mediaRecorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const sendToServer = async () => {
    if (!audioURL) return;

    const blob = new Blob(chunksRef.current, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("conversation_id", conversationId);
    formData.append("sender", sender);
    formData.append("audio", blob, "speech.webm");

    const res = await fetch("/speech", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    const json = await res.json();
    console.log("Server response:", json);
    // Optionally clear audio preview
    setAudioURL(null);
  };

  const supported = Boolean(navigator.mediaDevices && window.MediaRecorder);

  return (
    <div>
      {!supported && <div>Audio recording not supported in this browser</div>}
      {supported && (
        <>
          {!recording ? (
            <button onClick={startRecording}>🎙️ Start Recording</button>
          ) : (
            <button onClick={stopRecording}>⏹ Stop Recording</button>
          )}
          {audioURL && (
            <div>
              <audio controls src={audioURL} />
              <button onClick={sendToServer}>Send to Server</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
