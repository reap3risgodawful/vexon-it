# Field tracker regression checks

Run from the repository root with Node.js (no npm dependencies):

```sh
node --test tests/field-tracker.test.cjs
```

The test harness extracts and executes the actual inline script from `index.html` using Node's VM and synthetic DOM/localStorage objects. It covers normal saved records, malformed JSON and invalid record shapes, explicit storage recovery, storage failures, HTML-sensitive names and cities, nonnegative decimal rates including zero, and adding/removing records.

The harness checks the renderer's escaped HTML output and simulated DOM state. It does not replace a browser rendering, accessibility, or real customer-data review. All records in the tests are fictional; tests do not open a browser, make requests, or access browser storage.
