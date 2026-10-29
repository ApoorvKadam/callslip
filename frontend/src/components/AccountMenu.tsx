import { LogIn, LogOut, UserRound } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import { signIn, signOut } from "../api";

function errorText(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

// Sign in, create an account, or sign out. Signed in, uploads go to the user's own documents,
// which nobody else sees; the shared collection stays visible to everyone.
export function AccountMenu({
  email,
  onChange,
}: {
  email: string | null;
  onChange: (email: string | null) => void;
}) {
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [address, setAddress] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const box = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);

  // Like any menu: a click anywhere else closes it, and Escape closes it and returns to the button.
  useEffect(() => {
    if (!open) return;
    function onPointer(e: PointerEvent) {
      if (box.current && !box.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: globalThis.KeyboardEvent) {
      if (e.key !== "Escape") return;
      setOpen(false);
      trigger.current?.focus();
    }
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const account = await signIn(address.trim(), password, creating);
      setPassword("");
      setOpen(false);
      setCreating(false); // next time, after signing out, the menu offers plain sign-in
      onChange(account.email);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  async function leave() {
    setError(null);
    try {
      await signOut();
      onChange(null); // only once the server has ended the sign-in
    } catch (err) {
      setError(`Could not sign out: ${errorText(err)}`);
    }
  }

  if (email) {
    return (
      <div className="account">
        <span className="meta account-email">
          <UserRound size={14} aria-hidden="true" />
          {email}
        </span>
        <button type="button" className="text-button" onClick={() => void leave()}>
          <LogOut size={14} aria-hidden="true" />
          Sign out
        </button>
        {error && (
          <p className="error account-error" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="account" ref={box}>
      <button
        ref={trigger}
        type="button"
        className="btn"
        aria-expanded={open}
        aria-controls="sign-in"
        onClick={() => setOpen(!open)}
      >
        <LogIn size={15} aria-hidden="true" />
        Sign in
      </button>
      {open && (
        <form
          id="sign-in"
          className="sign-in"
          aria-label={creating ? "Create an account" : "Sign in"}
          onSubmit={(e) => void submit(e)}
        >
          <label>
            <span className="label">Email</span>
            <input
              type="email"
              required
              autoFocus
              autoComplete="email"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </label>
          <label>
            <span className="label">Password</span>
            <input
              type="password"
              required
              minLength={creating ? 10 : undefined}
              autoComplete={creating ? "new-password" : "current-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {creating && <p className="meta">At least 10 characters.</p>}
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button type="submit" className="btn btn-primary" disabled={busy}>
            {creating ? "Create account" : "Sign in"}
          </button>
          <button
            type="button"
            className="text-button"
            onClick={() => {
              setCreating(!creating);
              setError(null);
            }}
          >
            {creating ? "I already have an account" : "Create an account"}
          </button>
          <p className="meta">
            Your uploads are visible only to you. The shared collection stays visible to everyone.
          </p>
        </form>
      )}
    </div>
  );
}
