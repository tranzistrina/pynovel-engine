from vnengine.cli import main


def test_assets_scan_command(tmp_path, monkeypatch, capsys):
    (tmp_path / "art.png").write_bytes(b"png")
    (tmp_path / "music.ogg").write_bytes(b"ogg")
    monkeypatch.setattr("sys.argv", ["pynovel", "assets", "scan", str(tmp_path)])
    main()
    out = capsys.readouterr().out
    assert "Indexed 2 assets" in out
    assert "image: 1" in out
    assert "audio: 1" in out
    assert (tmp_path / ".pynovel" / "assets.json").exists()
