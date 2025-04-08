import pytest

from scripts.bluetooth_utils import DevicesManager


@pytest.fixture
def manager():
    return DevicesManager()


def test_extract_mac(manager):
    assert (
        manager._extract_mac("Device AA:BB:CC:DD:11:22 WF-1000XM5")
        == "AA:BB:CC:DD:11:22"
    )
    assert manager._extract_mac("Device AA:BB WF-1000XM5") == "AA:BB"
    assert manager._extract_mac("AA:BB BB:CC DD:FF") == ""


def test_is_valid_mac_address(manager):
    assert manager._is_valid_mac_address("AA:BB:CC:DD:11:22")
    assert manager._is_valid_mac_address("AA-BB-CC-DD-11-22")
    assert not manager._is_valid_mac_address("AA:BB:CC:DD-11-22")
    assert not manager._is_valid_mac_address("AA:BB")
