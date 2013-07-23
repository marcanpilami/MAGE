$(document).ready(function()
{
	// Add a formset
	$('#add_content').show();
	$('#add_content').click(function()
	{
		var form_idx = $('#id_iis-TOTAL_FORMS').val();
		$('#iisf').append($('#emptyformset').html().replace(/__prefix__/g, form_idx));
		if ($('#commonversion').val() != "")
			$('#commonversion').trigger('keyup');
		$('#iisf select[id$=target]').trigger('change');
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
			select.hide();
			select.siblings().text("");
			return;
		}

		// possible CIC
		var legal = lc_im[selected];
		var options = $('#emptyformset select[id$=how_to_install] option');

		// Fill the SELECT with allowed values
		select.empty();
		var displayed=0;
		var how_label="";
		for ( var i = 0; i < options.length; i++)
		{
			var o = $(options.get(i));
			if (legal.indexOf(parseInt(o.val())) > -1)
			{
				var a = o.clone();
				a.prop("selected", true);
				select.append(a);
				displayed++;
				how_label += a.text();
			}
		}

		// Hide or show the SELECT (one option = no need to) and replace it with the method name
		if (displayed <= 1)
		{
			select.hide();
			select.siblings().text(how_label);
		}
		else
		{
			select.show();
			select.siblings().text("");
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
	
	// Common version
	var input_commonv = $('#commonversion');
	var txts_version =	$('input[id$=-version]');
	
	input_commonv.keyup(function()
	{
		$('input[id$=-version]').val($('#commonversion').val());
	});
	input_commonv.change(function()
	{
		$('input[id$=-version]').val($('#commonversion').val());
	});

	var vv = $(txts_version[0]).val();
	var vl = null;
	var found = true;
	for (var i = 0; i < txts_version.length; i++)
	{
		vl = $(txts_version[i]).val();
		if (vl === "")
			break; // The additional form
		if (vl !== vv)
		{
			found = false;
			break;
		}
	}
	if (found)
	{
		$('#commonversion').val(vv);
		$('#tr_commonversion').show();
		txts_version.parents('tr').hide();
	}
	
	$('#bt_percompo').click(function()
	{
		$('#tr_commonversion').hide();
		txts_version.parents('tr').show();
	});
	
	
	// Hidden elements are not taken into account in a form
	$('#submit').click(function()
	{
		//$('#tr_commonversion').hide();
		//$('input[id$=-version]').show();
		//$('select[id$=how_to_install]').show();
		//txts_version.parents('tr').show();
		
		// Remove version from empty formsets
		$('input[id$=-version]').each(function()
		{
			var t = $(this);
			if (t.parents('table').find('select[id$=target]').val() === "")
			{
				t.val("");
				t.parents('table').find('select[id$=how_to_install]').val("");
			}
		});
		
	})
	
});
