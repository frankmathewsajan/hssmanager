$(document).ready(function () {
    $('h5 select').change(function () {
        const c = $(this).val();
        $.get("/classes", { class: c }, function(data, status) {
            console.log(data)
            alert("Data: " + data.id + "\nStatus: " + status);
        });
    });
    $('#AdBranchNow').change(function (){
        const branch = $(this).val();
        $.get("/branches", { branch: branch }, function(data, status) {
            console.log(data)
            alert("Data: " + data.id + "\nStatus: " + status);
        });
    })
});
