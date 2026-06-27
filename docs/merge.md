# Overview

# Code Sources

| Endpoint                            | status | Method    | Description                  | Source                                                                                                                                  |
| ----------------------------------- | ------ | --------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `/`                                 |        | GET       | Main entry                   | [Mdwiki-TD/mdwiki.toolforge.org](https://github.com/Mdwiki-TD/mdwiki.toolforge.org)                                                     |
| `/Translation_Dashboard`            |        | GET       | -                            | [Mdwiki-TD/Translation-Dashboard](https://github.com/Mdwiki-TD/Translation-Dashboard)                                                   |
| `/publish`, `/cxtoken` , `/reports` | ✔️     | POST      | Publish endpoint and Reports | [Mdwiki-TD/publish](https://github.com/Mdwiki-TD/publish)                                                                               |
| `/login`, `/logout`, `/callback`    | ✔️     | GET       | OAuth                        | [Mdwiki-TD/auth-repo](https://github.com/Mdwiki-TD/auth-repo)                                                                           |
| `/fixrefs`                          | ✔️     | GET, POST | Fix refs                     | [MrIbrahem/fix_refs_new_py](https://github.com/MrIbrahem/fix_refs_new_py) & [Mdwiki-TD/fix_refs](https://github.com/Mdwiki-TD/fix_refs) |
| `/api`                              |        | GET       | API                          | [Mdwiki-TD/TD_API](https://github.com/Mdwiki-TD/TD_API)                                                                                 |
| `/new_html`                         |        | GET       | -                            | [mdwikicx/new_html](https://github.com/mdwikicx/new_html)                                                                               |
| `/admin`                            |        | GET       | -                            | [Mdwiki-TD/tdc](https://github.com/Mdwiki-TD/tdc/)                                                                                      |

# End points

## Main entry

| Route    | Method | Description                                        | Status | Source                                                                                  |
| -------- | ------ | -------------------------------------------------- | ------ | --------------------------------------------------------------------------------------- |
| `/`      | GET    | Homepage                                           | ✔️     |                                                                                         |
| `/views` | GET    | PageViews                                          |        |                                                                                         |
| `/prior` | GET    | Prior List                                         |        | [Source](https://github.com/Mdwiki-TD/mdwiki.toolforge.org/tree/main/public_html/prior) |
| `/WHO`   | GET    | World Health Organization essential medicines list |        | [Source](https://github.com/Mdwiki-TD/mdwiki.toolforge.org/tree/main/public_html/WHO)   |

## Translation Dashboard

| Route                                      | Method | Description           | Status |
| ------------------------------------------ | ------ | --------------------- | ------ |
| `/Translation_Dashboard`                   | GET    | Homepage              |        |
| `/Translation_Dashboard/missing`           | GET    | Missing pages report  |        |
| `/Translation_Dashboard/leaderboard`       | GET    |                       | ✔️     |
| `/Translation_Dashboard/leaderboard/langs` | GET    | languages leaderboard | ✔️     |
| `/Translation_Dashboard/leaderboard/users` | GET    | users leaderboard     | ✔️     |

## Publish

Manages the final steps in the process of publishing Wikipedia articles that have been translated using the [ContentTranslation tool](https://github.com/mdwikicx/cx-1) in [medwiki.toolforge.org](http://medwiki.toolforge.org/). It takes the translated text in wikitext format, refines it further, and then publishes it to Wikipedia.

| Route | Method | Description | Status |
| ----- | ------ | ----------- | ------ |
| `/`   | GET    | Homepage    | ✔️     |

## Publish Reports

| Route      | Method | Description | Status |
| ---------- | ------ | ----------- | ------ |
| `/reports` | GET    | Homepage    | ✔️     |

## OAuth

| Route       | Method | Description | Status |
| ----------- | ------ | ----------- | ------ |
| `/login`    | GET    |             | ✔️     |
| `/callback` | GET    |             | ✔️     |
| `/logout`   | GET    |             | ✔️     |

## Fix refs

| Route | Method | Description | Status |
| ----- | ------ | ----------- | ------ |
| `/`   | GET    | Homepage    |        |

## API

| Route | Method | Description | Status |
| ----- | ------ | ----------- | ------ |
| `/`   | GET    | Homepage    |        |

## new html

| Route | Method | Description | Status |
| ----- | ------ | ----------- | ------ |
| `/`   | GET    | Homepage    |        |

## Admin

| Route | Method | Description | Status |
| ----- | ------ | ----------- | ------ |
| `/`   | GET    | Homepage    |        |
