// @ts-nocheck

let allResults = [];
let originalResults = [];

function populateFilterOptions(results) {
    const unique = (key, transform = val => val) => {
        return [...new Set(results.map(item => transform(item[key])))].filter(Boolean).sort();
    };

    const options = {
        year: unique('date', d => typeof d === 'string' ? d.split('-')[0] : ''),
        month: unique('date', d => typeof d === 'string' ? d.split('-')[1] : ''),
        // sourcetitle: unique('sourcetitle'),
        user: unique('user'),
        lang: unique('lang'),
        result: unique('result')
    };

    for (const [id, values] of Object.entries(options)) {
        const select = document.getElementById(id);
        select.innerHTML = '<option value="">-- All --</option>' +
            values.map(value => `<option data-tokens="${value}" value="${value}">${value}</option>`).join('');
    }
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
function render_reports_table() {
    // Load filters once only
    $.getJSON('/api/publish_reports')
        .done(function (json) {
            if (json && json.results) {
                populateFilterOptions(json.results);
                $('.selectpicker').selectpicker('refresh');
            }
        })
        .fail(function (xhr, status, error) {
            console.error('Failed to load filter options:', error);
            // Optionally show user-friendly error message
        });

    // إعداد DataTable
    let table = $('#resultsTable').DataTable({
        ajax: {
            url: '/api/publish_reports',
            data: function (d) {
                const formData = $('#filterForm').serializeArray();
                formData.forEach(field => {
                    if (field.value.trim()) {
                        d[field.name] = field.value;
                    }
                });
            },
            dataSrc: function (json) {
                // تخزين البيانات الأصلية كاملة
                originalResults = json.results;

                // تجميع الصفوف حسب الحقول المطلوبة
                const grouped = {};
                originalResults.forEach(item => {
                    const datePart = (typeof item.date === 'string') ? item.date.split(' ')[0] : '';
                    const key = [
                        datePart,
                        item.title,
                        item.user,
                        item.lang,
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
        },
        columns: [
            {
                data: 'id',
                visible: false
            },
            {
                data: null,
                title: "#",
                render: function (data, type, row, meta) {
                    return meta.row + 1;
                }
            },
            {
                data: 'date',
                title: "Date",
                render: function (data, type) {
                    if ((type === 'display' || type === 'filter') && typeof data === 'string') {
                        return data.split(' ')[0];
                    }
                    return data;
                },
            },
            {
                data: 'lang',
                title: "Language"
            },
            {
                data: null,
                title: "Title",
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
                title: "User"
            },
            {
                data: 'sourcetitle',
                title: "Source Title"
            },
            {
                data: null,
                title: "Result",
                render: function (data, type, row) {
                    // Display multiple buttons for grouped results
                    return row.resultsArray.map((res, index) => {
                        const id = row.idsArray[index];
                        const escapedRes = res;
                        const safeId = parseInt(id, 10); // Ensure ID is numeric
                        return `<span class="badge bg-secondary" style="cursor:pointer; margin-right:4px;" onclick="showDetails(${safeId})">${escapedRes}</span>`;
                    }).join('');
                }
            }
        ],
        order: [
            [1, 'asc']
        ],
        responsive: {
            details: true
        }
    });

    // حدث إرسال الفورم
    $('#filterForm').on('submit', function (e) {
        e.preventDefault();
        table.ajax.reload();
    });

    // زر إعادة التهيئة
    $('#resetBtn').on('click', function () {
        $('#filterForm')[0].reset();
        table.ajax.reload();
        $('.selectpicker').selectpicker('refresh');
    });
}
