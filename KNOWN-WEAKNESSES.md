# Known weaknesses (planted on purpose, fixed in phase 6)

This app is a target for the [CS54 AI-BOM security lab](https://github.com/pankhuri-labs/CaseStudies/tree/main/CS54-AI-BOM-and-AI-Security-Posture-Lab). IDs match the CS54 [threat model](https://github.com/pankhuri-labs/CaseStudies/blob/main/CS54-AI-BOM-and-AI-Security-Posture-Lab/docs/threat-model.md). Attack tests that prove each one are in `tests/test_attacks.py` (phase 3): they assert the safe behaviour and are marked as expected failures while the weakness is present. Phase 6 fixed them and removed the markers; the second table shows each fix.

| ID | Weakness | Where | OWASP LLM 2025 |
| --- | --- | --- | --- |
| AT-09 | Model output runs as SQL with no parsing or allow-list, on a read-write connection, and several statements are allowed | `app/assistant.py` `ask()`, `app/db.py` `connect()` | LLM05, LLM06 |
| AT-10 | The "own region only" rule lives only in the prompt; the database does not enforce it, and the restricted salaries table is reachable | `prompts/system.txt`, `app/assistant.py` | LLM02 |

## Phase 6 fixes

Each fix follows a playbook in the CS54 remediation plan. A fix counts as closed only when its attack test passes **and** the AI-BOM rescan no longer raises the signal.

| ID | Playbook | Fix | Proof |
| --- | --- | --- | --- |
| AT-09 | PB-09 | The assistant opens the database read-only, runs exactly one statement, and an SQLite authorizer allows only SELECT. Anything else returns a refusal instead of running. At most 200 rows come back. | `test_at09_question_cannot_delete_data`, `test_at09_stacked_statement_cannot_drop_a_table`, `test_at09_assistant_opens_the_database_read_only` |
| AT-10 | PB-10 | The own-region rule moved from the prompt into the database. Each session gets a view, `my_orders`, holding only the signed-in employee's region, and the authorizer allows reads only through that view. The salaries table and the base orders table are denied whatever SQL the model writes. | `test_at10_employee_sees_only_own_region`, `test_at10_salaries_are_not_reachable`, `test_at10_model_cannot_read_the_base_table` |

The lesson from AT-10: a rule written only in the prompt is a request to the model, not a control. The phase 2 scanner could not see this weakness; phase 6 adds a detector for it.
