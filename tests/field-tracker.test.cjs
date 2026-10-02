const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

// Exercise the shipped inline application, rather than a duplicate of its logic.
const html = readFileSync(join(__dirname, '..', 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
assert.equal(scripts.length, 1, 'Update the harness if the page gains more scripts');
const app = new vm.Script(scripts[0][1], { filename: 'index.html inline script' });

class Element {
  constructor() {
    this.value = '';
    this.innerHTML = '';
    this.hidden = false;
    this.validityMessage = '';
    this.reportedValidity = 0;
    const classes = new Set();
    this.classList = {
      add: name => classes.add(name),
      remove: name => classes.delete(name),
      contains: name => classes.has(name),
      toggle: name => classes.has(name) ? classes.delete(name) : classes.add(name),
    };
  }
  set textContent(value) { this.text = String(value); }
  get textContent() { return this.text || ''; }
  setCustomValidity(message) { this.validityMessage = message; }
  reportValidity() { this.reportedValidity++; return !this.validityMessage; }
  focus() { this.focused = true; }
}

function openPage(initial, failures = {}) {
  const elements = new Map([...html.matchAll(/\bid="([^"]+)"/g)]
    .map(match => [match[1], new Element()]));
  const values = new Map(initial === undefined ? [] : [['vexon_clients', initial]]);
  const writes = [];
  const removals = [];
  const document = {
    getElementById(id) {
      assert.ok(elements.has(id), 'The page must contain element ' + id);
      return elements.get(id);
    },
    querySelectorAll(selector) {
      return selector === '.page'
        ? [...elements].filter(([id]) => id.startsWith('page-')).map(([, el]) => el)
        : [...elements].filter(([id]) => id.startsWith('nav-')).map(([, el]) => el);
    },
    querySelector() { return new Element(); },
  };
  const localStorage = {
    getItem(key) {
      if (failures.read) throw new Error('Storage unavailable');
      return values.has(key) ? values.get(key) : null;
    },
    setItem(key, value) {
      if (failures.write) throw new Error('Storage quota exceeded');
      writes.push([key, value]);
      values.set(key, value);
    },
    removeItem(key) {
      if (failures.remove) throw new Error('Storage unavailable');
      removals.push(key);
      values.delete(key);
    },
  };
  const context = vm.createContext({ document, localStorage });
  app.runInContext(context, { timeout: 1000 });
  return {
    elements, values, writes, removals, context,
    element: id => elements.get(id),
    clients: () => JSON.parse(vm.runInContext('JSON.stringify(clients)', context)),
    invoke: expression => vm.runInContext(expression, context, { timeout: 1000 }),
    add(name, rate, city = '') {
      elements.get('cf-name').value = name;
      elements.get('cf-rate').value = rate;
      elements.get('cf-city').value = city;
      elements.get('client-form').classList.add('open');
      vm.runInContext('addClient()', context, { timeout: 1000 });
    },
  };
}

function assertLiteralMarkup(page, name, city) {
  const rendered = page.element('client-list').innerHTML;
  assert.ok(rendered.includes(name));
  assert.ok(rendered.includes(city));
  assert.doesNotMatch(rendered, /<(?:img|svg|script)\b/i,
    'Untrusted input must not introduce executable elements');
}

test('normal saved records load intact without rewriting storage', () => {
  const records = [{ name: 'First', rate: 200, city: 'Pharr' },
    { name: 'Second', rate: 125.5, city: null }, { name: 'Third', rate: 0 }];
  const raw = JSON.stringify(records);
  const page = openPage(raw);
  assert.deepEqual(page.clients(), records);
  assert.equal(page.values.get('vexon_clients'), raw);
  assert.equal(page.writes.length, 0);
  assert.equal(page.removals.length, 0);
  assert.equal(page.element('client-count').textContent, '3');
  assert.equal(page.element('mrr-display').textContent, '$325.5');
  assert.equal(page.element('tracker-storage-notice').hidden, true);
  assert.match(page.element('client-list').innerHTML, /RGV/);
});

test('missing storage initializes an empty, working tracker', () => {
  const page = openPage();
  assert.deepEqual(page.clients(), []);
  assert.equal(page.element('monthly-total').textContent, '$0');
  page.add('New client', '200', 'Harlingen');
  assert.deepEqual(page.clients(), [{ name: 'New client', rate: 200, city: 'Harlingen' }]);
  assert.equal(page.element('client-count').textContent, '1');
  assert.equal(page.element('monthly-total').textContent, '$200');
  assert.equal(page.element('cf-name').value, '');
  assert.equal(page.element('client-form').classList.contains('open'), false);
});

for (const raw of ['{broken JSON', '', 'null', '{}', '"string"',
  '[null]', '[{"name":"Bad rate","rate":"200"}]',
  '[{"name":"Negative","rate":-1}]', '[{"name":"Huge","rate":1e999}]',
  '[{"name":"City","rate":20,"city":{}}]', '[{"name":12,"rate":20}]']) {
  test('unreadable saved data is retained and does not break the page: ' + raw, () => {
    const page = openPage(raw);
    assert.deepEqual(page.clients(), []);
    assert.equal(page.element('mrr-display').textContent, '$0');
    assert.equal(page.element('tracker-storage-notice').hidden, false);
    assert.equal(page.element('tracker-clear-storage').hidden, false);
    assert.match(page.element('tracker-storage-message').textContent, /not been changed/);
    page.invoke("switchTab('income')");
    assert.equal(page.element('page-income').classList.contains('active'), true);
    page.add('Must not overwrite unreadable storage', '200');
    assert.equal(page.values.get('vexon_clients'), raw);
    assert.equal(page.writes.length, 0);
    assert.equal(page.removals.length, 0);
    assert.deepEqual(page.clients(), []);
  });
}

test('explicit recovery clear enables saving new records', () => {
  const page = openPage('{broken');
  page.invoke('clearUnreadableClients()');
  assert.deepEqual(page.removals, ['vexon_clients']);
  assert.equal(page.values.has('vexon_clients'), false);
  assert.equal(page.element('tracker-storage-notice').hidden, true);
  page.add('Recovered tracker', '12.50');
  assert.deepEqual(page.clients(), [{ name: 'Recovered tracker', rate: 12.5, city: '' }]);
  assert.equal(page.writes.length, 1);
});

test('recovery action cannot clear readable existing records', () => {
  const raw = '[{"name":"Keep","rate":200,"city":"Pharr"}]';
  const page = openPage(raw);
  page.invoke('clearUnreadableClients()');
  assert.equal(page.removals.length, 0);
  assert.equal(page.values.get('vexon_clients'), raw);
  assert.equal(page.clients().length, 1);
});

test('storage access and clearing failures remain usable and retain data', () => {
  const raw = '{broken';
  const page = openPage(raw, { read: true, remove: true });
  assert.equal(page.element('tracker-storage-notice').hidden, false);
  page.invoke('clearUnreadableClients()');
  assert.match(page.element('tracker-storage-message').textContent, /could not be cleared/);
  assert.equal(page.values.get('vexon_clients'), raw);
  page.add('Blocked write', '20');
  assert.equal(page.writes.length, 0);
});

test('stored names and cities render as literal text with all HTML delimiters escaped', () => {
  const name = '<img src=x onerror="globalThis.compromised=true"> & \'quoted\'';
  const city = '<svg/onload="globalThis.compromised=true">';
  const page = openPage(JSON.stringify([{ name, city, rate: 200 }]));
  assertLiteralMarkup(page,
    '&lt;img src=x onerror=&quot;globalThis.compromised=true&quot;&gt; &amp; &#39;quoted&#39;',
    '&lt;svg/onload=&quot;globalThis.compromised=true&quot;&gt;');
  assert.equal(page.context.compromised, undefined);
  assert.deepEqual(page.clients(), [{ name, city, rate: 200 }]);
});

test('new names and cities remain literal after save and reload', () => {
  const page = openPage();
  page.add('<script>bad()</script>', '25.25', 'Town <b> & "test"');
  const reloaded = openPage(page.values.get('vexon_clients'));
  for (const current of [page, reloaded]) {
    assertLiteralMarkup(current, '&lt;script&gt;bad()&lt;/script&gt;', 'Town &lt;b&gt; &amp; &quot;test&quot;');
    assert.equal(current.clients()[0].rate, 25.25);
  }
});

for (const rate of ['', '  ', '-1', '-0.50', '25oops', '25.50oops',
  'Infinity', 'NaN', '0x10', '1e2', '12.345']) {
  test('invalid monthly rate is rejected without changing records: ' + JSON.stringify(rate), () => {
    const page = openPage();
    page.add('Do not save', rate, 'Pharr');
    assert.deepEqual(page.clients(), []);
    assert.equal(page.writes.length, 0);
    assert.match(page.element('cf-rate').validityMessage, /zero or more/);
    assert.equal(page.element('cf-rate').reportedValidity, 1);
    assert.equal(page.element('cf-name').value, 'Do not save');
    assert.equal(page.element('client-form').classList.contains('open'), true);
  });
}

for (const [input, expected] of [['0', 0], ['0.00', 0], ['12.50', 12.5], ['.50', 0.5], ['200', 200]]) {
  test('valid full decimal rate saves without truncation: ' + input, () => {
    const page = openPage();
    page.add('Fictional client', input);
    assert.equal(page.clients()[0].rate, expected);
    assert.equal(JSON.parse(page.values.get('vexon_clients'))[0].rate, expected);
    assert.equal(page.element('cf-rate').validityMessage, '');
    assert.match(page.element('client-list').innerHTML, new RegExp('\\$' + String(expected).replace('.', '\\.') + '/mo'));
  });
}

test('a corrected rate clears the prior validation error and saves', () => {
  const page = openPage();
  page.add('Corrected', '-5');
  page.element('cf-rate').value = '5.25';
  page.invoke('addClient()');
  assert.equal(page.clients()[0].rate, 5.25);
  assert.equal(page.element('cf-rate').validityMessage, '');
});

test('add and remove persistence failures retain existing records and form values', () => {
  const raw = '[{"name":"Keep","rate":200,"city":"Pharr"}]';
  const page = openPage(raw, { write: true });
  page.add('Unsaved', '12.50', 'Harlingen');
  assert.deepEqual(page.clients(), [{ name: 'Keep', rate: 200, city: 'Pharr' }]);
  assert.equal(page.element('cf-name').value, 'Unsaved');
  assert.equal(page.element('cf-rate').value, '12.50');
  assert.equal(page.element('client-count').textContent, '1');
  page.invoke('removeClient(0)');
  assert.equal(page.clients().length, 1);
  assert.equal(page.values.get('vexon_clients'), raw);
  assert.match(page.element('tracker-storage-message').textContent, /could not be saved/);
});

test('removing one client persists the remaining record and updates totals', () => {
  const page = openPage('[{"name":"Remove","rate":200},{"name":"Keep","rate":12.5}]');
  page.invoke('removeClient(0)');
  assert.deepEqual(page.clients(), [{ name: 'Keep', rate: 12.5 }]);
  assert.equal(page.element('monthly-total').textContent, '$12.5');
  assert.equal(JSON.parse(page.values.get('vexon_clients')).length, 1);
});
