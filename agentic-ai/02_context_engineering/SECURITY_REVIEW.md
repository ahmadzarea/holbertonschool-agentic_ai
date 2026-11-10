# Security Review

## 1. Prompt used to request the fix

```text
ROLE:
You are a senior security engineer refactoring legacy Node.js code.

CONTEXT:
The file @agentic-ai/02_context_engineering/src/legacy_auth.js contains a critical
SQL injection vulnerability. User input is being concatenated directly into a SQL
query string instead of being passed as a parameter.

TASK:
Refactor the vulnerable query in @agentic-ai/02_context_engineering/src/legacy_auth.js to use a parameterized (prepared) query instead of string concatenation, eliminating the SQL injection risk.

CONSTRAINTS:
- Do not change the function signature(s) in @agentic-ai/02_context_engineering/src/legacy_auth.js.
- Do not change the shape/structure of the object returned on a successful authentication.
- Do not modify @agentic-ai/02_context_engineering/test_security.js.
- Keep the fix scoped only to the injection vulnerability, no unrelated refactoring, renaming, or style changes.

VALIDATION:
The existing test suite at @agentic-ai/02_context_engineering/test_security.js must continue to pass after the change, including both the legitimate login test case and the injection test case (which should now correctly fail/block the attack instead of succeeding).
```

## 2. Identified vulnerability

**Type:** SQL injection (CWE-89). **Severity:** Critical.

`authenticateUser(email, password)` built its query by concatenating the raw user input into the SQL string:

```javascript
const sql = "SELECT * FROM users WHERE email = '" + email + "' AND password = '" + password + "'";
```

An attacker could close the string literal and add their own SQL. With the email `admin@entreprise.com' OR '1'='1`, the query became:

```sql
SELECT * FROM users WHERE email = 'admin@entreprise.com' OR '1'='1' AND password = 'hack'
```

The `OR '1'='1'` condition is always true, so the attacker got past authentication without a valid password and received an admin user record.

## 3. Changes proposed by the Agent

- **`authenticateUser`:** The SQL text is now a fixed query with placeholders, and the user values are passed separately as bound parameters. User input is treated only as data and can no longer change the query structure.

  ```javascript
  const sql = "SELECT * FROM users WHERE email = ? AND password = ?";
  const results = db.query(sql, [email, password]);
  ```

- **Mock `db` connector:** `query(sql)` became `query(sql, params = [])`, matching the calling pattern of real drivers such as `mysql2` and `pg`. The legitimate-login check now matches the placeholder query together with the bound values, and the log line also prints the parameters.
- **Unchanged:** the `authenticateUser(email, password)` signature, the returned objects (`{ success: true, user }` / `{ success: false, message }`), and `test_security.js`.

**Remaining recommendation (out of scope):** passwords are still compared in plaintext. Store salted hashes (e.g. bcrypt or argon2) and verify them in application code.

## 4. Test results (`node test_security.js`)

### Before the fix — FAILED (exit code 1)

```text
=== Starting security test suite (Task 2) ===

Test 1 : Legitimate connection...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = 'dev@entreprise.com' AND password = 'password123'
-> OK

Test 2 : SQL injection attempt...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = 'admin@entreprise.com' OR '1'='1' AND password = 'hack'
❌ FAILED: FAILLE CRITIQUE DÉTECTÉE : L'injection SQL a réussi ! Votre prompt IA n'a pas sécurisé la requête.

true !== false

-> Relaunch your Agent with better instructions to fix the flaw.
```

### After the fix — PASSED (exit code 0)

```text
=== Starting security test suite (Task 2) ===

Test 1 : Legitimate connection...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = ? AND password = ? | Paramètres : ["dev@entreprise.com","password123"]
-> OK

Test 2 : SQL injection attempt...
[DB ENGINE] Exécution de la requête : SELECT * FROM users WHERE email = ? AND password = ? | Paramètres : ["admin@entreprise.com' OR '1'='1","hack"]
-> OK

✅ PASSED: The code has been properly secured by the AI agent.
```

The injection payload now arrives only as a bound parameter value and never becomes part of the SQL text, so authentication correctly fails.
