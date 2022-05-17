$(document).ready( function () {
    $('#myTable').DataTable();
} );

$(document).ready( function () {
    $('#dartTable').DataTable({
        scrollX: true,
//        ordering: false,
        order: [[3, 'asc']],
        scrollY: '  50vh',
        scrollCollapse: true,
        paging: false,
//        bAutoWidth: false,
//        aoColumns : [
//          { sWidth: '30%' },
//          { sWidth: '70%' }
//        ]
    });
} );