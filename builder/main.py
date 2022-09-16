"""
    Build script for test.py
    test-builder.py
"""

from os.path import join
from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

env = DefaultEnvironment()

print( '<<<<<<<<<<<< ' + env.BoardConfig().get("name").upper() + " 2022 Lucas Teske >>>>>>>>>>>>" )

target_elf = env.BuildProgram()
target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)
upload = env.Alias(["upload"], target_bin, "$UPLOADCMD")
AlwaysBuild(upload)
Default(target_bin)