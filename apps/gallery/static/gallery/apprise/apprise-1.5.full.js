// Apprise 1.5 by Daniel Raftery
// http://thrivingkings.com/apprise
//
// Button text added by Adam Bezulski
//

function apprise(string, args, callback){
    var default_args = {
    		'confirm'		:	false, 		// Ok and Cancel buttons
    		'verify'		:	false,		// Yes and No buttons
    		'input'			:	false, 		// Text input (can be true or string for default text)
    		'animate'		:	false,		// Groovy animation (can true or number, default is 400)
    		'textOk'		:	'OK',		// Ok button default text
    		'textCancel'	:	'CANCEL',	// Cancel button default text
    		'textYes'		:	'YES',		// Yes button default text
    		'textNo'		:	'NO'		// No button default text
		}
	
	if(args){
		for(var index in default_args){
		    if(typeof args[index] == "undefined") args[index] = default_args[index];
	    } 
	}
    
	var aHeight = $(document).height();
	var aWidth = $(document).width();
	$('body').append('<div class="appriseOverlay appriseLayout" id="aOverlay"></div>');
	$('.appriseOverlay').css('height', aHeight).css('width', aWidth).fadeIn(100);
	$('body').append('<div class="appriseOuter appriseLayout"></div>');
	$('.appriseOuter').append('<div class="appriseInner appriseLayout"></div>');
	$('.appriseInner').append(string);
    $('.appriseOuter').css("left", ( $(window).width() - $('.appriseOuter').width() ) / 2+$(window).scrollLeft() + "px");
    var wHeight = $(window).height(),
        oHeight = $('.appriseOuter').height();
    var tHeight = (wHeight-oHeight)/2
    if(args){
		if(args['animate']){
			var aniSpeed = args['animate'];
			if(isNaN(aniSpeed)){aniSpeed = 400;}
			$('.appriseOuter').css('top', '-200px').show().animate({top: tHeight}, aniSpeed);
		}else{
		    $('.appriseOuter').css('top', tHeight).fadeIn(200);
	    };
	}else{
	    $('.appriseOuter').css('top', tHeight).fadeIn(200);
    };
    
    if(args){
    	if(args['input']){
    		if(typeof(args['input'])=='string'){
    			$('.appriseInner').append('<div class="aInput"><input type="text" class="aTextbox" t="aTextbox" value="'+args['input']+'" /></div>');
			}else{
				$('.appriseInner').append('<div class="aInput"><input type="text" class="aTextbox" t="aTextbox" /></div>');
			}
			$('.aTextbox').focus();
		}
	}
    
    $('.appriseInner').append('<div class="aButtons"></div>');
    if(args){
		if(args['confirm'] || args['input']){ 
			$('.aButtons').append('<button value="ok">'+args['textOk']+'</button>');
			$('.aButtons').append('<button value="cancel">'+args['textCancel']+'</button>'); 
		}else if(args['verify']){
			$('.aButtons').append('<button value="ok">'+args['textYes']+'</button>');
			$('.aButtons').append('<button value="cancel">'+args['textNo']+'</button>');
		}else{
		    $('.aButtons').append('<button value="ok">'+args['textOk']+'</button>');
	    }
	}else{
	    $('.aButtons').append('<button value="ok">'+default_args['textOk']+'</button>');
    }
	
	$(document).keydown(function(e){
        if($('.appriseOverlay').is(':visible')){
            if(e.keyCode == 13){
                e.preventDefault();
                $('.aButtons > button[value="ok"]').click();
            };
			if(e.keyCode == 27){
			    e.preventDefault();
				$('.aButtons > button[value="cancel"]').click();
            };
		}
	});

	$('.appriseLayout').click(function(e){
	    return false;
	})

	var aText = $('.aTextbox').val();
	if(!aText){aText = false;}
	$('.aTextbox').keyup(function(){aText = $(this).val();});
   
    $('.aButtons > button').click(function(){
        $('.appriseOverlay').remove();
        $('.appriseOuter').remove();
    	if(callback){
            var wButton = $(this).attr("value");
			if(wButton=='ok'){ 
				if(args){
					if(args['input']){callback(aText);}
					else{callback(true);}
				}else{callback(true);}
			}else if(wButton=='cancel'){callback(false);}
		}
		return false;
	});
}
