import pytest
from ucho.rules_engine import evaluate_rules

# TODO: fix use case
# @pytest.mark.parametrize(
#     "rules", [
#         {
#             "rule": "msg[0]",
#             "result": False,
#             "context": {
#                 "msg": []
#             }
#         }
#     ]
# )
# def test_with_exception(rules):
#     assert rules['result'] == evaluate_rules(rules['rule'], context=rules['context'])


@pytest.mark.parametrize(
    "rules",
    [
        {"rule": "1 == 1", "result": True, "context": None},
        {
            "rule": "'live' in message ",
            "result": True,
            "context": {"message": "live and let live"},
        },
        {
            "rule": "msg['commits'][0] != '0000000000000000000000000000000000000000'",
            "result": True,
            "context": {
                "msg": {
                    "newrev": "d95ceb35fc20b0db49c6ca81f275b5a9151228b2",
                    "commits": ["d95ceb35fc20b0db49c6ca81f275b5a9151228b2"],
                }
            },
        },
        {
            "rule": "msg['pullrequest']['comments'][-1]['notification'] or '[citest]' in msg['pullrequest']['comments'][-1]['comment']",
            "result": True,
            "context": {
                "msg": {
                    "agent": "dhodovsk",
                    "pullrequest": {
                        "comments": [
                            {
                                "comment": "/cc @gandalf",
                                "notification": False,
                            },
                            {
                                "comment": "You shall not pass!",
                                "notification": False,
                            },
                            {"comment": "[citest]", "notification": False},
                        ]
                    },
                }
            },
        },
        {"rule": "1 == 2", "result": False, "context": None},
        {
            "rule": "'die' in message ",
            "result": False,
            "context": {"message": "live and let live"},
        },
        {
            "rule": "msg['commits'][0] != '0000000000000000000000000000000000000000'",
            "result": False,
            "context": {
                "msg": {
                    "newrev": "d95ceb35fc20b0db49c6ca81f275b5a9151228b2",
                    "commits": ["0000000000000000000000000000000000000000"],
                }
            },
        },
    ],
)
def test_true(rules):
    assert rules["result"] == evaluate_rules(rules["rule"], context=rules["context"])
