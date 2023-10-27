if(!(typeof(Hoshi)&&Hoshi.version&&Hoshi.verifyVersion&&Hoshi.verifyVersion(Hoshi.version, "1.0.0")&&
     typeof($)&&$.fn&&$.fn.jquery&&Hoshi.verifyVersion($.fn.jquery, "1.3.2")))
   alert("Hoshi.TableView requere Hoshi>1.0.0, jQuery>1.3.2");

Hoshi.ConditionView = function(options) {
    var $this = this;
    var mainWindow = $(options.window).addClass("ui-conditionview");
    var conditionCollection = {};
    var conditionCounter = 0;
    // Search condition list
    var window = $H.ib({tag:"div", appendTo:mainWindow, className: "ui-cond-list"});

    // Add condition button and spliter
    var newRowCommand = $H.ib({tag:"div", appendTo:mainWindow, className:"ui-cond-bottom"});
    newRowCommand.createButton = $H.ib({tag:"div", appendTo:newRowCommand, className:"ui-cond-button", style:"clear: both", innerHTML:"<input type=\"button\" value=\"新增搜尋條件\" />"}).bind("click", function() {
        $this.addCondition();
    });
    
    /* Root of add condition */
    this.addCondition = function() {
        var r = $H.ib({tag:"div", appendTo:window, className:"ui-cond-row", style:""});

        var fnButton = $H.ib({tag:"tag", appendTo:r, className:"ui-cond-fn"});
        $H.ib({tag:"div", appendTo:fnButton, className:"ui-cond-button", innerHTML:"<input type=\"button\" value=\"移除搜尋條件\" style=\"font-size: 10px\"/>", style:"float: right;"}).click(function() {
            c.dropCondition();
            r.remove();
            delete(conditionCollection[index]);
        });


        var c = this.appendCondition(r, options.conditions);
        var index = conditionCounter++;
        conditionCollection[index] = c;
    }

    this.appendCondition = function(r, condition, keyName) {
        var conObject;
        var $cell = $H.ib({tag:"div", appendTo:r, className:"ui-cond-cell"})
        if(condition.type&&this["appendCondition_" + condition.type]) {
            conObject = new this["appendCondition_" + condition.type]($cell, condition);
        }
        
        if(conObject) {
            conObject.dropCondition = function() {
                if(conObject.child) conObject.child.dropCondition();
                conObject.remove();
            }
            
            conObject.getCondition = function(parent) {
                if(!parent) parent = []
                parent.push(conObject.condition_value());
                if(conObject.child) conObject.child.getCondition(parent);
                return parent;
            }
        }
        return conObject;        
    }
    
    this.appendCondition_selector = function(r, condition) {
        var s = new $H.ib({tag:"select", appendTo:r}).bind("change", function() {
            if(s.child) {s.child.dropCondition();}
            s.child = (condition.option[s.find('option:selected').val()])?
                    ($this.appendCondition(r, condition.option[s.find('option:selected').val()])):undefined;
        });
        for(key in condition.option)
            $H.ib({tag:"option", appendTo:s, value:key, innerHTML:condition.option[key].text});
        s.trigger("change");
        
        s.condition_value = function() {
            return s.find('option:selected').val();
        }
        return s;
    }
    
    this.appendCondition_text = function(r, condition) {
        var s = new $H.ib({tag:"input", appendTo:r, type:"text"});
        s.condition_value = function() {
            return s.val();
        }
        return s;
    }
    
    this.appendCondition_between_text = function(r, conditino) {
        var s = new $H.ib({tag:"div", appendTo:r, style:"display:inline-box"});
        var leftT = new $H.ib({tag:"input", appendTo:s, type:"text"})
        var middleT = new $H.ib({tab:"span", appendTo:s, innerHTML:" ~ "});
        var rightT = new $H.ib({tag:"input", appendTo:s, type:"text"})
        s.condition_value = function() {
            return "[" + leftT.val() + ", " + rightT.val() + "]";
        }
        return s;
    }

    
    this.addCondition();
    
    this.get_search_condition = function() {
        var searchCondition = [];
        for(index in conditionCollection) {
            var eachC = conditionCollection[index].getCondition();
            searchCondition.push(eachC);
        }
        return searchCondition;
    }
    
    return this;
}
