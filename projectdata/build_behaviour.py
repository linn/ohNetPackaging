# Defines the build behaviour for continuous integration builds.

import sys
import os
import shutil
import glob

try:
    from ci import (OpenHomeBuilder, require_version)
except ImportError:
    print "You need to update ohDevTools."
    sys.exit(1)

require_version(45)


class Builder(OpenHomeBuilder):
    output_dir = "build/packages"

    def setup(self):
        self.nuget_server = self.env.get('NUGET_SERVER')
        self.nuget_api_key = self.env.get('NUGET_API_KEY')

    def clean(self):
        if os.path.isdir(self.output_dir):
            shutil.rmtree(self.output_dir)

    def build(self):
        os.makedirs(self.output_dir)
        self.pack_nuget('src/ohNet.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProxies.nuspec', '.')
        self.pack_nuget('src/ohNetGeneratedProviders.nuspec', '.')

    def publish(self):
        self.publish_nuget(os.path.join('build', 'packages', '*.nupkg'), self.nuget_api_key, self.nuget_server)
