import assert from "node:assert/strict";

import { getValidatableActions, isActionMeaningful } from "./technicalReportsActionHelpers.js";

assert.equal(isActionMeaningful({ __userCreated: false }), false, "a??o vazia com __userCreated false n?o deve ser significativa");
assert.equal(isActionMeaningful({ source_id: "abc-123" }), false, "source_id isolado n?o deve tornar a a??o significativa");
assert.equal(isActionMeaningful({ __userCreated: true }), true, "a??o criada manualmente deve ser significativa");
assert.equal(isActionMeaningful({ place_action: "Pra?a XV" }), true, "campo operacional preenchido deve tornar a a??o significativa");

const validatable = getValidatableActions([
  { __userCreated: false },
  { source_id: "abc-123" },
  { __userCreated: true },
  { final_hour: "18:00" },
]);

assert.equal(validatable.length, 2, "somente duas a??es devem ser validadas");
assert.deepEqual(validatable.map(({ index }) => index), [2, 3], "devem permanecer apenas as a??es reais");

console.log("technicalReportsActionHelpers.test.mjs: OK");
