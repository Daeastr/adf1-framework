// frontend/src/components/ConversationView.tsx
import { useState } from 'react';
import { MicCapture } from './MicCapture';
// We will also import the fallback for the next step
import { MicCaptureServerFallback } from './MicCaptureServerFallback';
import { SmartMicCapture } from './SmartMicCapture';

// This is a placeholder for your authentication logic.
const MOCK_USER_DATA = {
  sender: "user1" as "user1" | "user2",
  token: "mock-auth-token-12345",
  lang: "en-US", // BCP-47 language code
};

export function ConversationView({ conversationId }: { conversationId:string }) {
  const { sender, token, lang } = MOCK_USER_DATA;
  const [lastText, setLastText] = useState("");

  return (
    <div>
      <h2>Conversation Active</h2>
      <p>
        Now showing conversation with ID: <strong>{conversationId}</strong>
      </p>
      <div className="message-history">
        {/* Placeholder for where chat messages and suggestions will be displayed */}
      </div>

      <hr />

      <div className="input-area">
        <h3>Your Message</h3>
        
        {/*
          This now uses the SmartMicCapture component, which internally decides
          whether to use on-device STT or the server fallback.
          The onTextReady callback allows this parent component to know what was
          last transcribed.
        */}
        <SmartMicCapture
          conversationId={conversationId}
          sender={sender}
          token={token}
          lang={lang}
          onTextReady={setLastText}
        />
        
        {lastText && (
          <div className="text-xs text-gray-500" style={{marginTop: '10px'}}>
            Last captured: “{lastText}”
          </div>
        )}
      </div>
    </div>
  );
}