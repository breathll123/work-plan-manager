import app.platform_utils as pu


def test_open_missing_path_returns_error(tmp_path):
    msg = pu.open_path(str(tmp_path / "不存在"))
    assert msg is not None and "不存在" in msg


def test_open_existing_path_calls_launcher(tmp_path, monkeypatch):
    called = {}
    monkeypatch.setattr(pu, "_launch", lambda p: called.setdefault("p", p))
    assert pu.open_path(str(tmp_path)) is None
    assert called["p"] == str(tmp_path)


def test_launcher_failure_returns_error(tmp_path, monkeypatch):
    def boom(p):
        raise OSError("no handler")

    monkeypatch.setattr(pu, "_launch", boom)
    msg = pu.open_path(str(tmp_path))
    assert msg is not None and "无法打开" in msg


def test_path_exists(tmp_path):
    assert pu.path_exists(str(tmp_path)) is True
    assert pu.path_exists(str(tmp_path / "x")) is False
