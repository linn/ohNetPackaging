# Defines the build behaviour for continuous integration builds.

import sys
import os
import shutil
import glob
import subprocess

try:
    from ci import (OpenHomeBuilder, require_version)
except ImportError:
    print "You need to update ohDevTools."
    sys.exit(1)

require_version(67)


class Builder(OpenHomeBuilder):
    output_dir = "build/packages"
    build_dir = "build"

    def setup(self):
        self.nuget_api_key = self.env.get('NUGET_API_KEY')
		
        # write release version in dependencies.json
        f1 = open('projectdata/dependencies.json', 'r')
        c = f1.read() % {'ohnet_version' : self.env.get('OHNET_VERSION'), 'ohnet_generated_version' : self.env.get('OHNET_GENERATED_VERSION')}
        f1.close()
		
        f2 = open('projectdata/dependencies.json', 'w')
        f2.write(c)
        f2.close()

    def clean(self):
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)

    def build(self):
        os.makedirs(self.build_dir)
        os.makedirs(self.output_dir)
        iosFatBinaryDir = os.path.join(self.build_dir, 'ios/arm-universal/ohNet/lib')
        os.makedirs(iosFatBinaryDir)
        architectures = ['armv7', 'arm64']
        archives = str.join(" ", ["./dependencies/ios/%s/ohNet/lib/libohNetCore.a" % (a) for a in architectures])
        libtoolcmd = "/usr/bin/libtool -static %s -o \"%s/libohNetCore.a\"" % (archives, iosFatBinaryDir)
        print libtoolcmd
        subprocess.check_call(libtoolcmd, cwd=os.getcwd(), shell=True)

        iosFatBinaryDir = os.path.join(self.build_dir, 'ios/x86-universal/ohNet/lib')
        os.makedirs(iosFatBinaryDir)
        architectures = ['x86', 'x64']
        archives = str.join(" ", ["./dependencies/ios/%s/ohNet/lib/libohNetCore.a" % (a) for a in architectures])
        libtoolcmd = "/usr/bin/libtool -static %s -o \"%s/libohNetCore.a\"" % (archives, iosFatBinaryDir)
        print libtoolcmd
        subprocess.check_call(libtoolcmd, cwd=os.getcwd(), shell=True)

        self.pack_nuget('src/ohNet.nuspec', '.')
        self.pack_nuget('src/ohNet.NET.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProxies.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProviders.nuspec', '.')

    def publish(self):
        self.publish_nuget(os.path.join('build', 'packages', '*.nupkg'), self.nuget_api_key, 'https://api.nuget.org/v3/index.json')
