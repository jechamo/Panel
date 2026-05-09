from app.runners.templating import render


def test_render_returns_empty_string_for_missing_keys():
    assert render("hi {{nope}}", {}) == "hi "


def test_render_top_level_value():
    assert render("user is {{a}}", {"a": "alice"}) == "user is alice"


def test_render_nested_path():
    ctx = {"u": {"name": "alice", "addr": {"city": "NYC"}}}
    assert render("city: {{u.addr.city}}", ctx) == "city: NYC"


def test_render_serialises_complex_values():
    out = render("x={{u}}", {"u": {"a": 1}})
    assert out.startswith('x={"a":')
    assert "1" in out


def test_render_handles_no_placeholders():
    assert render("plain text", {"a": 1}) == "plain text"


def test_render_handles_empty_input():
    assert render("", {"a": 1}) == ""
    assert render(None, {"a": 1}) == ""  # type: ignore[arg-type]


def test_render_with_dashes_and_underscores_in_node_id():
    assert render("v={{node-1.user_id}}", {"node-1": {"user_id": 42}}) == "v=42"
