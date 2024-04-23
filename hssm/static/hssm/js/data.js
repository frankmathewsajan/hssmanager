ids = [
    "IED",
    "AdYear",
    "AdDate",
    "AdNum",
    "AdBranch",
    "AdClassNow",
    "RollNumber",
    "AdQuota",
    "IEDRemarks",
    "index",
    "PrevSchool",
    "PrevType",
    "name",
    "dob",
    "gender",
    "Religion",
    "Caste",
    "Community",
    "Parish",
    "Slang",
    "FeeDue",
    "FeePaid",
    "idm",
    "dob",
    "aadhar",
    "bankNo",
    "bankBranch",
    "guardian",
    "FName",
    "FOccupation",
    "MName",
    "MOccupation",
    "GName",
    "GOccupation",
    "StudentPhone",
    "ParentPhone",
    "AdditionalPhone",
    "BusRoute",
    "RouteRemark",
    "fullAPlus",
    "passed",
    "TCDate",
    "TCNum",
    "TCYear",
    "LeavingDate",
    "LeaveReason",
    "CGPA",
    "LeavStudyStatuseReason",
    "HSEReg",
    "HSEMonYear"
]


function BAlert(message, type) {
    const alertPlaceholder = document.getElementById('liveAlertPlaceholder')
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
}

document.addEventListener("DOMContentLoaded", () => {
    

    const IEDElement = document.getElementById('IED');
    const IEDRemarksElement = document.getElementById('IEDRemarks');

    const GuardianElement = document.getElementById('guardian');
    const GuardianRemarksElement = document.getElementById('Guardian');

    const ReligionElement = document.getElementById('Religion');
    const ParishElement = document.getElementById('Parish');

    const adYearElement = document.getElementById('AdYear');
    const currentYear = new Date().getFullYear();

    const adDate = document.getElementById('AdDate');
    const today = new Date();


    IEDElement.addEventListener('change', () => {
        if (IEDElement.checked) {
            IEDRemarksElement.disabled = false;
        } else {
            IEDRemarksElement.disabled = true;
        }
    });

    GuardianElement.addEventListener('change', () => {
        if (GuardianElement.checked) {
            GuardianRemarksElement.hidden = false;
        } else {
            GuardianRemarksElement.hidden = true;
        }
    });

    ReligionElement.addEventListener('change', () => {
        if (ReligionElement.value == '2') {
            ParishElement.disabled = false;
        } else {
            ParishElement.disabled = true;
        }
    });

    const casteElement = document.getElementById('Caste');
    const genderElement = document.getElementById('gender');
    const BranchElement = document.getElementById('AdBranch');
    const communityElement = document.getElementById('Community');
    let SCSTOEC = 0;
    casteElement.addEventListener('change', () => {
        const selectedCaste = casteElement.options[casteElement.selectedIndex];
        communityElement.value = selectedCaste.getAttribute('data-community');
        const FeeDue = document.getElementById('FeeDue');
        const e = communityElement.value;
        SCSTOEC = (e == 'S. C.' || e == 'S. T.' || e == 'O. E. C.') ? 1 : 0;
        const gender = Number(genderElement.value);
        if (BranchElement.value != '...' && gender != NaN && SCSTOEC != NaN) {
            fetch(`/fees/${SCSTOEC}`)
                .then(response => response.json())
                .then(data => {

                    console.log(data);
                    console.log(gender, BranchElement.value, SCSTOEC, communityElement)
                    FeeDue.value = (gender == 1 || gender == 3) ? Number(data['boys'][BranchElement.value]) : Number(data['girls'][BranchElement.value]);
                });
        } else {
            communityElement.value = '';
            FeeDue.value = 0;
            BAlert('Make sure to select the branch, caste & gender for calculating the fee!!!', 'danger')
            selectedCaste.options.length = 0;
        }

    });





    adYearElement.value = `${currentYear}-${String(currentYear + 1).slice(-2)}`;
    adDate.value = today.toISOString().slice(0, 10);

    const indexElement = document.getElementById('index');
    indexElement.addEventListener('change', () => {
        if (indexElement.value > 10 || indexElement.value < 1) {
            indexElement.value = 1;
            BAlert('Index should be between 1 and 10','danger');
        }
    });
});


