import os
import shutil
import time
import nbt
import urllib.request
import json


class PterodactylControl:

    def __init__(self, server_location):
        self.srv = server_location

    def setupFromZIP(self, zip_location):
        temp_path = "./tmp"
        shutil.unpack_archive(zip_location, temp_path)
        level_check = os.path.join(temp_path, "level.dat")
        if os.path.exists(level_check):
            res = self.setupWorld(temp_path)
            shutil.rmtree(temp_path)
            return res
        else:
            for check_dir in os.listdir(temp_path):
                check_dir = os.path.join(temp_path, check_dir)
                level_check = os.path.join(check_dir, "level.dat")
                print(level_check)
                if os.path.exists(level_check):
                    res = self.setupWorld(check_dir)
                    shutil.rmtree(temp_path)
                    return res
            print("No valid world file was found")
            shutil.rmtree(temp_path)
            return False

    def setupWorld(self, world_location):
        if not os.path.isdir(self.srv):
            os.mkdir(self.srv)
        new_location = os.path.join(self.srv, "world")
        if os.path.isdir(new_location):
            new_location2 = os.path.join(self.srv, "world-"+str(int(time.time())))
            os.rename(new_location, new_location2)
        os.mkdir(new_location)
        self.copytree(world_location, new_location)
        if os.path.exists(os.path.join(new_location, "icon.png")):
            world_icon = os.path.join(new_location, "icon.png")
            srv_icon = os.path.join(self.srv, "icon.png")
            if os.path.exists(srv_icon):
                os.remove(srv_icon)
            shutil.copyfile(world_icon,srv_icon)
        self.setupServer()
        return True

    def setupServer(self):
        nbt_location = os.path.join(self.srv, os.path.join("world","level.dat"))
        nbtfile = nbt.nbt.NBTFile(nbt_location, 'rb')
        version = nbtfile["Data"]["Version"]["Name"]
        print("Minecraft Map Uses: "+str(version))
        jar_location = os.path.join(self.srv, "server.jar")
        if os.path.exists(jar_location):
            os.remove(jar_location)
        print("Finding jar from Mojang directly")
        with urllib.request.urlopen("https://launchermeta.mojang.com/mc/game/version_manifest.json") as url:
            data = json.loads(url.read().decode())
            for versionData in data["versions"]:
                # version = data["versions"][version_index]
                #print("Checking")
                if (str(versionData["id"]) == str(version)):
                    print("Found Matching version in version_manifest.json")
                    with urllib.request.urlopen(str(versionData["url"])) as url:
                        data = json.loads(url.read().decode())
                        print("Should Download From: "+data["downloads"]["server"]["url"])
                        with urllib.request.urlopen(data["downloads"]["server"]["url"]) as response, open(jar_location, 'wb') as out_file:
                            shutil.copyfileobj(response, out_file)

    def copytree(self, src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
