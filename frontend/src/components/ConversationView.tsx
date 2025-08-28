// frontend/src/components/ConversationView.tsx

// --- IMPORTS UPDATED ---
// The specific mic components are no longer needed here.
// We import the single, intelligent wrapper component.
import { SmartMicCapture } from './SmartMicCapture';

// This is a placeholder for your authentication logic.
const MOCK_USER_DATA = {
  // A mock sender role and language, in a real app this would be dynamic
  sender: "user1" as "user1" | "user2",
  token: "mock-auth-token-12345",
  lang: "en-US", // BCP-47 language code
};

export function ConversationView({ conversationId }: { conversationId:string }) {
  const { sender, token, lang } = MOCK_USER_DATA;

  return (
    <div>
      <h2>Conversation Active</h2>
      <p>
        Now showing conversation with ID: <strong>{conversationId}</strong>
      </p>
      <div className="message-history">
        {/* Placeholder for where chat messages will be displayed */}
      </div>

      <hr />

      <div className="input-area">
        <h3>Your Message</h3>
        
        {/* --- USAGE SWAPPED --- */}
        {/*
          The previous if/else block is replaced with a single, clean call
          to the SmartMicCapture component. It handles the browser
          feature detection and renders the correct underlying component internally.
        */}
        <SmartMicCapture
          conversationId={conversationId}
          sender={sender}
          token={token}
          lang={lang}
        />
        
      </div>
    </div>
  );
}