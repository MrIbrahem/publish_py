
/**
 * @param {any} data
 * @param {string} term
 */
function filterData(data, term) {
	// @ts-ignore
	return $.map(data, function (/** @type {{ code: string; name: any; autonym: any; }} */ item) {
		if (item) {
			if (item.code.toLowerCase().indexOf(term.toLowerCase()) === 0) {
				return {
					label: `${item.code} - ${item.name} (${item.autonym})`,
					value: item.code
				};
			}
		}
	});
}


// attach autocomplete behavior to input field
// @ts-ignore
$(".td_user_input").autocomplete({
	source: function (/** @type {{ term: any; }} */ request, /** @type {(arg0: any) => void} */ response) {
		// make AJAX request to Wikipedia API
		// @ts-ignore
		$.ajax({
			url: document.location.origin + "/api/users",
			dataType: "json",
			data: {
				userlike: request.term
			},
			success: function (/** @type {{ results: any; }} */ data) {
				// extract titles from API response and pass to autocomplete
				// @ts-ignore
				response($.map(data.results, function (/** @type {{ username: any; }} */ item) {
					return item.username
				}));
			}
		});
	}
});

/**
 * @type {null}
 */
let cachedData = null; // Variable for temporary data storage

// @ts-ignore
$(".lang_input").autocomplete({
	source: function (/** @type {{ term: any; }} */ request, /** @type {(arg0: any) => void} */ response) {
		// If data is already cached, use it directly
		if (cachedData) {
			const filteredData = filterData(cachedData, request.term);
			response(filteredData);
			return;
		}

		// Fetch data from API only once on first call
		// @ts-ignore
		$.ajax({
			url: document.location.origin + "/api/langs",
			dataType: "json",
			success: function (/** @type {{ results: any; }} */ data) {
				cachedData = data.results;
				const filteredData = filterData(cachedData, request.term);
				response(filteredData);
			}
		});
	}
});

