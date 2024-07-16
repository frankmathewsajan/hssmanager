$(document).ready(function () {

    function BAlert(message, type) {
        const alertPlaceholder = $('#liveAlertPlaceholder');
        const wrapper = $(`
            <div class="alert alert-${type} alert-dismissible" role="alert">
                <div>${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        alertPlaceholder.append(wrapper);
        $('html, body').animate({ scrollTop: 0 }, 'smooth');
    }

    $('#AdNum').on('blur', function () {
        const AdNum = $(this).val();
        if (AdNum) {
            fetch(`/admission/${AdNum}`)
                .then(response => response.json())
                .then(data => {
                    if (data['taken']) {
                        BAlert(`Admission Number ${AdNum} already in use!!!`, 'danger');
                        $('#AdNum').focus();
                    }
                });
        }
    });

    $('input[id], select[id]').each(function () {
        const id = $(this).attr('id');
        if (id !== 'GName' && id !== 'GOccupation') {
            $(this).attr('name', id);
        }
    });

    $('#CAdd').on('change', function () {
        if (this.checked) {
            $('#CAddress').val($('#PAddress').val()).prop('disabled', true);
        } else {
            $('#CAddress').val('').prop('disabled', false).focus();
        }
    });

    $('#IED_toggle').on('change', function () {
        $('#IEDRemarks').prop('disabled', !this.checked);
        $('#IED').val(this.checked ? "1" : "0");
    });

    $('#fullAPlus_toggle').on('change', function () {
        $('#fullAPlus').val(this.checked ? "1" : "0");
    });

    $('#passedHSE_toggle').on('change', function () {
        $('#passedHSE').val(this.checked ? "1" : "0");
    });

    $('#Religion').on('change', function () {
        $('#Parish').prop('disabled', $(this).val() !== '2');
    });

    const currentYear = new Date().getFullYear();
    const today = new Date().toISOString().slice(0, 10);
    const AdDate = $('#AdDate')

    $('#AdYear').val(`${currentYear}-${String(currentYear + 1).slice(-2)}`);

    AdDate.val(AdDate.val() || today);

    $('#Caste, #gender, #AdBranch').on('change', function () {
        const selectedCaste = $('#Caste option:selected');
        const community = selectedCaste.data('community');
        const Community = $('#Community')
        Community.val(community);

        const SCSTOEC = (community === 'S. C.' || community === 'S. T.' || community === 'O. E. C.') ? 1 : 0;
        const gender = Number($('#gender').val());
        const branch = Number($('#AdBranch').val());

        if (!isNaN(branch) && !isNaN(gender) && !isNaN(SCSTOEC)) {
            fetch(`/fees/${SCSTOEC}`)
                .then(response => response.json())
                .then(data => {
                    const FeeDue = $('#FeeDue');
                    const FeeHolder = $('#FeeHolder');
                    const fee = (gender === 1 || gender === 3) ? Number(data['boys'][branch]) : Number(data['girls'][branch]);
                    FeeDue.val(fee);
                    FeeHolder.val(fee);
                });
        } else {
            Community.val('');
            $('#FeeDue').val(0);
            $('#Caste').prop('selectedIndex', -1);
            BAlert('Make sure to select the branch, caste & gender for calculating the fee!!!', 'danger');
        }
    });

    $('#index').on('change', function () {
        const value = $(this).val();
        if (value > 10 || value < 1) {
            $(this).val(1);
            BAlert('Index should be between 1 and 10', 'danger');
        }
    });
});
