# Break-testing (targeted mutation)

Break-testing is the core mechanism of the gate. It answers the one question a green test suite
cannot answer on its own: **"if the behavior were actually broken, would any test notice?"**

A green suite proves the tests pass. It does not prove the tests would fail when they should. Those
are different claims, and the gap between them is where fake-green suites live — tests with no
assertion, tests that assert on a mock instead of real behavior, tests written to lock in whatever
the code currently does. Break-testing closes that gap by *making* the behavior broken and checking
that a test screams.

## The procedure

For each intent you're verifying:

```
1. Pick the smallest production-code change that SHOULD violate this intent.
2. Apply it.
3. Run the test suite.
4. Expect: at least one test goes red — AND the red test is the one semantically
   tied to this intent (not some unrelated collateral failure).
5. If the suite stays fully green → this intent is fake-green → record a gap.
6. Revert the change immediately (no-fix rule — you never leave code modified).
```

Do this for **every Critical intent** (mandatory), and **sample** it for Peripheral intents. Core
intents sit in between — cover the ones where breakage would actually hurt.

## Worked example

Spec intent: *"A negative amount must be rejected."*

1. Locate the guard, e.g. `if (amount < 0) throw new Error('amount must be >= 0')`.
2. Smallest breaking change: turn the guard off — `if (false) ...`.
3. Run the suite.
4. **Good outcome:** a test like `rejects negative amount` goes red. The intent is genuinely
   verified. Revert and move on.
5. **Bad outcome:** everything stays green. Nothing actually checks the negative-amount rule — the
   green you saw was meaningless. Record a gap citing this intent.

## Choosing a good mutation

The mutation has to be one that *genuinely violates the intent* — otherwise a green suite is the
correct result and you've learned nothing. Good mutations:

- **Flip the guard that enforces the rule:** `<` → `<=`, `if (cond)` → `if (false)`, remove a
  `return`/`throw` on the error path.
- **Neutralize the transformation:** make a function return its input unchanged, a discount return
  0, a formatter return the raw value.
- **Break the boundary write/read:** skip the DB write, drop the field from the payload, return a
  hardcoded value instead of the fetched one.

Avoid mutations that are *too* destructive (e.g. deleting a whole function so unrelated things
error out) — a cascade of unrelated failures doesn't tell you whether *this specific intent* is
tested. You want a surgical change that maps to exactly one behavior.

## Reading the result honestly

- **A test went red, and it's the right test** → intent genuinely verified. ✅
- **A test went red, but it's an unrelated test / a compile error** → inconclusive. The suite
  noticed *something*, but maybe not *this* behavior. Refine the mutation to be more surgical and
  retry.
- **Nothing went red** → gap. The behavior is not protected, regardless of how green the suite
  looked. This is the finding break-testing exists to produce.

## If a mutation-testing tool exists

Tools like Stryker (JS), PIT (Java), mutmut/cosmic-ray (Python) automate whole-suite mutation. They
can be a useful *supplement* — a low surviving-mutant score is a strong signal. But this skill is
tool-agnostic and does not depend on them. Targeted, intent-anchored mutation by hand is cheaper
(you mutate only what maps to a spec intent, not the entire codebase) and more meaningful (each
mutation is tied to a behavior a human actually cares about), so it stays the default. If a tool is
present, read its surviving-mutant report as extra evidence, not as a replacement for checking your
Critical intents by hand.
