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

require_version(45)


class Builder(OpenHomeBuilder):
    output_dir = "build/packages"
    build_dir = "build"

    def setup(self):
        self.nuget_server = self.env.get('NUGET_SERVER')
        self.nuget_api_key = self.env.get('NUGET_API_KEY')

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
        self.pack_nuget('src/ohNet.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProxies.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProviders.nuspec', '.')

    def publish(self):
        self.publish_nuget(os.path.join('build', 'packages', '*.nupkg'), self.nuget_api_key, self.nuget_server)
