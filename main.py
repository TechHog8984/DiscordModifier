import sys, os, re;
from pathlib import Path;

last_message = "";

discord_path = os.getenv("LOCALAPPDATA") + "\\Discord";
for path in os.listdir(discord_path):
    if path[:3] == "app" and Path(discord_path + "\\" + path).is_dir():
        app_path = discord_path + "\\" + path;

modules_path = app_path + "\\modules";
core_path = modules_path + "\\discord_desktop_core-1\\discord_desktop_core";
core_backup_path = core_path + "\\backup.discord_modifier_backup";
core_decompiled_path = core_path + "\\decompiled";
core_asar_path = core_path + "\\core.asar";

core_app_path = core_decompiled_path + "\\app";
core_app_index_js_path = core_app_path + "\\index.js";
core_app_main_screen_js_path = core_app_path + "\\mainScreen.js";
core_app_system_tray_js_path = core_app_path + "\\systemTray.js";

resources_path = app_path + "\\resources";
app_backup_path = resources_path + "\\backup.discord_modifier_backup";
app_decompiled_path = resources_path + "\\decompiled";
app_asar_path = resources_path + "\\app.asar";

def read(path):
    result = "";
    with open(path) as f:
        result = f.read();
        f.close();
    return result;
def write(path, contents):
    with open(path, "w") as f:
        f.write(contents);
        f.close();

def copy(path_from, path_to):
    with open(path_from, "rb") as from_file:
        with open(path_to, "wb") as to_file:
            to_file.write(from_file.read());
            to_file.close();
        from_file.close();

def f_createCoreBackup():
    global last_message;
    try:
        copy(core_asar_path, core_backup_path);
        last_message = "Successfully created core backup!";
    except Exception as e:
        last_message = f"Failed to create core backup: {e}";
def f_createAppBackup():
    global last_message;
    try:
        copy(app_asar_path, app_backup_path);
        last_message = "Successfully created app backup!";
    except Exception as e:
        last_message = f"Failed to create app backup: {e}";

def f_restoreCoreBackup():
    global last_message;
    try:
        if Path(core_backup_path).exists():
            copy(core_backup_path, core_asar_path);
            last_message = "Successfully restored core asar!";
        else:
            raise Exception("No core backup found! Did you forget to create one?");
    except Exception as e:
        last_message = f"Failed to restore core backup: {e}";
def f_restoreAppBackup():
    global last_message;
    try:
        if Path(app_backup_path).exists():
            copy(app_backup_path, app_asar_path);
            last_message = "Successfully restored app asar!";
        else:
            raise Exception("No app backup found! Did you forget to create one?");
    except Exception as e:
        last_message = f"Failed to restore app backup: {e}";

def f_decompileCore():
    global last_message;
    try:
        os.system(f'npx asar e "{core_asar_path}" "{core_decompiled_path}"');
        last_message = "Successfully decompiled core.asar";
    except Exception as e:
        last_message = f"Failed to decompile core.asar: {e}";
def f_decompileApp():
    global last_message;
    try:
        os.system(f'npx asar e "{app_asar_path}" "{app_decompiled_path}"');
        last_message = "Successfully decompiled app.asar";
    except Exception as e:
        last_message = f"Failed to decompile app.asar: {e}";

def f_openCoreDecompiledFolder():
    try:
        os.system("explorer " + core_decompiled_path);
        last_message = "Opened decompiled core folder";
    except Exception as e:
        last_message = f"Failed to open decompiled core folder: {e}";
def f_openAppDecompiledFolder():
    try:
        os.system("explorer " + app_decompiled_path);
        last_message = "Opened decompiled app folder";
    except Exception as e:
        last_message = f"Failed to open decompiled app folder: {e}";

def f_compileCore():
    global last_message;
    try:
        if not Path(core_backup_path).exists():
            raise Exception("No core backup found! Did you forget to create one?");
        os.system(f'npx asar p "{core_decompiled_path}" "{core_asar_path}"');
        last_message = "Successfully compiled core";
    except Exception as e:
        last_message = f"Failed to compile core: {e}";
def f_compileApp():
    global last_message;
    try:
        if not Path(app_backup_path).exists():
            raise Exception("No app backup found! Did you forget to create one?");
        os.system(f'npx asar p "{app_decompiled_path}" "{app_asar_path}"');
        last_message = "Successfully compiled app";
    except Exception as e:
        last_message = f"Failed to compile app: {e}";

def f_applyDeveloperToolsPatch():
    global last_message;
    try:
        if not Path(core_decompiled_path).exists():
            f_decompileCore();

        write(core_app_index_js_path, re.sub(
            "buildInfo\.releaseChannel === 'stable' \? enableDevtoolsSetting : true;",
            "true;",
            read(core_app_index_js_path)
        ));
        write(core_app_main_screen_js_path, re.sub(
            "_buildInfo\.buildInfo\.releaseChannel === 'stable' \? settings\.get\('DANGEROUS_ENABLE_DEVTOOLS_ONLY_ENABLE_IF_YOU_KNOW_WHAT_YOURE_DOING', false\) : ",
            "",
            read(core_app_main_screen_js_path)
        ));

        last_message = "Successfully applied developer tools patch";
    except Exception as e:
        last_message = f"Failed to apply Developer Tools patch: {e}";

def addToSystemTray(label, click):
    global last_message;
    try:
        # new_menu_item = f"menuItems['{label}'] = {{label: '{label}', type: 'normal', click: () => {{{click}}}}}";
        new_menu_item = "menuItems['" + label + "'] = {label: '" + label + "', type: 'normal', click: () => {" + click + "}};";
        contents = read(core_app_system_tray_js_path);
        contents = re.sub(
            "menuItems\[MenuItems\.QUIT\] =",
            new_menu_item + "\n  menuItems[MenuItems.QUIT] =",
            contents
        );
        contents = re.sub(
            "separator, menuItems\[MenuItems\.QUIT\]",
            "separator, menuItems['" + label + "'], menuItems[MenuItems.QUIT]",
            contents
        );
        contents = re.sub(
            ", menuItems\[MenuItems\.QUIT\]",
            ", separator, menuItems[MenuItems.QUIT]",
            contents
        );
        write(core_app_system_tray_js_path, contents);
        last_message = f"Successfully added '{label}' to system tray";
    except Exception as e:
        last_message = f"Failed to add '{label}' to system tray: {e}";

def f_addDeveloperToolsButtonToSystemTray():
    f_applyDeveloperToolsPatch();
    addToSystemTray("Open Developer Tools", "const list = _electron.BrowserWindow.getAllWindows(); if (list && list[0]) list[0].toggleDevTools();");

function_list = [
    f_createCoreBackup, f_restoreCoreBackup, f_decompileCore, f_openCoreDecompiledFolder, f_compileCore,
    f_createAppBackup, f_restoreAppBackup, f_decompileApp, f_openAppDecompiledFolder, f_compileApp,
    f_applyDeveloperToolsPatch, f_addDeveloperToolsButtonToSystemTray
];

def printMessage():
    os.system("cls");

    print("""Welcome to techhog's DiscordModifier
Your choices are:
    Exit (0) - Quits the program.
    Core:
        Backup (1) - Create a backup of core.asar.
        Restore (2) - Restore the core.asar backup created, if present.
        Decompile (3) - Decompiles core.asar.
        Open Decompiled Folder (4) - Opens the decompiled folder in file explorer.
        Compile (5) - Compiles the decompiled core to core.asar, overwriting the current one (HAVE A BACKUP!)
    App:
        Backup (6) - Create a backup of app.asar.
        Restore (7) - Restore the app.asar backup created, if present.
        Decompile (8) - Decompiles app.asar.
        Open Decompiled Folder (9) - Opens the decompiled folder in file explorer.
        Compile (10) - Compiles the decompiled app to app.asar, overwriting the current one (HAVE A BACKUP!)

    Auto Core Modifications: Decompile core (if not already decompiled) and apply certain modifications
        Note: you will need to compile afterward for changes to take place.
        Enable Developer Tools (11)
            Enables Developer Tools.
        Add Developer Tools Button to System Tray (12)
            Enables Developer Tools and adds a button the system tray that will open them.
""");
    global last_message;
    if last_message:
        print("MESSAGE: " + last_message + "\n");
    last_message = None;

def loop():
    printMessage();
    choice = input("Choice: ");
    try:
        choice = int(choice);
    except:
        return loop();

    printMessage();
    if choice == 0:
        return;
    elif choice > 0 and choice <= len(function_list) + 1:
        function_list[choice - 1]();
    else:
        global last_message;
        last_message = f"Invalid option {choice}";

    loop();

loop();
