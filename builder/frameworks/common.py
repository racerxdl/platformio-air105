import os
from os.path import join, normpath, basename
from shutil import copyfile
from colorama import Fore
from SCons.Script import DefaultEnvironment, Builder, ARGUMENTS

binary_type_info = []

def do_copy(src, dst, name):
    if False == os.path.isfile( join(dst, name) ):
        copyfile( join(src, name), join(dst, name) )

def do_mkdir(path, name):
    dir = join(path, name)
    if False == os.path.isdir( dir ):
        try:
            os.mkdir(dir)
        except OSError:
            print ("[ERROR] Creation of the directory %s failed" % dir)
            exit(1)
    return dir

def ini_file(env):
    ini = join(env.subst("$PROJECT_DIR"), 'platformio.ini')
    f = open(ini, "r")
    txt = f.read()
    f.close()
    f = open(ini, "a+")
    if 'monitor_port'  not in txt: f.write("\n;monitor_port = SERIAL_PORT\n")
    if 'monitor_speed' not in txt: f.write(";monitor_speed = 115200\n")
    if 'monitor_rts'   not in txt: f.write("monitor_rts = 0 ; AIR105 board has inverted RTS\n")
    if 'build_flags'   not in txt: f.write("\n;build_flags = \n")
    if 'lib_deps'      not in txt: f.write("\n;lib_deps = \n")
    f.close()

def dev_create_template(env):
    ini_file(env)
    src = join(env.PioPlatform().get_package_dir("framework-megahunt"), "templates")
    dst = do_mkdir( env.subst("$PROJECT_DIR"), "include" )

    if "freertos" in env.GetProjectOption("lib_deps", []) or "USE_FREERTOS" in env.get("CPPDEFINES"):
        do_copy(src, dst, "FreeRTOSConfig.h")

    if "VFS" in env.GetProjectOption("lib_deps", []) or "USE_VFS" in env.get("CPPDEFINES"):
        do_copy(src, dst, "vfs_config.h")

    if 'APPLICATION'== env.get("PROGNAME"):
        if "fatfs" in env.GetProjectOption("lib_deps", []):
            do_copy(src, dst, "ffconf.h")
        dst = do_mkdir( env.subst("$PROJECT_DIR"), join("include", "megahunt") )
        do_copy(src, dst, "config_autogen.h" )
        dst = join(env.subst("$PROJECT_DIR"), "src")
        if False == os.path.isfile( join(dst, "main.cpp") ):
            do_copy(src, dst, "main.c" )

    if 'BOOT-2'== env.get("PROGNAME"):
        dst = do_mkdir( env.subst("$PROJECT_DIR"), join("include", "megahunt") )
        do_copy(src, dst, "config_autogen.h" )

def dev_nano(env):
    nano = ["-specs=nano.specs", "-specs=nosys.specs", "-u", "_printf_float", "-u", "_scanf_float" ]
    if len(nano) > 0: print('  * SPECS        :', nano[0][7:])
    else:             print('  * SPECS        : default')
    return nano

def dev_compiler(env, application_name = 'APPLICATION'):
    env.sdk = env.BoardConfig().get("build.sdk", "SDK") # get/set default SDK
    print()
    print( Fore.BLUE + "%s Megahunt ( Air105 - %s )" % (env.platform.upper(), env.sdk.upper()) )
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
        AR="arm-none-eabi-ar",
        AS="arm-none-eabi-as",
        CC="arm-none-eabi-gcc",
        GDB="arm-none-eabi-gdb",
        CXX="arm-none-eabi-g++",
        OBJCOPY="arm-none-eabi-objcopy",
        RANLIB="arm-none-eabi-ranlib",
        SIZETOOL="arm-none-eabi-size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.boot2|\.rodata)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.ram_vector_table)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        PROGSUFFIX=".elf",
        PROGNAME = application_name
    )
    # "-mfloat-abi=hard"
    cortex = ["-mcpu=cortex-m4","-mfpu=fpv4-sp-d16","-mfloat-abi=softfp","-mthumb"]
    env.heap_size = env.BoardConfig().get("build.heap", "2048")
    optimization = env.BoardConfig().get("build.optimization", "-Os")
    stack_size = env.BoardConfig().get("build.stack", "2048")
    print('  * OPTIMIZATION :', optimization)
    print('  * STACK        :', stack_size)
    print('  * HEAP         :', env.heap_size)
    env.Append(
        ASFLAGS=[ cortex, "-x", "assembler-with-cpp" ],
        CPPPATH = [
            join("$PROJECT_DIR", "src"),
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include"),
            join( env.framework_dir, "megahunt", "mh1903"),
            join( env.framework_dir, "megahunt", "newlib"),
            join( env.framework_dir, env.sdk, "include"),
            join( env.framework_dir, env.sdk, "include", "hal"),
            join( env.framework_dir, env.sdk, "usb", "include"),
            join( env.framework_dir, env.sdk, "device", "include"),
            join( env.framework_dir, env.sdk, "lib", "heap"),
            join( env.framework_dir, env.sdk, "cmsis", "include"), #
        ],
        CPPDEFINES = [
            "NDEBUG",
            "CORTEX_M4",
            "__AIR105_BSP__",
            "CMB_CPU_PLATFORM_TYPE=CMB_CPU_ARM_CORTEX_M4",
            "HSE_VALUE=12000000"
        ],
        CCFLAGS = [
            cortex,
            optimization,
            "-fdata-sections",
            "-ffunction-sections",
            "-Wall",
            "-Wextra",
            "-Wfatal-errors",
            "-Wno-sign-compare",
            "-Wno-type-limits",
            "-Wno-unused-parameter",
            "-Wno-unused-function",
            "-Wno-unused-but-set-variable",
            "-Wno-unused-variable",
            "-Wno-unused-value",
            "-Wno-strict-aliasing",
            "-Wno-maybe-uninitialized"
        ],
        CFLAGS = [
            cortex,
            "-std=c99",
            "-Wno-discarded-qualifiers",
            "-Wno-ignored-qualifiers",
            "-Wno-attributes", #
        ],
        CXXFLAGS = [
            "-fno-rtti",
            "-fno-exceptions",
            "-fno-threadsafe-statics",
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
        ],
        LINKFLAGS = [
            cortex,
            optimization,
            "-Xlinker", "--gc-sections",
            "-Wl,--gc-sections",
            dev_nano(env)
        ],
        LIBSOURCE_DIRS = [ join(env.framework_dir, "library"),  ],
        LIBPATH        = [ join(env.framework_dir, "library"), join("$PROJECT_DIR", "lib") ],
        LIBS           = ['m', 'gcc'],
        BUILDERS = dict(
            ElfToBin = Builder(
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY", "-O",  "binary",
                    "$SOURCES", "$TARGET",
                ]), "Building $TARGET"),
                suffix = ".bin"
            )
        ),
    )

def add_libraries(env):
    env.Append( CPPPATH = [ join(env.framework_dir, "include"), join(env.framework_dir, "include","hal"), ])
    if "freertos" in env.GetProjectOption("lib_deps", []) or "USE_FREERTOS" in env.get("CPPDEFINES"):
        env.Append(  CPPPATH = [ join(join(env.framework_dir, "library", "freertos"), "include") ]  )
        print('  * RTOS         : FreeRTOS')
        if "USE_FREERTOS" not in env.get("CPPDEFINES"):
            env.Append(  CPPDEFINES = [ "USE_FREERTOS"] )

    if "cmsis-dap" in env.GetProjectOption("lib_deps", []):
        env.Append( CPPDEFINES = [ "DAP" ], )

def add_binary_type(env):
    binary_type = env.BoardConfig().get("build.binary_type", 'default')
    env.address = env.BoardConfig().get("build.address", "empty")
    linker      = env.BoardConfig().get("build.linker", "empty")
    env.address = '0x10001000'
    linker = 'mh1903.ld'
    env.Append( LDSCRIPT_PATH = join(env.framework_dir, "ldscripts", linker) )
    binary_type_info.append(linker)
    binary_type_info.append(env.address)
    print('  * BINARY TYPE  :' , binary_type, binary_type_info  )
    add_libraries(env)

def dev_finalize(env):
    env.BuildSources( join("$BUILD_DIR", env.platform, "mh1903"), join(env.framework_dir, "mh1903") )
    add_binary_type(env)
    add_sdk(env)
    env.Append(LIBS = env.libs)
    print()

def add_sdk(env):
    filter = [ "+<*>",
        "-<lib>",
        "-<newlib>"
    ]
    env.BuildSources( join("$BUILD_DIR", env.platform, env.sdk), join(env.framework_dir, env.sdk), src_filter = filter )
    env.BuildSources( join("$BUILD_DIR", env.platform, "megahunt"), join(env.framework_dir, "megahunt"), src_filter = filter )
