    $(document).ready(function(){
$('.dropdown-submenu>a').unbind('click').click(function(e){
$(this).next('ul').toggle();
e.stopPropagation();
e.preventDefault();
});
});