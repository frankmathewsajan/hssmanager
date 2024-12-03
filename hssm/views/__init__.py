staff_form = {
    "layout": {
        "personal_information": {
            "header": "Personal Information",
            "rows": [
                {
                    "columns": [
                        {"field_id": "personalName", "col_size": 6},
                        {"field_id": "dateOfBirth", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "sex", "col_size": 3},
                        {"field_id": "religion", "col_size": 3},
                        {"field_id": "caste", "col_size": 3},
                        {"field_id": "parish", "col_size": 3}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "address", "col_size": 12}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "mobileNumber", "col_size": 6},
                        {"field_id": "phoneNumber", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "penNumber", "col_size": 6},
                        {"field_id": "electionId", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "bankName", "col_size": 6},
                        {"field_id": "bankAccountNumber", "col_size": 6}
                    ]
                }
            ]
        },
        "professional_information": {
            "header": "Professional Information",
            "rows": [
                {
                    "columns": [
                        {"field_id": "designation", "col_size": 6},
                        {"field_id": "subject", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "basicPay", "col_size": 6},
                        {"field_id": "payScale", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "incrementAmount", "col_size": 6},
                        {"field_id": "incrementDate", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "joinDate", "col_size": 6},
                        {"field_id": "ConServ", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "ConServHSE", "col_size": 6},
                        {"field_id": "ConServPrevDes", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "retirementDate", "col_size": 6},
                        {"field_id": "qualification", "col_size": 6}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "remarks", "col_size": 4},
                        {"field_id": "transferDate", "col_size": 4},
                        {"field_id": "status", "col_size": 4}
                    ]
                },
                {
                    "columns": [
                        {"field_id": "PFAccNo", "col_size": 4},
                        {"field_id": "PFAmount", "col_size": 4},
                        {"field_id": "PFDate", "col_size": 4}
                    ]
                },
            ]
        }
    },
    "fields": {
        "personalName": {"type": "text", "label": "Name", "required": True},
        "dateOfBirth": {"type": "date", "label": "DOB (Date of Birth)", "required": True},
        "sex": {"type": "select", "label": "Sex", "options": ["Female", "Male", "Other"], "required": True},
        "religion": {"type": "select", "label": "Religion", "options": ["Christian", "Hindu", "Muslim", "Other"],
                     "required": True},
        "caste": {"type": "select", "label": "Caste", "options": ["RCSC", "SC", "ST", "OBC", "Other"],
                  "required": True},
        "parish": {"type": "text", "label": "Parish", "required": True},
        "address": {"type": "textarea", "label": "Address", "required": True},
        "mobileNumber": {"type": "tel", "label": "Mobile Number", "required": True},
        "phoneNumber": {"type": "tel", "label": "Phone Number", "required": True},
        "penNumber": {"type": "text", "label": "PEN No", "required": True},
        "electionId": {"type": "text", "label": "Election ID", "required": True},
        "bankName": {"type": "text", "label": "Bank", "required": True},
        "bankAccountNumber": {"type": "text", "label": "Account No", "required": True},
        "designation": {"type": "select", "label": "Designation", "options": ["HSST", "Other"], "required": True},
        "subject": {"type": "text", "label": "Subject", "required": True},
        "basicPay": {"type": "number", "label": "Basic Pay", "required": True},
        "payScale": {"type": "number", "label": "Scale of Pay", "required": True},
        "incrementAmount": {"type": "number", "label": "Increment", "required": True},
        "incrementDate": {"type": "date", "label": "Increment Date", "required": True},
        "joinDate": {"type": "date", "label": "Join Date", "required": True},
        "ConServ": {"type": "text", "label": "Continuous Service", "required": True},
        "ConServHSE": {"type": "text", "label": "Continuous Service HSE", "required": True},
        "ConServPrevDes": {"type": "text", "label": "Continuous Service Prev Designation", "required": True},
        "retirementDate": {"type": "date", "label": "Retirement Date", "required": True},
        "qualification": {"type": "select", "label": "Qualification", "options": ["Aided", "Government"],
                          "required": True},
        "remarks": {"type": "text", "label": "Remarks", "required": True},
        "transferDate": {"type": "date", "label": "Transfer Date", "required": True},
        "status": {"type": "select", "label": "Status", "options": ["Aided", "Government"],
                   "required": True},
        "PFAccNo": {"type": "text", "label": "PF Account No", "required": True},
        "PFAmount": {"type": "number", "label": "PF Amount", "required": True},
        "PFDate": {"type": "date", "label": "PF Start Date", "required": True},
    }
}


def generate_html(form_data):
    html = []

    def generate_field_html(field_id, field):
        field_html = ""
        if field["type"] == "text":
            field_html = f'''
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="{field_id}" required>
                    <label for="{field_id}">{field['label']}</label>
                    <div class="invalid-feedback">
                        Please provide a valid {field['label'].lower()}.
                    </div>
                </div>'''
        elif field["type"] == "date":
            field_html = f'''
                <div class="form-floating mb-3">
                    <input type="date" class="form-control" id="{field_id}" required>
                    <label for="{field_id}">{field['label']}</label>
                    <div class="invalid-feedback">
                        Please provide a valid {field['label'].lower()}.
                    </div>
                </div>'''
        elif field["type"] == "select":
            options_html = ''.join([f'<option value="{opt}">{opt}</option>' for opt in field["options"]])
            field_html = f'''
                <div class="form-floating mb-3">
                    <select class="form-select" id="{field_id}" required>
                        <option value="" disabled selected>Select</option>
                        {options_html}
                    </select>
                    <label for="{field_id}">{field['label']}</label>
                    <div class="invalid-feedback">
                        Please select your {field['label'].lower()}.
                    </div>
                </div>'''
        elif field["type"] == "tel":
            field_html = f'''
                <div class="form-floating mb-3">
                    <input type="tel" class="form-control" id="{field_id}" required>
                    <label for="{field_id}">{field['label']}</label>
                    <div class="invalid-feedback">
                        Please provide a valid {field['label'].lower()}.
                    </div>
                </div>'''
        elif field["type"] == "number":
            field_html = f'''
                <div class="form-floating mb-3">
                    <input type="number" class="form-control" id="{field_id}" required>
                    <label for="{field_id}">{field['label']}</label>
                    <div class="invalid-feedback">
                        Please provide a valid {field['label'].lower()}.
                    </div>
                </div>'''
        elif field["type"] == "textarea":
            field_html = f'''
                <div class="form-floating mb-3">
                    <textarea class="form-control" id="{field_id}" style="height: 100px;" required></textarea>
                    <label for="{field_id}">{field['label']}</label>
                    <div class="invalid-feedback">
                        Please provide a valid {field['label'].lower()}.
                    </div>
                </div>'''
        return field_html

    html.append('<div class="container mt-5">')
    html.append('<form class="needs-validation" novalidate>')
    html.append('<div class="row g-3">')

    for section, content in form_data["layout"].items():
        html.append(f'<div class="col-md-6">')
        html.append('<div class="card">')
        html.append('<div class="card-header">')
        html.append(f'<h4>{content["header"]}</h4>')
        html.append('</div>')
        html.append('<div class="card-body">')

        for row in content["rows"]:
            html.append('<div class="row g-3">')
            for column in row["columns"]:
                field_id = column["field_id"]
                field = form_data["fields"][field_id]
                html.append(f'<div class="col-md-{column["col_size"]}">')
                html.append(generate_field_html(field_id, field))
                html.append('</div>')
            html.append('</div>')

        html.append('</div>')
        html.append('</div>')
        html.append('</div>')

    html.append('</div>')
    html.append('<div class="col-12">')
    html.append('<button type="submit" class="btn btn-outline-light mb-3">Submit</button>')
    html.append('</div>')
    html.append('</form>')
    html.append('</div>')

    return "\n".join(html)
