import { useState } from "react";
import { useAuth } from "../auth/AuthContext";

export default function AuthControl() {
  const { configured, user, loading, signIn, signUp, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  if (!configured || loading) return null;
  if (user) return <button type="button" onClick={() => void signOut()} className="auth-button rounded-md px-3 py-2 text-sm font-bold transition">Sign out</button>;

  async function submit() {
    setMessage("");
    try {
      if (mode === "login") await signIn(email, password);
      else {
        const result = await signUp(email, password);
        setMessage(result.needsConfirmation ? "Check your email to confirm your account." : "Account created.");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Authentication failed.");
    }
  }

  return <div className="relative">
    <button type="button" onClick={() => setOpen(!open)} className="auth-button rounded-md px-3 py-2 text-sm font-bold transition sm:text-base">Log in / Sign up</button>
    {open && <div className="absolute right-0 top-12 z-20 w-72 rounded-md border border-neutral bg-card p-4 text-ink shadow-lg">
      <p className="text-lg font-black">{mode === "login" ? "Welcome back" : "Create your account"}</p>
      <input aria-label="Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" className="mt-3 w-full rounded-md border border-neutral px-3 py-2" />
      <input aria-label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" className="mt-2 w-full rounded-md border border-neutral px-3 py-2" />
      <button type="button" onClick={() => void submit()} className="mt-3 w-full rounded-md bg-cranberry px-3 py-2 font-bold text-white">{mode === "login" ? "Log in" : "Sign up"}</button>
      <button type="button" onClick={() => setMode(mode === "login" ? "signup" : "login")} className="mt-2 text-sm font-bold text-cranberry">{mode === "login" ? "Need an account? Sign up" : "Already have an account? Log in"}</button>
      {message && <p className="mt-2 text-sm text-ink/70">{message}</p>}
    </div>}
  </div>;
}
