function NewUploader($buttom,sop_id){
	var buttom_id = $buttom.attr('id');
	var file_type = parseInt($buttom.attr('file_type'));
	if (file_type==0){
		var filters = "png";
	}else if(file_type==1){
		var filters = "doc,docx";
	}else if(file_type==3){
		var filters = "vsd";
	}else{
		alert('fuck');
	};
	var uploader = new plupload.Uploader({
			runtimes: 'html5',
			browse_button: buttom_id,
			url: '/sop/admin/create_item/',
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
	    		if(confirm('確定上傳'+files[0].name+'?')){
	    				up.settings.multipart_params.sop_id = sop_id;
	    				up.settings.multipart_params.file_type = file_type;
	    				up.start();
	    				$buttom.parents('.file-up').children('.file-name').children('span').html(files[0].name);
	    			}else{
	    				return false
	    			}
	    		},
	    		FileUploaded:function(up, file){
	    			alert("上傳成功")
	    		}
	    	}
		});
	uploader.init();
}


function NewFormsUploader(sop_id){
	var files_count = 0;
	var uploader = new plupload.Uploader({
			runtimes: 'html5',
			browse_button: "new_form_select",
			url: '/sop/admin/create_item/',
			multi_selection: true,
			max_file_size : '20mb',
			multipart: true,
			headers: {
				'X-Requested-With': 'XMLHttpRequest',
			},
			multipart_params : {
				csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
	      "file_type":2,
	    	},
	    	filters :[{title : "form", extensions : "doc,docx,pdf,xls,xlsx,png,jpg,jpeg,ppt,pptx,gif,vsd"}],
	    	init:{
	    		FilesAdded:function(up, files){
	    			files_count = files.length;
	    			$("#form-files-name").html("");
	    			$.each(files, function(i, file) {
							$("#form-files-name").append('<p id="'+file.id +'"><input type="text"></input><span class="hide fi-ch-name">fuck</span>.<span class="ext"></span><a id="cancel_'+file.id+'">取消</a></p>');
							$("#cancel_"+file.id).click(function(){
								uploader.removeFile(file);
								$(this).parents('p').remove();
							});
							var fullname = file.name.split(".");
							var ext = fullname[fullname.length - 1];
							fullname.splice(fullname.length - 1,1);
							name = fullname.toString();
							$("#"+file.id+" input").val(name);
							$("#"+file.id+" .fi-ch-name").html(name);
							$("#"+file.id+" .ext").html(ext);
						});
						return files_count
	    		},
	    		BeforeUpload:function(up, file){
	    			up.settings.multipart_params.item_name=$('#' + file.id+" input").val();
	    			up.settings.multipart_params.sop_id = sop_id;
	    		},
	    		FileUploaded:function(up, file){
	    			$("#"+file.id+" span.fi-ch-name").html($('#' + file.id+" input").val());
	    			$("#"+file.id+" input").hide();
	    			$("#cancel_"+file.id).remove();
	    			$("#"+file.id+" span.fi-ch-name").show();
	    		},	    		
	    	},
		});
// lauch SopForm uploader 
	uploader.init();
	$("#new_form_submit").click(function(){
  	if(confirm('確定上傳上述'+files_count+'個表單?')){
			uploader.start();
		}else{
			return false
		}
	})

}


function CreateSop(){
	var sop_name = $("#new_sop_title_input").val();
	if(confirm('確定新增"'+sop_name+'"之標準作業程序?')){
			$.ajax({
				url:"/sop/admin/create_sop/",
				type:"POST",
				dataType: 'json',
				data:{
					csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
					title: sop_name,
				},
				success: function(data){
					$(".step-2").show();
					$("[uploader]").each(function(){
						NewUploader($(this),data["id"]);
					});
					NewFormsUploader(data["id"]);
				},
			});
	}else{
		return false
	}
}



$(document).ready(function(){
	CSRFMIDDLEWARETOKEN = $('input[name=csrfmiddlewaretoken]').val();
	$("#cr_sop_btn").click(CreateSop);

});




















