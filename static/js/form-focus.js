/** Y0072003 */
/** Focuses forms to a specific element on page load */

/* Use the #first-field id as the field to select, unless an element has been specified elsewhere */
if (typeof first_field === 'undefined' || !first_field) {
	first_field = "#first-field";
}

$(document).ready(function() {
	if ($(first_field).length) {
		$(first_field).focus();
	}
});
