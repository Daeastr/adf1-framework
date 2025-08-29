import { useState } from "react";
import { ConversationView } from "./ConversationView";
import { MicCapture } from "./MicCapture";

export function ConversationScreen({
  conversationId,
  sender,
  token,
  userLang,
}: {
  conversationId: string;
  sender: "user1" | "user2";
  token: string;
  userLang: string; // e.g., "en-US", "es-ES"
}) {
  const [lastText, setLastText] = useState("");

  return (
    <div className="grid gap-4">
      <ConversationView conversationId={conversationId} />
      <MicCapture
        conversationId={conversationId}
        sender={sender}
        token={token}
        lang={userLang}
        onTextReady={setLastText}
      />
      {lastText && (
        <div className="text-xs text-gray-500">
          Last captured: “{lastText}”
        </div>
      )}
    </div>
  );
}