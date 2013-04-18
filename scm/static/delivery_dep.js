$(document).ready(function()
{

	// Update version field if logical component is selected
	$('#mainForm').find('.ifjs').show();
	$('#mainForm').find('select[id$=target]').each(function() {
		t = $(this);
		if (!t.val() && t.parent().attr('name'))
			t.val(t.parent().attr('name'));
	});
	$('#mainForm').on('change', 'select[id$=target]', load_lc_versions);
	$('#mainForm').find('select[id$=target]').change();
	
	
	// Add a formset
	$('.add_content').show();
	$('.add_content').click(function()
	{
		var t = $(this);
		var subform = t.parents('div.subform');
		var to_copy_container = subform.find('div.addFS');
		var form_idx = subform.find('input[id$=TOTAL_FORMS]').val();
		
		subform.find('div.iifss').append(to_copy_container.html().replace(/__prefix__/g, form_idx));
		
		subform.find('input[id$=TOTAL_FORMS]').val(parseInt(form_idx) + 1);
	});
	
	// Remove a formset
	$('.deleteContent:button').show();
	$('div.iifss').on('click', '.deleteContent:button', function()
	{
		var fs = $(this).parents('div.subformset');
		var deleteBox = fs.find('input:checkbox[id$=DELETE]');
		deleteBox.attr('checked', true);
		fs.hide();
	});
	$('input:checkbox[id$=DELETE]').hide();
	
});

function load_lc_versions()
{
	var t = $(this);
	var subform = t.parents('div.subformset');
	var selected_lc_id = t.val();
	var url = versionfinder.replace("99999999", selected_lc_id);
	var version_list = subform.find('select[id$=version]');
	var previous_version = version_list.val();
//alert(previous_version);
//alert(version_list.html());

	version_list.empty();

	// If nothing selected - abort after emptying list
	if (!selected_lc_id)
		return;

	$.ajax(
	{
		url : url,
		type : "GET",
		dataType : "json"
	}).done(function(json)
	{
		// First "---------" line without value
		var selected = "";
		var opt = $("<option value >---------</option>");
		version_list.append(opt);
		
		// One line per result
		for ( var i = json.length - 1; i >= 0; i--)
		{
			var id = $.trim(json[i][0]);
			var version = json[i][1];
			selected = "";
			if (previous_version && id === previous_version)
				selected = "selected='selected'";
			opt = $("<option value='" + id + "' " + selected + ">" + version + "</option>");
			version_list.append(opt);
		}
	})
}