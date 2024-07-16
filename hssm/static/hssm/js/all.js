$(document).ready(function () {
    $('table tbody tr').click(function () {
        const href = $(this).data('href');
        window.open(href, '_blank');
        return false;
    });
    $(".pagination li").click(function () {
        const page = $(this).data("get-page");
        $("form input[name='page']").val(page);
        $("form").submit();
    });
    $("table th i").click(function () {
        const target = $(this).data('sort')
        $("form input[name='target']").val(target);
        $("form").submit();
    })
    $("select").change(function () {
        const branch = $(this).val()
        $("form input[name='branch']").val(branch);
        $("form").submit();
    })
});