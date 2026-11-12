# 0. Forge the "QA Engineer Strict" Agent

This is an Agentic E-Commerce microservice in vanilla Node.js, tested with Jest, with no TypeScript.

`cart_calculator.js` is legacy technical debt: the rest of the app works in cents, but this calculator still returns euros with two decimal places. That behavior stays as-is for now.

The absolute QA rule is that `/src` is read-only during test generation. Scope is tests only; business logic is not refactored or patched.

The next step is a solid unit-test suite for the cart calculator before any migration.