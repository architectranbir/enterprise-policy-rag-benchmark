import assert from "node:assert/strict";
import test from "node:test";
import { casesToCsv, metric, milliseconds } from "./benchmark.js";

test("formats benchmark values without inventing them", () => {
  assert.equal(metric(0.75), "0.7500");
  assert.equal(milliseconds(12.345), "12.35 ms");
  assert.equal(metric(null), "N/A");
  assert.equal(milliseconds(null), "N/A");
  assert.match(casesToCsv([{ case_id: "one", retrieved_chunk_ids: ["a", "b"] }]), /"a\|b"/);
});
