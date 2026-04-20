API endpoint:
top_langs

SELECT
    p.lang,
    la.name as lang_name,
    COUNT(p.target) AS targets,
    SUM(
        CASE
            WHEN p.word IS NOT NULL
            AND p.word != 0
            AND p.word != '' THEN p.word
            WHEN translate_type = 'all' THEN w.w_all_words
            ELSE w.w_lead_words
        END
    ) AS words,
    SUM(
        CASE
            WHEN v.views IS NULL
            OR v.views = '' THEN 0
            ELSE CAST(v.views AS UNSIGNED)
        END
    ) AS views
FROM
    pages p
    LEFT JOIN users_list u ON p.user = u.username
    LEFT JOIN words w ON w.w_title = p.title
    LEFT JOIN views_new_all v ON p.target = v.target
    AND p.lang = v.lang
    LEFT JOIN langs la ON p.lang = la.code
WHERE
    p.target != ''
    AND p.target IS NOT NULL
    AND p.user != ''
    AND p.user IS NOT NULL
    AND p.lang != ''
    AND p.lang IS NOT NULL
GROUP BY
    p.lang
ORDER BY
    2 DESC



top_users:

SELECT
    p.user,
    COUNT(p.target) AS targets,
    SUM(
        CASE
            WHEN p.word IS NOT NULL
            AND p.word != 0
            AND p.word != '' THEN p.word
            WHEN translate_type = 'all' THEN w.w_all_words
            ELSE w.w_lead_words
        END
    ) AS words,
    SUM(
        CASE
            WHEN v.views IS NULL
            OR v.views = '' THEN 0
            ELSE CAST(v.views AS UNSIGNED)
        END
    ) AS views
FROM
    pages p
    LEFT JOIN users_list u ON p.user = u.username
    LEFT JOIN words w ON w.w_title = p.title
    LEFT JOIN views_new_all v ON p.target = v.target
    AND p.lang = v.lang
    LEFT JOIN langs la ON p.lang = la.code
WHERE
    p.target != ''
    AND p.target IS NOT NULL
    AND p.user != ''
    AND p.user IS NOT NULL
    AND p.lang != ''
    AND p.lang IS NOT NULL
GROUP BY
    p.user
ORDER BY
    2 DESC
