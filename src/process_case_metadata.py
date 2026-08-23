import csv
import re
import sys

csv_output_file_path = "data/summary/processed_case_metadata.csv"


def get_info_from_title(title):
    regex = (
        r"(?P<applicant>(Applicant|Appellant)(/Respondent)?)(\s)?"
        r"(?P<applicant_role>(Land(l)?ord|Tenant|Tenanst|Third Part(y|ies)|\s)(s)?)(\s)*:?(\s)*"
        r"(?P<applicant_names>.*?)(\s)*(–|vs|v|&)?(\s)*"
        r"(?P<respondent>(Respondent|Respondant|Appellant)(/Applicant)?)(\s)*"
        r"(?P<respondent_role>(Land(l)?ord|Tenant|Tenanst|Third Part(y|ies)|\s)(s)?)(\s)*:?(\s)*"
        r"(?P<respondent_names>.*)"
    )

    match = re.search(regex, title, re.IGNORECASE)
    if not match:
        print(f"Could not match {title}")
        return {
            "tenants": "",
            "tenant_role": "",
            "landlords": "",
            "landlord_role": "",
        }

    applicant = match.group("applicant")
    applicant_role = match.group("applicant_role")
    respondent = match.group("respondent")
    respondent_role = match.group("respondent_role")
    applicant_names = match.group("applicant_names")
    respondent_names = match.group("respondent_names")
    try:
        if "Tenant" in applicant_role or "Landlord" in respondent_role:
            tenants = applicant_names
            tenant_role = applicant
        if "Landlord" in applicant_role or "Tenant" in respondent_role:
            landlords = applicant_names
            landlord_role = applicant
        if "Tenant" in respondent_role or "Landlord" in applicant_role:
            tenants = respondent_names
            tenant_role = respondent
        if "Landlord" in respondent_role or "Tenant" in applicant_role:
            landlords = respondent_names
            landlord_role = respondent
        return {
            "tenants": tenants,
            "tenant_role": tenant_role,
            "landlords": landlords,
            "landlord_role": landlord_role,
        }
    except UnboundLocalError as e:
        print(f"{e}")
        print(f"{title=}")
        print(f"{match=}")
        print(
            f"{applicant_role=}\n{respondent_role=}\n{applicant_names=}\n{respondent_names=}"
        )
        return {
            "tenants": "",
            "tenant_role": "",
            "landlords": "",
            "landlord_role": "",
        }


def read_case_metadata(file_path):
    output_rows = []
    with open(file_path, "r", encoding="utf-8") as case_metadata:
        csv_reader = csv.DictReader(case_metadata)
        for r in csv_reader:
            output_row = []
            t = r.get("Title")
            t_info = get_info_from_title(t)

            output_row.extend(
                [
                    t_info["tenants"],
                    t_info["tenant_role"],
                    t_info["landlords"],
                    t_info["landlord_role"],
                    r.get("Upload Date"),
                    r.get("Subject"),
                    r.get("Determination"),
                    r.get("DR No.Determination Doc"),
                    r.get("Tribunal"),
                    r.get("TR No."),
                    r.get("Tribunal Doc"),
                ]
            )
            output_rows.append(output_row)
    with open(csv_output_file_path, mode="a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        for r in output_rows:
            csv_writer.writerow(r)


def process_case_metadata(file_paths):
    # Write CSV header
    with open(csv_output_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "Tenant Name(s)",
                "Tenant Role",
                "Landlord Name(s)",
                "Landlord Role",
                "Upload Date",
                "Subject",
                "Determination",
                "DR No.Determination Doc",
                "Tribunal",
                "TR No.",
                "Tribunal Doc",
            ]
        )

    for file_path in file_paths:
        print(f"Processing: {file_path}")
        read_case_metadata(file_path)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        process_case_metadata(sys.argv[1:])
    else:
        print("Need at least one file path argument!")
