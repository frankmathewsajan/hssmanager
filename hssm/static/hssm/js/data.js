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


document.addEventListener("DOMContentLoaded", () => {
    const IEDElement = document.getElementById('IED');
    const IEDRemarksElement = document.getElementById('IEDRemarks');

    const GuardianElement = document.getElementById('guardian');
    const GuardianRemarksElement = document.getElementById('Guardian');
    

    const ReligionElement = document.getElementById('Religion');

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
            document.getElementById('Parish').disabled = false;
        } else {
            document.getElementById('Parish').disabled = true;
        }
    });


});
