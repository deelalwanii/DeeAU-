AUDIT_GROUPS = [
    {
        "id": "DATA",
        "name": "Data Integrity & Completeness",
        "description": "Foundational checks for missing identifiers, dates and transaction amounts.",
        "rules": [
            {"id":"DATA-001","name":"Mandatory Transaction ID","description":"Flag transactions without a transaction/document identifier.","group":"Data Integrity & Completeness"},
            {"id":"DATA-002","name":"Mandatory Transaction Date","description":"Flag missing or invalid transaction dates.","group":"Data Integrity & Completeness"},
            {"id":"DATA-003","name":"Mandatory Amount","description":"Flag missing or non-numeric transaction amounts.","group":"Data Integrity & Completeness"},
        ],
    },
    {
        "id": "DUP",
        "name": "Duplicate & Repeat Transactions",
        "description": "Identify potentially duplicated transaction identifiers and invoice/reference numbers.",
        "rules": [
            {"id":"DUP-001","name":"Duplicate Transaction ID","description":"Flag repeated transaction IDs.","group":"Duplicate & Repeat Transactions"},
            {"id":"DUP-002","name":"Duplicate Invoice / Reference","description":"Flag repeated invoice or reference numbers.","group":"Duplicate & Repeat Transactions"},
        ],
    },
    {
        "id": "DATE",
        "name": "Date & Cut-off Review",
        "description": "Identify future-dated transactions and transaction/posting date inconsistencies.",
        "rules": [
            {"id":"DATE-001","name":"Future-Dated Transaction","description":"Flag transactions dated after the current date.","group":"Date & Cut-off Review"},
            {"id":"DATE-002","name":"Transaction Date After Posting Date","description":"Flag transaction dates later than posting/accounting dates.","group":"Date & Cut-off Review"},
        ],
    },
    {
        "id": "AMT",
        "name": "Amount & Outlier Review",
        "description": "Review zero-value and statistically unusual transaction amounts.",
        "rules": [
            {"id":"AMT-001","name":"Zero-Value Transaction","description":"Flag transactions with an amount of zero.","group":"Amount & Outlier Review"},
            {"id":"AMT-002","name":"Statistical Amount Outlier","description":"Flag unusually high absolute transaction values using an IQR-based threshold.","group":"Amount & Outlier Review"},
        ],
    },
    {
        "id": "GST",
        "name": "GST / Tax Consistency",
        "description": "Basic GST field consistency and rate validation. Exact tax rules should be mapped from the approved Rule Book.",
        "rules": [
            {"id":"GST-001","name":"GST Rate vs GST Amount Consistency","description":"Flag records where one GST field is populated while the other is zero/missing.","group":"GST / Tax Consistency"},
            {"id":"GST-002","name":"GST Rate Range","description":"Flag GST/tax rates outside 0–100%.","group":"GST / Tax Consistency"},
        ],
    },
    {
        "id": "PARTY",
        "name": "Party / Master Data Review",
        "description": "Review party-name completeness and GSTIN structure.",
        "rules": [
            {"id":"PARTY-001","name":"Missing Party Name","description":"Flag transactions with missing vendor/customer/party names.","group":"Party / Master Data Review"},
            {"id":"PARTY-002","name":"GSTIN Format","description":"Flag non-empty GSTIN values that do not match the expected 15-character structure.","group":"Party / Master Data Review"},
        ],
    },
    {
        "id": "TEXT",
        "name": "Narration / Documentation",
        "description": "Basic review of transaction descriptions or narrations.",
        "rules": [
            {"id":"TEXT-001","name":"Missing Narration / Description","description":"Flag transactions without a usable description or narration.","group":"Narration / Documentation"},
        ],
    },
]
