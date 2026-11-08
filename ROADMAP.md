# Roadmap

## A. Core Features
- [x] Raise exceptions / build responses dynamically via `add_result`
- [x] Per-call result queues (different result for the first and second call)
- [ ] `create_inline_query` and `create_chat_member_updated` factories
- [ ] `Dispatcher` helper to feed an update and return recorded requests

## B. Test Coverage
- [x] MockedSession and factory unit tests
- [ ] Tests for factories with `bot` binding for every event type
- [ ] Python 3.9 / 3.12 CI matrix

## C. Architecture & Refactoring
- [ ] Split request inspection helpers into a mixin
- [ ] Typed `py.typed` marker and mypy configuration

## D. Performance & Polish
- [ ] Usage guide with FSM and middleware examples in README
- [ ] pytest plugin exposing `bot` and `session` fixtures
