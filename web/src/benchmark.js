export function metric(value) { return value == null ? "N/A" : Number(value).toFixed(4); }
export function milliseconds(value) { return value == null ? "N/A" : `${Number(value).toFixed(2)} ms`; }

export function casesToCsv(cases) {
  const columns = ["case_id", "repetition", "relevant_chunk_ids", "retrieved_chunk_ids", "precision_at_k", "recall_at_k", "reciprocal_rank", "ndcg_at_k", "latency_ms"];
  const escape = (value) => `"${String(Array.isArray(value) ? value.join("|") : value ?? "").replaceAll('"', '""')}"`;
  return [columns.join(","), ...cases.map((item) => columns.map((column) => escape(item[column])).join(","))].join("\n");
}

export function download(name, content, type) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([content], { type }));
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}
