$(document).ready(function()
{
	// Add a formset
	$('#add_content').show();
	$('#add_content').click(function()
	{
		var form_idx = $('#id_iis-TOTAL_FORMS').val();
		$('#iisf').append($('#emptyformset').html().replace(/__prefix__/g, form_idx));
		$('#id_iis-TOTAL_FORMS').val(parseInt(form_idx) + 1);
	});

	// Remove a formset
	$('.deleteContent:button').show();
	$('#iisf').on('click', '.deleteContent:button', function()
	{
		var div = $(this).parent();
		var deleteBox = div.find('input:checkbox[id$=DELETE]');
		deleteBox.attr('checked', true);
		div.hide();
	});
	$('input:checkbox[id$=DELETE]').parent().parent().hide();

	// Installation Method filter
	$('#iisf').on('change', 'select[id$=target]', function()
	{
		var select = $(this).parent().parent().parent().find('select[id$=how_to_install]')
		var selected = $(this).val();

		// If no value selected, no IM available!
		if (!selected)
		{
			select.empty();
			return;
		}

		// possible CIC
		var legal = lc_im[selected];
		var options = $('#emptyformset select[id$=how_to_install] option');

		// Fill the SELECT with allowed values
		select.empty();
		for ( var i = 0; i < options.length; i++)
		{
			var o = $(options.get(i));
			if (legal.indexOf(parseInt(o.val())) > -1)
			{
				var a = o.clone();
				a.prop("selected", true);
				select.append(a);
			}
		}
	});

	// Installation Method init
	$('#iisf select[id$=how_to_install]').each(function()
	{
		var t = $(this)
		var selected = t.children('option:selected');
		var arr = [];
		selected.each(function()
		{
			arr.push($(this).val());
		});

		var target = t.parent().parent().parent().find('select[id$=target]')
		target.trigger('change');
		t.children('option').each(function()
		{
			if ($.inArray($(this).val(), arr) !== -1)
				$(this).attr('selected', 'selected');
			else
				$(this).removeAttr('selected');
		});
	});
});
