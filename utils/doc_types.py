"""
Central config for all document types.
Defines: API type string, S3 folder, default structure, classifier label.
"""

DOC_TYPES = {
    "Insurance": {
        "api_type": "Insurance",
        "s3_folder": "insurance",
        "classifier_label": "Certificate of Insurance",
        "structure": {
            "Certificate_Issue_Date": "string (YYYY-MM-DD)",
            "Producer": {
                "Name": "string",
                "Contact": "string",
                "Phone": "string",
                "Fax": "string",
                "Email": "string",
                "Address": "string"
            },
            "Insured": {
                "Name": "string",
                "Address": "string"
            },
            "Insurers": [[
                {
                    "Insurer_Name": "string",
                    "NAIC_Number": "string"
                }
            ]],
            "Policies": [[
                {
                    "Type": "string",
                    "Policy_Number": "string",
                    "Effective_Date": "string (YYYY-MM-DD)",
                    "Expiration_Date": "string (YYYY-MM-DD)",
                    "Coverage_Limits": {},
                    "Additional_Insured": "boolean",
                    "Subrogation_Waived": "boolean"
                }
            ]],
            "Certificate_Holder": "sentence",
            "Description_of_Operations": "sentence",
            "Cancellation_Clause": "sentence"
        }
    },
    "Rent Roll": {
        "api_type": "Rentroll",
        "s3_folder": "rentroll",
        "classifier_label": "Rent Roll",
        "structure": {
            "Total_Monthly_Income": "float or null",
            "Projected_Annual_Income": "float or null",
            "Units": [
                {
                    "UNIT": "string",
                    "TENANT": "string",
                    "RENT": "float",
                    "LEASE_END_DATE": "string",
                    "SQ_FT": "float or null"
                }
            ]
        }
    },
    "PFS": {
        "api_type": "PFSIncomeStatement",
        "s3_folder": "pfs",
        "classifier_label": "Personal Financial Statement",
        "structure": {
    "ASSETS": {
        "Cash with us": 0.0,
        "Cash in Other Financial Institutions": 0.0,
        "Marketable Securities": 0.0,
        "Non-Marketable Securities": 0.0,
        "Accounts and Notes Receivable": 0.0,
        "Net Cash Surrender Value of Life Insurance": 0.0,
        "Residential Real Estate": 0.0,
        "Real Estate Investments": 0.0,
        "Partnerships / PC Interests": 0.0,
        "Retirement Accounts": 0.0,
        "Deferred Income": 0.0,
        "Personal Property": 0.0,
        "Other Assets": 0.0
    },
    "LIABILITIES": {
        "Notes Payable to us - Secured": 0.0,
        "Notes Payable to us - Unsec.": 0.0,
        "Notes Payable to Others - Secured": 0.0,
        "Notes Payable to Others - Unsecured": 0.0,
        "Accounts Payable (Incl. Credit Cards)": 0.0,
        "Margin Accounts": 0.0,
        "Taxes Payable": 0.0,
        "Mortgage Debt": 0.0,
        "Investment RE Debt": 0.0,
        "Life Insurance Loans": 0.0,
        "Other Liabilities": 0.0,
        "Contingent Liabilities": 0.0,
        "OUTSIDE NET WORTH": 0.0,
        "Notes Due: Partnership": 0.0
    },
    "INCOME": {
        "Salary (Applicant)": 0.0,
        "Salary (Co-applicant)": 0.0,
        "Bonuses & Commissions (Applicant)": 0.0,
        "Bonuses & Commissions (Co-applicant)": 0.0,
        "Interest & Dividends [Sch B]": 0.0,
        "Rental Income": 0.0,
        "Capital Gains": 0.0,
        "Partnership Income": 0.0,
        "IRA Distribution (Pension)": 0.0,
        "Interest Income": 0.0,
        "Dividend Income": 0.0,
        "Other Investment Income": 0.0,
        "Other Income": 0.0,
        "Sole Proprietorship Income (Loss)": 0.0,
        "Alimony/Child Support": 0.0,
        "Part. / S-Corp Distrib": 0.0,
        "Rental Real Estate Debt Service": 0.0,
        "Cash flow adjustments": 0.0,
        "Interest, Depreciation, amortization, depletion": 0.0,
        "Interest, Depreciation, amortization, depletion(RE)": 0.0,
        "1. Loans from (to) Partnerships / S-Corps.": 0.0,
        "2. Loans from (to) Partnerships / S-Corps.": 0.0
    },
    "DSCR": {
        "Adjustment to Living Expenses": 0.0
    }
}
    }
}

DOC_TYPE_NAMES = list(DOC_TYPES.keys())
