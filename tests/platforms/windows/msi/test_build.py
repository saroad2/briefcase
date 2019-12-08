# import sys
from unittest import mock

import pytest

from briefcase.platforms.windows.msi import WindowsMSIBuildCommand


@pytest.fixture
def build_command(tmp_path):
    command = WindowsMSIBuildCommand(base_path=tmp_path)
    command.subprocess = mock.MagicMock()
    command.candle_exe = tmp_path / 'wix' / 'bin' / 'candle.exe'
    command.light_exe = tmp_path / 'wix' / 'bin' / 'light.exe'
    command.heat_exe = tmp_path / 'wix' / 'bin' / 'heat.exe'
    return command


def test_build_msi(build_command, first_app_config, tmp_path):
    "A Wwindows app can be packaged as an MSI"

    build_command.build_app(first_app_config)

    build_command.subprocess.run.assert_has_calls([
        # Collect manifest
        mock.call(
            [
                str(tmp_path / 'wix' / 'bin' / 'heat.exe'),
                "dir",
                "src",
                "-nologo",
                "-gg",
                "-sfrag",
                "-sreg",
                "-srd",
                "-scom",
                "-dr", "first_ROOTDIR",
                "-cg", "first_COMPONENTS",
                "-var", "var.SourceDir",
                "-out", "first-manifest.wxs",
            ],
            check=True,
            cwd=str(tmp_path / 'windows' / 'First App'),
        ),
        # Compile MSI
        mock.call(
            [
                str(tmp_path / 'wix' / 'bin' / 'candle.exe'),
                "-nologo",
                "-ext", "WixUtilExtension",
                "-ext", "WixUIExtension",
                "-dSourceDir=src",
                "first.wxs",
                "first-manifest.wxs",
            ],
            check=True,
            cwd=str(tmp_path / 'windows' / 'First App'),
        ),

        # Link MSI
        mock.call(
            [
                str(tmp_path / 'wix' / 'bin' / 'light.exe'),
                "-nologo",
                "-ext", "WixUtilExtension",
                "-ext", "WixUIExtension",
                "-o", str(tmp_path / 'windows' / 'First App-0.0.1.msi'),
                "first.wixobj",
                "first-manifest.wixobj",
            ],
            check=True,
            cwd=str(tmp_path / 'windows' / 'First App'),
        ),
    ])
