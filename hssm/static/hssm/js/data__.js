ids = [
    "IED",
    "CAdd",
    "CAddress",
    "PAddress",
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
    "StudyStatus",
    "HSEReg",
    "HSEMonYear"
]

// fn to get all url query ad set it to ids
function getQuery() { 
    const urlParams = new URLSearchParams(window.location.search);
    ids.forEach(id => {
        const value = urlParams.get(id);
        if (value) {
            document.getElementById(id).value = value;
        }
    })}
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
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.addEventListener("DOMContentLoaded", () => {
    const AdNumElement = document.getElementById('AdNum');
    AdNumElement.addEventListener('blur', () => {
        const AdNum = AdNumElement.value;
        if (AdNum) {
            fetch(`/admission/${AdNum}`)
                .then(response => response.json())
                .then(data => {
                    if (data['taken']) {
                        BAlert(`Admission Number ${AdNum} already in use!!!`, 'danger');
                        AdNumElement.focus();
                    }
                });
        }
    });

    const elements = document.querySelectorAll('input[id], select[id]');
    elements.forEach(element => {
        const id = element.getAttribute('id');
        if (id !== 'GName' && id !== 'GOccupation') {
            element.setAttribute('name', id);
        }
    });



    const IEDElement = document.getElementById('IED');
    const IEDToggle = document.getElementById('IED_toggle')

    const passedHSEElement = document.getElementById('passedHSE');
    const passedHSEToggle = document.getElementById('passedHSE_toggle')

    const fullAPlusElement = document.getElementById('fullAPlus');
    const fullAPlusToggle = document.getElementById('fullAPlus_toggle')


    const IEDRemarksElement = document.getElementById('IEDRemarks');

    const GuardianElement = document.getElementById('guardian');
    const GuardianRemarksElement = document.getElementById('Guardian');

    const ReligionElement = document.getElementById('Religion');
    const ParishElement = document.getElementById('Parish');

    const adYearElement = document.getElementById('AdYear');
    const currentYear = new Date().getFullYear();

    const adDate = document.getElementById('AdDate');
    const today = new Date();

    const AddressToggle = document.getElementById('CAdd');

    AddressToggle.addEventListener('change', () => {
        
        if (AddressToggle.checked) {
            document.getElementById('CAddress').value = document.getElementById('PAddress').value;
            document.getElementById('CAddress').disabled = true;
        } else {
            document.getElementById('CAddress').value = '';
            document.getElementById('CAddress').disabled = false;
            document.getElementById('CAddress').focus()
        }
    });

    IEDToggle.addEventListener('change', () => {
        IEDRemarksElement.disabled = !IEDToggle.checked;
        IEDElement.value = IEDToggle.checked ? "1" : "0";
    });

    fullAPlusToggle.addEventListener('change', () => {
        fullAPlusElement.value = fullAPlusToggle.checked ? "1" : "0";
    });

    passedHSEToggle.addEventListener('change', () => {
        passedHSEElement.value = passedHSEToggle.checked ? "1" : "0";
    });

    /*GuardianElement.addEventListener('change', () => {
        if (GuardianElement.checked) {
            GuardianRemarksElement.hidden = false;
            document.getElementById('GName').setAttribute('name', 'GName');
            document.getElementById('GOccupation').setAttribute('name', 'GOccupation');
        } else {
            GuardianRemarksElement.hidden = true;
            document.getElementById('GName').removeAttribute('name')
            document.getElementById('GOccupation').removeAttribute('name')
        }
    });*/

    ReligionElement.addEventListener('change', () => {
        ParishElement.disabled = ReligionElement.value !== '2';
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
        const FeeHolder = document.getElementById('FeeHolder');
        const e = communityElement.value;
        SCSTOEC = (e === 'S. C.' || e === 'S. T.' || e === 'O. E. C.') ? 1 : 0;
        const gender = Number(genderElement.value);
        if (!isNaN(BranchElement.value) && !isNaN(gender) && !isNaN(SCSTOEC)) {
            fetch(`/fees/${SCSTOEC}`)
                .then(response => response.json())
                .then(data => {

                    console.log(data);
                    console.log(gender, BranchElement.value, SCSTOEC, communityElement)
                    FeeDue.value = FeeHolder.value = (gender === 1 || gender === 3) ? Number(data['boys'][BranchElement.value]) : Number(data['girls'][BranchElement.value]);
                });
        } else {
            communityElement.value = '';
            FeeDue.value = 0;
            casteElement.selectedIndex = -1;
            BAlert('Make sure to select the branch, caste & gender for calculating the fee!!!', 'danger')
            
        }

    });





    adYearElement.value = `${currentYear}-${String(currentYear + 1).slice(-2)}`;
    
    adDate.value = adDate.value === '' ? today.toISOString().slice(0, 10) : adDate.value;

    const indexElement = document.getElementById('index');
    indexElement.addEventListener('change', () => {
        if (indexElement.value > 10 || indexElement.value < 1) {
            indexElement.value = 1;
            BAlert('Index should be between 1 and 10','danger');
        }
    });
});


