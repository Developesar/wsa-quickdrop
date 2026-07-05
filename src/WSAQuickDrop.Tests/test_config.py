from __future__ import annotations

from WSAQuickDrop.config import AppConfig, parse_endpoint


def test_config_serialization_round_trip(tmp_path) -> None:
    config = AppConfig(
        adbPath=r"C:\Android\platform-tools\adb.exe",
        wsaHost="127.0.0.1",
        wsaPort=58526,
        defaultRouteMode="pictures",
        lastDestination="/sdcard/Pictures/Custom",
        autoMediaScan=False,
        closeAfterSend=True,
        theme="dark",
        language="fa",
        optionalTargetAppPackage="ir.persiandots.ocr",
        appendTimestampOnCollision=True,
    )
    config.save(tmp_path)
    loaded = AppConfig.load(tmp_path)
    assert loaded == config


def test_parse_endpoint_defaults_port() -> None:
    assert parse_endpoint("127.0.0.1") == ("127.0.0.1", 58526)
    assert parse_endpoint("127.0.0.1:1234") == ("127.0.0.1", 1234)
