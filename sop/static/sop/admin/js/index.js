// $.ajaxSetup({ async: false });
function UpdateUploader(buttom,sop_id,sop_name){
	// SopFlowChart uploader settings
	var item_id = $("#"+buttom).attr('item_id');
	var file_type = $("#"+buttom).attr('file_type');
	// var filters = $("#"+buttom).attr('filters');
	if (parseInt(file_type)==0){
		var filters = "png";
	}else if(parseInt(file_type)==1){
		var filters = "doc,docx";
	}else if(parseInt(file_type)==2){
		var filters = "doc,docx,xls,xlsx,pdf,png,jpeg,jpg,vsd";
	}else{
		var filters = "vsd";
	};
	var uploader = new plupload.Uploader({
			runtimes: 'html5',
			browse_button: buttom,
			url: '/sop/admin/update_upload/',
			multi_selection: false,
			max_file_size : '10mb',
			multipart: true,
			headers: {
				'X-Requested-With': 'XMLHttpRequest',
			},
			multipart_params : {
				csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
	    	},
	    	filters :[{extensions : filters}],
	    	init:{
	    		FilesAdded:function(up, files){
	    			if(confirm('確定更新 "'+sop_name+'"'+files[0].name+'於SOP'+sop_name)){
	    				up.start();
	    			}else{
	    				$.each(files,function(i,file){
	    					up.removeFile(file);
	    				});
	    			}
	    		}
	    	}
		});
	uploader.bind('BeforeUpload', function(up, file) {
		var fullname = file.name.split(".");
		var ext = fullname[fullname.length - 1];
		fullname.splice(fullname.length - 1,1);
		name = fullname.toString();
		uploader.settings.multipart_params.item_id = item_id;
		uploader.settings.multipart_params.sop_id = sop_id;
		uploader.settings.multipart_params.file_type = file_type;
		uploader.settings.multipart_params.name = name;
	});

	uploader.bind('FileUploaded',function(up,file,info){
		res = $.parseJSON(info['response']);
		if (res['status'] == 'new'){
			alert('已新建'+res['item_name']);
			$('#'+buttom+'_list').unbind('click');
			$("#"+buttom).attr('item_id',res['item_id']);
			$('#'+buttom+'_list').click(function(){SetModal(buttom+'_list',sop_id,file_type)});
		}else{
			alert('已更新'+res['item_name']+'(第'+res['file_count']+'版本)');
		};

	});
	uploader.init();
	return  uploader

}


function ModalUpdateUploader(buttom,sop_id,sop_name){
	// SopFlowChart uploader settings
	var item_id = $("#"+buttom).attr('item_id');
	var file_type = $("#"+buttom).attr('file_type');
	if (parseInt(file_type)==0){
		var filters = "vsd";
	}else if(parseInt(file_type)==1){
		var filters = "doc,docx";
	}else{
		var filters = "doc,docx,xls,xlsx,pdf,png,jpeg,jpg,vsd";
	};
	// var filters = $("#"+buttom).attr('filters');
	var uploader = new plupload.Uploader({
			runtimes: 'html5',
			browse_button: buttom,
			url: '/admin/update_upload/',
			multi_selection: false,
			max_file_size : '10mb',
			multipart: true,
			headers: {
				'X-Requested-With': 'XMLHttpRequest',
			},
			multipart_params : {
				csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
	    	},
	    	filters :[{extensions : filters}],
	    	init:{
	    		FilesAdded:function(up, files){
	    			if(confirm('確定更新 "'+sop_name+'"'+files[0].name+'於SOP'+sop_name)){
	    				up.start();
	    			}else{
	    				$.each(files,function(i,file){
	    					up.removeFile(file);
	    				});
	    			}
	    		}
	    	}
		});
	uploader.bind('BeforeUpload', function(up, files) {
		uploader.settings.multipart_params.item_id = item_id;
		uploader.settings.multipart_params.sop_id = sop_id;
		uploader.settings.multipart_params.file_type = file_type;
	});

	uploader.bind('FileUploaded',function(up,file,info){
		res = $.parseJSON(info['response']);
		if (res['status'] == 'new'){
			alert('已新建'+res['item_name']);
			$('#'+buttom+'_list').unbind('click');
		}else{
			alert('已更新'+res['item_name']+'(第'+res['file_count']+'版本)');
		};
		$.ajax({
			url:"/sop/api/v1/auth_item/"+res['item_id']+'/?format=json',
			type:"GET",
			dataType: 'json',
			beforeSend: function(jqXHR) {
				jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
			},
			success: function(data){
				$("#"+buttom).parents('.files-box').find('.file-in-use').remove();
				$("#"+buttom).parents('.files-box').find('.file-list-tbody').html("");
				LoadItemFile(data['files'], item_id);
			},
		})

	});
	uploader.init();
	$("#FilesListModal").on('hide',function(){
		uploader.destroy();
	})
}


function LoadItemFile(files,item_id){
	$.each(files, function(j,file){
		file.item_id = item_id;
		if(file.is_use == true){
			file.checked = 'Checked';
			var file_tr = $('#file_list_tmpl').tmpl(file);
			$("#ItemFilesBox_"+item_id+" .file-list-title").after(file_tr);
			file_tr.find('td input:radio').addClass('file-in-use');
		}else{
			var file_tr = $('#file_list_tmpl').tmpl(file);
			$("#ItemFilesBox_"+item_id+" .file-list-tbody").append(file_tr);
		}
	});

}


function DoItem(item_list,buttom,file_type){
	$.ajaxSetup({ async: false });
	var count = item_list.length;
	$('#ItemFilesPanel').on('change','input:radio',function(){
		var old_file = $(this).parents("table").find('.file-in-use');
		var new_file = $(this);
		var data = {};
		data['is_use']=false;
		$.ajax({
			url:"/sop/api/v1/auth_file/"+old_file.val()+"/?format=json",
			type:"PUT",
			dataType: 'json',
			contentType: "application/json",
			data:JSON.stringify(data),
			beforeSend: function(jqXHR) {
				jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
			},
			success: function(){
				var data = {};
				data['is_use']=true;
				$.ajax({
					url:"/sop/api/v1/auth_file/"+new_file.val()+"/?format=json",
					type:"PUT",
					dataType: 'json',
					contentType: "application/json",
					data:JSON.stringify(data),
					beforeSend: function(jqXHR) {
						jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
					},
					success: function(data){
						old_file.attr('value',new_file.val());
						$.ajaxSetup({ async: true })
						console.log('ok!!!')
					},
				});
			},
		});
	});
	$.each(item_list,function(i,item_id){
		$.ajax({
			url:"/sop/api/v1/auth_item/"+item_id+'/?format=json',
			type:"GET",
			dataType: 'json',
			beforeSend: function(jqXHR) {
				jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
			},
			success: function(data){
				var item_box = $('#item_box_tmpl').tmpl(data).appendTo('#ItemFilesPanel');
				// ModalUpdateUploader("ModalItemUploader_"+data['id'],$("#FilesListModal").attr('sop_id'),$("#FilesListLabel").text());
				$("#ModalChangeName_"+data['id']).click(function(){
					ChangeItemTitle($(this),buttom);
				});
				var li_html =  $.parseHTML('<li id="li_item_'+data['id']+'"><a href="#ItemFilesBox_'+data['id']+'">'+data['name']+'</a></li>');
				$("#ItemsTab").append(li_html);
				var del_item = $.parseHTML('<span style="cursor:pointer;float:right;font-size:16px;;line-height:30px;color:white;"><strong>×</strong></sapn>');
				$(li_html).children("a").on('show',function(){
		  			$(del_item).insertBefore($(this))
		  			.click(function(){
						if(confirm('確定刪除"'+data['name']+'嗎?刪除後無法復原')){
							$.ajax({
								url:"/sop/api/v1/auth_item/"+item_id+"/",
								type:"DELETE",
								dataType: 'json',
								contentType: "application/json",
								beforeSend: function(jqXHR) {
									jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
								},
								success: function(){
									$(li_html).after().children("a").tab('show');
									$(li_html).remove();

									item_box.remove();
									alert("已刪除完成");
								},
							})
						}else{

						}
		  			});
	  			});
				$(li_html).children("a").on('hide',function(){
		  			$(del_item).remove()
	  			});
				$(li_html).children("a").click(function(e){
					e.preventDefault();
	  				$(this).tab('show');
	  			});
				LoadItemFile(data['files'],item_id);
			},
		}).done(function(){
			i++;
			if(i == count){
				$("#FilesListModal").modal("show");
				if(parseInt(file_type) != 2){
					$(".just-form").hide();
				};
				$("#ItemsTab li:first a").tab('show');
				// var sop_id = $("#FilesListModal").attr('sop_id');
			};
		});
	});

}


function SetModal(buttom,sop_id,file_type){
	var sop_name = $("#"+buttom).parent().parent().find(".sop-name").text();
	$.ajax({
		url:"/sop/api/v1/auth_sop/"+sop_id+'/'+file_type+'/?format=json',
		type:"GET",
		dataType: 'json',
		beforeSend: function(jqXHR) {
			jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
		},
		success: function(data){
			$("#FilesListModal").attr('sop_id',sop_id);
			$("#FilesListLabel").text(sop_name);
			var item_list = new Array();
			$(data['objects']).each(function(i, item){
				item_list.push(parseInt(item.id));
			});
			item_list.sort(function(a,b){return a-b});
			if(item_list.length==0){
				alert('沒有任何檔案，請上傳')
			}else{
				DoItem(item_list, buttom, file_type);
			};
		},
	});
}


function ChangeSopTitle(o){
	var that = o;
	that.hide();
	var sop_id = that.parent().parent().attr("sop_id");
	that.parent().children(".sop-name-input").show();
	var title_input = that.parent().children(".sop-name-input").children("input");
	title_input.css('width', title_input.val().length*14);
	title_input.focus();
	title_input.blur(function(){
		that.show();
		that.parent().children(".sop-name-input").hide();
	});
	title_input.change(function(){
		var new_title = $(this).val();
		var data = {};
		data['title'] = new_title
		$.ajax({
			url:"/sop/api/v1/auth_sop/"+sop_id+'/?format=json',
			type:"PUT",
			dataType: 'json',
			contentType: "application/json",
			data:JSON.stringify(data),
			beforeSend: function(jqXHR) {
				jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
			},
			success: function(data){
				that.text(new_title);
				that.show();
				title_input.parent().hide();
			},
		});
	});
}

function ChangeItemTitle(o,buttom){
	var that = o;
	var item_id = that.attr("item_id");
	var old_name = $("#li_item_"+item_id).children("a").text();
	$("#ItemNameModal").modal("show");
	$("#FormNameInput").val(old_name);
	$("#ItemNameModal").on("shown",function(){
		$("#FormNameInput").focus();
	});
	$("#FormNameInput").change(function(){
	var new_name = $(this).val();
	var data = {csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN};
	data['name'] = new_name
	data['item_id'] = item_id
		$.ajax({
			// url:"/sop/api/v1/auth_item/"+item_id+'/?format=json',
			url:"/sop/admin/change_item_name/",
			type:"POST",
			dataType: 'json',
			contentType: "application/json",
			data:data,
			beforeSend: function(jqXHR) {
				jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
			},
			success: function(data){
				$("#ItemNameModal").modal('hide');
				$("#FormNameInput").unbind();
				$("#"+buttom).get(0).click();
			},
		});
	});
	$("#ItemNameModal").css("top",'40%');
	$("#FilesListModal").modal("hide");
}



function OpenFormsUploader(sop_id,item_list){
	var sop_name = $("tr[sop_id='"+sop_id+"']").find(".sop-name").text();
	$("#FormsSopName").text(sop_name);
	$.ajaxSetup({ async: false });
	var count = item_list.length;
	if(item_list==""){
		$("#FormsSelectModal").modal("show");
		$("#forms_select").change(function(){
			var that = $(this);
			$("#form_uploader").attr("item_id",$('#forms_select').val());
			if (that.val()=="-1"){
				$('.btn-clear').remove();
			}else{
				$('.btn-clear').remove();
				$("#forms_select").after('<button id="form_uploader_'+that.val()+'" file_type="2" item_id="'+that.val()+'" class="btn btn-clear" aria-hidden="true">上傳</button>');
				UpdateUploader("form_uploader_"+that.val(),sop_id,sop_name);
			};
		});
		$("#FormsSelectModal").on("hidden",function(){
			$("option.clear").remove();
			$("#forms_select").unbind();
		});		
	}else{
		$(item_list).each(function(i,item_id){
			$.ajax({
				url:"/sop/api/v1/auth_item/"+item_id+'/?format=json',
				type:"GET",
				dataType: 'json',
				beforeSend: function(jqXHR) {
					jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
				},
				success: function(data){
					$('#forms_select').append('<option class="clear" value="'+data['id']+'">'+data['name']+'</option>');
				},
			}).done(function(){
				i++
				if(i==count){
					$.ajaxSetup({ async: true });
					$("#FormsSelectModal").modal("show");
					$("#forms_select").change(function(){
						var that = $(this);
						$("#form_uploader").attr("item_id",$('#forms_select').val());
						if (that.val()=="-1"){
							$('.btn-clear').remove();
						}else{
							$('.btn-clear').remove();
							$("#forms_select").after('<button id="form_uploader_'+that.val()+'" file_type="2" item_id="'+that.val()+'" class="btn btn-clear" aria-hidden="true">上傳</button>');
							UpdateUploader("form_uploader_"+that.val(),sop_id,sop_name);
						};
					});
					$("#FormsSelectModal").on("hidden",function(){
						$("option.clear").remove();
						$("#forms_select").unbind();
					});

				};	
			});
		});
	}
	// $("#FormsSelectModal").modal("show");

}


function SopIsUse(sop_id,o){
	var data = {};
	data["is_use"] = o.is(":checked");
	$.ajax({
		url:"/sop/api/v1/auth_sop/"+sop_id+"/?format=json",
		type:"PUT",
		dataType: 'json',
		contentType: "application/json",
		data:JSON.stringify(data),
		beforeSend: function(jqXHR) {
			jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
		},
		success: function(){
			$.ajax({
				url:"/sop/api/v1/auth_sop/"+sop_id+"/?format=json",
				type:"GET",
				dataType: 'json',
				contentType: "application/json",
				beforeSend: function(jqXHR) {
					jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
				},
				success: function(data){
					if(data['is_use']){
						alert(data['title']+"已經啟用")

						// o.parent().parent().addClass("success").removeClass("error");
					}else{
						alert(data['title']+"已經關閉")
						// o.parent().parent().addClass("error").removeClass("success");
					}
					
				},
			});	
		},
	});	

}


function DelSop(sop){
	var sop_id = sop.attr('sop_id');
	var sop_name = sop.find(".sop-name").text();
	if(confirm('確定刪除"'+sop_name+'嗎?刪除後無法復原')){
		$.ajax({
			url:"/sop/api/v1/auth_sop/"+sop_id+"/",
			type:"DELETE",
			dataType: 'json',
			contentType: "application/json",
			beforeSend: function(jqXHR) {
				jqXHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
			},
			success: function(){
				sop.remove();
				alert("已刪除完成");
			},
		})
	}else{

	}
}


function update_sop() {
	var obj = $(this),
		row = obj.closest('tr'),
		id = row.attr('sop_id'),
		field = obj.data('field');

	var data = {};
	data[field] = obj.val();

	$.ajax({
		url: '/sop/api/v1/auth_sop/' + id + '/',
		type: 'PUT',
		dataType: 'json',
		contentType: "application/json",
		data: JSON.stringify(data),
		beforeSend: function(XHR) {
            XHR.setRequestHeader('X-CSRFToken', $("input[name='csrfmiddlewaretoken']").val());
        },
	})
}


$(document).ready(function(){
	CSRFMIDDLEWARETOKEN = $('input[name=csrfmiddlewaretoken]').val();
	$.each($(".uploader"),function(){
		var buttom = $(this).attr('id');
		var sop_id = $("#"+buttom).parent().parent().attr("sop_id");
		var sop_name = $("#"+buttom).parent().parent().children(".sop-name").text();
		UpdateUploader(buttom,sop_id,sop_name);
	});

	$(".item-list").click(function(){
		var buttom = $(this).attr('id');
		var sop_id = $(this).parent().parent().attr('sop_id');
		var file_type = $(this).attr('file_type');
		SetModal(buttom,sop_id,file_type);
	});

	$('#FilesListModal').on('hidden', function () {
		$(".close-clear").html("");
	});

	$(".sop-name").click(function(){
		ChangeSopTitle($(this));
	});

	$(".forms-modal-uploader-buttom").click(function(){
		var sop_id = $(this).parent().parent().attr('sop_id');
		var forms_list = $(this).attr("item_id").split(",");
		OpenFormsUploader(sop_id,forms_list);
	});

	$(".chb").change(function(){
		var sop_id = $(this).parent().parent().attr('sop_id');
		SopIsUse(sop_id,$(this));
	});

	$(".sop-delete").click(function(){
		var sop = $(this).parent().parent();
		DelSop(sop);
	});

	$('#FilesListModal').on('change','input:radio',function(){

	});

	$('body').on('change', '.sop_fields', update_sop);
})
