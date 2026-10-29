"use client";

import { FilePlus2, FolderOpen, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import StatusBadge from "@/components/StatusBadge";
import { listCases, type CaseRecord } from "@/lib/api";

const fmt = (iso: string) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });

export default function CasesPage() {
  const [cases, setCases] = useState<CaseRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const load = () =>
      listCases()
        .then((c) => alive && (setCases(c), setError(null)))
        .catch((e: Error) => alive && setError(e.message));
    load();
    const timer = setInterval(load, 5000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Cases</h1>
          <p className="sub">Each case compares one provider bill with its explanation of benefits.</p>
        </div>
        <Link href="/cases/new" className="btn">
          <FilePlus2 size={18} aria-hidden /> New case
        </Link>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          <TriangleAlert size={18} aria-hidden />
          <span>Could not load cases: {error}. Check that the API is running.</span>
        </div>
      )}

      {cases && cases.length === 0 && (
        <div className="card empty">
          <FolderOpen size={32} aria-hidden />
          <p>No cases yet. Upload a bill and its EOB to get started.</p>
        </div>
      )}

      {cases && cases.length > 0 && (
        <div className="card table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Bill</th>
                <th>Created</th>
                <th>Status</th>
                <th>Flags</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.id}>
                  <td data-label="Bill">
                    <Link href={`/cases/${c.id}`}>{c.bill_name || c.id.slice(0, 8)}</Link>
                  </td>
                  <td data-label="Created">{fmt(c.created_at)}</td>
                  <td data-label="Status">
                    <StatusBadge status={c.status} />
                  </td>
                  <td data-label="Flags">{c.status === "done" ? c.flags.length : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
