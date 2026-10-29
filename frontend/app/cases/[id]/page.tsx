"use client";

import { ArrowLeft, CircleCheck, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import StatusBadge from "@/components/StatusBadge";
import { FLAG_LABELS, getCase, type CaseRecord } from "@/lib/api";

const money = (v?: string) => (v === undefined ? "-" : `$${Number(v).toLocaleString(undefined, { minimumFractionDigits: 2 })}`);

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [rec, setRec] = useState<CaseRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    let timer: ReturnType<typeof setTimeout>;
    const load = async () => {
      try {
        const c = await getCase(id);
        if (!alive) return;
        setRec(c);
        setError(null);
        if (c.status === "queued" || c.status === "processing") timer = setTimeout(load, 3000);
      } catch (e) {
        if (alive) setError((e as Error).message);
      }
    };
    load();
    return () => {
      alive = false;
      clearTimeout(timer);
    };
  }, [id]);

  return (
    <>
      <p>
        <Link href="/" className="nav-link" style={{ display: "inline-flex", padding: "0 8px 0 0" }}>
          <ArrowLeft size={18} aria-hidden /> Back to cases
        </Link>
      </p>

      {error && (
        <div className="alert alert-danger" role="alert">
          <TriangleAlert size={18} aria-hidden />
          <span>{error}</span>
        </div>
      )}

      {rec && (
        <>
          <div className="page-head">
            <div>
              <h1>{rec.bill_name || "Case"}</h1>
              <p className="sub">EOB: {rec.eob_name}</p>
            </div>
            <StatusBadge status={rec.status} />
          </div>

          {rec.status === "failed" && (
            <div className="alert alert-danger" role="alert">
              <TriangleAlert size={18} aria-hidden />
              <span>Processing failed: {rec.error}</span>
            </div>
          )}

          {rec.status === "done" && (
            <>
              <div className="card summary-grid">
                <div>
                  <div className="stat-label">Bill total</div>
                  <div className="stat-value">{money(rec.bill?.stated_total)}</div>
                </div>
                <div>
                  <div className="stat-label">Bill asks patient to pay</div>
                  <div className="stat-value">{money(rec.bill?.patient_owes)}</div>
                </div>
                <div>
                  <div className="stat-label">EOB patient responsibility</div>
                  <div className="stat-value">{money(rec.eob?.patient_responsibility)}</div>
                </div>
              </div>

              <h2>Findings</h2>
              {rec.flags.length === 0 ? (
                <div className="alert alert-ok">
                  <CircleCheck size={18} aria-hidden />
                  <span>No differences found by the automated checks. This does not guarantee the bill is correct.</span>
                </div>
              ) : (
                rec.flags.map((f, i) => (
                  <div className="flag" key={i}>
                    <div className="flag-title">
                      <TriangleAlert size={16} aria-hidden /> {FLAG_LABELS[f.kind] ?? f.kind}
                    </div>
                    <div>{f.message}</div>
                    {f.evidence.length > 0 && f.evidence.some(Boolean) && (
                      <div className="flag-evidence mono">Source: {f.evidence.filter(Boolean).slice(0, 3).join(" | ")}</div>
                    )}
                  </div>
                ))
              )}

              <h2 style={{ marginTop: 24 }}>Extracted line items</h2>
              <p className="notice">Values were read by AI from the uploaded image. Verify them against your original document.</p>
              <div className="card table-wrap scroll-x">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Code</th>
                      <th className="amount">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rec.bill?.lines.map((l, i) => (
                      <tr key={i}>
                        <td data-label="Date">{l.date}</td>
                        <td data-label="Code" className="mono">{l.code}</td>
                        <td data-label="Amount" className="amount">{money(l.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </>
  );
}
