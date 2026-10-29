"use client";

import { FileCheck2, FileUp, Loader2, TriangleAlert } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { createCase } from "@/lib/api";

const ACCEPT = "image/png,image/jpeg,image/webp,application/pdf";

function Drop({ label, file, onFile }: { label: string; file: File | null; onFile: (f: File) => void }) {
  return (
    <label className={file ? "dropzone has-file" : "dropzone"}>
      {file ? <FileCheck2 size={28} aria-hidden /> : <FileUp size={28} aria-hidden />}
      <strong>{label}</strong>
      {file ? (
        <span className="file-name">{file.name}</span>
      ) : (
        <span>PDF, PNG, JPG or WebP, up to 10 MB</span>
      )}
      <input type="file" accept={ACCEPT} onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
    </label>
  );
}

export default function NewCasePage() {
  const router = useRouter();
  const [bill, setBill] = useState<File | null>(null);
  const [eob, setEob] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!bill || !eob) return;
    setBusy(true);
    setError(null);
    try {
      const { id } = await createCase(bill, eob);
      router.push(`/cases/${id}`);
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>New case</h1>
          <p className="sub">Upload the provider bill and the matching explanation of benefits.</p>
        </div>
      </div>

      <div className="alert alert-warn">
        <TriangleAlert size={18} aria-hidden />
        <span>
          Documents are read by a third-party AI service on a free tier, which may retain and
          review submitted content. Upload only redacted or sample documents, not real health records.
        </span>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          <TriangleAlert size={18} aria-hidden />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={submit}>
        <div className="dropzone-grid">
          <Drop label="Provider bill" file={bill} onFile={setBill} />
          <Drop label="Explanation of benefits" file={eob} onFile={setEob} />
        </div>
        <button className="btn" type="submit" disabled={!bill || !eob || busy}>
          {busy ? <Loader2 size={18} className="spin" aria-hidden /> : null}
          {busy ? "Uploading" : "Start review"}
        </button>
      </form>
    </>
  );
}
