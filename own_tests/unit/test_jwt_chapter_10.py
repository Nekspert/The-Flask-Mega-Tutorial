import jwt


def test_json_web_token():
    token = jwt.encode({"test": "b"}, "test", algorithm="HS256")
    assert {"test": "b"} == jwt.decode(token, "test", algorithms=["HS256"])
