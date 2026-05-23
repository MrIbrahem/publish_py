let UrlDone = [];

function add_data(ix, value, code) {
    $(`input[name="rows[${ix}][${code}]"]`).val(value);
}
function delete_row($row_id) {
    $(`#row_${$row_id}`).remove();
}

async function add_new_row() {
    const options = $('.catsoptions').html();
    const ii = $('#tab_data > tr').length + 1;

    const row = `
        <tr id="row_${ii}">
            <td data-order='${ii}' data-content='#'>${ii}</td>
            <td data-content="mdwiki title">
                <input class="form-control mdtitles" size="15" name="rows[${ii}][mdtitle]" required />
            </td>
            <td data-content="Campaign">
                <select class="form-select" name="rows[${ii}][cat]">${options}</select>
            </td>
            <td data-content="Type">
                <select name="rows[${ii}][type]" class="form-select">
                    <option value="lead">Lead</option>
                    <option value="all">All</option>
                </select>
            </td>
            <td data-content="User">
                <input class="form-control td_user_input" size="10" name="rows[${ii}][user]" required />
            </td>
            <td data-content="Language">
                <input class="form-control lang_input" size="2" name="rows[${ii}][lang]" required />
            </td>
            <td data-content="Wiki title">
                <input class="form-control" size="20" name="rows[${ii}][target]" required />
            </td>
            <td data-content="Published">
                <input class="form-control" size="10" name="rows[${ii}][pupdate]" placeholder='YYYY-MM-DD' required />
            </td>
            <td data-content="Delete">
                <div id="delete_${ii}">
                    <button type="button" class="btn btn-danger btn-sm" onclick="delete_row(${ii})">Delete</button>
                </div>
                <div id="load_${ii}" style="display: none;">
                    <i class="bi spinner-border spinner-border-sm"></i>
                </div>
            </td>
        </tr>
    `;

    $('#tab_data').append(row);
    return ii;
}

async function get_info(articleTitle, language) {
    const params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": articleTitle,
        "utf8": 1,
        "formatversion": "2",
        "rvprop": "timestamp|comment|user",
        "origin": "*",
        // "rvtag": "OAuth CID: 9394"
        "rvdir": "newer",
    };

    const url = `https://${language}.wikipedia.org/w/api.php?` + new URLSearchParams(params).toString();
    const response = await fetch(url, { method: "GET", mode: "cors" });

    const data = await response.json();
    return data;
}

async function get_page_info(language, articleTitle) {
    const data = await get_info(articleTitle, language);

    const revisions = data.query.pages[0].revisions[0];
    const user = revisions.user;
    // ---
    // 2025-01-26T12:40:17Z to 2025-01-26
    let pupdate = revisions.timestamp;
    pupdate = pupdate.split("T")[0];
    // ---
    let mdtitle = "";
    // Created by translating the page [[:mdwiki:Special:Redirect/revision/1438968|Entrectinib]] to:ar #mdwikicx
    // match Entrectinib
    const match = revisions.comment.match(/\[\[:mdwiki:Special:Redirect\/revision\/\d+\|(.*?)\]\]/);
    if (match) {
        mdtitle = match[1];
    }
    // ---
    const page_data = {
        "user": user,
        "pupdate": pupdate,
        "mdtitle": mdtitle
    };

    return page_data;
}

async function workinurl(url) {
    try {
        if (!url.includes("wikipedia.org")) {
            $("#alert_text").text("The link was ignored because it is not from Wikipedia.");
            $("#alert").show();
            return;
        }
        const parsedUrl = new URL(url);

        const hostnameParts = parsedUrl.hostname.split('.');
        if (hostnameParts.length < 3) {
            $("#alert_text").text("The link is not from a Wikipedia subreddit (does not contain a language code).");
            $("#alert").show();
            return;
        }
        const language = hostnameParts[0];

        const pathParts = parsedUrl.pathname.split('/wiki/');
        if (pathParts.length < 2) {
            $("#alert_text").text("The link does not contain a valid path to a Wikipedia article.");
            $("#alert").show();
            return;
        }
        if (UrlDone.includes(url)) {
            $("#alert_text").text("The link has already been added.");
            $("#alert").show();
            return;
        }
        const articleTitle = decodeURIComponent(pathParts[1]);

        console.log(`Language: ${language}\nArticle Name: ${articleTitle}`);

        const row_numb = await add_new_row();

        $(`#load_${row_numb}`).show();
        $(`#delete_${row_numb}`).hide();
        // ---
        add_data(row_numb, articleTitle, "target");
        add_data(row_numb, language, "lang");
        // ---
        const info = await get_page_info(language, articleTitle);
        // ---
        add_data(row_numb, info.user, "user");
        add_data(row_numb, info.pupdate, "pupdate");
        add_data(row_numb, info.mdtitle, "mdtitle");
        // ---
        UrlDone.push(url);
        // ---
        $(`#load_${row_numb}`).hide();
        $(`#delete_${row_numb}`).show();
        // ---

    } catch (error) {
        $("#alert_text").text("Invalid link! " + error);
        $("#alert").show();
    }
}

async function start_one_url(button) {
    $("#alert_text").text("");
    $("#alert").hide();

    // الحصول على العنصر الأب وهو `cardbody`
    const endpointContent = button.closest('.cardbody');

    // البحث عن جميع الحقول داخل العنصر الأب
    const paramInputs = endpointContent.querySelectorAll('.url');

    // عرض القيم في تنبيه
    paramInputs.forEach(input => {
        let url = input.value;
        workinurl(url);
    });
}
