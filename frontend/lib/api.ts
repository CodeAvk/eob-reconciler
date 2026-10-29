export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type CaseStatus = "queued" | "processing" | "done" | "failed";

export interface Flag {
  kind: string;
  message: string;
  evidence: string[];
}

export interface BillLine {
  date: string;
  code: string;
  amount: string;
  source: string;
}

export interface CaseRecord {
  id: string;
  status: CaseStatus;
  created_at: string;
  updated_at: string;
  bill_name: string;
  eob_name: string;
  flags: Flag[];
  error: string | null;
  bill?: { lines: BillLine[]; stated_total: string; patient_owes: string };
  eob?: { patient_responsibility: string };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* keep default message */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const listCases = () => request<CaseRecord[]>("/api/cases");
export const getCase = (id: string) => request<CaseRecord>(`/api/cases/${id}`);

export function createCase(bill: File, eob: File) {
  const form = new FormData();
  form.append("bill", bill);
  form.append("eob", eob);
  return request<{ id: string; status: CaseStatus }>("/api/cases", {
    method: "POST",
    body: form,
  });
}

export const FLAG_LABELS: Record<string, string> = {
  sum_mismatch: "Total does not match line items",
  duplicate_line: "Possible duplicate charge",
  eob_mismatch: "Bill differs from EOB",
};
