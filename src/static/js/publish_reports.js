
let allResults = [];
let originalResults = []; // لتخزين البيانات الأصلية قبل التجميع

function populateFilterOptions(results) {
    if (!results) return;
    const unique = (key, transform = val => val) => {
        return [...new Set(results.map(item => transform(item[key])))].filter(Boolean).sort();
    };

    // إعداد القيم الافتراضية
    const now = new Date();
    const defaults = {
        year: String(now.getFullYear()),
        month: String(now.getMonth() + 1).padStart(2, '0')
    };

    const options = {
        year: unique('year', d => String(d)),
        month: unique('month', d => String(d).padStart(2, '0')),
        user: unique('user'),
        lang: unique('lang'),
        result: unique('result')
    };

    // التأكد من وجود القيم الافتراضية ضمن الخيارات
    for (const key of ['year', 'month']) {
        if (!options[key].includes(defaults[key])) {
            options[key].push(defaults[key]);
            options[key].sort();
        }
    }

    for (const [id, values] of Object.entries(options)) {
        const select = document.getElementById(id);
        select.innerHTML = '<option value="">All</option>' +
            values.map(value => `<option value="${value}">${value}</option>`).join('');

        select.setAttribute('data-container', 'body');
        select.setAttribute('data-live-search-style', 'begins');
        select.setAttribute('data-bs-theme', 'auto');
        select.setAttribute('data-style', 'btn active');

        // select.value = defaults[id] || '';
    }

    $('.selectpicker').selectpicker('refresh');
}

async function load_form() {
    // // if $("#year") has options then console.warn("year has options"); and do nothing
    // if ($("#year option").length > 1) {
    //     console.warn("year has options");

    //     return;
    // }

    console.log("loading publish_reports_stats");
    try {
        const response = await $.getJSON('/api/publish_reports_stats');
        if (response?.results) {
            populateFilterOptions(response.results);
        }
    } catch (error) {
        console.error('Failed to load filter options:', error);
    }
    /*
    $.getJSON('/api/publish_reports_stats')
        .done(await function (json) {
            if (json && json.results) {
                populateFilterOptions(json.results);
            }
        })
        .fail(function (xhr, status, error) {
            console.error('Failed to load filter options:', error);
        });
    */
}

function getTableColumns() {
    return [{
        data: 'id',
        visible: false
    },
    {
        data: 'date',
        render: function (data, type) {
            if (type === 'display' || type === 'filter') {
                return data.split('T')[0];
            }
            return data;
        }
    },
    {
        data: 'lang',
        render: function (data, type) {
            return `<a href="/leaderboard/langs/${data}" target="_blank">${data}</a>`;
        }
    },
    {
        data: null,
        render: function (data, type, row) {

            // Validate language code (basic validation)
            const lang = /^[a-z]{2,3}$/.test(row.lang) ? row.lang : 'en';
            const title = encodeURIComponent(row.title || '');
            const escapedTitle = row.title || '';

            if (!title) return escapedTitle;

            return `<a href="https://${lang}.wikipedia.org/wiki/${title}" target="_blank" rel="noopener noreferrer">${escapedTitle}</a>`;
        }
    },
    {
        data: 'user',
        render: function (data, type) {
            return `<a href="/leaderboard/users/${data}" target="_blank">${data}</a>`;
        }
    },
    {
        data: 'sourcetitle',
        render: function (data, type) {
            return `<a href="https://mdwiki.org/wiki/${data}" target="_blank">${data}</a>`;
        }
    },
    {
        data: null,
        render: function (data, type, row) {
            // Display multiple buttons for grouped results
            return row.resultsArray.map((res, index) => {
                const id = row.idsArray[index];
                // remove .json from res
                const escapedRes = res.replace('.json', '');
                const safeId = parseInt(id, 10); // Ensure ID is numeric
                const uclass = (res == "success" || escapedRes == "success") ? "success" : "warning";
                return `<span class="btn d-inline-flex mb-2 px-2 py-1 fw-semibold text-${uclass}-emphasis bg-${uclass}-subtle border border-${uclass}-subtle rounded-2" onclick="showDetails(${safeId})">${escapedRes}</span>`;

            }).join('<br>');
        }
    }
    ]
}
function getFormData(d) {
    const formData = $('#filterForm').serializeArray();
    formData.forEach(field => {
        if (field.value.trim()) {
            d[field.name] = field.value;
        }
    });
}

function processTableData(json) {
    // تخزين البيانات الأصلية كاملة
    originalResults = json.results;

    // تجميع الصفوف حسب الحقول المطلوبة
    const grouped = {};
    originalResults.forEach(item => {
        const key = [
            item.date.split(' ')[0], // فقط جزء التاريخ بدون الوقت
            item.lang,
            item.title,
            item.user,
            item.sourcetitle
        ].join('|');

        if (!grouped[key]) {
            grouped[key] = {
                ...item,
                resultsArray: [item.result],
                idsArray: [item.id]
            };
        } else {
            grouped[key].resultsArray.push(item.result);
            grouped[key].idsArray.push(item.id);
        }
    });

    allResults = Object.values(grouped);
    $('#count_result').text(allResults.length);
    return allResults;
}

function setupEventHandlers(table) {

    // $('#searchBtn').on('click', function () {
    $('#filterForm').on('submit', function (e) {
        e.preventDefault();

        $('#loadingIndicator').show();

        table.ajax.reload(function () {
            $('#loadingIndicator').hide();
            $('#count_result').text(allResults.length);
        });
    });

    $('#resetBtn').on('click', function () {
        $('#filterForm')[0].reset();
        table.ajax.reload(function () {
            $('#count_result').text(allResults.length);
        });
    });
}

function showDetails(id) {
    // Search in original data
    const result = originalResults.find(row => row.id == id);
    if (!result) {
        document.getElementById('modalData').textContent = 'Data not found.';
        return;
    }

    try {
        const json = typeof result.data === 'string' ? JSON.parse(result.data) : result.data;
        // Use textContent to prevent XSS
        const formattedJson = JSON.stringify(json, null, 2);
        document.getElementById('modalData').textContent = formattedJson;
        const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
        modal.show();
    } catch (e) {
        console.error('JSON parsing error:', e);
        document.getElementById('modalData').textContent = 'Unable to parse data.';
    }
}

async function newDataTable() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const end_point = `/api/publish_reports`;

    // إعداد DataTable
    let table = $('#resultsTable').DataTable({
        ajax: {
            url: end_point,
            data: getFormData,
            dataSrc: processTableData
        },
        columns: getTableColumns(),
        // saveState: true,
        order: [
            [1, 'desc']
        ],
        lengthMenu: [
            [100, 200, 500, 1000],
            [100, 200, 500, 1000]
        ]
    });
    return table;
}
