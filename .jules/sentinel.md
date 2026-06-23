## 2025-05-15 - [Missing Standard Security Headers]
**Vulnerability:** The application was missing standard security headers (X-Frame-Options, X-Content-Type-Options, Referrer-Policy), leaving it vulnerable to clickjacking and MIME-sniffing attacks.
**Learning:** While Flask provides many security features, it does not inject these specific headers by default. They must be explicitly added, ideally via an `after_request` hook or a specialized extension like Flask-Talisman.
**Prevention:** Always implement a global response processor to inject standard security headers in every new Flask project.
