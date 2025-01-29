from flask import jsonify, request
from flask_openapi3 import Tag, Info, OpenAPI

from models.base import SuccessResponse
from routes.therapists import therapist_api
from routes.appointments import appointment_api
from routes.clients import client_api
from utils.intakeq_bot.bot import create_new_form

response_json = {
    "event_id": "01JHT5Y038XAE3DDGVW59SH78Y",
    "event_type": "form_response",
    "form_response": {
        "form_id": "TMxI2YZz",
        "token": "5nrwx22qacsa3u4vdvnor5nrwx9aadgb",
        "landed_at": "2025-01-17T13:01:39Z",
        "submitted_at": "2025-01-17T13:06:10Z",
        "hidden": {
            "utm_medium": "",
            "utm_source": ""
        },
        "calculated": {
            "score": 0
        },
        "variables": [
            {
                "key": "alcohol",
                "type": "number",
                "number": 0
            },
            {
                "key": "drugs",
                "type": "number",
                "number": 0
            },
            {
                "key": "gad",
                "type": "number",
                "number": 0
            },
            {
                "key": "phq",
                "type": "number",
                "number": 0
            },
            {
                "key": "score",
                "type": "number",
                "number": 0
            },
            {
                "key": "si",
                "type": "number",
                "number": 0
            }
        ],
        "definition": {
            "id": "TMxI2YZz",
            "title": "Sign Up (test copy)",
            "fields": [
                {
                    "id": "fSDqGEVkMCdR",
                    "ref": "e256b923-dbd5-45dc-9870-095fb8bfdb63",
                    "type": "yes_no",
                    "title": "Are you based in *NY, NJ, CT, FL, *or* TX*?",
                    "properties": {}
                },
                {
                    "id": "P9jETkuWB85E",
                    "ref": "cf6c1ace-73ef-47c5-a1a8-e0833448a7e1",
                    "type": "yes_no",
                    "title": "Over the past two weeks, have you been *actively suicidal or homicidal *OR have you been experiencing *hallucinations or delusions*?",
                    "properties": {}
                },
                {
                    "id": "Bcd3yhtVV8qA",
                    "ref": "5756e4ea-dfbc-4157-9caa-d6cbc6355777",
                    "type": "short_text",
                    "title": "First name",
                    "properties": {}
                },
                {
                    "id": "91kMGKU8j2CH",
                    "ref": "9154eaac-867c-4df8-bebe-658bd3492ed2",
                    "type": "short_text",
                    "title": "Last name",
                    "properties": {}
                },
                {
                    "id": "b9DkubXQl2D3",
                    "ref": "dee42c6d-e644-4542-99d2-c02a1dbc9d0a",
                    "type": "phone_number",
                    "title": "Phone number",
                    "properties": {}
                },
                {
                    "id": "0aZPHNSS2AEa",
                    "ref": "157795ea-4579-4351-88c2-168ae4b51bf7",
                    "type": "email",
                    "title": "Email",
                    "properties": {}
                },
                {
                    "id": "B443qff2ZRvs",
                    "ref": "f4384935-2135-47cd-bfa1-0bf2e0104399",
                    "type": "multiple_choice",
                    "title": "I would like a therapist that",
                    "properties": {},
                    "allow_multiple_selections": True,
                    "choices": [
                        {
                            "id": "QB6zl95ogYdb",
                            "ref": "dd335846-cc2b-4d2d-9530-b3e9660fcbfb",
                            "label": "Assigns homework"
                        },
                        {
                            "id": "qmrQpX6kIY7e",
                            "ref": "1edc86bd-263e-4baa-921a-193770468d89",
                            "label": "CBT-focused"
                        },
                        {
                            "id": "1AlTSzfg8eGk",
                            "ref": "a4ce8a2f-4023-4f8c-906a-bf2ec1886889",
                            "label": "Challenges my beliefs"
                        },
                        {
                            "id": "V5QMOkaDCYLT",
                            "ref": "8159790f-c424-4338-9c51-b5d2a68983d8",
                            "label": "DBT skills based"
                        },
                        {
                            "id": "q0GTB9PJOrLh",
                            "ref": "3d65cdc8-7818-436a-a28d-ac22378dd079",
                            "label": "Empathic"
                        },
                        {
                            "id": "0THJOH8Cx1UI",
                            "ref": "a2011563-ce96-4c36-a274-08f3b53d2cd3",
                            "label": "Explores my past"
                        },
                        {
                            "id": "MnfPILYEta2m",
                            "ref": "30cbd9cd-fae9-45c6-a4f9-b483ab38ed2e",
                            "label": "Explores my thoughts"
                        },
                        {
                            "id": "8cDQL6gFXDuu",
                            "ref": "e1ad3364-6667-4155-a318-3c9ef9af0280",
                            "label": "Helps me set goals"
                        },
                        {
                            "id": "QxJkeVgclWY8",
                            "ref": "07d30340-25ed-447d-bfed-e2047bbdcf2b",
                            "label": "Is curious"
                        },
                        {
                            "id": "ou8CBu3pLE4m",
                            "ref": "8f67bef8-d8a3-4c0e-bf68-4aa301b455ab",
                            "label": "Is male"
                        },
                        {
                            "id": "3gVdRiiSl7IN",
                            "ref": "ee7750c9-5a6a-40ce-9c82-404959554a5e",
                            "label": "Is female"
                        },
                        {
                            "id": "2UMubc3D4ML3",
                            "ref": "bc2da1e1-685f-40cc-b7d1-80729a9b6f81",
                            "label": "Multicultural"
                        },
                        {
                            "id": "CqGc4JnI077o",
                            "ref": "f9a17119-7a4e-43c8-8963-5107935a1bb7",
                            "label": "Open-minded"
                        },
                        {
                            "id": "cL32kd5S4P1c",
                            "ref": "aa9c1490-5560-48b1-9900-228248d74771",
                            "label": "Psychodynamic"
                        },
                        {
                            "id": "kpswGZyMjqOP",
                            "ref": "42a65ad3-6d57-4207-8824-29e1e5cd49b3",
                            "label": "Teaches new skills"
                        }
                    ]
                },
                {
                    "id": "pTMOjbjkbSWL",
                    "ref": "a56351d1-d292-4d96-bb95-7323219ee5f2",
                    "type": "multiple_choice",
                    "title": "Are there any lived experiences you identify with that you feel are important to your match?",
                    "properties": {},
                    "allow_multiple_selections": True,
                    "choices": [
                        {
                            "id": "zgCmKD1VBXx9",
                            "ref": "b0383ce1-0f03-4097-ac9a-90a9541608db",
                            "label": "🏡 Grew up in a non-traditional family (e.g. single or divorced parents or foster family)"
                        },
                        {
                            "id": "DNq6yiUHZGoK",
                            "ref": "e364a0e6-ad29-490f-9320-08205666343e",
                            "label": "🌏 First/second generation immigrant"
                        },
                        {
                            "id": "Enf2GgB4CEMV",
                            "ref": "332c5ec2-4a63-4f5b-8742-31bd80e497a4",
                            "label": "🧍‍♂️Raised in an individualist culture"
                        },
                        {
                            "id": "mpTV4XZzVPTv",
                            "ref": "d3cdb0c4-5935-422e-a952-069938479751",
                            "label": "🤝 Raised in a collectivist culture"
                        },
                        {
                            "id": "APhgNl59W40e",
                            "ref": "4050bab1-7a23-48b1-bb3b-feff11500187",
                            "label": "🗺️ Lived in many places"
                        },
                        {
                            "id": "4uYQe6gb1EDf",
                            "ref": "b36fccb5-8930-49c2-82ac-080b6312b492",
                            "label": "🫶 Been in a caretaker role"
                        },
                        {
                            "id": "TaxuLRETEXhp",
                            "ref": "1cb75c5e-9f2f-4f86-9913-ff44f738e145",
                            "label": "🌈 Identifying as LGBTQ+"
                        },
                        {
                            "id": "2dtGN1qOo2uZ",
                            "ref": "6380e493-eb31-4b04-99dc-4b939d0e4531",
                            "label": "🤳Negatively affected by social media"
                        },
                        {
                            "id": "w0y1jCidgT0t",
                            "ref": "bfa4a67e-2f43-486e-ad5e-5fb58df879b7",
                            "label": "🎨 Performing/visual arts is important"
                        }
                    ]
                },
                {
                    "id": "DxXG5npFnjPd",
                    "ref": "1e9868b4-9c8c-41ad-af9a-d1cdafdc9915",
                    "type": "multiple_choice",
                    "title": "Do you drink *alcohol*? If yes, how often per week?",
                    "properties": {},
                    "choices": [
                        {
                            "id": "PmN145PWZJWk",
                            "ref": "85bd6416-2aef-4cfe-bbec-045fcbe108e3",
                            "label": "Not at all"
                        },
                        {
                            "id": "1DoYDg1TCfBj",
                            "ref": "87a46a27-0b83-47e7-900c-b29b106e0b0b",
                            "label": "Several days"
                        },
                        {
                            "id": "8T24he6F0WKJ",
                            "ref": "515bb978-6353-411b-a3b7-1fcdaa6f3492",
                            "label": "More than half the days"
                        },
                        {
                            "id": "btOIEyxTTDne",
                            "ref": "8142be9a-739e-40aa-918f-640934469905",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "DEC8S8r60O1U",
                    "ref": "28963f0c-debd-4b55-b39e-46c56a6a6949",
                    "type": "multiple_choice",
                    "title": "Do you use *recreational drugs*? If yes, how often per week? ",
                    "properties": {},
                    "choices": [
                        {
                            "id": "zvBEMIh374bI",
                            "ref": "dba05692-a53c-40d5-a633-79e46f7ef70c",
                            "label": "Not at all"
                        },
                        {
                            "id": "afara6zzQnOl",
                            "ref": "6b4cfcd3-af00-4af1-914f-4fb0aa975fab",
                            "label": "Several days"
                        },
                        {
                            "id": "KOQV2l1IBjPl",
                            "ref": "e1cce7cc-b89e-401f-9657-aa50d406e30f",
                            "label": "More than half the days"
                        },
                        {
                            "id": "MJlZ5p5C67YK",
                            "ref": "8cd5f680-0305-4890-89cd-51d1e3ae527f",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "7kQjFzstcJts",
                    "ref": "0df712be-e6db-4f67-9090-bc3f8acd03b1",
                    "type": "multiple_choice",
                    "title": "Little interest or pleasure in doing things",
                    "properties": {},
                    "choices": [
                        {
                            "id": "YQ8mp7bOF8NB",
                            "ref": "379f5435-7dde-45da-96a2-19777cdae9b4",
                            "label": "Not at all"
                        },
                        {
                            "id": "suLZus7S7Fok",
                            "ref": "f2fd96af-27b9-4a02-bbe2-80e3eaf380d6",
                            "label": "Several days"
                        },
                        {
                            "id": "VDbNZEmgM2at",
                            "ref": "1e7b8243-4350-49de-b58a-9d6eae8cda59",
                            "label": "More than half the days"
                        },
                        {
                            "id": "H1Kf0NYlHwc1",
                            "ref": "4ef1f30d-504b-49ef-94ad-fad427cda24b",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "uUQMfw2xRiQ4",
                    "ref": "571c3436-0da5-4b3e-9615-d7f5b5337f62",
                    "type": "multiple_choice",
                    "title": "Feeling down, depressed, or hopeless",
                    "properties": {},
                    "choices": [
                        {
                            "id": "2DKGjdNgUNME",
                            "ref": "b8682870-0757-48a5-9243-c221f50e3de9",
                            "label": "Not at all"
                        },
                        {
                            "id": "xnHdxzTKSjMi",
                            "ref": "2fd87e5d-794e-40d9-af31-d2f5a7536895",
                            "label": "Several days"
                        },
                        {
                            "id": "cKMV3O18Ulv4",
                            "ref": "949d87b0-7154-47d1-81bc-40c6cf37522f",
                            "label": "More than half the days"
                        },
                        {
                            "id": "jQtgDqV9RCIv",
                            "ref": "5f89218f-5574-44ad-8f2f-8db20a4a65af",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "G9LdjqKeO7f4",
                    "ref": "79b190b1-e1b5-4ae8-a883-74458baf2ba8",
                    "type": "multiple_choice",
                    "title": "Trouble falling or staying asleep, or sleeping too much",
                    "properties": {},
                    "choices": [
                        {
                            "id": "rg2e9agBmqvu",
                            "ref": "91c9109d-6be0-4768-99ac-cb920cdd70f4",
                            "label": "Not at all"
                        },
                        {
                            "id": "mJoLDpRyJNqN",
                            "ref": "6b969e5a-196c-4f0b-86e7-3ffa51a9b4fb",
                            "label": "Several days"
                        },
                        {
                            "id": "3VFjUjod3Jwr",
                            "ref": "6f25276d-ace1-4c00-a55e-8ac651957a9c",
                            "label": "More than half the days"
                        },
                        {
                            "id": "ZmODoDD5E0SY",
                            "ref": "9b4f3038-4dc5-47d1-857d-002ba1f1ef14",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "YFkgwTszPtMN",
                    "ref": "038f9c71-97c7-4aa0-98a2-8a781c75a2fc",
                    "type": "multiple_choice",
                    "title": "Feeling tired or having little energy",
                    "properties": {},
                    "choices": [
                        {
                            "id": "k2EKTGCbtdb4",
                            "ref": "c6184041-c7d2-4acb-bd7e-7caa2106c70d",
                            "label": "Not at all"
                        },
                        {
                            "id": "g3hrvNzZPJvP",
                            "ref": "450136c8-8497-4e02-82ef-8554c07d0843",
                            "label": "Several days"
                        },
                        {
                            "id": "H8htmJIfK7j5",
                            "ref": "99437385-d132-4aed-b5b3-e078f4c8b412",
                            "label": "More than half the days"
                        },
                        {
                            "id": "vSakyeOYDbKe",
                            "ref": "006565d3-c3f4-4491-846f-45f7a005453c",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "TKA1j8lE6SSd",
                    "ref": "1cf50bd4-aa7a-4672-8b50-d1ecf458ab55",
                    "type": "multiple_choice",
                    "title": "Poor appetite or overeating",
                    "properties": {},
                    "choices": [
                        {
                            "id": "ISx77uyoJLxr",
                            "ref": "ab708488-909e-4440-a252-86c1841bfbf8",
                            "label": "Not at all"
                        },
                        {
                            "id": "aStqHPOmyjoU",
                            "ref": "8c4746eb-4731-4f56-8b34-426b367c8ac4",
                            "label": "Several days"
                        },
                        {
                            "id": "EaUZ1GfrXCbw",
                            "ref": "70c014f6-e066-41eb-bea4-58194c0afbe9",
                            "label": "More than half the days"
                        },
                        {
                            "id": "NzKBjwVmDjTO",
                            "ref": "d82f4d33-2b19-427a-995a-d6c35748c654",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "TsZ80LFOtbCq",
                    "ref": "9bb34921-0926-46b9-b3fc-bd29d6987602",
                    "type": "multiple_choice",
                    "title": "Feeling bad about yourself - or that you are a failure or have let yourself or your family down\t",
                    "properties": {},
                    "choices": [
                        {
                            "id": "Jwd7IRMVo2zF",
                            "ref": "8e828d22-0e66-420d-a0ee-b0371938b27a",
                            "label": "Not at all"
                        },
                        {
                            "id": "yQNBH8W9EwLT",
                            "ref": "623414f3-d5c6-4aa1-ad0a-89eb14005297",
                            "label": "Several days"
                        },
                        {
                            "id": "5UQr0Y2vndmz",
                            "ref": "bfb3604f-9b9f-4117-9981-2792ee7f1f0a",
                            "label": "More than half the days"
                        },
                        {
                            "id": "A0aOw2eYFbHp",
                            "ref": "bf7f33a6-5041-4ec1-97f3-c06fb534e41f",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "3SCH6BP1SZWt",
                    "ref": "522d3b7a-7608-4ed2-8e65-36503f1bb0db",
                    "type": "multiple_choice",
                    "title": "Trouble concentrating on things, such as reading the newspaper or watching television",
                    "properties": {},
                    "choices": [
                        {
                            "id": "LJ6MnHyCXA8S",
                            "ref": "38719cc7-d21b-4159-a8d3-d4817b085ae1",
                            "label": "Not at all"
                        },
                        {
                            "id": "NAAtDcGMcHpQ",
                            "ref": "c600f9d5-a0a0-4d2d-8331-04626d3eea90",
                            "label": "Several days"
                        },
                        {
                            "id": "1BArVXl5yMqW",
                            "ref": "62d4b98c-dd9e-40cd-a9e6-81517792e727",
                            "label": "More than half the days"
                        },
                        {
                            "id": "VRGRoHXCrAkU",
                            "ref": "18e6d5a0-96d6-478c-a4ec-ab99a56247d9",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "eca2CSO04vLl",
                    "ref": "990e62e6-0c9c-425e-88d2-65e1e9271341",
                    "type": "multiple_choice",
                    "title": "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual.",
                    "properties": {},
                    "choices": [
                        {
                            "id": "RLudVDDF3yOR",
                            "ref": "d5bf33ce-5108-47bb-929b-d21da743b00c",
                            "label": "Not at all"
                        },
                        {
                            "id": "SlV3bnl9BYAp",
                            "ref": "ef62d6cb-13d6-4623-9c81-1c7e23e050e3",
                            "label": "Several days"
                        },
                        {
                            "id": "cH52kdUdqCfp",
                            "ref": "ad9f46d9-d80b-47ee-9267-3b46c24170b0",
                            "label": "More than half the days"
                        },
                        {
                            "id": "ppa8oZFuadu4",
                            "ref": "d62398db-3a1c-40a2-8b52-25efb70afb15",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "chxgOkME9qj4",
                    "ref": "d7d36e9d-25e5-4e9f-be54-4db916a10891",
                    "type": "multiple_choice",
                    "title": "Thoughts that you would be better off dead, or of hurting yourself",
                    "properties": {},
                    "choices": [
                        {
                            "id": "YIvR3JhKhobh",
                            "ref": "fb8d9aa1-fe32-4e13-b308-cd22e483c722",
                            "label": "Not at all"
                        },
                        {
                            "id": "vk1JfIT3kJ6J",
                            "ref": "7c28a4af-1434-46e4-bc42-fcde3585a61b",
                            "label": "Several days"
                        },
                        {
                            "id": "kMfiJdv5Wi5H",
                            "ref": "a2eeeb41-652f-44dc-8526-3216b4f580b2",
                            "label": "More than half the days"
                        },
                        {
                            "id": "9iETfXrxlM8d",
                            "ref": "d4f83971-17d8-4cbd-a1f1-7c5dfba160cd",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "B3cxNBp1tpIq",
                    "ref": "7e560f59-a2f2-494d-8e6b-860741592d07",
                    "type": "multiple_choice",
                    "title": "Feeling nervous, anxious, or on edge",
                    "properties": {},
                    "choices": [
                        {
                            "id": "5o7FSGSy09Kj",
                            "ref": "b8272bf6-1992-44eb-a2ff-ece13b9202a7",
                            "label": "Not at all"
                        },
                        {
                            "id": "2wVQtSSyfxew",
                            "ref": "038c5013-628c-4a89-93a9-33aded37f9a6",
                            "label": "Several days"
                        },
                        {
                            "id": "Ca26UveZncfS",
                            "ref": "71bfe04c-6690-4cb1-bdf5-394d8f9d1bfa",
                            "label": "More than half the days"
                        },
                        {
                            "id": "kVgOdJ5dV5fO",
                            "ref": "f81f61b0-fb0b-4905-aaff-fcfc3578293f",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "bvL83C6M9nb1",
                    "ref": "1fdc1b54-7abc-44e9-b6bd-a65dd0f7fe2a",
                    "type": "multiple_choice",
                    "title": "Not being able to stop or control worrying",
                    "properties": {},
                    "choices": [
                        {
                            "id": "soGVbIy0xg0C",
                            "ref": "fb66fc9c-f87a-402b-bb4e-66fbf74d57ec",
                            "label": "Not at all"
                        },
                        {
                            "id": "27FJ0tgnuGXe",
                            "ref": "19a4fd37-d6ae-4a5c-8093-6d0b3e86217c",
                            "label": "Several days"
                        },
                        {
                            "id": "SasF8mkO09ra",
                            "ref": "2f225818-e675-4709-9c9a-19967b4db315",
                            "label": "More than half the days"
                        },
                        {
                            "id": "XNjm3g99Vdxt",
                            "ref": "c9e2ff37-b91c-419f-9c0c-813261d516c0",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "RdiG8vKXrbVB",
                    "ref": "449f9821-efaa-49e3-b632-4f4bc8a18a22",
                    "type": "multiple_choice",
                    "title": "Worrying too much about different things",
                    "properties": {},
                    "choices": [
                        {
                            "id": "UUvW9lZUW1EH",
                            "ref": "797de514-67d8-42f3-a334-b7b9fa723ecc",
                            "label": "Not at all"
                        },
                        {
                            "id": "LGciRUU7GV9b",
                            "ref": "7ba773f0-1e2b-4b34-a98e-2c9f4afb4b3d",
                            "label": "Several days"
                        },
                        {
                            "id": "UPRKKcTvgids",
                            "ref": "1007446f-e0b0-46a6-811d-481b999132fe",
                            "label": "More than half the days"
                        },
                        {
                            "id": "FifjBS1DeiuB",
                            "ref": "347195f0-6d7e-4e79-9646-6fa9f110a2b0",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "98pYB4y1REbK",
                    "ref": "d6e8ce4f-84b6-4d5e-b584-6ab69fec5087",
                    "type": "multiple_choice",
                    "title": "Trouble relaxing",
                    "properties": {},
                    "choices": [
                        {
                            "id": "FWyj8JfvGZWO",
                            "ref": "ad57a751-8784-4daf-ac94-c65d60668999",
                            "label": "Not at all"
                        },
                        {
                            "id": "fLx2DVk8EZBF",
                            "ref": "6fd455bd-9f61-42de-9d4e-8fc7b644f770",
                            "label": "Several days"
                        },
                        {
                            "id": "93uCA1Gl5Zl9",
                            "ref": "7ccb5faa-26a3-4ef7-8ef4-effa82cffb9f",
                            "label": "More than half the days"
                        },
                        {
                            "id": "s0AttJuRNmvY",
                            "ref": "b906501c-2b1a-41c4-bf42-6e5a9650d38d",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "yVJsRQvXsi1T",
                    "ref": "cdf74907-9bc3-48b1-b080-9f18a27b9d8f",
                    "type": "multiple_choice",
                    "title": "Being so restless that it is hard to sit still",
                    "properties": {},
                    "choices": [
                        {
                            "id": "pUteyUejRcy5",
                            "ref": "9510ab45-fb0c-4fc6-a84d-409dda9a5615",
                            "label": "Not at all"
                        },
                        {
                            "id": "E5t9F0tk7EAu",
                            "ref": "9108eba4-d1ce-4a64-90bf-31ec7e2057e1",
                            "label": "Several days"
                        },
                        {
                            "id": "5rVHi4SmZ8Mq",
                            "ref": "9fee6bef-5f85-496b-b946-fc3a4d0ca9b4",
                            "label": "More than half the days"
                        },
                        {
                            "id": "AezwTo8Z0MFt",
                            "ref": "3b270132-82b1-4535-9b40-b4033ee8dca3",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "QtDBqAbfBRAR",
                    "ref": "7d1a2322-840c-494a-8155-0bdea0eefdb6",
                    "type": "multiple_choice",
                    "title": "Becoming easily annoyed or irritable",
                    "properties": {},
                    "choices": [
                        {
                            "id": "ifUwuzqu6PVc",
                            "ref": "e66078e5-633c-4d73-8e66-e7ee5733c203",
                            "label": "Not at all"
                        },
                        {
                            "id": "pUyLTms0qj4H",
                            "ref": "2f92bae1-1dfb-415a-8365-a0fb876e2709",
                            "label": "Several days"
                        },
                        {
                            "id": "FHZKiKVzahA2",
                            "ref": "fd37bb66-48a3-4ed4-ab11-f0ecf8950a52",
                            "label": "More than half the days"
                        },
                        {
                            "id": "xUPdVkRKGO4K",
                            "ref": "ef880809-5b70-4088-8e97-72ef9153a8a8",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "1l3TD4JycX7a",
                    "ref": "3d7046be-905b-4c67-af66-01ca3373c433",
                    "type": "multiple_choice",
                    "title": "Feeling afraid, as if something awful might happen",
                    "properties": {},
                    "choices": [
                        {
                            "id": "89DV1huvypPY",
                            "ref": "2423ac0e-c350-401d-a060-8bf34e636025",
                            "label": "Not at all"
                        },
                        {
                            "id": "kbvE4Ht3FmNv",
                            "ref": "809d73b9-79d5-41d6-9f87-cd96bbfcfe0b",
                            "label": "Several days"
                        },
                        {
                            "id": "nhoOahDVGxec",
                            "ref": "1ee624d1-29a1-4d8f-8b20-ef3a88104843",
                            "label": "More than half the days"
                        },
                        {
                            "id": "3XEjydXZSUUN",
                            "ref": "caeed31d-06af-47d1-a8da-0aafb3d92a26",
                            "label": "Nearly every day"
                        }
                    ]
                },
                {
                    "id": "RngVovIqApk0",
                    "ref": "f29960c6-2c0b-44e9-ae7f-8ace0d09c2f6",
                    "type": "short_text",
                    "title": "What brings you to therapy at this time?",
                    "properties": {}
                },
                {
                    "id": "NFyGjLRsvOQb",
                    "ref": "fe5e6540-7043-403b-9d01-cf655043622e",
                    "type": "number",
                    "title": "Please enter your *age*",
                    "properties": {}
                },
                {
                    "id": "clAn8i6OQOI3",
                    "ref": "0332dede-1cbf-4add-b4ed-aa9decd3f7e9",
                    "type": "multiple_choice",
                    "title": "Please enter your *gender*",
                    "properties": {},
                    "choices": [
                        {
                            "id": "nTnh3ZK2R0fD",
                            "ref": "63ed36e5-8dee-4abf-a911-50545e01ca92",
                            "label": "Female"
                        },
                        {
                            "id": "b2f6XULjo15V",
                            "ref": "5e637f08-39c1-4737-95ca-fe8230b6bd9c",
                            "label": "Male"
                        },
                        {
                            "id": "Fubm07Pf4beR",
                            "ref": "7b8391c6-c4aa-41dd-b96b-3caf603cb872",
                            "label": "Transgender"
                        },
                        {
                            "id": "aZwRVzbnaJ5H",
                            "ref": "44dad4dd-d362-4a67-98a7-f1bf264ed0ce",
                            "label": "Non-binary"
                        },
                        {
                            "id": "p1gkMzqZSYTw",
                            "ref": "c53008c5-8a8c-49f0-ad9d-ef39cfef6cee",
                            "label": "Other"
                        }
                    ]
                },
                {
                    "id": "3AQyhzE0XBx5",
                    "ref": "35ff5a97-a750-4233-9820-26b671b1438e",
                    "type": "dropdown",
                    "title": "What *state* are you currently based in? ",
                    "properties": {}
                },
                {
                    "id": "sHR59ObUeLCw",
                    "ref": "b720b2a6-721a-4094-9a7b-49ddc6800fa1",
                    "type": "short_text",
                    "title": "Please enter your *university* and (anticipated or past) graduation year.",
                    "properties": {}
                },
                {
                    "id": "V7DQU2HoEvfK",
                    "ref": "1c2371f5-54ac-4153-84f6-6d14c280bf33",
                    "type": "short_text",
                    "title": "What days and times work best for your first session?",
                    "properties": {}
                },
                {
                    "id": "ntVzKN7vWQhO",
                    "ref": "5c32892f-fd6a-4085-9a10-1721a570c09f",
                    "type": "multiple_choice",
                    "title": "Lastly, how did you hear about Sol Health?",
                    "properties": {},
                    "allow_multiple_selections": True,
                    "choices": [
                        {
                            "id": "igWefQD9o8sj",
                            "ref": "ba601604-b154-422d-96e6-50362ee59b0b",
                            "label": "Campus Event"
                        },
                        {
                            "id": "ZlhYNHXUwSg3",
                            "ref": "456d4f37-5c09-4669-9b24-d647ab9d42b7",
                            "label": "College Counseling Clinic"
                        },
                        {
                            "id": "aGmEiaEII6eU",
                            "ref": "fb8b33c9-0453-4c18-9ebc-53128f601fbb",
                            "label": "Email Outreach"
                        },
                        {
                            "id": "OagMsoPpxD46",
                            "ref": "9b3449e6-e861-4441-9eb7-8469ae708beb",
                            "label": "Flyer / Poster"
                        },
                        {
                            "id": "i5rgtOldEqa2",
                            "ref": "c5357713-9dc8-4057-95af-4c042be9bb41",
                            "label": "Instagram"
                        },
                        {
                            "id": "ZyAB0CU4uda2",
                            "ref": "03b7654d-9561-449c-ba39-cc6542605f7f",
                            "label": "Google Ad"
                        },
                        {
                            "id": "ve5iY9VbfcRS",
                            "ref": "01e50ef8-6462-409e-bfe3-507b88ebe414",
                            "label": "Google Search"
                        },
                        {
                            "id": "lrwSy6Zce3oQ",
                            "ref": "fa691f96-1614-4bd6-a414-9cb3d0342767",
                            "label": "Open Path Collective"
                        },
                        {
                            "id": "lTuJErc4Sb4k",
                            "ref": "40cca50c-c7a0-45ef-bf06-10052f83d4cd",
                            "label": "Psychology Today"
                        },
                        {
                            "id": "8xGRVzLJnJrN",
                            "ref": "18447fe8-1fcd-44e7-9c05-5bed7345d2ae",
                            "label": "Referral/Word-of-Mouth"
                        },
                        {
                            "id": "0LOOOdDRjzNR",
                            "ref": "1c9acd86-3f51-4675-b88d-a55b973d8ac4",
                            "label": "TikTok"
                        },
                        {
                            "id": "v2biVDuaURKN",
                            "ref": "c358acf5-b573-4854-bef0-44b59cdab88b",
                            "label": "Other"
                        }
                    ]
                },
                {
                    "id": "NMN7aB4l64kj",
                    "ref": "20abed52-aa6a-44cf-821a-b924be43cf3d",
                    "type": "multiple_choice",
                    "title": "I agree to Sol Health's [Terms of Service](https://www.solhealth.co/terms-of-service), [Privacy Policy](https://www.solhealth.co/privacy-policy), and [Telehealth Consent](https://www.solhealth.co/telehealth-consent) forms.\n",
                    "properties": {},
                    "choices": [
                        {
                            "id": "9ldceMwTC7Op",
                            "ref": "cacbbd45-74ee-4f5a-beb4-2d5392c2d655",
                            "label": "I accept"
                        }
                    ]
                }
            ],
            "endings": [
                {
                    "id": "RPWmHaDFESDu",
                    "ref": "542a7611-28f2-4c95-adf4-75f0279b5d11",
                    "title": "*We're excited to have you at Sol, **{{field:5756e4ea-dfbc-4157-9caa-d6cbc6355777}}**. *☀️ ",
                    "type": "thankyou_screen",
                    "properties": {
                        "description": "_*You will receive an email within 24 hours regarding your match, scheduled first session, and video meeting link.*_\n\n*Your Commitment Matters*\nAt Sol Health, our mission is to make therapy accessible and affordable. The reason we’re able to offer therapy at $30/session is our unique model, where therapists-in-training gain valuable clinical hours by working with clients like you.\n\nWhen you sign up for therapy with us, you're not just taking care of yourself—you’re helping our therapists-in-training progress toward licensure.\n\nWe understand that life happens, but if you cancel or don’t show up to your sessions, it impacts not only you but also our therapists-in-training, who have set aside that time to support you on your journey. They rely on these sessions to meet their required clinical hours, which are crucial for their path to licensure. \n\nThank you for helping us make a positive difference—for you, for others, and for our therapists-in-training! 🌱\n\nPlease email us at [contact@solhealth.co](mailto:contact@solhealth.co) if you have any questions. ",
                        "button_text": "Go to Home",
                        "show_button": True,
                        "share_icons": False,
                        "button_mode": "redirect",
                        "redirect_url": "https://www.solhealth.co"
                    },
                    "attachment": {
                        "type": "image",
                        "href": "https://images.typeform.com/images/5CFtfPyPw8Gp",
                        "properties": {
                            "description": "quiz 12"
                        }
                    },
                    "layout": {
                        "type": "stack",
                        "attachment": {
                            "type": "image",
                            "href": "https://images.typeform.com/images/5CFtfPyPw8Gp",
                            "properties": {
                                "brightness": 0,
                                "description": "quiz 12"
                            }
                        },
                        "viewport_overrides": {
                            "small": {
                                "type": "split"
                            }
                        }
                    }
                }
            ]
        },
        "answers": [
            {
                "type": "boolean",
                "boolean": True,
                "field": {
                    "id": "fSDqGEVkMCdR",
                    "type": "yes_no",
                    "ref": "e256b923-dbd5-45dc-9870-095fb8bfdb63"
                }
            },
            {
                "type": "boolean",
                "boolean": False,
                "field": {
                    "id": "P9jETkuWB85E",
                    "type": "yes_no",
                    "ref": "cf6c1ace-73ef-47c5-a1a8-e0833448a7e1"
                }
            },
            {
                "type": "text",
                "text": "PoC though our logic",
                "field": {
                    "id": "Bcd3yhtVV8qA",
                    "type": "short_text",
                    "ref": "5756e4ea-dfbc-4157-9caa-d6cbc6355777"
                }
            },
            {
                "type": "text",
                "text": "Therapist auto assigning",
                "field": {
                    "id": "91kMGKU8j2CH",
                    "type": "short_text",
                    "ref": "9154eaac-867c-4df8-bebe-658bd3492ed2"
                }
            },
            {
                "type": "phone_number",
                "phone_number": "+12015555555",
                "field": {
                    "id": "b9DkubXQl2D3",
                    "type": "phone_number",
                    "ref": "dee42c6d-e644-4542-99d2-c02a1dbc9d0a"
                }
            },
            {
                "type": "email",
                "email": "ayanushkevich+poc@remedypointsolutions.com",
                "field": {
                    "id": "0aZPHNSS2AEa",
                    "type": "email",
                    "ref": "157795ea-4579-4351-88c2-168ae4b51bf7"
                }
            },
            {
                "type": "choices",
                "choices": {
                    "ids": [
                        "q0GTB9PJOrLh"
                    ],
                    "labels": [
                        "Empathic"
                    ],
                    "refs": [
                        "3d65cdc8-7818-436a-a28d-ac22378dd079"
                    ]
                },
                "field": {
                    "id": "B443qff2ZRvs",
                    "type": "multiple_choice",
                    "ref": "f4384935-2135-47cd-bfa1-0bf2e0104399"
                }
            },
            {
                "type": "choices",
                "choices": {
                    "ids": [
                        "Enf2GgB4CEMV"
                    ],
                    "labels": [
                        "🧍‍♂️Raised in an individualist culture"
                    ],
                    "refs": [
                        "332c5ec2-4a63-4f5b-8742-31bd80e497a4"
                    ]
                },
                "field": {
                    "id": "pTMOjbjkbSWL",
                    "type": "multiple_choice",
                    "ref": "a56351d1-d292-4d96-bb95-7323219ee5f2"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "PmN145PWZJWk",
                    "label": "Not at all",
                    "ref": "85bd6416-2aef-4cfe-bbec-045fcbe108e3"
                },
                "field": {
                    "id": "DxXG5npFnjPd",
                    "type": "multiple_choice",
                    "ref": "1e9868b4-9c8c-41ad-af9a-d1cdafdc9915"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "zvBEMIh374bI",
                    "label": "Not at all",
                    "ref": "dba05692-a53c-40d5-a633-79e46f7ef70c"
                },
                "field": {
                    "id": "DEC8S8r60O1U",
                    "type": "multiple_choice",
                    "ref": "28963f0c-debd-4b55-b39e-46c56a6a6949"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "YQ8mp7bOF8NB",
                    "label": "Not at all",
                    "ref": "379f5435-7dde-45da-96a2-19777cdae9b4"
                },
                "field": {
                    "id": "7kQjFzstcJts",
                    "type": "multiple_choice",
                    "ref": "0df712be-e6db-4f67-9090-bc3f8acd03b1"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "2DKGjdNgUNME",
                    "label": "Not at all",
                    "ref": "b8682870-0757-48a5-9243-c221f50e3de9"
                },
                "field": {
                    "id": "uUQMfw2xRiQ4",
                    "type": "multiple_choice",
                    "ref": "571c3436-0da5-4b3e-9615-d7f5b5337f62"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "rg2e9agBmqvu",
                    "label": "Not at all",
                    "ref": "91c9109d-6be0-4768-99ac-cb920cdd70f4"
                },
                "field": {
                    "id": "G9LdjqKeO7f4",
                    "type": "multiple_choice",
                    "ref": "79b190b1-e1b5-4ae8-a883-74458baf2ba8"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "k2EKTGCbtdb4",
                    "label": "Not at all",
                    "ref": "c6184041-c7d2-4acb-bd7e-7caa2106c70d"
                },
                "field": {
                    "id": "YFkgwTszPtMN",
                    "type": "multiple_choice",
                    "ref": "038f9c71-97c7-4aa0-98a2-8a781c75a2fc"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "ISx77uyoJLxr",
                    "label": "Not at all",
                    "ref": "ab708488-909e-4440-a252-86c1841bfbf8"
                },
                "field": {
                    "id": "TKA1j8lE6SSd",
                    "type": "multiple_choice",
                    "ref": "1cf50bd4-aa7a-4672-8b50-d1ecf458ab55"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "Jwd7IRMVo2zF",
                    "label": "Not at all",
                    "ref": "8e828d22-0e66-420d-a0ee-b0371938b27a"
                },
                "field": {
                    "id": "TsZ80LFOtbCq",
                    "type": "multiple_choice",
                    "ref": "9bb34921-0926-46b9-b3fc-bd29d6987602"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "LJ6MnHyCXA8S",
                    "label": "Not at all",
                    "ref": "38719cc7-d21b-4159-a8d3-d4817b085ae1"
                },
                "field": {
                    "id": "3SCH6BP1SZWt",
                    "type": "multiple_choice",
                    "ref": "522d3b7a-7608-4ed2-8e65-36503f1bb0db"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "RLudVDDF3yOR",
                    "label": "Not at all",
                    "ref": "d5bf33ce-5108-47bb-929b-d21da743b00c"
                },
                "field": {
                    "id": "eca2CSO04vLl",
                    "type": "multiple_choice",
                    "ref": "990e62e6-0c9c-425e-88d2-65e1e9271341"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "YIvR3JhKhobh",
                    "label": "Not at all",
                    "ref": "fb8d9aa1-fe32-4e13-b308-cd22e483c722"
                },
                "field": {
                    "id": "chxgOkME9qj4",
                    "type": "multiple_choice",
                    "ref": "d7d36e9d-25e5-4e9f-be54-4db916a10891"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "5o7FSGSy09Kj",
                    "label": "Not at all",
                    "ref": "b8272bf6-1992-44eb-a2ff-ece13b9202a7"
                },
                "field": {
                    "id": "B3cxNBp1tpIq",
                    "type": "multiple_choice",
                    "ref": "7e560f59-a2f2-494d-8e6b-860741592d07"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "soGVbIy0xg0C",
                    "label": "Not at all",
                    "ref": "fb66fc9c-f87a-402b-bb4e-66fbf74d57ec"
                },
                "field": {
                    "id": "bvL83C6M9nb1",
                    "type": "multiple_choice",
                    "ref": "1fdc1b54-7abc-44e9-b6bd-a65dd0f7fe2a"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "UUvW9lZUW1EH",
                    "label": "Not at all",
                    "ref": "797de514-67d8-42f3-a334-b7b9fa723ecc"
                },
                "field": {
                    "id": "RdiG8vKXrbVB",
                    "type": "multiple_choice",
                    "ref": "449f9821-efaa-49e3-b632-4f4bc8a18a22"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "FWyj8JfvGZWO",
                    "label": "Not at all",
                    "ref": "ad57a751-8784-4daf-ac94-c65d60668999"
                },
                "field": {
                    "id": "98pYB4y1REbK",
                    "type": "multiple_choice",
                    "ref": "d6e8ce4f-84b6-4d5e-b584-6ab69fec5087"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "pUteyUejRcy5",
                    "label": "Not at all",
                    "ref": "9510ab45-fb0c-4fc6-a84d-409dda9a5615"
                },
                "field": {
                    "id": "yVJsRQvXsi1T",
                    "type": "multiple_choice",
                    "ref": "cdf74907-9bc3-48b1-b080-9f18a27b9d8f"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "ifUwuzqu6PVc",
                    "label": "Not at all",
                    "ref": "e66078e5-633c-4d73-8e66-e7ee5733c203"
                },
                "field": {
                    "id": "QtDBqAbfBRAR",
                    "type": "multiple_choice",
                    "ref": "7d1a2322-840c-494a-8155-0bdea0eefdb6"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "89DV1huvypPY",
                    "label": "Not at all",
                    "ref": "2423ac0e-c350-401d-a060-8bf34e636025"
                },
                "field": {
                    "id": "1l3TD4JycX7a",
                    "type": "multiple_choice",
                    "ref": "3d7046be-905b-4c67-af66-01ca3373c433"
                }
            },
            {
                "type": "text",
                "text": "PoC",
                "field": {
                    "id": "RngVovIqApk0",
                    "type": "short_text",
                    "ref": "f29960c6-2c0b-44e9-ae7f-8ace0d09c2f6"
                }
            },
            {
                "type": "number",
                "number": 35,
                "field": {
                    "id": "NFyGjLRsvOQb",
                    "type": "number",
                    "ref": "fe5e6540-7043-403b-9d01-cf655043622e"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "b2f6XULjo15V",
                    "label": "Male",
                    "ref": "5e637f08-39c1-4737-95ca-fe8230b6bd9c"
                },
                "field": {
                    "id": "clAn8i6OQOI3",
                    "type": "multiple_choice",
                    "ref": "0332dede-1cbf-4add-b4ed-aa9decd3f7e9"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "W3HQIOv0u3CG",
                    "label": "NY",
                    "ref": "67672563-0048-4906-88b5-c69d4443b2da"
                },
                "field": {
                    "id": "3AQyhzE0XBx5",
                    "type": "dropdown",
                    "ref": "35ff5a97-a750-4233-9820-26b671b1438e"
                }
            },
            {
                "type": "text",
                "text": "Hogwarts",
                "field": {
                    "id": "sHR59ObUeLCw",
                    "type": "short_text",
                    "ref": "b720b2a6-721a-4094-9a7b-49ddc6800fa1"
                }
            },
            {
                "type": "text",
                "text": "Mondays 6-7pm, Thursdays 4-6pm ET",
                "field": {
                    "id": "V7DQU2HoEvfK",
                    "type": "short_text",
                    "ref": "1c2371f5-54ac-4153-84f6-6d14c280bf33"
                }
            },
            {
                "type": "choices",
                "choices": {
                    "ids": [
                        "i5rgtOldEqa2"
                    ],
                    "labels": [
                        "Instagram"
                    ],
                    "refs": [
                        "c5357713-9dc8-4057-95af-4c042be9bb41"
                    ]
                },
                "field": {
                    "id": "ntVzKN7vWQhO",
                    "type": "multiple_choice",
                    "ref": "5c32892f-fd6a-4085-9a10-1721a570c09f"
                }
            },
            {
                "type": "choice",
                "choice": {
                    "id": "9ldceMwTC7Op",
                    "label": "I accept",
                    "ref": "cacbbd45-74ee-4f5a-beb4-2d5392c2d655"
                },
                "field": {
                    "id": "NMN7aB4l64kj",
                    "type": "multiple_choice",
                    "ref": "20abed52-aa6a-44cf-821a-b924be43cf3d"
                }
            }
        ],
        "ending": {
            "id": "RPWmHaDFESDu",
            "ref": "542a7611-28f2-4c95-adf4-75f0279b5d11"
        }
    }
}

__jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
__security_schemes = {"jwt": __jwt}

info = Info(title="SolHealth API", version="1.0.0")
app = OpenAPI(__name__, info=info, security_schemes=__security_schemes)

app.register_api(client_api)
app.register_api(appointment_api)
app.register_api(therapist_api)

@app.post('/hook', tags=[Tag(name="Webhook")], responses={200: SuccessResponse}, summary="Webhook for typeform")
def typeform_webhook():
    print(request)
    # response_json = request.get_json()
    questions_json = response_json['form_response']['definition']['fields']
    questions = dict(map(lambda item: (item['ref'], item), questions_json))
    answers = response_json['form_response']['answers']
    json: dict = {}
    for answer in answers:
        question = questions[answer['field']['ref']]
        json[question['id']] = {
            'ref': answer['field']['ref'],
            'answer': answer[answer['type']] if answer['type'] != 'multiple_choice' else answer['choices'],
            'title': question['title'],
            'type': question['type']
        }
    result = create_new_form(json)
    print(result)
    return jsonify({"success": result}), 200 if result else 417

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)