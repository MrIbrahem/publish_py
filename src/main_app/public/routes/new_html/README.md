```
src/main_app/
├── config/
│   └── classes.py                    # ← نضيف NewHtmlConfig هنا
├── public/
│   └── routes/
│       └── new_html/
            ├── __init__.py
            ├── routes.py                  # كلاس NewHtmlRoutes
            ├── config.py
            ├── services/
            │   ├── __init__.py
            │   ├── file_utils.py
            │   ├── http_client.py
            │   ├── mdwiki_api.py
            │   ├── transform_api.py
            │   ├── segment_api.py
            │   └── json_data.py
            └── utils.py
└── services/
    └── new_html/
        ├── __init__.py
        ├── clients.py                # mdwiki + transform + segment
        ├── storage.py                # cache + JSON index
        ├── html_utils.py             # remove_data_parsoid فقط حالياً
        └── process.py                # المنطق الرئيسي (بدون fix_wikitext الحقيقي)
```
