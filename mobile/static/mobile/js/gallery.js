function switch_page() {
    var target;
    var current_page = $('#pager').data('page'),
        final_page = $('#pager').data('final');

    switch ($(this).data('go')) {
        case 'previous':
            target = current_page - 1 > 0 ? current_page - 1 : 1;
            break;
        case 'next':
            target = current_page + 1 <= final_page ? current_page + 1 : final_page;
            break;
        default:
            target = current_page
    }

    if (target == current_page) return false;

    if (window.location.search) {
        if (window.location.search.indexOf('page') > -1) {
            return window.location = window.location.pathname + window.location.search.replace(new RegExp('(page' + '=)[^&]+'), 'page=' + target);
        }

        return window.location = window.location.pathname + window.location.search + '&page=' + target;
    }

    return window.location = window.location.pathname + '?page=' + target;
}


function switch_order() {
    var order = $(this).data('order'),
        current_order;

    if (!window.location.search || window.location.search.indexOf('order') < 0 || window.location.search.indexOf('order=time') > -1) {
        current_order = 'time';
    }

    if (window.location.search && window.location.search.indexOf('order=node') > -1) {
        current_order = 'node';
    }

    if (order == current_order) {
        $('#filter_item').toggleClass('active');
        return false;
    }

    if (window.location.search && window.location.search.indexOf('order') > -1) {
        return window.location = window.location.pathname + window.location.search.replace(new RegExp('(order' + '=)[^&]+'), 'order=' + order);
    }

    if (window.location.search) {
        return window.location = window.location.pathname + window.location.search + '&order=' + order;
    }

    return window.location = window.location.pathname + '?order=' + order;
}


function initial() {
    $('#filter').click(function() {
        $('#filter_item').toggleClass('active');
    });

    $('.pager').click(switch_page);
    $('.order').click(switch_order);
}


$(document).ready(function(){
    initial();
    $('#project_info_menu').find('li[name="gallary"]').find('a').addClass('w3-text-teal');
});