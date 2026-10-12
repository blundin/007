# Specs

Specs are written and approved by humans. Agents read them and never edit them.

Each requirement the loop builds has an acceptance-criterion ID: a short area prefix and a number, such as `AUTH-03` or `PAGE-06`. Tests name the ID they verify with the criterion tag in the Project profile (`AGENTS.md`), and a scope is done when every ID in it has a passing tagged test.

A spec works best for the loop when it has:

- the criteria, each with its ID and exact required behavior
- a threat model that bounds adversarial testing by actor
- an open-questions list, so the project manager can flag what blocks a scope
