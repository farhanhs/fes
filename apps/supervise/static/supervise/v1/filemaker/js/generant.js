(function($){
    $.fn.DocxGenerant = function(template_path, data, new_file_name, default_text, download_text){
        var obj = $(this);
        if(template_path == null || template_path == "") {
            return false;
        }
        if(data == null) {
            data = {};
        }
        if(new_file_name == null) {
            new_file_name = "new_file.docx";
        }
        if(default_text == null) {
            default_text = "Processing...";
        }
        if(download_text == null) {
            download_text = "Download File";
        }
        if(obj.children().length) {
            obj.children().attr("value", default_text);
            obj.children().html(default_text);
        } else {
            obj.html(default_text);
        }
        
        var xhr = new XMLHttpRequest();
        xhr.open('GET', template_path, true);
        if (xhr.overrideMimeType) {
            xhr.overrideMimeType('text/plain; charset=x-user-defined');
        }

        xhr.onreadystatechange = function(e) {
            if (this.readyState == 4 && this.status == 200) {
                var file= new DocxGen(this.response);
                file.setTemplateVars(data);
                file.applyTemplateVars()
                file.output(null, new_file_name, obj, download_text)
            }
        };
        xhr.send();
        return false;
    };
})(jQuery);
