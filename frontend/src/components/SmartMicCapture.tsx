import React from "react";
import { MicCapture } from "./MicCapture";
import { MicCaptureServerFallback } from "./MicCaptureServerFallback";

export function SmartMicCapture({
  conversationId,
  sender,
  token,
  lang
}: {
  conversationId: string;
  sender: string;
  token: string;
  lang?: string;
}) {
  const hasClientSTT =
    typeof window !== "undefined" &&
    (window.SpeechRecognition || (window as any).webkitSpeechRecognition);

  return hasClientSTT ? (
    <MicCapture
      conversationId={conversationId}
      sender={sender}
      token={token}
      lang={lang}
    />
  ) : (
    <MicCaptureServerFallback
      conversationId={conversationId}
      sender={sender}
      token={token}
    />
  );
}
