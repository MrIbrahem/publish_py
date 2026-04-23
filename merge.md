# Overview

This repository manages the final steps in the process of publishing Wikipedia articles that have been translated using the [ContentTranslation tool](https://github.com/mdwikicx/cx-1) in [medwiki.toolforge.org](http://medwiki.toolforge.org/). It takes the translated text in wikitext format, refines it further, and then publishes it to Wikipedia.

# Code Sources

| Endpoint                                                   | status | Method    | Description     | Source                                                                                                             |
| ---------------------------------------------------------- | ------ | --------- | --------------- | ------------------------------------------------------------------------------------------------------------------ |
| `/publish`, `/cxtoken`                                     | ✔️     | POST      | Publish endpint | [PHP Source](https://github.com/Mdwiki-TD/publish)                                                                 |
| `/reports`                                                 | ✔️     | GET       | publish Reports | [PHP Source](https://github.com/Mdwiki-TD/publish/tree/main/src/publish_reports)                                   |
| `/login`, `/logout`, `/callback`                           | ✔️     | GET       | OAuth auth      | [PHP Source](https://github.com/Mdwiki-TD/auth-repo)                                                               |
| `/fixrefs`                                                 | ✔️     | GET, POST | Fix refs        | [fix_refs_py](https://github.com/MrIbrahem/fix_refs_new_py) \| [PHP Source](https://github.com/Mdwiki-TD/fix_refs) |
| `/api`                                                     |        | GET       | API             | [PHP Source](https://github.com/Mdwiki-TD/TD_API)                                                                  |
| `/new_html`                                                |        | GET       | -               | [PHP Source](https://github.com/mdwikicx/new_html)                                                                 |
| `/admin`                                                   |        | GET       | -               | [PHP Source](https://github.com/Mdwiki-TD/tdc/)                                                                    |
| [Translation Dashboard](#Translation-Dashboard-End-points) |        | GET       | -               | [PHP Source](https://github.com/Mdwiki-TD/Translation-Dashboard)                                                   |

# Translation Dashboard End points

| Endpoint   | Method | Description        | Status |
| ---------- | ------ | ------------------ | ------ |
| `/`        | GET    | Homepage           | ✅     |
| `/missing` | GET    | Missing pages page | ✅     |
