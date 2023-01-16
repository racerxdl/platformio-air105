"""
    Build script for test.py
    test-builder.py
"""

from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()

print( '<<<<<<<<<<<< ' + env.BoardConfig().get("name").upper() + " 2022 Lucas Teske >>>>>>>>>>>>" )

target_elf = env.BuildProgram()
target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)
upload = env.Alias(["upload"], target_bin, "$UPLOADCMD")

AlwaysBuild(upload)
Default(target_bin)

upload_protocol = env.subst("$UPLOAD_PROTOCOL")

if upload_protocol == "mhboot":
    if not env.subst("$UPLOAD_PORT"):
         env.Replace(UPLOAD_PORT="/dev/ttyUSB0")
    env.Replace(
        UPLOADER=join(
            platform.get_package_dir("air105-uploader") or "",
            "upload.py"),
        UPLOADCMD='"$PYTHONEXE" "$UPLOADER" "$UPLOAD_PORT" $SOURCE'
    )
    env.Execute("$PYTHONEXE -m pip install pycryptodome")
    if set(["uploadfs", "uploadfsota"]) & set(COMMAND_LINE_TARGETS):
        env.Append(UPLOADERFLAGS=["--spiffs"])
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]