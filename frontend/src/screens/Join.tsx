import { useState } from "react";
import { apiPost } from "../lib/api";
import { auth } from "../firebase";

export function Join({ onConversation }: { onConversation: (id: string) => void }) {
  const [code, setCode] = useState("");

  async function join() {
    const token = await auth.currentUser?.getIdToken();
    const { conversation_id } = await apiPost("/accept", { code }, token!);
    onConversation(conversation_id);
  }

  return (
    <div>
      <input placeholder="Enter PIN" value={code} onChange={e => setCode(e.target.value)} />
      <button onClick={join}>Join Conversation</button>
    </div>
  );
}
