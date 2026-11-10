# **Context Engineering**

## Prompt

```
understand the repository access pattern and the exception handling that exists in here @user.repository.js  and here @user.service.js 

I want to generate a new data export service which export user data, this new service should follow the same access pattern. 
```

## Files provided as context

- `src/services/user.service.js`
- `src/repositories/user.repository.js`

## Generated service

- Name: `exportUserData`
- Path: `src/services/data_export.service.js`

## Existing architecture elements reused by AI

- **Data access:** the new service only reads through the `userRepository` singleton and never touches `db` directly.
- **Error handling:** the repository still returns `null` for a missing user. The service turns that into a plain Error with the same message `UserService` uses, so callers can catch both services the same way.
- **Exports and async:** the method is async, and the module exports one shared instance, just like `UserService`.