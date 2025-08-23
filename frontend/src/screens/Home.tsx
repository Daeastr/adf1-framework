import { useState } from "react";
import { apiPost } from "../lib/api";
import { auth } from "../firebase";

export function Home({ onConversation }: { onConversation: (id: string) => void }) {
  const [user1Lang, setUser1Lang] = useState("en");
  const [user2Lang, setUser2Lang] = useState("es");
  const [mode, setMode] = useState("user1-user2");
  const [opener, setOpener] = useState("@^2");
  const [pin, setPin] = useState<string | null>(null);

  async function start() {
    const token = await auth.currentUser?.getIdToken();
    const { conversation_id } = await apiPost(
      "/initiate",
      { opener, user1_lang: user1Lang, user2_lang: user2Lang, mode },
      token!
    );
    if (mode === "user1-user2") {
      const { code } = await apiPost("/pair", { conversation_id }, token!);
      setPin(code);
    }
    onConversation(conversation_id);
  }

  return (
    <div>
      <label>User1 language: <input value={user1Lang} onChange={e => setUser1Lang(e.target.value)} /></label>
      <label>User2 language: <input value={user2Lang} onChange={e => setUser2Lang(e.target.value)} /></label>
      <label>Mode:
        <select value={mode} onChange={e => setMode(e.target.value)}>
          <option value="user1-person1">User1→Person1</option>
          <option value="user1-user2">User1→User2</option>
        </select>
      </label>
      <input value={opener} onChange={e => setOpener(e.target.value)} />
      <button onClick={start}>Start</button>

      {pin && <div className="pin-display">Share this PIN with User2: <strong>{pin}</strong></div>}
    </div>
  );
}
